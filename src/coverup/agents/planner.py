"""UCB Planner – Upper Confidence Bound target selection for CoverAgent-ML.

Selects which focal target (code segment) to work on next based on
estimated reward (coverage gain potential) vs. exploration.

Each "arm" corresponds to a code segment.  The planner tracks:
  - ``p_success``:  empirical probability the segment compiles & runs
  - ``mean_gain``:  average coverage delta *when successful*
  - ``pulls``:      number of times this segment was attempted
  - ``plateau``:    how many consecutive useless (U) outcomes

The scoring formula separates compile-success from gain:

    score = UCB(p_success) × UCB(gain) × (1 - plateau_penalty) × recency

Plateau detection: arms with ≥3 consecutive useless (compiles ok but
gains nothing) are "frozen" — they still have a small exploration
chance but are ranked far lower than fresh arms.

The planner now exposes ``select_batch(k)`` which returns the top-k
arms for the next wave.  The main loop in ``coverup.py`` should call
this each wave instead of scheduling all segments at once.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from ..diagnostic_ir import DiagnosticIR


# ── Constants ───────────────────────────────────────────────────────

PLATEAU_THRESHOLD = 3      # consecutive U outcomes before freezing
FROZEN_PENALTY = 0.05      # frozen arms get this fraction of their score
MAX_PULLS_PER_ARM = 8      # give up on an arm after this many attempts


@dataclass
class Arm:
    """Represents one focal target (code segment) as a bandit arm."""
    segment_id: str          # e.g. "src/lib.rs:42-80"
    total_reward: float = 0.0
    pulls: int = 0
    total_cost_sec: float = 0.0
    total_cost_tokens: int = 0
    successes: int = 0       # times status=ok with coverage gain
    compiles: int = 0        # times status=ok (regardless of gain)
    # ── P4: Lightweight gap features ──
    missing_lines: int = 0   # how many lines need coverage
    missing_branches: int = 0
    gap_complexity: float = 1.0  # 1.0 = normal, >1 = harder, <1 = easier
    failures: int = 0        # times status=fail (compile/run error)
    total_gain: float = 0.0  # sum of coverage delta when successful
    consecutive_useless: int = 0  # consecutive "compiles ok, no gain"
    frozen: bool = False

    @property
    def mean_reward(self) -> float:
        return self.total_reward / self.pulls if self.pulls > 0 else 0.0

    @property
    def p_success(self) -> float:
        """Probability of compiling+running (not necessarily gaining coverage)."""
        return self.compiles / self.pulls if self.pulls > 0 else 0.5

    @property
    def mean_gain(self) -> float:
        """Average coverage gain when the test compiles and runs."""
        return self.total_gain / max(self.compiles, 1)

    @property
    def success_rate(self) -> float:
        """Rate of coverage-improving outcomes."""
        return self.successes / self.pulls if self.pulls > 0 else 0.0


class UCBPlanner:
    """Selects segments using enhanced UCB with plateau detection.

    Usage::

        planner = UCBPlanner()
        for seg in segments:
            planner.add_arm(seg.identify())

        # Batch-wave loop
        while planner.has_active_arms():
            batch = planner.select_batch(k=8)
            for seg_id in batch:
                ...  # run improve_coverage for seg_id
                planner.update(seg_id, diagnostic_ir)
    """

    def __init__(self, c: float = 1.5, budget_tokens: int = 0, budget_sec: float = 0.0,
                 min_passes: int = 2):
        """
        Args:
            c: Exploration constant.  Higher = more exploration.
            budget_tokens: Total token budget (0 = unlimited).
            budget_sec: Total time budget in seconds (0 = unlimited).
            min_passes: Minimum number of full passes before allowing termination.
        """
        self.c = c
        self.budget_tokens = budget_tokens
        self.budget_sec = budget_sec
        self.min_passes = min_passes
        self._arms: Dict[str, Arm] = {}
        self._completed: Set[str] = set()  # arms that succeeded (G)
        self._exhausted: Set[str] = set()  # arms that hit max_pulls
        self._total_pulls: int = 0
        self._spent_tokens: int = 0
        self._spent_sec: float = 0.0
        self._pass_count: int = 0  # increments each time all arms have been tried once

    def add_arm(
        self,
        segment_id: str,
        missing_lines: int = 0,
        missing_branches: int = 0,
    ) -> None:
        """Register a segment as a selectable arm with gap features."""
        if segment_id not in self._arms:
            # P4: compute gap_complexity from segment size
            # Small gaps (1-5 lines) are easier; large gaps (>30) are harder
            total = missing_lines + missing_branches
            if total <= 5:
                complexity = 0.7  # easy — boost priority
            elif total <= 15:
                complexity = 1.0  # normal
            elif total <= 30:
                complexity = 1.2  # moderate
            else:
                complexity = 1.5  # hard — deprioritize slightly

            self._arms[segment_id] = Arm(
                segment_id=segment_id,
                missing_lines=missing_lines,
                missing_branches=missing_branches,
                gap_complexity=complexity,
            )

    def select(self) -> Optional[str]:
        """Select the single best arm.  Wrapper around select_batch(1)."""
        batch = self.select_batch(1)
        return batch[0] if batch else None

    def select_batch(self, k: int = 8) -> List[str]:
        """Select top-k arms for the next wave.

        Returns up to k segment_ids ranked by composite UCB score.
        Frozen/exhausted/completed arms are excluded unless there aren't
        enough active arms.
        """
        if not self._arms or self._is_budget_exhausted():
            return []

        scored: List[Tuple[str, float]] = []
        t = self._total_pulls

        for arm_id, arm in self._arms.items():
            # Skip completed and exhausted arms
            if arm_id in self._completed or arm_id in self._exhausted:
                continue

            score = self._score_arm(arm, t)
            scored.append((arm_id, score))

        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)
        return [sid for sid, _ in scored[:k]]

    def update(self, segment_id: str, ir: DiagnosticIR) -> None:
        """Update arm statistics after a verification attempt."""
        arm = self._arms.get(segment_id)
        if arm is None:
            return

        reward = self._compute_reward(ir)
        arm.total_reward += reward
        arm.pulls += 1
        arm.total_cost_sec += ir.cost_sec
        arm.total_cost_tokens += ir.cost_tokens_in + ir.cost_tokens_out
        self._total_pulls += 1
        self._spent_sec += ir.cost_sec
        self._spent_tokens += ir.cost_tokens_in + ir.cost_tokens_out

        if ir.is_ok:
            arm.compiles += 1
            gain = ir.delta_line + ir.delta_branch
            if gain > 0:
                arm.successes += 1
                arm.total_gain += gain
                arm.consecutive_useless = 0
                arm.frozen = False
                # Mark as completed (we got coverage!)
                self._completed.add(segment_id)
            else:
                # Compiled OK but no coverage gain → useless
                arm.consecutive_useless += 1
                if arm.consecutive_useless >= PLATEAU_THRESHOLD:
                    arm.frozen = True
        else:
            arm.failures += 1
            # Compile failure resets useless counter (different problem)
            arm.consecutive_useless = 0

        # Check exhaustion
        if arm.pulls >= MAX_PULLS_PER_ARM and segment_id not in self._completed:
            self._exhausted.add(segment_id)

    def mark_completed(self, segment_id: str) -> None:
        """Manually mark an arm as completed (e.g. coverage achieved)."""
        self._completed.add(segment_id)

    def remove_arm(self, segment_id: str) -> None:
        """Remove arm entirely."""
        self._arms.pop(segment_id, None)
        self._completed.discard(segment_id)
        self._exhausted.discard(segment_id)

    def has_active_arms(self) -> bool:
        """True if there are arms that haven't completed or been exhausted.

        If we haven't done min_passes yet, unfreeze promising arms
        to give them another chance with accumulated memory experience.
        """
        if self._is_budget_exhausted():
            return False

        active = [
            arm_id for arm_id in self._arms
            if arm_id not in self._completed and arm_id not in self._exhausted
        ]

        if active:
            return True

        # No active arms — check if we should start another pass
        self._pass_count += 1
        if self._pass_count < self.min_passes:
            unfrozen = self._unfreeze_promising_arms()
            if unfrozen > 0:
                return True

        return False

    def _unfreeze_promising_arms(self) -> int:
        """Unfreeze arms that had at least one success or compile.

        Returns the number of arms unfrozen.
        """
        count = 0
        for arm_id, arm in self._arms.items():
            if arm_id in self._completed:
                continue
            if arm.frozen and arm.p_success > 0.3:
                # This arm compiled before — give it another shot
                # with the memory experience accumulated in pass 1
                arm.frozen = False
                arm.consecutive_useless = 0
                count += 1
            if arm_id in self._exhausted and arm.pulls < MAX_PULLS_PER_ARM + 3:
                # Give exhausted arms a few extra pulls in the new pass
                self._exhausted.discard(arm_id)
                count += 1
        return count

    def get_stats(self) -> Dict[str, dict]:
        """Return per-arm statistics."""
        return {
            arm_id: {
                "mean_reward": round(arm.mean_reward, 4),
                "pulls": arm.pulls,
                "p_success": round(arm.p_success, 4),
                "mean_gain": round(arm.mean_gain, 4),
                "success_rate": round(arm.success_rate, 4),
                "consecutive_useless": arm.consecutive_useless,
                "frozen": arm.frozen,
                "total_cost_sec": round(arm.total_cost_sec, 2),
                "total_cost_tokens": arm.total_cost_tokens,
            }
            for arm_id, arm in self._arms.items()
        }

    def get_global_stats(self) -> dict:
        """Return global planner statistics."""
        return {
            "total_pulls": self._total_pulls,
            "spent_tokens": self._spent_tokens,
            "spent_sec": round(self._spent_sec, 2),
            "num_arms": len(self._arms),
            "completed": len(self._completed),
            "exhausted": len(self._exhausted),
            "active": sum(
                1 for a in self._arms
                if a not in self._completed and a not in self._exhausted
            ),
            "frozen": sum(1 for a in self._arms.values() if a.frozen),
            "budget_tokens_remaining": max(0, self.budget_tokens - self._spent_tokens)
                if self.budget_tokens > 0 else -1,
            "budget_sec_remaining": max(0.0, self.budget_sec - self._spent_sec)
                if self.budget_sec > 0 else -1.0,
        }

    # ── internals ───────────────────────────────────────────────────

    def _score_arm(self, arm: Arm, t: int) -> float:
        """Composite UCB score: UCB(p_success) × UCB(gain) × plateau_factor.

        Unpulled arms get a high default score for exploration.
        """
        if arm.pulls == 0:
            return 1e6  # explore first

        n = arm.pulls
        log_t = math.log(t + 1)

        # UCB on compile-success probability
        p_hat = arm.p_success
        explore_p = self.c * math.sqrt(log_t / (2 * n))
        ucb_p = min(p_hat + explore_p, 1.0)

        # UCB on gain (only from successful compilations)
        g_hat = arm.mean_gain
        explore_g = self.c * math.sqrt(log_t / (2 * max(arm.compiles, 1)))
        ucb_g = g_hat + explore_g

        # Plateau penalty
        if arm.frozen:
            plateau_factor = FROZEN_PENALTY
        elif arm.consecutive_useless > 0:
            # Gradual decay before full freeze
            plateau_factor = 1.0 - 0.2 * arm.consecutive_useless
        else:
            plateau_factor = 1.0

        score = ucb_p * ucb_g * max(plateau_factor, 0.01)

        # P4: gap complexity adjustment — prefer easier gaps early
        # (they have lower complexity → higher score)
        if arm.gap_complexity > 0:
            score /= arm.gap_complexity

        return score

    def _compute_reward(self, ir: DiagnosticIR) -> float:
        """Compute reward from a DiagnosticIR.

        Reward formula:
          R = 0.7 * delta_line + 0.3 * delta_branch
              + 1.0  if ok
              - 0.5  if fail
              - 0.8  if flaky
              - 0.05 * cost_sec
        """
        cov = 0.7 * ir.delta_line + 0.3 * ir.delta_branch

        if ir.status == "ok":
            status_bonus = 1.0
        elif ir.status == "timeout":
            status_bonus = -0.3
        else:
            status_bonus = -0.5

        flaky_penalty = -0.8 if ir.error_category == "flaky" else 0.0
        cost_penalty = -0.05 * ir.cost_sec

        return cov + status_bonus + flaky_penalty + cost_penalty

    def _is_budget_exhausted(self) -> bool:
        if self.budget_tokens > 0 and self._spent_tokens >= self.budget_tokens:
            return True
        if self.budget_sec > 0 and self._spent_sec >= self.budget_sec:
            return True
        return False
