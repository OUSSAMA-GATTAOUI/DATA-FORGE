
from __future__ import annotations

import os
import re

import numpy as np
import pandas as pd
from dateutil.parser import parse
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QComboBox,
    QDialog,
    QFileDialog,
    QFrame,
    QHeaderView,
    QInputDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMessageBox,
    QProgressDialog,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QStackedWidget,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
)

from .dialogs.chart_dialog import chartwindow
from .dialogs.clean_dialog import cleanwindow
from .dialogs.compare_dialog import CompareDialog
from .dialogs.filter_dialog import FilterWindow
from .dialogs.merge_dialog import MergeDialog
from .dialogs.sort_dialog import sortwindow
from .dialogs.summary_dialog import SummaryWindow
from .utils.styles import SIDEBAR_WIDTH, SPACING_LG, SPACING_MD


class FileLoaderThread(QThread):
    finished = pyqtSignal(object, str)
    error = pyqtSignal(str)
    
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
    
    def run(self):
        try:
            file_size = os.path.getsize(self.file_path) / (1024 * 1024)
            if file_size > 100:
                chunk_list = []
                chunk_size = 50000
                for chunk in pd.read_csv(self.file_path, low_memory=False, engine='c', chunksize=chunk_size):
                    chunk_list.append(chunk)
                
                if chunk_list:
                    df = pd.concat(chunk_list, ignore_index=True)
                else:
                    df = pd.DataFrame()
            else:
                df = pd.read_csv(self.file_path, low_memory=False, engine='c')
            
            self.finished.emit(df, self.file_path)
        except MemoryError:
            self.error.emit("File is too large to load into memory. Please use a smaller dataset or filter the data first.")
        except Exception as e:
            self.error.emit(str(e))


