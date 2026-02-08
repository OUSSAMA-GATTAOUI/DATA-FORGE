from __future__ import annotations
from PyQt5.QtCore import Qt
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


class FilterWindow(QWidget):
    def __init__(self, columns, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Filter Options")
        self.columns = columns
        self.parent = parent
        self.resize(300, 200)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Select Column:"))
        self.column_combo = QComboBox()
        self.column_combo.addItems(columns)
        layout.addWidget(self.column_combo)
        layout.addWidget(QLabel("Select Data Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "",
            "Number",
            "Duration",
            "Duration (Years , days or others)",
            "Date",
            "Seasons (for series)",
            "Text",
        ])
        self.duration_widget = QWidget()
        duration_layout = QHBoxLayout()
        self.hours_label = QLabel("Enter the hours:")
        self.minute_label = QLabel("Enter the minute:")
        self.second_label = QLabel("Enter the second:")
        self.hours_input = QLineEdit()
        self.minute_input = QLineEdit()
        self.second_input = QLineEdit()
        self.day_label = QLabel("DAY:")
        self.month_label = QLabel("MONTH:")
        self.year_label = QLabel("YEAR:")
        self.day_input = QLineEdit()
        self.month_input = QLineEdit()
        self.year_input = QLineEdit()
        self.day2_label = QLabel("DAY 2:")
        self.month2_label = QLabel("MONTH 2:")
        self.year2_label = QLabel("YEAR 2:")
        self.day2_input = QLineEdit()
        self.month2_input = QLineEdit()
        self.year2_input = QLineEdit()
        layout.addWidget(self.type_combo)
        layout.addWidget(QLabel("Select Condition:"))
        self.operator_combo = QComboBox()
        self.operator_combo.addItems(["", "==", "!=", "≥", ">", "≤", "<", "contains", "not contains", "empty", "between"])
        layout.addWidget(self.operator_combo)
        for w in [self.hours_label, self.hours_input,
                self.minute_label, self.minute_input,
                self.second_label, self.second_input]:
            duration_layout.addWidget(w)
        self.duration_widget.setLayout(duration_layout)
        self.duration_widget.hide()
        self.date_widget = QWidget()
        date_layout = QHBoxLayout()
        for w in [self.day_label, self.day_input,
                self.month_label, self.month_input,
                self.year_label, self.year_input,
                self.day2_label, self.day2_input,
                self.month2_label, self.month2_input,
                self.year2_label, self.year2_input]:
            date_layout.addWidget(w)
        self.date_widget.setLayout(date_layout)
        self.date_widget.hide()
        self.date2_widget = QWidget()
        date2_layout = QHBoxLayout()
        for w in [self.day2_label, self.day2_input,
                self.month2_label, self.month2_input,
                self.year2_label, self.year2_input]:
            date2_layout.addWidget(w)
        self.date2_widget.setLayout(date2_layout)
        self.date2_widget.hide()
        layout.addWidget(self.duration_widget)
        layout.addWidget(self.date_widget)
        layout.addWidget(self.date2_widget)
        self.operator_combo.currentIndexChanged.connect(self.ubdate_input)
        self.type_combo.currentIndexChanged.connect(self.ubdate_input)
        self.min_label = QLabel("Enter the minimal Value:")
        self.min_Value = QLineEdit()
        self.max_label = QLabel("Enter the maximal Value:")
        self.max_Value = QLineEdit()
        self.value_label = QLabel("Enter a Value:")
        self.value_input = QLineEdit()
        layout.addWidget(self.min_label)
        layout.addWidget(self.min_Value)
        layout.addWidget(self.max_label)
        layout.addWidget(self.max_Value)
        layout.addWidget(self.value_label)
        layout.addWidget(self.value_input)
        self.min_label.hide()
        self.min_Value.hide()
        self.max_label.hide()
        self.max_Value.hide()
        self.value_input.hide()
        self.value_label.hide()
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self.apply_filter)
        layout.addWidget(apply_btn)
        self.setLayout(layout)
        self.ubdate_input()

    def ubdate_input(self):
        op = self.operator_combo.currentText()
        dt = self.type_combo.currentText().strip()
        
        # Update operator options based on data type
        current_operator = self.operator_combo.currentText()
        self.operator_combo.blockSignals(True)
        self.operator_combo.clear()
        
        if dt == "Text":
            # Text only supports these operators
            self.operator_combo.addItems(["", "==", "!=", "contains", "not contains", "empty"])
        else:
            # All other types get the full list
            self.operator_combo.addItems(["", "==", "!=", "≥", ">", "≤", "<", "contains", "not contains", "empty", "between"])
        
        # Restore previous selection if possible
        index = self.operator_combo.findText(current_operator)
        if index >= 0:
            self.operator_combo.setCurrentIndex(index)
        self.operator_combo.blockSignals(False)
        
        self.duration_widget.hide()
        self.date_widget.hide()
        self.date2_widget.hide()
        self.value_label.hide()
        self.value_input.hide()
        self.min_label.hide()
        self.min_Value.hide()
        self.max_label.hide()
        self.max_Value.hide()
        if dt == "Duration":
            self.duration_widget.show()
        elif dt == "Duration (Years , days or others)":
            self.value_label.show()
            self.value_input.show()
        elif dt == "Date":
            if op == "between":
                self.date_widget.show()
                self.date2_widget.show()
            else:
                self.date_widget.show()
        elif dt in ["Number", "Text"]:
            if op == "between":
                self.min_label.show()
                self.min_Value.show()
                self.max_label.show()
                self.max_Value.show()
            elif op == "empty":
                pass
            else:
                self.value_label.show()
                self.value_input.show()

    def apply_filter(self):
        column = self.column_combo.currentText()
        operator = self.operator_combo.currentText()
        data_type = self.type_combo.currentText()
        if not column or not operator or not data_type:
            QMessageBox.warning(self, "Input Error", "Please select a Column, Data Type, and Condition.")
            return
        if operator == "between":
            if data_type == "Date":
                day1 = self.day_input.text().strip()
                month1 = self.month_input.text().strip()
                year1 = self.year_input.text().strip()
                day2 = self.day2_input.text().strip()
                month2 = self.month2_input.text().strip()
                year2 = self.year2_input.text().strip()
                min_val = f"{year1}-{month1.zfill(2)}-{day1.zfill(2)}" if year1 and month1 and day1 else ""
                max_val = f"{year2}-{month2.zfill(2)}-{day2.zfill(2)}" if year2 and month2 and day2 else ""
                if not min_val or not max_val:
                    QMessageBox.warning(self, "Input Error", "Please enter both start and end dates.")
                    return
                value = [min_val, max_val]
            else:
                min_text = self.min_Value.text()
                max_text = self.max_Value.text()
                if not min_text or not max_text:
                    QMessageBox.warning(self, "Input Error", "Please enter both min and max values.")
                    return
                value = [min_text, max_text]

        else:
            if data_type == "Duration":
                hours = self.hours_input.text()
                minutes = self.minute_input.text()
                seconds = self.second_input.text()
                value = ""
                if hours:
                    value += hours + " hours "
                if minutes:
                    value += minutes + " minutes "
                if seconds:
                    value += seconds + " seconds "
                value = value.strip()
            elif data_type == "Date":
                day = self.day_input.text()
                month = self.month_input.text()
                year = self.year_input.text()
                value = f"{year}-{month.zfill(2)}-{day.zfill(2)}" if year and month and day else ""
                if operator not in ["empty"] and not value:
                    QMessageBox.warning(self, "Input Error", "Please enter a value.")
                    return
            else:
                value = self.value_input.text()
                if operator not in ["empty"] and not value:
                    QMessageBox.warning(self, "Input Error", "Please enter a value.")
                    return
        if self.parent:
            self.parent.apply_user_filter(column, operator, value, data_type)

        self.close()
