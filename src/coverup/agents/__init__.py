"""CoverAgent-ML agent modules.

Provides the four core agent components:
- **ReflectiveMemory** – success-weighted recipe library for repair strategies.
- **RepairOrchestrator** – applies deterministic (tool-first) then LLM repairs.
- **UCBPlanner** – selects focal targets via Upper Confidence Bound.
- **TraceLogger** – structured JSONL trace for offline analysis.
"""

from .memory import ReflectiveMemory
from .repair import RepairOrchestrator
from .planner import UCBPlanner
from .trace import TraceLogger
from .blocker import CoverageBlocker, extract_blockers, format_blockers_for_prompt

__all__ = [
    "ReflectiveMemory", "RepairOrchestrator", "UCBPlanner", "TraceLogger",
    "CoverageBlocker", "extract_blockers", "format_blockers_for_prompt",
]
