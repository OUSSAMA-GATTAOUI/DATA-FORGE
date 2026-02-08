
from __future__ import annotations

import re

import numpy as np
import pandas as pd
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QMessageBox,
)


class sortwindow(QWidget):
    def __init__(self, df, parent=None):
        super().__init__(parent)
        self.df = df
        self.column = df.columns.tolist()
        self.parent = parent
        self.setWindowTitle("Sort Data")
        self.resize(400, 200)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Select Column:"))
        self.column_combo = QComboBox()
        self.column_combo.addItems(self.column)
        layout.addWidget(self.column_combo)
        layout.addWidget(QLabel("Select Sort Method:"))
        self.method_combo = QComboBox()
        layout.addWidget(self.method_combo)
        btn_layout = QHBoxLayout()
        self.apply_btn = QPushButton("Sort")
        btn_layout.addWidget(self.apply_btn)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        self.column_combo.currentIndexChanged.connect(self.update_sort_methods)
        self.apply_btn.clicked.connect(self.apply_sort)
        self.update_sort_methods()

    def parse_duration_to_days(self, val):
        if isinstance(val, (int, float)):
            return float(val)
        if isinstance(val, str):
            total_days = 0
            val_lower = val.lower().strip()
            if val_lower.isdigit():
                return float(val_lower) / 1440
            time_match = re.match(r"(\d+):(\d+)(?::(\d+))?", val_lower)
            if time_match:
                hours = int(time_match.group(1))
                minutes = int(time_match.group(2))
                seconds = int(time_match.group(3)) if time_match.group(3) else 0
                return hours / 24 + minutes / 1440 + seconds / 86400
            h = re.search(r"(\d+)\s*hour", val_lower)
            m_ = re.search(r"(\d+)\s*min", val_lower)
            s = re.search(r"(\d+)\s*sec", val_lower)
            hours = int(h.group(1)) if h else 0
            minutes = int(m_.group(1)) if m_ else 0
            seconds = int(s.group(1)) if s else 0
            if hours or minutes or seconds:
                return hours / 24 + minutes / 1440 + seconds / 86400
            y = re.findall(r"(\d+)\s*year", val_lower)
            mo = re.findall(r"(\d+)\s*month", val_lower)
            w = re.findall(r"(\d+)\s*week", val_lower)
            d = re.findall(r"(\d+)\s*day", val_lower)
            total_days += sum(int(x) * 365 for x in y)
            total_days += sum(int(x) * 30 for x in mo)
            total_days += sum(int(x) * 7 for x in w)
            total_days += sum(int(x) for x in d)
            if total_days == 0:
                num_match = re.search(r"\d+", val_lower)
                if num_match:
                    total_days = float(num_match.group())
                else:
                    return np.nan

            return total_days

    def update_sort_methods(self):
        self.method_combo.clear()
        col = self.column_combo.currentText()
        series = self.df[col]
        options = []
        if pd.api.types.is_numeric_dtype(series):
            options = ["Ascending", "Descending", "Nulls First", "Nulls Last"]
        elif pd.api.types.is_datetime64_any_dtype(series):
            options = ["Oldest → Newest", "Newest → Oldest", "Nulls First", "Nulls Last"]
        else:
            try:
                parsed_dates = pd.to_datetime(series, dayfirst=False, errors='coerce')
                date_valid_1 = parsed_dates.notna().sum()
                parsed_dates_2 = pd.to_datetime(series, dayfirst=True, errors='coerce')
                date_valid_2 = parsed_dates_2.notna().sum()
                date_valid = max(date_valid_1, date_valid_2) / len(series)

                if date_valid > 0.5:
                    options = ["Oldest → Newest", "Newest → Oldest", "Nulls First", "Nulls Last"]
            except Exception as e:
                print(f"Column '{col}': Date parsing failed: {e}")
            if not options:
                try:
                    numeric_series = series.map(self.parse_duration_to_days)
                    numeric_valid = numeric_series.notna().sum() / len(series)
                    if numeric_valid > 0.5:
                        options = ["Ascending", "Descending", "Nulls First", "Nulls Last"]
                except Exception as e:
                    print(f"Column '{col}': Duration parsing failed: {e}")
            if not options:
                options = ["A → Z", "Z → A"]
        self.method_combo.addItems(options)

    def apply_sort(self):
        column = self.column_combo.currentText()
        method = self.method_combo.currentText()
        if not column or not method:
            QMessageBox.warning(self, "Input Error", "Please select a column and sort method.")
            return
        if self.parent:
            self.parent.apply_user_sort(column, method)
        self.close()
