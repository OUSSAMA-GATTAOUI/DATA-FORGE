
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Tuple, Union

import numpy as np
import pandas as pd


@dataclass
class MergeSummary:

    rows_left: int
    rows_right: int
    rows_result: int
    matched_rows: int
    unmatched_left: int
    unmatched_right: int
    new_columns_added: List[str]
    columns_from_left: List[str]
    columns_from_right: List[str]
    missing_values_introduced: dict  
    join_keys: List[str]
    merge_type: str
    validation_passed: bool
    validation_warnings: List[str] = field(default_factory=list)


@dataclass
class MergeResult:

    merged_df: pd.DataFrame
    summary: MergeSummary
    success: bool
    error: Optional[str] = None


class MergeValidationError(Exception):

    pass


class MergeEngine:
    DEFAULT_SUFFIXES: Tuple[str, str] = ("_left", "_right")

    def __init__(self, suffixes: Tuple[str, str] = ("_left", "_right")) -> None:
        self.suffixes = suffixes

    def merge(
        self,
        dataset_left: pd.DataFrame,
        dataset_right: pd.DataFrame,
        on: Optional[Union[str, Sequence[str]]] = None,
        left_on: Optional[Union[str, Sequence[str]]] = None,
        right_on: Optional[Union[str, Sequence[str]]] = None,
        how: str = "inner",
        suffixes: Optional[Tuple[str, str]] = None,
        columns_left: Optional[Sequence[str]] = None,
        columns_right: Optional[Sequence[str]] = None,
        exclude_left: Optional[Sequence[str]] = None,
        exclude_right: Optional[Sequence[str]] = None,
        validate: bool = True,
        indicator: bool = True,
    ) -> MergeResult:
        suffixes = suffixes or self.suffixes
        join_keys = self._resolve_join_keys(on, left_on, right_on, dataset_left, dataset_right)

        if validate:
            validation_warnings = self._validate_merge(
                dataset_left, dataset_right, join_keys, how
            )
            if any("ERROR" in w for w in validation_warnings):
                return MergeResult(
                    merged_df=pd.DataFrame(),
                    summary=MergeSummary(
                        rows_left=len(dataset_left),
                        rows_right=len(dataset_right),
                        rows_result=0,
                        matched_rows=0,
                        unmatched_left=0,
                        unmatched_right=0,
                        new_columns_added=[],
                        columns_from_left=[],
                        columns_from_right=[],
                        missing_values_introduced={},
                        join_keys=list(join_keys[0]) + list(join_keys[1]),
                        merge_type=how,
                        validation_passed=False,
                        validation_warnings=validation_warnings,
                    ),
                    success=False,
                    error="Validation failed. Check summary.validation_warnings.",
                )

        left_subset = self._apply_column_selection(
            dataset_left, join_keys[0], columns_left, exclude_left
        )
        right_subset = self._apply_column_selection(
            dataset_right, join_keys[1], columns_right, exclude_right
        )

        try:
            merged = pd.merge(
                left_subset,
                right_subset,
                left_on=join_keys[0],
                right_on=join_keys[1],
                how=how,
                suffixes=suffixes,
                indicator=indicator,
            )
        except Exception as e:
            return MergeResult(
                merged_df=pd.DataFrame(),
                summary=MergeSummary(
                    rows_left=len(dataset_left),
                    rows_right=len(dataset_right),
                    rows_result=0,
                    matched_rows=0,
                    unmatched_left=0,
                    unmatched_right=0,
                    new_columns_added=[],
                    columns_from_left=[],
                    columns_from_right=[],
                    missing_values_introduced={},
                    join_keys=list(join_keys[0]) + list(join_keys[1]),
                    merge_type=how,
                    validation_passed=validate,
                    validation_warnings=[],
                ),
                success=False,
                error=str(e),
            )

        summary = self._build_summary(
            dataset_left, dataset_right, merged, join_keys, how, validation_warnings if validate else []
        )
        return MergeResult(merged_df=merged, summary=summary, success=True)

    def _resolve_join_keys(
        self,
        on: Optional[Union[str, Sequence[str]]],
        left_on: Optional[Union[str, Sequence[str]]],
        right_on: Optional[Union[str, Sequence[str]]],
        left: pd.DataFrame,
        right: pd.DataFrame,
    ) -> Tuple[Tuple[str, ...], Tuple[str, ...]]:
        if on is not None:
            keys = (on,) if isinstance(on, str) else tuple(on)
            return (keys, keys)
        if left_on is not None and right_on is not None:
            lk = (left_on,) if isinstance(left_on, str) else tuple(left_on)
            rk = (right_on,) if isinstance(right_on, str) else tuple(right_on)
            if len(lk) != len(rk):
                raise MergeValidationError(
                    f"left_on and right_on must have same length: {len(lk)} vs {len(rk)}"
                )
            return (lk, rk)
        raise MergeValidationError("Must specify either 'on' or both 'left_on' and 'right_on'")

    def _validate_merge(
        self,
        left: pd.DataFrame,
        right: pd.DataFrame,
        join_keys: Tuple[Tuple[str, ...], Tuple[str, ...]],
        how: str,
    ) -> List[str]:
        warnings: List[str] = []
        left_keys, right_keys = join_keys
        for k in left_keys:
            if k not in left.columns:
                warnings.append(f"ERROR: Key '{k}' not found in left dataset")
        for k in right_keys:
            if k not in right.columns:
                warnings.append(f"ERROR: Key '{k}' not found in right dataset")
        if any("ERROR" in w for w in warnings):
            return warnings
        for lk, rk in zip(left_keys, right_keys):
            lt, rt = left[lk].dtype, right[rk].dtype
            if not self._dtypes_compatible(lt, rt):
                warnings.append(
                    f"WARNING: Type mismatch for keys: left[{lk}]={lt}, right[{rk}]={rt}"
                )
        dup_left = left[list(left_keys)].duplicated(keep=False).sum()
        dup_right = right[list(right_keys)].duplicated(keep=False).sum()
        if dup_left > 0:
            warnings.append(
                f"WARNING: {dup_left} duplicate key rows in left (may produce row multiplication)"
            )
        if dup_right > 0:
            warnings.append(
                f"WARNING: {dup_right} duplicate key rows in right (may produce row multiplication)"
            )
        null_left = left[list(left_keys)].isna().any(axis=1).sum()
        null_right = right[list(right_keys)].isna().any(axis=1).sum()
        if null_left > 0:
            warnings.append(f"WARNING: {null_left} rows with NA in join keys (left)")
        if null_right > 0:
            warnings.append(f"WARNING: {null_right} rows with NA in join keys (right)")

        return warnings

    def _dtypes_compatible(self, left_dtype, right_dtype) -> bool:
        if left_dtype == right_dtype:
            return True
        try:
            if pd.api.types.is_numeric_dtype(left_dtype) and pd.api.types.is_numeric_dtype(
                right_dtype
            ):
                return True
            if pd.api.types.is_datetime64_any_dtype(
                left_dtype
            ) and pd.api.types.is_datetime64_any_dtype(right_dtype):
                return True
        except (TypeError, AttributeError):
            pass
        return False

    def _apply_column_selection(
        self,
        df: pd.DataFrame,
        key_cols: Tuple[str, ...],
        include: Optional[Sequence[str]],
        exclude: Optional[Sequence[str]],
    ) -> pd.DataFrame:
        cols = list(df.columns)
        if exclude:
            cols = [c for c in cols if c not in exclude]
        if include:
            key_set = set(key_cols)
            cols = [c for c in include if c in cols or c in key_set]
            # Ensure keys are included
            for k in key_cols:
                if k not in cols:
                    cols.insert(0, k)
        return df[[c for c in cols if c in df.columns]]

    def _build_summary(
        self,
        left: pd.DataFrame,
        right: pd.DataFrame,
        merged: pd.DataFrame,
        join_keys: Tuple[Tuple[str, ...], Tuple[str, ...]],
        how: str,
        validation_warnings: List[str],
    ) -> MergeSummary:
        rows_left = len(left)
        rows_right = len(right)
        rows_result = len(merged)

        left_cols = set(left.columns)
        right_cols = set(right.columns)
        result_cols = set(merged.columns)
        new_cols = result_cols - left_cols - right_cols
        cols_from_left = [c for c in result_cols if c in left_cols or c.endswith("_left")]
        cols_from_right = [c for c in result_cols if c in right_cols or c.endswith("_right")]

        matched = 0
        unmatched_left = 0
        unmatched_right = 0
        if "_merge" in merged.columns:
            vc = merged["_merge"].value_counts()
            matched = int(vc.get("both", 0))
            unmatched_left = int(vc.get("left_only", 0))
            unmatched_right = int(vc.get("right_only", 0))
        missing_introduced = {}
        for col in merged.columns:
            if col in left.columns and col in right.columns:
                continue  # Key column or suffix-resolved
            if col == "_merge":
                continue
            orig_null = 0
            if col in left.columns:
                orig_null = left[col].isna().sum()
            elif col in right.columns:
                orig_null = right[col].isna().sum()
            new_null = merged[col].isna().sum()
            if new_null > orig_null:
                missing_introduced[col] = int(new_null - orig_null)

        return MergeSummary(
            rows_left=rows_left,
            rows_right=rows_right,
            rows_result=rows_result,
            matched_rows=matched,
            unmatched_left=unmatched_left,
            unmatched_right=unmatched_right,
            new_columns_added=sorted(new_cols),
            columns_from_left=sorted(cols_from_left),
            columns_from_right=sorted(cols_from_right),
            missing_values_introduced=missing_introduced,
            join_keys=list(join_keys[0]) + list(join_keys[1]),
            merge_type=how,
            validation_passed=True,
            validation_warnings=validation_warnings,
        )

    def suggest_join_keys(
        self, left: pd.DataFrame, right: pd.DataFrame, max_candidates: int = 5
    ) -> List[Tuple[List[str], float]]:
        candidates: List[Tuple[List[str], float]] = []
        left_cols = set(left.columns)
        right_cols = set(right.columns)
        common_names = left_cols & right_cols

        for col in common_names:
            if left[col].dtype == right[col].dtype or self._dtypes_compatible(
                left[col].dtype, right[col].dtype
            ):
                score = 1.0
                col_lower = col.lower()
                if "id" in col_lower or "key" in col_lower or col_lower == "index":
                    score += 0.5
                if left[col].nunique() == len(left) and right[col].nunique() == len(right):
                    score += 0.3
                candidates.append(([col], score))
        candidates.sort(key=lambda x: -x[1])
        return candidates[:max_candidates]