class main_menu(QMainWindow):
    def __init__(self, name):
        super().__init__()
        self.datasets = {} 
        self.current_dataset_name = None
        self.setWindowTitle("DataForge")
        self.setMinimumSize(900, 600)
        self.resize(1200, 750)
        self.data_loaded = False
        self.current_file_path = None
        self.loader_thread = None
        self.progress_dialog = None
        self.profiling_dialog = None
        self.max_display_rows = 1000
        self.max_display_cols = None
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.toolbar = QWidget()
        self.toolbar.setObjectName("mainToolbar")
        self.toolbar.setFixedHeight(48)
        toolbar_layout = QHBoxLayout(self.toolbar)
        toolbar_layout.setContentsMargins(SPACING_LG, SPACING_MD, SPACING_LG, SPACING_MD)
        toolbar_layout.setSpacing(SPACING_MD)
        app_title = QLabel("DataForge")
        app_title.setStyleSheet("font-size: 12pt; font-weight: 600; color: #e4e4e7;")
        toolbar_layout.addWidget(app_title)
        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setStyleSheet("background-color: #2d3142; max-width: 1px;")
        toolbar_layout.addWidget(sep)
        self.dataset_combo = QComboBox()
        self.dataset_combo.setMinimumWidth(200)
        self.dataset_combo.setPlaceholderText("No datasets")
        self.dataset_combo.currentTextChanged.connect(self.on_dataset_combo_changed)
        toolbar_layout.addWidget(QLabel("Dataset:"))
        toolbar_layout.addWidget(self.dataset_combo)
        open_btn = QPushButton("Open")
        open_btn.setProperty("primary", True)
        open_btn.clicked.connect(self.open_file)
        toolbar_layout.addWidget(open_btn)
        self.display_limits_btn = QPushButton("Display Limits")
        self.display_limits_btn.setProperty("flat", "true")
        self.display_limits_btn.setToolTip("Set how many rows/columns to show")
        self.display_limits_btn.clicked.connect(self.open_display_limits_dialog)
        self.display_limits_btn.setEnabled(False)
        toolbar_layout.addWidget(self.display_limits_btn)
        toolbar_layout.addStretch()
        main_layout.addWidget(self.toolbar)
        splitter = QSplitter(Qt.Horizontal)
        explorer_widget = QWidget()
        explorer_widget.setObjectName("datasetExplorer")
        explorer_widget.setMinimumWidth(SIDEBAR_WIDTH)
        explorer_widget.setMaximumWidth(SIDEBAR_WIDTH)
        explorer_layout = QVBoxLayout(explorer_widget)
        explorer_layout.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_MD)
        ds_label = QLabel("Datasets")
        ds_label.setStyleSheet("font-weight: 600; font-size: 10pt; color: #a1a1aa; padding-bottom: 8px;")
        explorer_layout.addWidget(ds_label)
        self.dataset_list = QListWidget()
        self.dataset_list.setObjectName("datasetList")
        self.dataset_list.itemClicked.connect(self._on_dataset_list_clicked)
        explorer_layout.addWidget(self.dataset_list)
        splitter.addWidget(explorer_widget)
        self.workspace_stack = QStackedWidget()
        self.workspace_stack.setMinimumWidth(400)
        empty_widget = QWidget()
        empty_widget.setObjectName("emptyState")
        empty_layout = QVBoxLayout(empty_widget)
        empty_layout.setAlignment(Qt.AlignCenter)
        self.empty_title = QLabel("No dataset loaded")
        self.empty_title.setObjectName("emptyTitle")
        self.empty_title.setAlignment(Qt.AlignCenter)
        self.empty_subtitle = QLabel("Load a CSV file using File → Open, or use the Open button above.")
        self.empty_subtitle.setObjectName("emptySubtitle")
        self.empty_subtitle.setAlignment(Qt.AlignCenter)
        self.empty_subtitle.setWordWrap(True)
        empty_layout.addWidget(self.empty_title)
        empty_layout.addWidget(self.empty_subtitle)
        self.workspace_stack.addWidget(empty_widget)
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setDefaultSectionSize(150)
        self.table.horizontalHeader().setMinimumSectionSize(100)
        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.setRowHeight(0, 40)
        self.table.setWordWrap(True)
        self.table.setTextElideMode(Qt.ElideRight)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_table_context_menu)
        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #3b3f5c;
                background-color: #1e2139;
            }
            QTableWidget::item {
                padding: 2px;
                color: #e4e4e7;
                font-size: 11pt;
            }
            QTableWidget::item:selected {
                background-color: #4f46e5;
                color: #ffffff;
            }
            QHeaderView::section {
                background-color: #252842;
                color: #e4e4e7;
                padding: 5px;
                border: none;
                font-weight: bold;
                font-size: 11pt;
            }
        """)
        self.workspace_stack.addWidget(self.table)
        splitter.addWidget(self.workspace_stack)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        main_layout.addWidget(splitter, 1)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("No data loaded")
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        self.open_action = QAction("Open", self)
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.triggered.connect(self.open_file)
        file_menu.addAction(self.open_action)        
        self.save_action = QAction("Save", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.setEnabled(False)  
        self.save_action.triggered.connect(self.save_file)
        file_menu.addAction(self.save_action)
        self.save_as_action = QAction("Save As", self)
        self.save_as_action.setShortcut("Ctrl+Shift+S")
        self.save_as_action.setEnabled(False)
        self.save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(self.save_as_action)
        file_menu.addSeparator()
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        edit_menu = menu_bar.addMenu("Edit")
        self.undo_action = QAction("Undo", self)
        self.undo_action.setShortcut("Ctrl+Z")
        self.undo_action.setEnabled(False)
        self.undo_action.triggered.connect(self.undo_filter)
        edit_menu.addAction(self.undo_action)
        self.redo_action = QAction("Redo", self)
        self.redo_action.setShortcut("Ctrl+Y")
        self.redo_action.setEnabled(False)
        self.redo_action.triggered.connect(self.redo_filter)
        edit_menu.addAction(self.redo_action)
        view_menu = menu_bar.addMenu("View")
        fullscreen_action = QAction("Full Screen", self)
        fullscreen_action.setShortcut("F11")
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        data_menu = menu_bar.addMenu("Data")
        self.filter_action = QAction("Filter", self)
        self.filter_action.setEnabled(False)
        self.filter_action.triggered.connect(self.open_filter_window)
        data_menu.addAction(self.filter_action)
        self.sort_action=QAction("Sort",self)
        self.sort_action.setEnabled(False)
        self.sort_action.triggered.connect(self.open_SORT_window)
        data_menu.addAction(self.sort_action)
        self.clean_action = QAction("Clean Data", self)
        self.clean_action.setEnabled(False)
        self.clean_action.triggered.connect(self.open_clean_window)
        data_menu.addAction(self.clean_action)
        analysis_menu = menu_bar.addMenu("Analysis")
        self.summary_action = QAction("summary statistic", self)
        self.summary_action.setEnabled(False)
        self.summary_action.triggered.connect(self.open_summary_window)
        analysis_menu.addAction(self.summary_action)
        self.charts_action = QAction("Charts / Visualization", self)
        self.charts_action.setEnabled(False)
        self.charts_action.triggered.connect(self.open_chart_window)
        analysis_menu.addAction(self.charts_action)
        help_menu = menu_bar.addMenu("Help")
        guide_action = QAction("User Guide", self)
        guide_action.setShortcut("F1")
        guide_action.triggered.connect(self.show_guide)
        help_menu.addAction(guide_action)
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        dataset_menu = menu_bar.addMenu("Dataset") 
        self.data_summary = QAction("Dataset Summary", self)
        self.data_summary.setEnabled(False) 
        self.data_summary.triggered.connect(self.show_dataset_summary) 
        dataset_menu.addAction(self.data_summary) 
        self.profile_action = QAction("Data Profiling", self) 
        self.profile_action.setEnabled(False) 
        self.profile_action.triggered.connect(self.show_profiling_report) 
        dataset_menu.addAction(self.profile_action) 
        self.merge_action = QAction("Merge Datasets", self)
        self.merge_action.setEnabled(True) 
        self.merge_action.triggered.connect(self.merge_datasets) 
        dataset_menu.addAction(self.merge_action) 
        self.compare_action = QAction("Compare Datasets", self)
        self.compare_action.setEnabled(True) 
        self.compare_action.triggered.connect(self.compare_datasets)
        dataset_menu.addAction(self.compare_action)
        dataset_menu.addSeparator()
        self.display_limits_action = QAction("Display limits...", self)
        self.display_limits_action.setEnabled(False)
        self.display_limits_action.setToolTip("Set how many rows/columns to show in the table")
        self.display_limits_action.triggered.connect(self.open_display_limits_dialog)
        dataset_menu.addAction(self.display_limits_action)
        self.redo_stack = []
        self.undo_stack = []

    def on_dataset_combo_changed(self, name):
        if not name or not self.datasets or name not in self.datasets:
            return
        if self.current_dataset_name == name:
            return
        self.switch_dataset(name)

    def _on_dataset_list_clicked(self, item):
        name = item.text()
        if name in self.datasets:
            self.dataset_combo.setCurrentText(name)

    def _refresh_dataset_list(self):
        self.dataset_list.clear()
        for name in self.datasets.keys():
            self.dataset_list.addItem(name)
        if self.current_dataset_name:
            items = self.dataset_list.findItems(self.current_dataset_name, Qt.MatchExactly)
            if items:
                self.dataset_list.setCurrentItem(items[0])

    def switch_dataset(self, name):
        if name not in self.datasets:
            return
        self.current_dataset_name = name
        self.data = self.datasets[name]
        self.original_data = self.data.copy()
        self.setWindowTitle(f"DataForge — {name}")
        self.show_data(self.data)

    def open_display_limits_dialog(self):
        if not self.data_loaded:
            return
        total_rows, total_cols = len(self.data), len(self.data.columns)
        current_rows = self.max_display_rows if self.max_display_rows else total_rows
        current_cols = self.max_display_cols if self.max_display_cols else total_cols
        rows_str, ok1 = QInputDialog.getText(
            self, "Display limits",
            f"Max rows to display (leave empty for all {total_rows:,}):",
            text=str(current_rows)
        )
        if not ok1:
            return
        cols_str, ok2 = QInputDialog.getText(
            self, "Display limits",
            f"Max columns to display (leave empty for all {total_cols}):",
            text=str(current_cols) if current_cols else ""
        )
        if not ok2:
            return
        try:
            self.max_display_rows = int(rows_str.strip()) if rows_str.strip() else None
            self.max_display_cols = int(cols_str.strip()) if cols_str.strip() else None
            if self.max_display_rows is not None and self.max_display_rows < 1:
                self.max_display_rows = 1
            if self.max_display_cols is not None and self.max_display_cols < 1:
                self.max_display_cols = 1
        except ValueError:
            QMessageBox.warning(self, "Invalid value", "Please enter positive integers or leave empty for no limit.")
            return
        self.show_data(self.data)

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv);;All Files (*)") 
        if path:
            self.progress_dialog = QProgressDialog("Loading dataset...", "Cancel", 0, 0, self)
            self.progress_dialog.setWindowTitle("Loading")
            self.progress_dialog.setWindowModality(Qt.WindowModal)
            self.progress_dialog.setCancelButton(None)
            self.progress_dialog.show()
            QApplication.processEvents()
            self.loader_thread = FileLoaderThread(path)
            self.loader_thread.finished.connect(self.on_file_loaded)
            self.loader_thread.error.connect(self.on_file_load_error)
            self.loader_thread.start()
    
    def on_file_loaded(self, df, path):
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
        
        try:
            dataset_name, ok = QInputDialog.getText(self, "Dataset Name", "Enter a name for this dataset:")
            if not ok or not dataset_name.strip(): 
                dataset_name = f"Dataset_{len(self.datasets)+1}"
            self.datasets[dataset_name] = df
            self.current_dataset_name = dataset_name
            self.data = df
            self.original_data = df.copy()
            self.current_file_path = path
            self.setWindowTitle(f"DataForge — {dataset_name}")
            self.workspace_stack.setCurrentWidget(self.table)
            self._refresh_dataset_list()
            self.show_data(self.data)
            self.save_action.setEnabled(True)
            self.save_as_action.setEnabled(True) 
            self.filter_action.setEnabled(True)
            self.sort_action.setEnabled(True)
            self.clean_action.setEnabled(True)
            self.summary_action.setEnabled(True)
            self.data_summary.setEnabled(True)
            self.profile_action.setEnabled(True)
            self.charts_action.setEnabled(True)
            self.undo_action.setEnabled(True)
            self.redo_action.setEnabled(True)
            self.data_loaded = True           
            self.dataset_combo.blockSignals(True)
            self.dataset_combo.clear()
            self.dataset_combo.addItems(list(self.datasets.keys()))
            self.dataset_combo.setCurrentText(dataset_name)
            self.dataset_combo.blockSignals(False)
            self.display_limits_btn.setEnabled(True)
            self.display_limits_action.setEnabled(True)
            total_rows = len(df)
            limit = self.max_display_rows or total_rows
            if total_rows > limit:
                QMessageBox.information(self, "Dataset Loaded", 
                    f"Dataset loaded successfully!\n\n"
                    f"Total rows: {total_rows:,}\n"
                    f"Total columns: {len(df.columns)}\n\n"
                    f"Showing first {min(limit, total_rows):,} rows in the table.\n"
                    f"Use Dataset → Display limits... to show more rows/columns.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to process loaded file:\n{e}")
    
    def on_file_load_error(self, error_msg):
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
        QMessageBox.warning(self, "Error", f"Failed to load file:\n{error_msg}")
    def show_dataset_summary(self):
        if not self.data_loaded:
            return
        rows, cols = self.data.shape
        missing = self.data.isna().sum().sum()
        msg = QMessageBox()
        msg.setWindowTitle("Dataset Summary")
        msg.setText(
            f"Dataset: {self.current_dataset_name}\n"
            f"Rows: {rows}\n"
            f"Columns: {cols}\n"
            f"Total Missing Values: {missing}"
        )
        msg.exec_()

    def show_profiling_report(self):
        if not self.data_loaded:
            QMessageBox.warning(self, "No Data", "Load a dataset first!")
            return
        if not hasattr(self, 'profiling_dialog') or self.profiling_dialog is None:
            self.profiling_dialog = QDialog(self)
            self.profiling_dialog.setWindowTitle("Data Profiling Report")
            layout = QVBoxLayout(self.profiling_dialog)

            table = QTableWidget()
            layout.addWidget(table)
            self.profiling_dialog.profiling_table = table
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(self.profiling_dialog.close)
            layout.addWidget(close_btn)
            self.profiling_dialog.finished.connect(lambda: setattr(self, 'profiling_dialog', None))
            self.profiling_dialog.resize(600, 400)
        table = self.profiling_dialog.profiling_table
        table.setRowCount(len(self.data.columns))
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Column", "Data Type", "Missing %", "Duplicate %"])

        for i, col in enumerate(self.data.columns):
            dtype = str(self.data[col].dtype)
            missing_pct = round(self.data[col].isna().mean() * 100, 2)
            duplicate_pct = round(self.data[col].duplicated().mean() * 100, 2)

            table.setItem(i, 0, QTableWidgetItem(col))
            table.setItem(i, 1, QTableWidgetItem(dtype))
            table.setItem(i, 2, QTableWidgetItem(f"{missing_pct}%"))
            table.setItem(i, 3, QTableWidgetItem(f"{duplicate_pct}%"))
        main_rect = self.geometry()
        x = main_rect.x() + (main_rect.width() - self.profiling_dialog.width()) // 2
        y = main_rect.y() + (main_rect.height() - self.profiling_dialog.height()) // 2
        self.profiling_dialog.move(x, y)
        self.profiling_dialog.setModal(False)
        self.profiling_dialog.show()
        self.profiling_dialog.raise_()
        self.profiling_dialog.activateWindow()

    def merge_datasets(self):
        if len(self.datasets) < 2:
            QMessageBox.warning(None, "Merge", "Need at least 2 datasets")
            return

        dlg = MergeDialog(self.datasets, self)
        if dlg.exec_() == QDialog.Accepted and dlg.result_df is not None:
            merged = dlg.result_df
            new_name = dlg.result_name
            self.datasets[new_name] = merged
            self.current_dataset_name = new_name
            self.data = merged
            self.original_data = merged.copy()
            self.dataset_combo.blockSignals(True)
            self.dataset_combo.clear()
            self.dataset_combo.addItems(list(self.datasets.keys()))
            self.dataset_combo.setCurrentText(new_name)
            self.dataset_combo.blockSignals(False)
            self._refresh_dataset_list()
            self.show_data(self.data)
            self.workspace_stack.setCurrentWidget(self.table)
            QMessageBox.information(self, "Merge", f"Datasets merged into {new_name}")

    def compare_datasets(self):
        if len(self.datasets) < 2:
            QMessageBox.warning(None, "Compare", "Need at least 2 datasets")
            return

        dlg = CompareDialog(self.datasets, self)
        dlg.exec_()

    def undo_filter(self):
        if self.undo_stack:
            self.redo_stack.append(self.data.copy())
            self.data = self.undo_stack.pop()
            self.show_data(self.data)
            print("Undo: Reverted to previous state")
        else:
            QMessageBox.information(self, "Undo", "No previous action to undo.")

    def redo_filter(self):
        if self.redo_stack:
            self.undo_stack.append(self.data.copy())
            self.data = self.redo_stack.pop()
            self.show_data(self.data)
            print("Redo: Restored last undone action")
        else:
            QMessageBox.information(self, "Redo", "No action to redo.")

    def save_file(self):
        if not self.data_loaded:
            QMessageBox.warning(self, "No Data", "Load a dataset first!")
            return
        if self.current_file_path:
            try:
                self.data.to_csv(self.current_file_path, index=False, encoding='utf-8')
                QMessageBox.information(self, "Saved", f"Data saved to {self.current_file_path}")
                self.setWindowTitle(f"DataForge — {self.current_file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save file:\n{e}")
        else:
            self.save_file_as()

    def save_file_as(self):
        if not self.data_loaded:
            QMessageBox.warning(self, "No Data", "Load a dataset first!")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save CSV As", "", "CSV Files (*.csv);;All Files (*)")
        if path:
            try:
                if not path.lower().endswith('.csv'):
                    path += '.csv'
                self.data.to_csv(path, index=False, encoding='utf-8')
                self.current_file_path = path
                self.setWindowTitle(f"DataForge — {path}")
                QMessageBox.information(self, "Saved", f"Data saved to {path}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save file:\n{e}")

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def show_guide(self):
        guide_text = """
