from __future__ import annotations
import re
import pandas as pd
from dateutil.parser import parse
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QLineEdit,
    QPushButton,
    QMessageBox,
)
class cleanwindow(QWidget):
    def __init__(self, df, parent=None):
        super().__init__(parent)
        self.df = df
        self.column = df.columns.tolist()
        self.parent = parent
        self.setWindowTitle("clean Data")
        self.resize(400, 200)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Select Column:"))
        self.column_combo = QComboBox()
        self.column_combo.addItems(self.column)
        layout.addWidget(self.column_combo)
        layout.addWidget(QLabel("Select clean Method:"))
        self.method_combo = QComboBox()
        layout.addWidget(self.method_combo)
        self.duration_label = QLabel("Select duration format:")
        layout.addWidget(self.duration_label)
        self.duration_label.hide()
        self.duration_combo = QComboBox()
        self.duration_combo.hide()
        self.duration_combo.addItems(["To days", "to HH:MM:SS", "to years", "to hours", "to minute", "to second"])
        layout.addWidget(self.duration_combo)
        self.Date_label = QLabel("Select Date format:")
        layout.addWidget(self.Date_label)
        self.Date_label.hide()
        self.date_combo = QComboBox()
        self.date_combo.hide()
        self.date_combo.addItems(["D/M/Y", "M/D/Y", "Y/M/D", "Y-M-D", "D-M-Y"])
        layout.addWidget(self.date_combo)
        self.normalize_numeric_label = QLabel("Enter a unit:")
        self.normalize_numeric_input = QLineEdit()
        self.normalize_numeric_label.hide()
        self.normalize_numeric_input.hide()
        self.replace_label = QLabel("Enter the default value:")
        self.replace_input = QLineEdit()
        self.replace_label.hide()
        self.replace_input.hide()
        self.max_label = QLabel("Enter the maximum value:")
        self.max_input = QLineEdit()
        self.max_label.hide()
        self.max_input.hide()
        self.min_label = QLabel("Enter the minimum value:")
        self.min_input = QLineEdit()
        self.min_label.hide()
        self.min_input.hide()
        layout.addWidget(self.replace_label)
        layout.addWidget(self.replace_input)
        layout.addWidget(self.min_label)
        layout.addWidget(self.min_input)
        layout.addWidget(self.max_label)
        layout.addWidget(self.max_input)
        layout.addWidget(self.normalize_numeric_label)
        layout.addWidget(self.normalize_numeric_input)
        btn_layout = QHBoxLayout()
        self.apply_btn = QPushButton("clean")
        btn_layout.addWidget(self.apply_btn)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        self.column_combo.currentIndexChanged.connect(self.update_clean_methods)
        self.method_combo.currentIndexChanged.connect(self.update_clean_input)
        self.apply_btn.clicked.connect(self.apply_clean)
        self.update_clean_methods()

    def looks_like_duration(self, series):
        pattern = r"(?:\d+:\d+)|(?:\d+\s*(?:hour|h|minute|min|sec|second|day|week|month|year))"
        matches = series.dropna().astype(str).str.contains(pattern, flags=re.IGNORECASE)
        return matches.mean() > 0.5

    def smart_parse_date(self, val):
        if not isinstance(val, str):
            return pd.NaT
        val = val.strip()
        if not val:
            return pd.NaT
        try:
            parsed = parse(val, dayfirst=True, yearfirst=False)
            return parsed
        except Exception:
            return pd.NaT

    def update_clean_methods(self):
        self.method_combo.clear()
        col = self.column_combo.currentText()
        series = self.df[col]
        options = []
        if pd.api.types.is_numeric_dtype(series):
            options = ["", "Fill missing values", "Replace negative values", "Handle outliers", "Normalize numeric formats"]
        elif pd.api.types.is_datetime64_any_dtype(series):
            options = ["Convert all to datetime"]
        else:
            try:
                parsed_dates = series.apply(self.smart_parse_date)
                date_valid = parsed_dates.notna().sum() / len(series)
                if date_valid > 0.5:
                    options = ["Convert all to datetime"]
            except Exception as e:
                print(f"Column '{col}': Date parsing failed: {e}")
            if not options and self.looks_like_duration(series):
                options = ["", "Fill missing values", "Handle negative values", "Handle outliers", "Normalize TIME formats"]
            if not options:
                options = ["", "Lower", "Upper", "Capitalize", "Title", "Strip", "Remove extra spaces", "Remove punctuation"]
        self.method_combo.addItems(options)

    def update_clean_input(self):
        op = self.method_combo.currentText()
        self.replace_label.hide()
        self.replace_input.hide()
        self.min_label.hide()
        self.min_input.hide()
        self.max_label.hide()
        self.max_input.hide()
        self.normalize_numeric_label.hide()
        self.normalize_numeric_input.hide()
        self.duration_combo.hide()
        self.date_combo.hide()
        self.duration_label.hide()
        self.Date_label.hide()
        if op in ["Fill missing values", "replace negative values"]:
            self.replace_label.show()
            self.replace_input.show()
        elif op == "Handle outliers":
            self.min_label.show()
            self.min_input.show()
            self.max_label.show()
            self.max_input.show()
        elif op == "Normalize TIME formats":
            self.duration_label.show()
            self.duration_combo.show()
        elif op == "Normalize numeric formats":
            self.normalize_numeric_label.show()
            self.normalize_numeric_input.show()
        elif op == "Convert all to datetime":
            self.Date_label.show()
            self.date_combo.show()

    def apply_clean(self):
        column = self.column_combo.currentText()
        operator = self.method_combo.currentText()
        value = None

        if not column or not operator:
            QMessageBox.warning(self, "Input Error", "Please select a Column and Method.")
            return
        if operator in ["Fill missing values", "Replace negative values"]:
            value = self.replace_input.text()
            if not value:
                QMessageBox.warning(self, "Input Error", "Please enter the replacement value")
                return

        elif operator == "Handle outliers":
            min_text = self.min_input.text()
            max_text = self.max_input.text()
            if not min_text or not max_text:
                QMessageBox.warning(self, "Input Error", "Please enter both min and max values.")
                return
            value = [min_text, max_text]

        elif operator == "Normalize TIME formats":
            value = self.duration_combo.currentText()
            if not value:
                QMessageBox.warning(self, "Input Error", "Please select a duration format")
                return

        elif operator == "Normalize numeric formats":
            value = self.normalize_numeric_input.text()
            if not value:
                QMessageBox.warning(self, "Input Error", "Please enter a unit (e.g., age, $, meters)")
                return

        elif operator == "Convert all to datetime":
            value = self.date_combo.currentText()
            if not value:
                QMessageBox.warning(self, "Input Error", "Please select a date format")
                return
        if self.parent:
            self.parent.apply_clean_window(column, operator, value)

        self.close()
