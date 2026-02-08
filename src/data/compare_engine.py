from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Union
import numpy as np
import pandas as pd
@dataclass
class StructureComparison:
    columns_only_left: List[str]
    columns_only_right: List[str]
    columns_common: List[str]
    dtype_mismatches: List[Dict[str, Any]]  
    rows_left: int
    rows_right: int
    cols_left: int
    cols_right: int


@dataclass
class RowComparison:
    rows_only_left: pd.DataFrame
    rows_only_right: pd.DataFrame
    rows_in_both: pd.DataFrame
    rows_in_both_differing: pd.DataFrame
    key_columns: List[str]
    total_only_left: int
    total_only_right: int
    total_in_both: int
    total_differing: int


@dataclass
class CellComparison:
    difference_report: pd.DataFrame
    change_log: pd.DataFrame
    column_diff_counts: Dict[str, int]
    total_differences: int


@dataclass
class SummaryStatsComparison:
    null_counts_left: Dict[str, int]
    null_counts_right: Dict[str, int]
    null_differences: Dict[str, Dict[str, int]]
    numeric_stats: Dict[str, Dict[str, Dict[str, float]]]
    stats_differences: List[Dict[str, Any]]


@dataclass
class ComparisonReport:
    structure: StructureComparison
    row_comparison: Optional[RowComparison] = None
    cell_comparison: Optional[CellComparison] = None
    summary_stats: Optional[SummaryStatsComparison] = None
    human_readable: Dict[str, Any] = field(default_factory=dict)


