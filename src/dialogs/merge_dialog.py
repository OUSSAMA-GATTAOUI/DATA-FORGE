
from __future__ import annotations

import pandas as pd
from PyQt5.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from ..data.merge_engine import MergeEngine


class MergeDialog(QDialog):

    def __init__(self, datasets: dict, parent=None):
        super().__init__(parent)
        self.datasets = datasets
        self.result_df = None
        self.result_name = None
        self.setWindowTitle("Merge Datasets")
        self.resize(420, 280)
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
        form.addRow("Left dataset:", self.left_combo)

        self.right_combo = QComboBox()
        self.right_combo.addItems(names)
        self.right_combo.setCurrentIndex(1 if len(names) > 1 else 0)
        form.addRow("Right dataset:", self.right_combo)

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Concat (append rows)", "Join: inner", "Join: left", "Join: right", "Join: outer"])
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        form.addRow("Mode:", self.mode_combo)

        self.key_combo = QComboBox()
        self.key_combo.setEnabled(False)
        form.addRow("Join key:", self.key_combo)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Merged_left_right")
        form.addRow("Output name:", self.name_edit)

        layout.addLayout(form)
        self._update_key_combo()

        self.left_combo.currentIndexChanged.connect(self._update_key_combo)
        self.right_combo.currentIndexChanged.connect(self._update_key_combo)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        ok_btn = QPushButton("Merge")
        ok_btn.clicked.connect(self._do_merge)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def _on_mode_changed(self):
        is_join = self.mode_combo.currentIndex() > 0
        self.key_combo.setEnabled(is_join)

    def _update_key_combo(self):
        left_name = self.left_combo.currentText()
        right_name = self.right_combo.currentText()
        if left_name not in self.datasets or right_name not in self.datasets:
            return
        df1 = self.datasets[left_name]
        df2 = self.datasets[right_name]
        common = list(set(df1.columns) & set(df2.columns))
        self.key_combo.clear()
        self.key_combo.addItems([""] + sorted(common))
        # Suggest best key
        engine = MergeEngine()
        suggestions = engine.suggest_join_keys(df1, df2, max_candidates=1)
        if suggestions:
            best = suggestions[0][0][0]
            idx = self.key_combo.findText(best)
            if idx >= 0:
                self.key_combo.setCurrentIndex(idx)

    def _do_merge(self):
        left_name = self.left_combo.currentText()
        right_name = self.right_combo.currentText()
        df1 = self.datasets[left_name]
        df2 = self.datasets[right_name]
        mode_idx = self.mode_combo.currentIndex()
        out_name = self.name_edit.text().strip() or f"Merged_{left_name}_{right_name}"

        if mode_idx == 0:
            # Concat
            self.result_df = pd.concat([df1, df2], ignore_index=True)
            self.result_name = out_name
            self.accept()
            return

        # Join
        key = self.key_combo.currentText()
        if not key:
            QMessageBox.warning(self, "Merge", "Select a join key for join mode.")
            return

        how_map = ["inner", "left", "right", "outer"]
        how = how_map[mode_idx - 1]

        engine = MergeEngine()
        result = engine.merge(df1, df2, on=key, how=how, validate=True)

        if not result.success:
            msg = result.error or "Merge failed."
            if result.summary.validation_warnings:
                msg += "\n\n" + "\n".join(result.summary.validation_warnings)
            QMessageBox.warning(self, "Merge", msg)
            return

        self.result_df = result.merged_df
        self.result_name = out_name
        self.accept()
