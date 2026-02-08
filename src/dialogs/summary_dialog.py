

from __future__ import annotations

import re

import numpy as np
import pandas as pd
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QHeaderView,
    QFileDialog,
    QMessageBox,
    QApplication,
)


class SummaryWindow(QDialog):
    def __init__(self, df, parent=None):
        super().__init__(parent)
        self.df = df.copy()
        self.summary_frames = {}

        self.setWindowTitle("Dataset Summary")
        self.resize(900, 620)

        main_layout = QVBoxLayout(self)
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        self._build_tabs()

        button_bar = QHBoxLayout()
        button_bar.addStretch()
        self.export_button = QPushButton("Export to CSV")
        self.copy_button = QPushButton("Copy to Clipboard")
        self.close_button = QPushButton("Close")
        button_bar.addWidget(self.export_button)
        button_bar.addWidget(self.copy_button)
        button_bar.addWidget(self.close_button)
        main_layout.addLayout(button_bar)

        self.export_button.clicked.connect(self.export_to_csv)
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        self.close_button.clicked.connect(self.accept)

    def _build_tabs(self):
        overview_df = self._overview_stats()
        if not overview_df.empty:
            self._add_table_tab("📊 Overview", overview_df)
        numeric_df = self._numeric_summary()
        if numeric_df is not None:
            self._add_table_tab("🔢 Numeric Data", numeric_df)
        cat_df = self._categorical_summary()
        if cat_df is not None:
            self._add_table_tab("📝 Text Data", cat_df)
        dt_df = self._datetime_summary()
        if dt_df is not None:
            self._add_table_tab("📅 Date/Time Data", dt_df)
        dur_df = self._duration_summary()
        if dur_df is not None:
            self._add_table_tab("⏱️ Duration Data", dur_df)
        desc = self.df.describe(include='all').transpose()
        if not desc.empty:
            self._add_table_tab("📈 Full Statistics", desc)
        if self.tab_widget.count() == 0:
            fallback = pd.DataFrame({"Message": ["No data to summarize."]})
            self._add_table_tab("Summary", fallback)
    
    def _overview_stats(self):
        data = {
            "Metric": [
                "Total Rows",
                "Total Columns",
                "Memory Usage",
                "Missing Values %",
                "Duplicate Rows",
                "Complete Rows"
            ],
            "Value": [
                str(len(self.df)),
                str(len(self.df.columns)),
                f"{self.df.memory_usage(deep=True).sum() / 1024:.2f} KB",
                f"{(self.df.isna().sum().sum() / (len(self.df) * len(self.df.columns)) * 100):.2f}%",
                str(self.df.duplicated().sum()),
                str(len(self.df.dropna()))
            ]
        }
        return pd.DataFrame(data)

    def _add_table_tab(self, title, df):
        table = QTableWidget()
        table.setSortingEnabled(False)
        table.setUpdatesEnabled(False)

        rows, cols = len(df.index), len(df.columns)
        table.setRowCount(rows)
        table.setColumnCount(cols)
        table.setHorizontalHeaderLabels([str(col) for col in df.columns])
        for col_idx, col_name in enumerate(df.columns):
            col_name_str = str(col_name)
            header_item = table.horizontalHeaderItem(col_idx)
            if header_item and len(col_name_str) > 20:
                header_item.setToolTip(col_name_str)

        row_headers = [str(idx) for idx in df.index]
        table.setVerticalHeaderLabels(row_headers)
        for row_idx, row_name in enumerate(df.index):
            row_name_str = str(row_name)
            if len(row_name_str) > 20:
                pass
        data_array = df.values
        for row_idx in range(rows):
            for col_idx in range(cols):
                value = data_array[row_idx, col_idx]
                if pd.isna(value):
                    item = QTableWidgetItem("")
                else:
                    val_str = str(value)
                    item = QTableWidgetItem(val_str)
                    if len(val_str) > 50:
                        item.setToolTip(val_str)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                table.setItem(row_idx, col_idx, item)

        table.setUpdatesEnabled(True)
        table.setSortingEnabled(True)
        table.resizeColumnsToContents()
        for col in range(cols):
            current_width = table.columnWidth(col)
            if current_width > 300:
                table.setColumnWidth(col, 300)
            elif current_width < 80:
                table.setColumnWidth(col, 80)
        table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        table.setAlternatingRowColors(True)
        self.tab_widget.addTab(table, title)

    def _numeric_summary(self):
        numeric_df = self.df.select_dtypes(include=[np.number])
        if numeric_df.empty:
            return None

        rows = []
        for col in numeric_df.columns:
            series = numeric_df[col]
            valid = series.dropna()
            rows.append({
                "Column": col,
                "Count": int(valid.count()),
                "Mean": self._format_number(valid.mean()),
                "Median": self._format_number(valid.median()),
                "Min": self._format_number(valid.min()),
                "Max": self._format_number(valid.max()),
                "Std": self._format_number(valid.std()),
                "Missing": int(series.isna().sum()),
            })
        return pd.DataFrame(rows)

    def _categorical_summary(self):
        cat_cols = [
            col for col in self.df.columns
            if pd.api.types.is_object_dtype(self.df[col])
            or pd.api.types.is_categorical_dtype(self.df[col])
            or pd.api.types.is_string_dtype(self.df[col])
        ]
        if not cat_cols:
            return None

        rows = []
        for col in cat_cols:
            series = self.df[col]
            non_null = series.dropna()
            top_values = ""
            if not non_null.empty:
                top_counts = non_null.astype(str).value_counts().head(3)
                top_values = ", ".join(f"{idx} ({cnt})" for idx, cnt in top_counts.items())
            avg_len = ""
            if not non_null.empty:
                avg_len_val = non_null.astype(str).map(len).mean()
                avg_len = self._format_number(avg_len_val)
            rows.append({
                "Column": col,
                "Unique": int(non_null.nunique()),
                "Top Values": top_values,
                "Missing": int(series.isna().sum()),
                "Avg String Length": avg_len,
            })
        return pd.DataFrame(rows)

    def _datetime_summary(self):
        candidate_cols = []
        for col in self.df.columns:
            series = self.df[col]
            if pd.api.types.is_datetime64_any_dtype(series):
                candidate_cols.append(col)
            else:
                coerced = pd.to_datetime(series, errors="coerce", utc=True)
                if coerced.notna().any():
                    candidate_cols.append(col)
        if not candidate_cols:
            return None

        rows = []
        for col in candidate_cols:
            series = self.df[col]
            coerced = pd.to_datetime(series, errors="coerce")
            valid = coerced.dropna()
            if valid.empty:
                continue
            min_val = valid.min()
            max_val = valid.max()
            missing = series.isna().sum() + (coerced.isna() & series.notna()).sum()
            rows.append({
                "Column": col,
                "Earliest": min_val.isoformat(sep=" "),
                "Latest": max_val.isoformat(sep=" "),
                "Range": str(max_val - min_val),
                "Missing": int(missing),
            })

        return pd.DataFrame(rows)

    def _duration_summary(self):
        duration_cols = []
        for col in self.df.columns:
            series = self.df[col]
            parsed = series.apply(self._parse_duration_seconds)
            valid_ratio = parsed.notna().sum() / len(series) if len(series) else 0
            if valid_ratio >= 0.4:
                duration_cols.append((col, parsed))
        if not duration_cols:
            return None

        rows = []
        for col, parsed_series in duration_cols:
            valid = parsed_series.dropna()
            if valid.empty:
                continue
            rows.append({
                "Column": col,
                "Count": int(valid.count()),
                "Min": self._format_timedelta(valid.min()),
                "Max": self._format_timedelta(valid.max()),
                "Mean": self._format_timedelta(valid.mean()),
                "Missing": int(parsed_series.isna().sum()),
            })
        return pd.DataFrame(rows)

    def _parse_duration_seconds(self, value):
        if pd.isna(value):
            return np.nan
        if isinstance(value, (pd.Timedelta, np.timedelta64)):
            return pd.to_timedelta(value).total_seconds()
        if isinstance(value, (int, float)):
            return float(value)

        text = str(value).strip().lower()
        if not text:
            return np.nan

        if re.fullmatch(r"\d+:\d+(:\d+)?", text):
            parts = [int(p) for p in text.split(":")]
            if len(parts) == 2:
                minutes, seconds = parts
                return minutes * 60 + seconds
            if len(parts) == 3:
                hours, minutes, seconds = parts
                return hours * 3600 + minutes * 60 + seconds

        total_seconds = 0.0
        found = False
        pattern = re.compile(r"(\d+(?:\.\d+)?)\s*(days?|day|d|hours?|hour|h|minutes?|minute|mins?|min|m|seconds?|second|secs?|sec|s)")
        for match in pattern.finditer(text):
            found = True
            value_num = float(match.group(1))
            unit = match.group(2)
            if unit.startswith("d"):
                total_seconds += value_num * 86400
            elif unit.startswith("h"):
                total_seconds += value_num * 3600
            elif unit.startswith("m") and not unit.startswith("sec"):
                total_seconds += value_num * 60
            else:
                total_seconds += value_num

        if found:
            return total_seconds

        try:
            td = pd.to_timedelta(text, errors="raise")
            return td.total_seconds()
        except (ValueError, OverflowError):
            return np.nan

    def _format_number(self, value):
        if value is None or pd.isna(value):
            return ""
        if isinstance(value, (int, np.integer)):
            return int(value)
        if isinstance(value, (float, np.floating)):
            return round(float(value), 3)
        return value

    def _format_timedelta(self, seconds):
        if seconds is None or pd.isna(seconds):
            return ""
        td = pd.to_timedelta(seconds, unit="s")
        total_seconds = int(td.total_seconds())
        days, remainder = divmod(total_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, secs = divmod(remainder, 60)
        parts = []
        if days:
            parts.append(f"{days}d")
        if hours:
            parts.append(f"{hours}h")
        if minutes:
            parts.append(f"{minutes}m")
        if secs or not parts:
            parts.append(f"{secs}s")
        return " ".join(parts)

    def _combined_frame(self):
        if not self.summary_frames:
            return pd.DataFrame()
        layers = []
        for title, frame in self.summary_frames.items():
            tagged = frame.copy()
            tagged.insert(0, "Summary", title)
            layers.append(tagged)
        return pd.concat(layers, ignore_index=True)

    def export_to_csv(self):
        export_frame = self._combined_frame()
        if export_frame.empty:
            QMessageBox.information(self, "Export", "Nothing to export.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export Summary", "summary.csv", "CSV Files (*.csv)")
        if not path:
            return
        try:
            export_frame.to_csv(path, index=False)
            QMessageBox.information(self, "Export", f"Summary saved to:\n{path}")
        except Exception as exc:
            QMessageBox.critical(self, "Export Error", f"Failed to save summary:\n{exc}")

    def copy_to_clipboard(self):
        export_frame = self._combined_frame()
        if export_frame.empty:
            QMessageBox.information(self, "Copy", "Nothing to copy.")
            return
        clipboard = QApplication.clipboard()
        clipboard.setText(export_frame.to_csv(index=False))
        QMessageBox.information(self, "Copy", "Summary copied to the clipboard.")
