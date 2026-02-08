
from __future__ import annotations

from typing import Dict, List, Optional

import pandas as pd


class DataManager:
    def __init__(self) -> None:
        self._datasets: Dict[str, pd.DataFrame] = {}

    def add_dataset(self, name: str, df: pd.DataFrame, overwrite: bool = False) -> None:
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame")
        if name in self._datasets and not overwrite:
            raise ValueError(f"Dataset '{name}' already exists. Use overwrite=True to replace.")
        self._datasets[name] = df.copy()

    def get_dataset(self, name: str) -> pd.DataFrame:
        if name not in self._datasets:
            raise KeyError(f"Dataset '{name}' not found. Available: {list(self._datasets.keys())}")
        return self._datasets[name].copy()

    def get_dataset_ref(self, name: str) -> pd.DataFrame:
        if name not in self._datasets:
            raise KeyError(f"Dataset '{name}' not found. Available: {list(self._datasets.keys())}")
        return self._datasets[name]

    def has_dataset(self, name: str) -> bool:
        return name in self._datasets

    def list_datasets(self) -> List[str]:
        return list(self._datasets.keys())

    def remove_dataset(self, name: str) -> None:
        if name not in self._datasets:
            raise KeyError(f"Dataset '{name}' not found")
        del self._datasets[name]

    def rename_dataset(self, old_name: str, new_name: str) -> None:
        if old_name not in self._datasets:
            raise KeyError(f"Dataset '{old_name}' not found")
        if new_name in self._datasets:
            raise ValueError(f"Dataset '{new_name}' already exists")
        self._datasets[new_name] = self._datasets.pop(old_name)

    def dataset_info(self, name: str) -> dict:
        df = self.get_dataset_ref(name)
        return {
            "name": name,
            "rows": len(df),
            "columns": list(df.columns),
            "dtypes": df.dtypes.astype(str).to_dict(),
        }
