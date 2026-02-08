"""
DataForge - Backend data management module.

Provides:
- DataManager: Central in-memory dataset store
- MergeEngine: Robust dataset merging with validation
- CompareEngine: Dataset comparison (structure, rows, cells, stats)
"""

from .data_manager import DataManager
from .merge_engine import MergeEngine, MergeResult, MergeSummary
from .compare_engine import (
    CompareEngine,
    StructureComparison,
    RowComparison,
    CellComparison,
    SummaryStatsComparison,
    ComparisonReport,
)

__all__ = [
    "DataManager",
    "MergeEngine",
    "MergeResult",
    "MergeSummary",
    "CompareEngine",
    "StructureComparison",
    "RowComparison",
    "CellComparison",
    "SummaryStatsComparison",
    "ComparisonReport",
]