class CompareEngine:
    def compare_structure(
        self, left: pd.DataFrame, right: pd.DataFrame
    ) -> StructureComparison:
        left_cols = set(left.columns)
        right_cols = set(right.columns)
        common = left_cols & right_cols

        dtype_mismatches = []
        for col in sorted(common):
            lt, rt = left[col].dtype, right[col].dtype
            if lt != rt:
                dtype_mismatches.append(
                    {
                        "column": col,
                        "left_dtype": str(lt),
                        "right_dtype": str(rt),
                    }
                )

        return StructureComparison(
            columns_only_left=sorted(left_cols - right_cols),
            columns_only_right=sorted(right_cols - left_cols),
            columns_common=sorted(common),
            dtype_mismatches=dtype_mismatches,
            rows_left=len(left),
            rows_right=len(right),
            cols_left=len(left.columns),
            cols_right=len(right.columns),
        )

    def compare_rows(
        self,
        left: pd.DataFrame,
        right: pd.DataFrame,
        key_columns: Union[str, Sequence[str]],
    ) -> RowComparison:
        keys = [key_columns] if isinstance(key_columns, str) else list(key_columns)
        for k in keys:
            if k not in left.columns or k not in right.columns:
                raise ValueError(f"Key column '{k}' must exist in both DataFrames")

        left_keys = left[keys].drop_duplicates()
        right_keys = right[keys].drop_duplicates()

        left_key_set = set(map(tuple, left_keys.values))
        right_key_set = set(map(tuple, right_keys.values))

        only_left_keys = left_key_set - right_key_set
        only_right_keys = right_key_set - left_key_set
        both_keys = left_key_set & right_key_set

        rows_only_left = left[left[keys].apply(tuple, axis=1).isin(only_left_keys)].drop_duplicates(
            subset=keys
        )
        rows_only_right = right[
            right[keys].apply(tuple, axis=1).isin(only_right_keys)
        ].drop_duplicates(subset=keys)

        # Rows in both - need to find differing
        common_cols = list(set(left.columns) & set(right.columns))
        compare_cols = [c for c in common_cols if c not in keys]

        rows_in_both_differing = []
        rows_in_both_same = []

        for key_tuple in both_keys:
            left_row = left[left[keys].apply(tuple, axis=1) == key_tuple].iloc[0]
            right_row = right[right[keys].apply(tuple, axis=1) == key_tuple].iloc[0]
            differs = False
            for c in compare_cols:
                lv, rv = left_row[c], right_row[c]
                if pd.isna(lv) and pd.isna(rv):
                    continue
                if pd.isna(lv) or pd.isna(rv):
                    differs = True
                    break
                if lv != rv:
                    differs = True
                    break
            if differs:
                rows_in_both_differing.append(left_row)
            else:
                rows_in_both_same.append(left_row)

        rows_in_both_df = pd.DataFrame(rows_in_both_same) if rows_in_both_same else pd.DataFrame()
        rows_in_both_differing_df = (
            pd.DataFrame(rows_in_both_differing) if rows_in_both_differing else pd.DataFrame()
        )

        if rows_in_both_df.empty and rows_in_both_same:
            rows_in_both_df = pd.DataFrame(rows_in_both_same)
        if rows_in_both_differing_df.empty and rows_in_both_differing:
            rows_in_both_differing_df = pd.DataFrame(rows_in_both_differing)

        return RowComparison(
            rows_only_left=rows_only_left,
            rows_only_right=rows_only_right,
            rows_in_both=rows_in_both_df,
            rows_in_both_differing=rows_in_both_differing_df,
            key_columns=keys,
            total_only_left=len(rows_only_left),
            total_only_right=len(rows_only_right),
            total_in_both=len(both_keys),
            total_differing=len(rows_in_both_differing),
        )

    def compare_cells(
        self,
        left: pd.DataFrame,
        right: pd.DataFrame,
        key_columns: Union[str, Sequence[str]],
    ) -> CellComparison:
        keys = [key_columns] if isinstance(key_columns, str) else list(key_columns)
        row_comp = self.compare_rows(left, right, keys)

        change_records = []
        column_diff_counts: Dict[str, int] = {}

        for _, left_row in row_comp.rows_in_both_differing.iterrows():
            key_tuple = tuple(left_row[k] for k in keys)
            right_match = right[right[keys].apply(tuple, axis=1) == key_tuple]
            if right_match.empty:
                continue
            right_row = right_match.iloc[0]
            row_key = key_tuple[0] if len(keys) == 1 else key_tuple

            common_cols = [c for c in left.columns if c in right.columns and c not in keys]
            for col in common_cols:
                lv, rv = left_row[col], right_row[col]
                if self._values_differ(lv, rv):
                    diff_type = self._classify_diff(lv, rv)
                    change_records.append(
                        {
                            "row_key": row_key,
                            "column": col,
                            "old_value": lv,
                            "new_value": rv,
                            "diff_type": diff_type,
                        }
                    )
                    column_diff_counts[col] = column_diff_counts.get(col, 0) + 1

        change_log = pd.DataFrame(
            [
                {
                    "row_key": r["row_key"],
                    "column": r["column"],
                    "old_value": r["old_value"],
                    "new_value": r["new_value"],
                }
                for r in change_records
            ]
        )
        diff_report = pd.DataFrame(change_records)

        return CellComparison(
            difference_report=diff_report,
            change_log=change_log,
            column_diff_counts=column_diff_counts,
            total_differences=len(change_records),
        )

    def _values_differ(self, a: Any, b: Any) -> bool:
        if pd.isna(a) and pd.isna(b):
            return False
        if pd.isna(a) or pd.isna(b):
            return True
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return not np.isclose(a, b, equal_nan=True)
        return a != b

    def _classify_diff(self, old_val: Any, new_val: Any) -> str:
        if pd.isna(old_val) and not pd.isna(new_val):
            return "filled"
        if not pd.isna(old_val) and pd.isna(new_val):
            return "nullified"
        return "changed"

    def compare_summary_stats(
        self, left: pd.DataFrame, right: pd.DataFrame
    ) -> SummaryStatsComparison:
        common_cols = list(set(left.columns) & set(right.columns))

        null_left = {c: int(left[c].isna().sum()) for c in common_cols}
        null_right = {c: int(right[c].isna().sum()) for c in common_cols}
        null_diffs = {
            c: {
                "left": null_left[c],
                "right": null_right[c],
                "diff": null_right[c] - null_left[c],
            }
            for c in common_cols
        }

        numeric_cols = [
            c
            for c in common_cols
            if pd.api.types.is_numeric_dtype(left[c]) and pd.api.types.is_numeric_dtype(right[c])
        ]
        numeric_stats: Dict[str, Dict[str, Dict[str, float]]] = {}
        stats_differences = []

        for col in numeric_cols:
            l_vals = left[col].dropna()
            r_vals = right[col].dropna()
            left_stats = {
                "mean": float(l_vals.mean()) if len(l_vals) else np.nan,
                "min": float(l_vals.min()) if len(l_vals) else np.nan,
                "max": float(l_vals.max()) if len(l_vals) else np.nan,
                "count": int(len(l_vals)),
            }
            right_stats = {
                "mean": float(r_vals.mean()) if len(r_vals) else np.nan,
                "min": float(r_vals.min()) if len(r_vals) else np.nan,
                "max": float(r_vals.max()) if len(r_vals) else np.nan,
                "count": int(len(r_vals)),
            }
            numeric_stats[col] = {"left": left_stats, "right": right_stats}
            for stat in ["mean", "min", "max"]:
                lv, rv = left_stats[stat], right_stats[stat]
                if not (np.isnan(lv) and np.isnan(rv)):
                    if np.isnan(lv) or np.isnan(rv) or not np.isclose(lv, rv):
                        stats_differences.append(
                            {
                                "column": col,
                                "statistic": stat,
                                "left_value": lv,
                                "right_value": rv,
                            }
                        )

        return SummaryStatsComparison(
            null_counts_left=null_left,
            null_counts_right=null_right,
            null_differences=null_diffs,
            numeric_stats=numeric_stats,
            stats_differences=stats_differences,
        )

    def full_compare(
        self,
        left: pd.DataFrame,
        right: pd.DataFrame,
        key_columns: Optional[Union[str, Sequence[str]]] = None,
    ) -> ComparisonReport:
        structure = self.compare_structure(left, right)
        row_comp = None
        cell_comp = None

        if key_columns:
            try:
                row_comp = self.compare_rows(left, right, key_columns)
                cell_comp = self.compare_cells(left, right, key_columns)
            except ValueError:
                pass

        summary_stats = self.compare_summary_stats(left, right)
        human = self._build_human_readable(
            structure, row_comp, cell_comp, summary_stats
        )

        return ComparisonReport(
            structure=structure,
            row_comparison=row_comp,
            cell_comparison=cell_comp,
            summary_stats=summary_stats,
            human_readable=human,
        )

    def _build_human_readable(
        self,
        structure: StructureComparison,
        row_comp: Optional[RowComparison],
        cell_comp: Optional[CellComparison],
        summary_stats: SummaryStatsComparison,
    ) -> Dict[str, Any]:
        lines = []

        lines.append(
            f"Left has {structure.rows_left} rows, {structure.cols_left} columns; "
            f"Right has {structure.rows_right} rows, {structure.cols_right} columns."
        )
        if structure.columns_only_left:
            lines.append(
                f"Columns only in left: {', '.join(structure.columns_only_left[:10])}"
                + (" ..." if len(structure.columns_only_left) > 10 else "")
            )
        if structure.columns_only_right:
            lines.append(
                f"Columns only in right: {', '.join(structure.columns_only_right[:10])}"
                + (" ..." if len(structure.columns_only_right) > 10 else "")
            )
        if structure.dtype_mismatches:
            lines.append(
                f"Dtype mismatches in {len(structure.dtype_mismatches)} columns: "
                + ", ".join(
                    f"{m['column']} ({m['left_dtype']} vs {m['right_dtype']})"
                    for m in structure.dtype_mismatches[:5]
                )
            )

        if row_comp:
            lines.append(
                f"Row comparison: {row_comp.total_only_left} only in left, "
                f"{row_comp.total_only_right} only in right, "
                f"{row_comp.total_in_both} in both ({row_comp.total_differing} differing)."
            )
        if cell_comp and cell_comp.total_differences > 0:
            lines.append(
                f"Cell-level differences: {cell_comp.total_differences} total. "
                f"Most affected columns: "
                + ", ".join(
                    f"{k}({v})"
                    for k, v in sorted(
                        cell_comp.column_diff_counts.items(),
                        key=lambda x: -x[1],
                    )[:5]
                )
            )

        if summary_stats.stats_differences:
            lines.append(
                f"Summary stats differ in {len(summary_stats.stats_differences)} column/stat pairs."
            )

        return {
            "summary": " ".join(lines),
            "bullet_points": lines,
            "structure": {
                "columns_only_left": structure.columns_only_left,
                "columns_only_right": structure.columns_only_right,
                "dtype_mismatches": structure.dtype_mismatches,
            },
            "row_counts": (
                {
                    "only_left": row_comp.total_only_left,
                    "only_right": row_comp.total_only_right,
                    "in_both": row_comp.total_in_both,
                    "differing": row_comp.total_differing,
                }
                if row_comp
                else None
            ),
            "cell_diff_total": cell_comp.total_differences if cell_comp else None,
        }

    def explain_differences_plain_english(self, report: ComparisonReport) -> str:
        parts = []
        s = report.structure

        parts.append(
            f"The left dataset has {s.rows_left} rows and {s.cols_left} columns. "
            f"The right dataset has {s.rows_right} rows and {s.cols_right} columns."
        )

        if s.columns_only_left:
            parts.append(
                f"The left dataset has {len(s.columns_only_left)} column(s) not in the right: "
                f"{', '.join(s.columns_only_left)}."
            )
        if s.columns_only_right:
            parts.append(
                f"The right dataset has {len(s.columns_only_right)} column(s) not in the left: "
                f"{', '.join(s.columns_only_right)}."
            )
        if s.dtype_mismatches:
            parts.append(
                f"There are {len(s.dtype_mismatches)} column(s) with different data types "
                f"between the two datasets."
            )

        if report.row_comparison:
            r = report.row_comparison
            parts.append(
                f"Using the key column(s) {r.key_columns}: "
                f"{r.total_only_left} row(s) appear only in the left, "
                f"{r.total_only_right} only in the right, "
                f"and {r.total_in_both} appear in both. "
                f"Of those in both, {r.total_differing} have different values in at least one column."
            )

        if report.cell_comparison and report.cell_comparison.total_differences > 0:
            c = report.cell_comparison
            parts.append(
                f"There are {c.total_differences} cell-level differences. "
                f"The columns with the most changes are: "
                + ", ".join(
                    f"{k} ({v} changes)"
                    for k, v in sorted(
                        c.column_diff_counts.items(),
                        key=lambda x: -x[1],
                    )[:5]
                )
                + "."
            )

        return " ".join(parts)