DataForge — User Guide

FILE OPERATIONS:
• Open (Ctrl+O): Load a CSV file to work with
• Save (Ctrl+S): Save changes to the current file
• Save As (Ctrl+Shift+S): Save to a new file location
• Exit (Ctrl+Q): Close the application

DATA OPERATIONS:
• Filter: Filter data based on conditions (Number, Duration, Date, Text)
• Sort: Sort data by column (Ascending, Descending, Nulls First/Last)
• Clean Data: Clean and normalize data (Fill missing, Remove outliers, Format text, etc.)
• Undo (Ctrl+Z): Revert the last action
• Redo (Ctrl+Y): Restore the last undone action

ANALYSIS:
• Summary Statistics: View detailed statistics for numeric, categorical, date, and duration columns
• Charts / Visualization: Create various charts:
  - Histogram: For numeric or duration data
  - Bar Chart: Categorical vs numeric/duration
  - Pie Chart: For categorical data
  - Scatter Plot: Numeric/duration vs numeric/duration
  - Line Chart: Datetime vs numeric/duration

FILTERING TIPS:
• Number: Use ==, >, <, >=, <=, between
• Duration: Enter time like "2 hours 30 minutes" or "1:30:00"
• Date: Enter dates in YYYY-MM-DD format
• Text: Use contains, not contains, ==, !=, empty

