"""Recipe Memory – success-weighted skill library for CoverAgent-ML.

Instead of tracking "what errors happen often" (frequency chart), this
module tracks "what repair actions succeed for which diagnostic signatures"
(recipe library).  Recipes are injected into LLM prompts as positive
prescriptions ("Do: ...") rather than negative warnings ("Avoid: ...").

Key design changes from the original ReflectiveMemory:
  - Key:  ``(language, phase, error_category, signature)``
  - Value: list of ``Recipe`` entries, each with action, success/try stats
  - Ranking: ``UCB(success_rate) × recency_decay`` instead of raw count
  - Injection: positive prescriptions, top-k ranked by effectiveness
  - Cold-start guard: recipes with <3 attempts are not injected

References
----------
Case-Based Reasoning (Kolodner 1992), Voyager skill library (Wang et al. 2023),
Reflexion (Shinn et al. NeurIPS 2023).
"""

from __future__ import annotations

import math
import re
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple

from ..diagnostic_ir import DiagnosticIR, ErrorCategory


# ── SuccessLevel enum ───────────────────────────────────────────────────

class SuccessLevel(str, Enum):
    """Outcome granularity for recipe weighting.

    FULL    – test compiled, ran, and gained coverage        (weight 1.0)
    PARTIAL – test compiled and ran but gained no coverage   (weight 0.3)
    COMPILE – test compiled but failed at runtime            (weight 0.1)
    NONE    – test did not compile                           (weight 0.0)
    """
    FULL = "full"
    PARTIAL = "partial"
    COMPILE = "compile"
    NONE = "none"

# Weights for computing weighted success rate
_LEVEL_WEIGHTS = {
    SuccessLevel.FULL: 1.0,
    SuccessLevel.PARTIAL: 0.3,
    SuccessLevel.COMPILE: 0.1,
    SuccessLevel.NONE: 0.0,
}


# ── Recipe dataclass ────────────────────────────────────────────────────

@dataclass
class Recipe:
    """A single repair action with success statistics."""
    action_name: str               # e.g. "rust_autofix_submodule_imports", "llm_fixed_import_E0432"
    success_count: int = 0         # FULL successes (legacy compat)
    try_count: int = 0
    total_cost_sec: float = 0.0
    total_delta_cov: float = 0.0   # cumulative coverage gain when successful
    last_seen_ts: float = field(default_factory=time.monotonic)
    # Per-level counters for weighted success rate
    full_count: int = 0
    partial_count: int = 0
    compile_count: int = 0
    none_count: int = 0

    @property
    def success_rate(self) -> float:
        """Weighted success rate across all outcome levels."""
        if self.try_count == 0:
            return 0.0
        weighted = (
            _LEVEL_WEIGHTS[SuccessLevel.FULL] * self.full_count
            + _LEVEL_WEIGHTS[SuccessLevel.PARTIAL] * self.partial_count
            + _LEVEL_WEIGHTS[SuccessLevel.COMPILE] * self.compile_count
            + _LEVEL_WEIGHTS[SuccessLevel.NONE] * self.none_count
        )
        return weighted / self.try_count

    @property
    def avg_cost(self) -> float:
        return self.total_cost_sec / self.try_count if self.try_count > 0 else 0.0

    @property
    def avg_delta_cov(self) -> float:
        return self.total_delta_cov / max(self.success_count, 1)


@dataclass
class SignatureEntry:
    """All recipes for a specific diagnostic signature."""
    language: str
    phase: str
    error_category: str
    signature: str                  # normalized error fingerprint
    recipes: Dict[str, Recipe] = field(default_factory=dict)
    total_seen: int = 0

    def key(self) -> Tuple[str, str, str, str]:
        return (self.language, self.phase, self.error_category, self.signature)


# ── Recipe Memory ───────────────────────────────────────────────────────

