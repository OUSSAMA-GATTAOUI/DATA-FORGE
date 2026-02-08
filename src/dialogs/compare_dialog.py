
from __future__ import annotations

from PyQt5.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from ..data.compare_engine import CompareEngine


class CompareDialog(QDialog):

    def __init__(self, datasets: dict, parent=None):
        super().__init__(parent)
        self.datasets = datasets
        self.setWindowTitle("Compare Datasets")
        self.resize(560, 480)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        names = list(self.datasets.keys())
        if len(names) < 2:
            layout.addWidget(QLabel("Need at least 2 datasets."))
            return

        form = QFormLayout()
        self.left_combo = QComboBox()
        self.left_combo.addItems(names)
        self.left_combo.setCurrentIndex(0)
        self.left_combo.currentIndexChanged.connect(self._run_compare)
        form.addRow("Left dataset:", self.left_combo)

        self.right_combo = QComboBox()
        self.right_combo.addItems(names)
        self.right_combo.setCurrentIndex(1 if len(names) > 1 else 0)
        self.right_combo.currentIndexChanged.connect(self._run_compare)
        form.addRow("Right dataset:", self.right_combo)

        self.key_edit = QLineEdit()
        self.key_edit.setPlaceholderText("Optional: column name for row/cell comparison")
        self.key_edit.textChanged.connect(self._run_compare)
        form.addRow("Key column:", self.key_edit)

        layout.addLayout(form)

        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)
        self.report_text.setMinimumHeight(300)
        layout.addWidget(QLabel("Comparison Report:"))
        layout.addWidget(self.report_text)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

        self._run_compare()

    def _run_compare(self):
        left_name = self.left_combo.currentText()
        right_name = self.right_combo.currentText()
        if left_name == right_name:
            self.report_text.setPlainText("Select two different datasets.")
            return
        if left_name not in self.datasets or right_name not in self.datasets:
            return

        df1 = self.datasets[left_name]
        df2 = self.datasets[right_name]
        key = self.key_edit.text().strip() or None

        engine = CompareEngine()
        report = engine.full_compare(df1, df2, key_columns=key)

        lines = []
        s = report.structure
        lines.append(f"=== Structure ===")
        lines.append(f"Left: {s.rows_left} rows, {s.cols_left} columns")
        lines.append(f"Right: {s.rows_right} rows, {s.cols_right} columns")
        if s.columns_only_left:
            lines.append(f"Only in left: {', '.join(s.columns_only_left)}")
        if s.columns_only_right:
            lines.append(f"Only in right: {', '.join(s.columns_only_right)}")
        if s.dtype_mismatches:
            for m in s.dtype_mismatches:
                lines.append(f"Dtype mismatch: {m['column']} ({m['left_dtype']} vs {m['right_dtype']})")

        if report.row_comparison:
            r = report.row_comparison
            lines.append("")
            lines.append("=== Row comparison ===")
            lines.append(f"Only in left: {r.total_only_left} | Only in right: {r.total_only_right}")
            lines.append(f"In both: {r.total_in_both} (differing: {r.total_differing})")

        if report.cell_comparison and report.cell_comparison.total_differences > 0:
            c = report.cell_comparison
            lines.append("")
            lines.append("=== Cell differences ===")
            lines.append(f"Total: {c.total_differences}")
            lines.append(f"By column: {c.column_diff_counts}")

        lines.append("")
        lines.append("=== Summary (plain English) ===")
        lines.append(engine.explain_differences_plain_english(report))

        self.report_text.setPlainText("\n".join(lines))