SORTING TIPS:
• Columns are automatically detected by type
• Date columns support date sorting
• Duration columns are converted for sorting
• Text columns can be sorted A→Z or Z→A

CLEANING TIPS:
• Fill missing values: Replace NaN with a default value
• Handle outliers: Set min/max bounds
• Normalize formats: Standardize date or duration formats
• Text operations: Lower, Upper, Capitalize, Strip, etc.

CHART CREATION:
• Select chart type first
• X and Y columns are automatically filtered based on chart type
• Duration data is converted to seconds for visualization
• Charts are displayed using matplotlib

SHORTCUTS:
• F1: Show this guide
• F11: Toggle fullscreen
• Ctrl+O: Open file
• Ctrl+S: Save file
• Ctrl+Shift+S: Save As
• Ctrl+Z: Undo
• Ctrl+Y: Redo
• Ctrl+Q: Exit

For more help, contact support or check the documentation.
support: gattaouioussama@gmail.com
        """
        msg = QMessageBox(self)
        msg.setWindowTitle("User Guide")
        msg.setText(guide_text.strip())
        msg.setIcon(QMessageBox.Information)
        msg.exec_()
    
    def show_about(self):
        about_text = """
        <html>
            <body style="font-family: Arial, sans-serif; padding: 10px;">
                <h2 style="color: #2c3e50; margin-bottom: 5px;">DataForge</h2>
                <p style="color: #7f8c8d; margin-top: 0; font-size: 12px;"><b>Version 1.0</b></p>
                
                <p style="color: #34495e; line-height: 1.6; margin-top: 15px;">
                    A comprehensive data analysis and visualization tool built with PyQt5 and pandas.
                </p>
                
                <h3 style="color: #2c3e50; margin-top: 15px; margin-bottom: 8px;">Features:</h3>
                <ul style="color: #34495e; line-height: 1.8; margin: 0; padding-left: 20px;">
                    <li>CSV file loading and editing</li>
                    <li>Advanced filtering and sorting</li>
                    <li>Data cleaning and normalization</li>
                    <li>Statistical analysis and summaries</li>
                    <li>Interactive chart generation</li>
                    <li>Undo/Redo functionality</li>
                </ul>
                
                <h3 style="color: #2c3e50; margin-top: 15px; margin-bottom: 8px;">Built with:</h3>
                <ul style="color: #34495e; line-height: 1.8; margin: 0; padding-left: 20px;">
                    <li>Python 3</li>
                    <li>PyQt5</li>
                    <li>Pandas</li>
                    <li>Matplotlib</li>
                    <li>NumPy</li>
                </ul>
                
                <hr style="border: 0; border-top: 1px solid #bdc3c7; margin: 15px 0;">
                <p style="color: #95a5a6; font-size: 11px; text-align: center;">
                    © 2025 DataForge. All rights reserved.
                </p>
            </body>
        </html>
        """
        msg = QMessageBox(self)
        msg.setWindowTitle("About DataForge")
        msg.setText(about_text.strip())
        msg.setIcon(QMessageBox.Information)
        msg.exec_()

    def show_data(self, df):  
        self.table.setSortingEnabled(False)
        self.table.setUpdatesEnabled(False)
        self.table.clearContents()
        
        total_rows, total_cols = len(df), len(df.columns)
        max_rows = self.max_display_rows if self.max_display_rows is not None else total_rows
        max_cols = self.max_display_cols if self.max_display_cols is not None else total_cols
        display_rows = min(total_rows, max_rows)
        display_cols = min(total_cols, max_cols)
        
        self.table.setRowCount(display_rows)
        self.table.setColumnCount(display_cols)
        if display_cols < total_cols:
            cols_to_show = df.columns[:display_cols].tolist()
        else:
            cols_to_show = df.columns.tolist()
        for col_idx, col_name in enumerate(cols_to_show):
            col_name_str = str(col_name)
            header_item = QTableWidgetItem(col_name_str)
            if len(col_name_str) > 30:
                header_item.setToolTip(col_name_str)
            self.table.setHorizontalHeaderItem(col_idx, header_item)
        
        display_df = df[cols_to_show].head(display_rows)
        data_array = display_df.values
        
        for i in range(display_rows):
            for j in range(display_cols):
                val = data_array[i, j]
                if pd.isna(val):
                    item = QTableWidgetItem("")
                else:
                    val_str = str(val)
                    item = QTableWidgetItem(val_str)
                    if len(val_str) > 50:
                        item.setToolTip(val_str)
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.table.setItem(i, j, item)
        self.table.resizeColumnsToContents()
        for col in range(display_cols):
            current_width = self.table.columnWidth(col)
            if current_width > 600:
                self.table.setColumnWidth(col, 600)
            elif current_width < 120:
                self.table.setColumnWidth(col, 120)
        # Set all row heights for consistency
        for row in range(display_rows):
            self.table.setRowHeight(row, 40)
        
        row_msg = f"{display_rows:,} of {total_rows:,} rows" if total_rows > display_rows else f"{total_rows:,} rows"
        col_msg = f", {display_cols} of {total_cols} columns" if total_cols > display_cols else f", {total_cols} columns"
        self.status_bar.showMessage(f"{row_msg}{col_msg}")
        
        self.table.setUpdatesEnabled(True)
        self.table.setSortingEnabled(True)
    
    def show_table_context_menu(self, position):
        if not self.data_loaded:
            return
        
        menu = QMenu(self)
        resize_action = QAction("Auto-resize all columns", self)
        resize_action.triggered.connect(self.auto_resize_columns)
        menu.addAction(resize_action)
        
        resize_selected_action = QAction("Auto-resize selected column", self)
        resize_selected_action.triggered.connect(lambda: self.auto_resize_column(self.table.currentColumn()))
        menu.addAction(resize_selected_action)
        
        menu.exec_(self.table.viewport().mapToGlobal(position))
    
    def auto_resize_columns(self):
        self.table.resizeColumnsToContents()
        for col in range(self.table.columnCount()):
            current_width = self.table.columnWidth(col)
            if current_width > 600:
                self.table.setColumnWidth(col, 600)
            elif current_width < 120:
                self.table.setColumnWidth(col, 120)
        # Ensure consistent row heights
        for row in range(self.table.rowCount()):
            self.table.setRowHeight(row, 40)
    
    def auto_resize_column(self, col):
        if col >= 0 and col < self.table.columnCount():
            self.table.resizeColumnToContents(col)
            current_width = self.table.columnWidth(col)
            if current_width > 500:
                self.table.setColumnWidth(col, 500)
            elif current_width < 100:
                self.table.setColumnWidth(col, 100)
    
    def parse_duration_to_days(self, val):
        if isinstance(val, (int, float)):
            return float(val)
        if isinstance(val, str):
            total_days = 0 
            val_lower = val.lower().strip()
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
            total_days += sum(int(x)*365 for x in y)
            total_days += sum(int(x)*30 for x in mo)
            total_days += sum(int(x)*7 for x in w)
            total_days += sum(int(x) for x in d)
            if total_days == 0:
                num_match = re.search(r"\d+", val_lower)
                if num_match:
                    total_days = float(num_match.group())
                else:
                    return np.nan

            return total_days
   
    def parse_season_to_number(self, val):
        if isinstance(val, str):
            match = re.search(r'\d+', val)
            return int(match.group(0)) if match else np.nan
        elif isinstance(val, (int, float)):
            return val
        return np.nan
    
    def parse_numeric(self, val):
        if isinstance(val, (int, float)):
            return val
        if isinstance(val, str):
            val_clean = re.sub(r'[^\d.-]', '', val)
            try:
                return float(val_clean)
            except:
                return np.nan
        return np.nan

    def smart_parse_date(self, val):
        if not isinstance(val, str):
            return pd.NaT
        val = val.strip()
        if not val:
            return pd.NaT
        try:
            parsed = parse(val, dayfirst=True, yearfirst=False)
            return parsed
        except Exception as e:
            print(f"Failed to parse date '{val}': {e}")
            return pd.NaT
        
    def apply_user_filter(self, column, operator, value, data_type):
        df = self.data.copy()
        col_data = df[column]
        self.undo_stack.append(self.data.copy())
        self.redo_stack.clear()      
        if data_type == "Duration":
            col_parsed = col_data.apply(self.parse_duration_to_days)
        elif data_type == "Duration (Years , days or others)":
            col_parsed = col_data.apply(self.parse_duration_to_days)
        elif data_type == "Seasons (for series)":
            col_parsed = col_data.apply(self.parse_season_to_number)
        elif data_type == "Date":
            col_parsed = pd.to_datetime(col_data, dayfirst=False, errors='coerce')
            if col_parsed.isna().any():
                fallback = col_data[col_parsed.isna()].apply(lambda x: self.smart_parse_date(str(x)))
                fallback = pd.to_datetime(fallback, errors='coerce')
                col_parsed.loc[falling := col_parsed.isna()] = fallback
        elif data_type == "Number":
            col_parsed = col_data.apply(self.parse_numeric)
        else:
            col_parsed = col_data.astype(str)
        filtered = df
        if operator == "between":
            min_val, max_val = value
            if data_type == "Date":
                min_ts = pd.to_datetime(min_val, dayfirst=False, errors='coerce')
                max_ts = pd.to_datetime(max_val, dayfirst=False, errors='coerce')
                if pd.isna(min_ts):
                    min_ts = self.smart_parse_date(min_val)
                if pd.isna(max_ts):
                    max_ts = self.smart_parse_date(max_val)
                if pd.isna(min_ts) or pd.isna(max_ts):
                    QMessageBox.warning(self, "Error", "Start and end dates must be valid.")
                    return
                min_ts = pd.to_datetime(min_ts).normalize()
                max_ts = pd.to_datetime(max_ts).normalize()
                col_norm = pd.to_datetime(col_parsed).dt.normalize()
                mask = (col_norm >= min_ts) & (col_norm <= max_ts)
                filtered = df[mask.fillna(False)]
            else:
                try:
                    min_num, max_num = float(min_val), float(max_val)
                except Exception:
                    QMessageBox.warning(self, "Error", "Min/Max must be numeric.")
                    return
                mask = (col_parsed >= min_num) & (col_parsed <= max_num)
                filtered = df[mask.fillna(False)]

        elif operator in [">", "<", "≥", "≤", "==", "!="]:
            if data_type == "Date":
                value_ts = pd.to_datetime(value, dayfirst=False, errors='coerce')
                if pd.isna(value_ts):
                    value_ts = self.smart_parse_date(value)
                if pd.isna(value_ts):
                    QMessageBox.warning(self, "Error", "Please enter a valid date value.")
                    return
                value_norm = pd.to_datetime(value_ts).normalize()
                col_norm = pd.to_datetime(col_parsed).dt.normalize()
                if operator == ">": mask = col_norm > value_norm
                elif operator == "<": mask = col_norm < value_norm
                elif operator == "≥": mask = col_norm >= value_norm
                elif operator == "≤": mask = col_norm <= value_norm
                elif operator == "==": mask = col_norm == value_norm
                elif operator == "!=": mask = col_norm != value_norm
                filtered = df[mask.fillna(False)]

            elif data_type in ["Duration", "Seasons (for series)", "Number"]:
                try:
                    value_num = float(self.parse_duration_to_days(value)) if data_type == "Duration" else float(value)
                except Exception:
                    QMessageBox.warning(self, "Error", "Value must be numeric.")
                    return
                if operator == ">": mask = col_parsed > value_num
                elif operator == "<": mask = col_parsed < value_num
                elif operator == "≥": mask = col_parsed >= value_num
                elif operator == "≤": mask = col_parsed <= value_num
                elif operator == "==": mask = col_parsed == value_num
                elif operator == "!=": mask = col_parsed != value_num
                filtered = df[mask.fillna(False)]

            else:
                value_str = value
                if operator == ">": mask = col_parsed > value_str
                elif operator == "<": mask = col_parsed < value_str
                elif operator == "≥": mask = col_parsed >= value_str
                elif operator == "≤": mask = col_parsed <= value_str
                elif operator == "==": mask = col_parsed == value_str
                elif operator == "!=": mask = col_parsed != value_str
                filtered = df[mask.fillna(False)]

        elif operator == "contains":
            filtered = df[col_data.astype(str).str.contains(str(value), case=False, na=False)]
        elif operator == "not contains":
            filtered = df[~col_data.astype(str).str.contains(str(value), case=False, na=False)]
        elif operator == "empty":
            filtered = df[col_data.isna() | (col_data.astype(str).str.strip() == "")]
        else:
            filtered = df[col_data.astype(str) == str(value)]
        self.data = filtered
        self.show_data(filtered)

    def open_filter_window(self):
        print("Filter window requested")  
        if not self.data_loaded:
            QMessageBox.warning(self, "No Data", "Load a dataset first!")
            return
        filter_window = FilterWindow(columns=self.data.columns.tolist(), parent=self)
        filter_window.resize(350, 250)
        main_rect = self.geometry()
        x = main_rect.x() + (main_rect.width() - filter_window.width()) // 2
        y = main_rect.y() + (main_rect.height() - filter_window.height()) // 2
        filter_window.move(x, y)
        filter_window.setWindowFlags(Qt.Window)
        filter_window.show()
        filter_window.raise_()
        filter_window.activateWindow()   

    def apply_user_sort(self, column, method):
        df = self.data.copy()
        col_data = df[column]
        self.undo_stack.append(self.data.copy())
        self.redo_stack.clear()
        sorted_data = df
        if method in ["Ascending", "Descending", "Nulls First", "Nulls Last"]:
            col_parsed = col_data.apply(self.parse_duration_to_days)
            if method == "Ascending":
                sorted_data = df.loc[col_parsed.sort_values(ascending=True).index]
            elif method == "Descending":
                sorted_data = df.loc[col_parsed.sort_values(ascending=False).index]
            elif method == "Nulls First":
                sorted_data = df.loc[col_parsed.sort_values(ascending=True, na_position="first").index]
            elif method == "Nulls Last":
                sorted_data = df.loc[col_parsed.sort_values(ascending=True, na_position="last").index]
        
        elif method in ["Oldest → Newest", "Newest → Oldest"]:
            col_parsed = pd.to_datetime(col_data, dayfirst=False, errors='coerce')
            if col_parsed.isna().any():
                fallback = col_data[col_parsed.isna()].apply(lambda x: self.smart_parse_date(str(x)))
                fallback = pd.to_datetime(fallback, errors='coerce')
                col_parsed.loc[col_parsed.isna()] = fallback           
            if method == "Oldest → Newest":
                sorted_data = df.loc[col_parsed.sort_values(ascending=True).index]
            elif method == "Newest → Oldest":
                sorted_data = df.loc[col_parsed.sort_values(ascending=False).index]
        
        elif method in ["A → Z", "Z → A"]:
            col_parsed = col_data.astype(str)
            if method == "A → Z":
                sorted_data = df.loc[col_parsed.sort_values(ascending=True).index]
            elif method == "Z → A":
                sorted_data = df.loc[col_parsed.sort_values(ascending=False).index]
        self.data = sorted_data
        self.show_data(sorted_data)  

    def open_SORT_window(self):
        if not self.data_loaded:
            QMessageBox.warning(self, "No Data", "Load a dataset first!")
            return
        sort_window = sortwindow(df=self.data, parent=self)
        sort_window.resize(350, 250)
        main_rect = self.geometry()
        x = main_rect.x() + (main_rect.width() - sort_window.width()) // 2
        y = main_rect.y() + (main_rect.height() - sort_window.height()) // 2
        sort_window.move(x, y)
        sort_window.setWindowFlags(Qt.Window)
        sort_window.show()
        sort_window.raise_()
        sort_window.activateWindow()
    def apply_clean_window(self, column, clean_action, value):
        if not self.data_loaded:
            QMessageBox.warning(self, "Error", "No data loaded!")
            return
        
        df = self.data.copy()
        col_data = df[column]
        self.undo_stack.append(self.data.copy())
        self.redo_stack.clear()
        
        try:
            if clean_action == "Fill missing values":
                if value is None or value == "":
                    QMessageBox.warning(self, "Error", "Please provide a value to fill.")
                    return
                try:
                    fill_value = float(value)
                    df[column] = col_data.fillna(fill_value)
                    QMessageBox.information(self, "Success", f"Filled {col_data.isna().sum()} missing values with {fill_value}")
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Invalid value: {e}")
                    return
            elif clean_action == "Replace negative values":
                if value is None or value == "":
                    QMessageBox.warning(self, "Error", "Please provide a replacement value.")
                    return
                try:
                    replacement = float(value)
                    col_parsed = col_data.apply(self.parse_numeric)
                    mask = col_parsed < 0
                    df.loc[mask, column] = replacement
                    QMessageBox.information(self, "Success", f"Replaced {mask.sum()} negative values")
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Error: {e}")
                    return
            elif clean_action == "Handle outliers":
                if not isinstance(value, list) or len(value) != 2:
                    QMessageBox.warning(self, "Error", "Please provide min and max values.")
                    return
                try:
                    min_val = float(value[0])
                    max_val = float(value[1])
                    col_parsed = col_data.apply(self.parse_numeric)
                    mask = (col_parsed < min_val) | (col_parsed > max_val)
                    removed = mask.sum()
                    df = df[~mask]
                    QMessageBox.information(self, "Success", f"Removed {removed} outliers")
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Error: {e}")
                    return
            elif clean_action == "Normalize numeric formats":
                if value is None or value == "":
                    QMessageBox.warning(self, "Error", "Please provide a unit (e.g., age, $, meters).")
                    return
                col_parsed = col_data.apply(self.parse_numeric)
                if value == "$":
                    df[column] = col_parsed.apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "")
                else:
                    df[column] = col_parsed.apply(lambda x: f"{x} {value}" if pd.notna(x) else "")
                
                QMessageBox.information(self, "Success", f"Normalized numeric values with unit: {value}")
            elif clean_action == "Normalize TIME formats":
                if value is None or value == "":
                    QMessageBox.warning(self, "Error", "Please select a target format.")
                    return
                col_parsed = col_data.apply(self.parse_duration_to_days)
                
                if value == "To days":
                    df[column] = col_parsed 
                elif value == "to HH:MM:SS":
                    def days_to_hms(days):
                        if pd.isna(days):
                            return ""
                        total_seconds = int(days * 86400)
                        hours = total_seconds // 3600
                        minutes = (total_seconds % 3600) // 60
                        seconds = total_seconds % 60
                        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                    df[column] = col_parsed.apply(days_to_hms)
                elif value == "to years":
                    df[column] = col_parsed / 365
                elif value == "to hours":
                    df[column] = col_parsed * 24
                elif value == "to minute":
                    df[column] = col_parsed * 1440
                elif value == "to second":
                    df[column] = col_parsed * 86400
                
                QMessageBox.information(self, "Success", f"Normalized durations to {value}")
            elif clean_action == "Convert all to datetime":
                if value is None or value == "":
                    QMessageBox.warning(self, "Error", "Please select a date format.")
                    return
                parsed = pd.to_datetime(col_data, dayfirst=False, errors='coerce')
                mask_na = parsed.isna()
                if mask_na.any():
                    fallback = col_data[mask_na].apply(lambda x: self.smart_parse_date(str(x)))
                    parsed.loc[mask_na] = pd.to_datetime(fallback, errors='coerce')
                if value == "D/M/Y":
                    df[column] = parsed.dt.strftime('%d/%m/%Y')
                elif value == "M/D/Y":
                    df[column] = parsed.dt.strftime('%m/%d/%Y')
                elif value == "Y/M/D":
                    df[column] = parsed.dt.strftime('%Y/%m/%d')
                elif value == "Y-M-D":
                    df[column] = parsed.dt.strftime('%Y-%m-%d')
                elif value == "D-M-Y":
                    df[column] = parsed.dt.strftime('%d-%m-%Y')
                else:
                    df[column] = parsed
                
                QMessageBox.information(self, "Success", f"Converted to datetime format: {value}")
            elif clean_action == "Lower":
                df[column] = col_data.astype(str).str.lower()
                QMessageBox.information(self, "Success", "Converted to lowercase")
            
            elif clean_action == "Upper":
                df[column] = col_data.astype(str).str.upper()
                QMessageBox.information(self, "Success", "Converted to uppercase")
            
            elif clean_action == "Capitalize":
                df[column] = col_data.astype(str).str.capitalize()
                QMessageBox.information(self, "Success", "Capitalized text")
            
            elif clean_action == "Title":
                df[column] = col_data.astype(str).str.title()
                QMessageBox.information(self, "Success", "Converted to title case")
            
            elif clean_action == "Strip":
                df[column] = col_data.astype(str).str.strip()
                QMessageBox.information(self, "Success", "Stripped whitespace")
            
            elif clean_action == "Remove extra spaces":
                df[column] = col_data.astype(str).str.replace(r'\s+', ' ', regex=True).str.strip()
                QMessageBox.information(self, "Success", "Removed extra spaces")
            
            elif clean_action == "Remove punctuation":
                df[column] = col_data.astype(str).str.replace(r'[^\w\s]', '', regex=True)
                QMessageBox.information(self, "Success", "Removed punctuation")
            
            elif clean_action == "":
                return
            
            else:
                QMessageBox.warning(self, "Error", f"Unknown clean action: {clean_action}")
                return
            
            self.data = df
            self.show_data(df)
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Cleaning failed: {str(e)}")
            return
        
    def open_clean_window(self):
        if not self.data_loaded:
            QMessageBox.warning(self, "No Data", "Load a dataset first!")
            return
        clean_window = cleanwindow(df=self.data, parent=self)
        clean_window.resize(400, 300)
        main_rect = self.geometry()
        x = main_rect.x() + (main_rect.width() - clean_window.width()) // 2
        y = main_rect.y() + (main_rect.height() - clean_window.height()) // 2
        clean_window.move(x, y)
        clean_window.setWindowFlags(Qt.Window)
        clean_window.show()
        clean_window.raise_()
        clean_window.activateWindow()

    def open_summary_window(self):
        if not self.data_loaded:
            QMessageBox.warning(self, "No Data", "Load a dataset first!")
            return
        summary_window = SummaryWindow(df=self.data, parent=self)
        summary_window.exec_()

    def open_chart_window(self):
        if not self.data_loaded:
            QMessageBox.warning(self, "No Data", "Load a dataset first!")
            return
        self.chart_window = chartwindow(df=self.data, parent=self)

        main_rect = self.geometry()
        x = main_rect.x() + (main_rect.width() - self.chart_window.width()) // 2
        y = main_rect.y() + (main_rect.height() - self.chart_window.height()) // 2
        self.chart_window.move(x, y)

        self.chart_window.setWindowFlags(Qt.Window)
        self.chart_window.setModal(False)

        self.chart_window.show()
        self.chart_window.raise_()
        self.chart_window.activateWindow()