class ReflectiveMemory:
    """Success-weighted recipe library for test generation repair.

    Usage::

        memory = ReflectiveMemory()

        # After a repair attempt (success or failure):
        memory.record(ir, action="rust_autofix_submodule_imports", succeeded=True)

        # Before the next LLM call — get positive prescriptions:
        text = memory.format_for_prompt(language="rust", max_lessons=5)

        # For a specific error — get targeted recipe:
        hint = memory.format_entry_for_error(ir)
    """

    MIN_ATTEMPTS_FOR_INJECTION = 2  # cold-start guard (lowered from 3 for short runs)
    RECENCY_HALF_LIFE = 600.0       # seconds; recipes older than this decay by 50%

    def __init__(self, max_entries: int = 300):
        self._entries: Dict[Tuple[str, str, str, str], SignatureEntry] = {}
        self._max_entries = max_entries
        self._lock = threading.Lock()
        self._creation_time = time.monotonic()
        self._global_record_count = 0  # total records across all recipes (for UCB)

        # Pre-built prescription templates: (language, error_category) → text
        self._prescription_templates: Dict[Tuple[str, str], str] = {
            # Rust
            ("rust", ErrorCategory.IMPORT.value):
                "Do: use explicit submodule imports (e.g. `use {crate}::{module}::ItemName;`). "
                "Check available import paths with get_info before adding use statements.",
            ("rust", ErrorCategory.TYPE.value):
                "Do: call get_info on the function to verify its signature, then match argument types exactly. "
                "Use `.into()`, `.as_ref()`, or explicit casts where types differ.",
            ("rust", ErrorCategory.VISIBILITY.value):
                "Do: only call public API. Test private code INDIRECTLY through public functions. "
                "Use get_info to check if a method is `pub`.",
            ("rust", ErrorCategory.OWNERSHIP.value):
                "Do: clone values to avoid borrow issues. Use owned types (String, Vec) in tests. "
                "Avoid holding references across assertion points.",
            ("rust", ErrorCategory.ASSERTION.value):
                "Do: re-read the source logic step by step before writing assert. "
                "Use `assert_eq!` with expected values computed from the algorithm, not guessed.",
            # Python
            ("python", ErrorCategory.IMPORT.value):
                "Do: use the exact module path matching the project directory structure. "
                "Check with `from package.subpackage.module import ClassName`.",
            ("python", ErrorCategory.TYPE.value):
                "Do: verify argument types by reading the function signature. "
                "Pass the exact types expected.",
            ("python", ErrorCategory.ASSERTION.value):
                "Do: trace the function logic manually to compute the expected return value.",
            ("python", ErrorCategory.PANIC.value):
                "Do: use `pytest.raises(ExceptionType)` for expected exceptions. "
                "Catch specific exception types, not bare except.",
            # Go
            ("go", ErrorCategory.IMPORT.value):
                "Do: ensure every import is used. Remove unused imports immediately. "
                "Use the exact package path for needed imports.",
            ("go", ErrorCategory.TYPE.value):
                "Do: match types exactly. Go has no implicit conversions. "
                "Use explicit casts like `int64(x)` or `string(b)`.",
            ("go", ErrorCategory.INTERFACE.value):
                "Do: implement ALL methods required by the interface. "
                "Check the interface definition with get_info.",
            ("go", ErrorCategory.ASSERTION.value):
                "Do: compute expected values from the algorithm logic. "
                "Use `t.Errorf` with descriptive formatting.",
        }

    # ── Record outcomes ─────────────────────────────────────────────

    def record(
        self,
        ir: DiagnosticIR,
        action: str = "",
        succeeded: bool = False,
        level: Optional[SuccessLevel] = None,
    ) -> None:
        """Record a repair attempt outcome.

        Args:
            ir: The diagnostic IR from this attempt.
            action: Name of the action taken (e.g. "tool_rust_autofix",
                    "llm_fixed_import_E0432"). Empty string = "llm_attempt".
            succeeded: Whether this action resolved the error (legacy).
            level: Fine-grained outcome level.  If provided, overrides *succeeded*.
                   If not provided, ``succeeded=True`` maps to FULL,
                   ``succeeded=False`` maps to NONE.
        """
        # Determine effective level
        if level is None:
            effective_level = SuccessLevel.FULL if succeeded else SuccessLevel.NONE
        else:
            effective_level = level

        lang = ir.language
        phase = ir.phase
        cat = ir.error_category
        sig = self._extract_signature(ir)
        skey = (lang, phase, cat, sig)
        act_name = action or f"llm_{cat}"

        with self._lock:
            if skey not in self._entries:
                if len(self._entries) >= self._max_entries:
                    self._evict_lru()
                self._entries[skey] = SignatureEntry(
                    language=lang, phase=phase,
                    error_category=cat, signature=sig,
                )

            entry = self._entries[skey]
            entry.total_seen += 1

            if act_name not in entry.recipes:
                entry.recipes[act_name] = Recipe(action_name=act_name)

            recipe = entry.recipes[act_name]
            recipe.try_count += 1
            recipe.last_seen_ts = time.monotonic()
            recipe.total_cost_sec += ir.cost_sec
            self._global_record_count += 1

            # Update per-level counter
            if effective_level == SuccessLevel.FULL:
                recipe.full_count += 1
                recipe.success_count += 1  # legacy compat
                recipe.total_delta_cov += ir.delta_line + ir.delta_branch
            elif effective_level == SuccessLevel.PARTIAL:
                recipe.partial_count += 1
            elif effective_level == SuccessLevel.COMPILE:
                recipe.compile_count += 1
            else:
                recipe.none_count += 1

    # ── Query ───────────────────────────────────────────────────────

    def query(
        self,
        language: str,
        error_category: Optional[str] = None,
        max_results: int = 10,
    ) -> List[Tuple[SignatureEntry, Recipe]]:
        """Retrieve top recipes ranked by UCB(success_rate) × recency.

        Returns list of (entry, best_recipe) tuples.
        """
        now = time.monotonic()
        results: List[Tuple[SignatureEntry, Recipe, float]] = []

        with self._lock:
            for skey, entry in self._entries.items():
                if entry.language != language:
                    continue
                if error_category and entry.error_category != error_category:
                    continue

                # Find best recipe for this signature
                best_recipe = None
                best_score = -1.0

                for recipe in entry.recipes.values():
                    if recipe.try_count < 1:
                        continue
                    score = self._score_recipe(recipe, now)
                    if score > best_score:
                        best_score = score
                        best_recipe = recipe

                if best_recipe and best_score > 0:
                    results.append((entry, best_recipe, best_score))

        results.sort(key=lambda x: x[2], reverse=True)
        return [(e, r) for e, r, _ in results[:max_results]]

    def format_for_prompt(self, language: str, max_lessons: int = 5) -> str:
        """Format top recipes as positive prescriptions for LLM prompt.

        Only injects recipes with >= MIN_ATTEMPTS_FOR_INJECTION attempts
        (cold-start guard).
        """
        results = self.query(language, max_results=max_lessons * 2)
        if not results:
            return ""

        lines = ["Based on successful repair patterns from previous attempts:"]
        count = 0
        for entry, recipe in results:
            if count >= max_lessons:
                break
            # Cold-start guard: skip recipes with too few attempts
            if recipe.try_count < self.MIN_ATTEMPTS_FOR_INJECTION:
                continue

            sr = recipe.success_rate
            # Only inject recipes that have shown some success
            if sr < 0.1:
                continue

            cat = entry.error_category
            prescription = self._get_prescription(entry, recipe)

            count += 1
            lines.append(
                f"  {count}. [{cat}] (success {sr:.0%} over {recipe.try_count} attempts) "
                f"{prescription}"
            )

        if count == 0:
            return ""

        return "\n".join(lines)

    def format_entry_for_error(self, ir: DiagnosticIR) -> str:
        """Return targeted prescriptions for a specific error category."""
        results = self.query(
            ir.language,
            error_category=ir.error_category,
            max_results=3,
        )
        if not results:
            # Fall back to template
            tmpl = self._prescription_templates.get(
                (ir.language, ir.error_category)
            )
            if tmpl:
                return f"Recommended fix strategy:\n  - {tmpl}"
            return ""

        lines = ["Recommended fix strategies (from successful past repairs):"]
        for entry, recipe in results:
            if recipe.try_count >= 2 and recipe.success_rate > 0:
                prescription = self._get_prescription(entry, recipe)
                lines.append(
                    f"  - {prescription} "
                    f"(worked {recipe.success_count}/{recipe.try_count} times)"
                )

        if len(lines) <= 1:
            tmpl = self._prescription_templates.get(
                (ir.language, ir.error_category)
            )
            if tmpl:
                return f"Recommended fix strategy:\n  - {tmpl}"
            return ""

        return "\n".join(lines)

    # ── Properties ──────────────────────────────────────────────────

    @property
    def size(self) -> int:
        with self._lock:
            return len(self._entries)

    def get_stats(self) -> Dict[str, dict]:
        """Per-category statistics: total attempts, successes, recipes."""
        with self._lock:
            stats: Dict[str, dict] = defaultdict(
                lambda: {"attempts": 0, "successes": 0, "recipes": 0}
            )
            for entry in self._entries.values():
                cat = entry.error_category
                for recipe in entry.recipes.values():
                    stats[cat]["attempts"] += recipe.try_count
                    stats[cat]["successes"] += recipe.success_count
                    stats[cat]["recipes"] += 1
            return dict(stats)

    def clear(self) -> None:
        with self._lock:
            self._entries.clear()

    # ── Internals ───────────────────────────────────────────────────

    def _extract_signature(self, ir: DiagnosticIR) -> str:
        """Create a normalized signature for dedup and matching.

        Signature = error_code (if available) + key tokens from message.
        """
        parts = []

        # Error code is the strongest signal
        if ir.error_code:
            parts.append(ir.error_code)

        # Extract key tokens from message
        msg = ir.message[:120].strip()
        # Remove line numbers, paths, concrete identifiers
        msg = re.sub(r'\d+', 'N', msg)
        msg = re.sub(r'/[^\s]+', '<path>', msg)
        msg = re.sub(r'`[^`]*`', '<sym>', msg)

        if msg:
            parts.append(msg[:60])

        return "|".join(parts) if parts else "unknown"

    def _score_recipe(self, recipe: Recipe, now: float) -> float:
        """Score a recipe: UCB(success_rate) × recency_decay.

        UCB component gives optimistic estimate for under-tested recipes.
        Recency decay ensures stale recipes rank lower.
        """
        n = recipe.try_count
        if n == 0:
            return 0.0

        # UCB: success_rate + exploration bonus
        sr = recipe.success_rate
        total = max(self._global_record_count, 1)
        exploration = math.sqrt(math.log(total + 1) / (2 * n))
        ucb = sr + 0.5 * exploration  # modest exploration bonus

        # Recency decay (exponential half-life)
        age = now - recipe.last_seen_ts
        recency = math.exp(-0.693 * age / self.RECENCY_HALF_LIFE)

        return ucb * (0.3 + 0.7 * recency)  # recency affects 70% of score

    def _get_prescription(self, entry: SignatureEntry, recipe: Recipe) -> str:
        """Get human-readable prescription text for a recipe."""
        # Try template first (most readable)
        tmpl = self._prescription_templates.get(
            (entry.language, entry.error_category)
        )
        if tmpl:
            return tmpl

        # Construct from action name
        action = recipe.action_name
        if action.startswith("tool_"):
            return f"Do: apply automatic fix '{action}' before retrying with LLM."
        elif action.startswith("llm_fixed_"):
            cat = action.replace("llm_fixed_", "")
            return f"Do: let LLM fix the {cat} error with corrected code."
        else:
            return f"Do: apply strategy '{action}'."

    def _evict_lru(self) -> None:
        """Evict the least-recently-used entry."""
        if not self._entries:
            return
        oldest_key = None
        oldest_ts = float('inf')
        for skey, entry in self._entries.items():
            if not entry.recipes:
                # Empty entry — good eviction candidate, use creation time
                ts = self._creation_time
            else:
                ts = max(r.last_seen_ts for r in entry.recipes.values())
            if ts < oldest_ts:
                oldest_ts = ts
                oldest_key = skey
        if oldest_key:
            del self._entries[oldest_key]
