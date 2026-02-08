from __future__ import annotations
import re
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QPushButton,
    QMessageBox,
)
from PyQt5.QtWidgets import QLabel as QtLabel


class chartwindow(QDialog):
    def __init__(self, df, parent=None):
        super().__init__(parent)
        self.df = df.copy()
        self.parent = parent
        self.column_types = {}
        self.setWindowTitle("Create Chart")
        self.resize(1000, 700)

        main_layout = QVBoxLayout(self)
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(QtLabel("Chart Type:"))
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems([
            "Histogram",
            "Bar Chart",
            "Pie Chart",
            "Scatter Plot",
            "Line Chart"
        ])
        self.chart_type_combo.currentIndexChanged.connect(self.update_chart_options)
        controls_layout.addWidget(self.chart_type_combo)

        controls_layout.addWidget(QtLabel("X Column:"))
        self.x_column_combo = QComboBox()
        controls_layout.addWidget(self.x_column_combo)

        self.y_label = QtLabel("Y Column:")
        controls_layout.addWidget(self.y_label)
        self.y_column_combo = QComboBox()
        controls_layout.addWidget(self.y_column_combo)

        self.generate_button = QPushButton("Generate Chart")
        self.generate_button.clicked.connect(self.generate_chart)
        controls_layout.addWidget(self.generate_button)
        main_layout.addLayout(controls_layout)
        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        main_layout.addWidget(self.canvas)
        self.update_chart_options()
    def get_column_type(self, col):
        if col in self.column_types:
            return self.column_types[col]

        series = self.df[col].dropna()
        if series.empty:
            self.column_types[col] = "categorical"
            return "categorical"
        if pd.api.types.is_numeric_dtype(series):
            self.column_types[col] = "numeric" if series.nunique() >= 20 else "categorical"
            return self.column_types[col]
        if pd.api.types.is_datetime64_any_dtype(series):
            self.column_types[col] = "datetime"
            return "datetime"
        sample = series.head(100).astype(str)
        duration_ratio = self.check_duration_pattern(sample)
        datetime_ratio = self.check_datetime_pattern(sample)
        if duration_ratio > 0.4:
            self.column_types[col] = "duration"
        elif datetime_ratio > 0.4:
            self.column_types[col] = "datetime"
        elif series.nunique() < 20:
            self.column_types[col] = "categorical"
        else:
            self.column_types[col] = "categorical"

        return self.column_types[col]

    def check_duration_pattern(self, series):
        pattern = r"(?:\d+:\d+(?::\d+)?)|(?:\d+\s*(?:hour|h|minute|min|sec|second|day|week|month|year|d|m|s))"
        matches = series.str.contains(pattern, flags=re.IGNORECASE, na=False)
        return matches.sum() / len(series) if len(series) > 0 else 0.0

    def check_datetime_pattern(self, series):
        parsed = series.apply(self.try_parse_date)
        return parsed.notna().sum() / len(series) if len(series) > 0 else 0.0

    def try_parse_date(self, val):
        if pd.isna(val):
            return pd.NaT
        if isinstance(val, (pd.Timestamp, datetime)):
            return pd.Timestamp(val)
        try:
            return pd.to_datetime(val, errors='coerce')
        except:
            return pd.NaT
    def parse_duration_to_seconds(self, value):
        if pd.isna(value):
            return np.nan
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, (pd.Timedelta, np.timedelta64)):
            return pd.to_timedelta(value).total_seconds()

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
        except:
            return np.nan
    def update_chart_options(self):
        chart_type = self.chart_type_combo.currentText()

        valid_x_cols = []
        valid_y_cols = []

        for col in self.df.columns:
            col_type = self.get_column_type(col)
            if chart_type == "Histogram":
                if col_type in ["numeric", "duration"]:
                    valid_x_cols.append(col)
            elif chart_type == "Bar Chart":
                if col_type == "categorical":
                    valid_x_cols.append(col)
                if col_type in ["numeric", "duration"]:
                    valid_y_cols.append(col)
            elif chart_type == "Pie Chart":
                if col_type == "categorical":
                    valid_x_cols.append(col)
            elif chart_type == "Scatter Plot":
                if col_type in ["numeric", "duration"]:
                    valid_x_cols.append(col)
                    valid_y_cols.append(col)
            elif chart_type == "Line Chart":
                if col_type == "datetime":
                    valid_x_cols.append(col)
                if col_type in ["numeric", "duration"]:
                    valid_y_cols.append(col)
        self.x_column_combo.clear()
        self.y_column_combo.clear()

        if valid_x_cols:
            self.x_column_combo.addItems(valid_x_cols)
            self.x_column_combo.setEnabled(True)
        else:
            self.x_column_combo.addItem("(No valid columns)")
            self.x_column_combo.setEnabled(False)
            QMessageBox.warning(
                self,
                "No Valid Columns",
                f"No valid columns found for {chart_type}.\n\n"
                f"Required:\n{self.get_requirements_text(chart_type)}"
            )

        if valid_y_cols:
            self.y_column_combo.addItems(valid_y_cols)
            self.y_column_combo.setEnabled(True)
            self.y_label.setVisible(True)
        else:
            self.y_column_combo.addItem("(No valid columns)")
            self.y_column_combo.setEnabled(False)
            self.y_label.setVisible(chart_type not in ["Histogram", "Pie Chart"])

    def get_requirements_text(self, chart_type):
        requirements = {
            "Histogram": "X: numeric or duration column",
            "Bar Chart": "X: categorical column\nY: numeric or duration column",
            "Pie Chart": "X: categorical column",
            "Scatter Plot": "X: numeric or duration column\nY: numeric or duration column",
            "Line Chart": "X: datetime column\nY: numeric or duration column"
        }
        return requirements.get(chart_type, "")
    def generate_chart(self):
        chart_type = self.chart_type_combo.currentText()
        x_col = self.x_column_combo.currentText()
        y_col = self.y_column_combo.currentText() if self.y_column_combo.isEnabled() else None

        if x_col == "(No valid columns)" or (y_col and y_col == "(No valid columns)"):
            QMessageBox.warning(self, "Invalid Selection", "Please select valid columns for the chart.")
            return

        if not x_col:
            QMessageBox.warning(self, "Missing Column", "Please select an X column.")
            return

        if chart_type in ["Bar Chart", "Scatter Plot", "Line Chart"] and not y_col:
            QMessageBox.warning(self, "Missing Column", "Please select a Y column.")
            return

        self.figure.clear()
        ax = self.figure.add_subplot(111)

        try:
            if chart_type == "Histogram":
                self.create_histogram(ax, x_col)
            elif chart_type == "Bar Chart":
                self.create_bar_chart(ax, x_col, y_col)
            elif chart_type == "Pie Chart":
                self.create_pie_chart(ax, x_col)
            elif chart_type == "Scatter Plot":
                self.create_scatter_plot(ax, x_col, y_col)
            elif chart_type == "Line Chart":
                self.create_line_chart(ax, x_col, y_col)

            self.figure.tight_layout()
            self.canvas.draw()
        except Exception as e:
            QMessageBox.critical(self, "Chart Error", f"Failed to generate chart:\n{str(e)}")
    def create_histogram(self, ax, x_col):
        series = self.df[x_col].dropna()
        if self.get_column_type(x_col) == "duration":
            values = series.apply(self.parse_duration_to_seconds).dropna()
            ax.hist(values, bins=30, edgecolor='black')
            ax.set_xlabel(f"{x_col} (seconds)")
        else:
            ax.hist(series, bins=30, edgecolor='black')
            ax.set_xlabel(x_col)
        ax.set_ylabel("Frequency")
        ax.set_title(f"Histogram of {x_col}")
        ax.grid(True, alpha=0.3)

    def create_bar_chart(self, ax, x_col, y_col):
        if self.get_column_type(y_col) == "duration":
            grouped = self.df.groupby(x_col)[y_col].apply(lambda x: self.parse_duration_to_seconds(x).mean())
        else:
            grouped = self.df.groupby(x_col)[y_col].mean()
        ax.bar(range(len(grouped)), grouped.values, edgecolor='black')
        ax.set_xticks(range(len(grouped)))
        ax.set_xticklabels(grouped.index, rotation=45, ha='right')
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col + (" (seconds)" if self.get_column_type(y_col) == "duration" else ""))
        ax.set_title(f"Bar Chart: {y_col} by {x_col}")
        ax.grid(True, alpha=0.3, axis='y')

    def create_pie_chart(self, ax, x_col):
        value_counts = self.df[x_col].value_counts()
        ax.pie(value_counts.values, labels=value_counts.index, autopct='%1.1f%%', startangle=90)
        ax.set_title(f"Pie Chart of {x_col}")

    def create_scatter_plot(self, ax, x_col, y_col):
        x_values = self.df[x_col]
        y_values = self.df[y_col]

        if self.get_column_type(x_col) == "duration":
            x_values = x_values.apply(self.parse_duration_to_seconds)
        if self.get_column_type(y_col) == "duration":
            y_values = y_values.apply(self.parse_duration_to_seconds)

        mask = x_values.notna() & y_values.notna()
        ax.scatter(x_values[mask], y_values[mask], alpha=0.6, edgecolors='black', linewidth=0.5)
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_title(f"Scatter Plot: {y_col} vs {x_col}")
        ax.grid(True, alpha=0.3)

    def create_line_chart(self, ax, x_col, y_col):
        df_sorted = self.df.sort_values(by=x_col)
        x_series = df_sorted[x_col]
        y_series = df_sorted[y_col]

        if self.get_column_type(y_col) == "duration":
            y_series = y_series.apply(self.parse_duration_to_seconds)

        mask = x_series.notna() & y_series.notna()
        ax.plot(x_series[mask], y_series[mask], marker='o', linestyle='-', linewidth=2, markersize=4)
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_title(f"Line Chart: {y_col} over {x_col}")
        ax.grid(True, alpha=0.3)
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
