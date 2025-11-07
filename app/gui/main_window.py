"""
Main Window - PyQt6 GUI main application window

Provides a modern desktop interface for Nimbus backup operations.
"""

from pathlib import Path
from typing import Optional
from loguru import logger

try:
    from PyQt6.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QLabel, QLineEdit, QTextEdit, QProgressBar,
        QFileDialog, QTabWidget, QTableWidget, QTableWidgetItem,
        QMessageBox, QCheckBox, QComboBox, QGroupBox, QSpinBox
    )
    from PyQt6.QtCore import Qt, QThread, pyqtSignal
    from PyQt6.QtGui import QIcon, QFont
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False
    logger.warning("PyQt6 not available - install with: pip install PyQt6")


if PYQT6_AVAILABLE:
    class BackupWorker(QThread):
        """Background worker for backup operations."""

        progress = pyqtSignal(dict)
        finished = pyqtSignal(dict)
        error = pyqtSignal(str)

        def __init__(self, source: str, destination: str, options: dict):
            """Initialize backup worker.

            Args:
                source: Source directory
                destination: Destination directory
                options: Backup options (incremental, encrypt, etc.)
            """
            super().__init__()
            self.source = source
            self.destination = destination
            self.options = options

        def run(self):
            """Run backup operation."""
            try:
                from app.core.backup import BackupEngine, IncrementalBackup

                # Create backup engine
                if self.options.get('incremental', False):
                    engine = IncrementalBackup(
                        Path(self.source),
                        Path(self.destination)
                    )
                else:
                    engine = BackupEngine(
                        Path(self.source),
                        Path(self.destination)
                    )

                # Progress callback
                def progress_callback(data):
                    self.progress.emit(data)

                # Perform backup
                stats = engine.backup(progress_callback)

                # Emit finished signal
                self.finished.emit(stats)

            except Exception as e:
                logger.error(f"Backup failed: {e}")
                self.error.emit(str(e))


    class MainWindow(QMainWindow):
        """Main application window."""

        def __init__(self):
            """Initialize main window."""
            super().__init__()

            if not PYQT6_AVAILABLE:
                raise ImportError("PyQt6 not available")

            self.backup_worker: Optional[BackupWorker] = None

            self.init_ui()

            logger.info("GUI main window initialized")

        def init_ui(self):
            """Initialize UI components."""
            self.setWindowTitle("Nimbus - Enterprise Backup Solution")
            self.setGeometry(100, 100, 1000, 700)

            # Create central widget
            central_widget = QWidget()
            self.setCentralWidget(central_widget)

            # Create main layout
            main_layout = QVBoxLayout(central_widget)

            # Create tab widget
            tabs = QTabWidget()
            main_layout.addWidget(tabs)

            # Add tabs
            tabs.addTab(self.create_backup_tab(), "Backup")
            tabs.addTab(self.create_restore_tab(), "Restore")
            tabs.addTab(self.create_schedule_tab(), "Schedule")
            tabs.addTab(self.create_history_tab(), "History")
            tabs.addTab(self.create_settings_tab(), "Settings")

            # Status bar
            self.statusBar().showMessage("Ready")

        def create_backup_tab(self) -> QWidget:
            """Create backup tab."""
            widget = QWidget()
            layout = QVBoxLayout(widget)

            # Source section
            source_group = QGroupBox("Source")
            source_layout = QHBoxLayout()

            self.source_input = QLineEdit()
            self.source_input.setPlaceholderText("Select source directory...")
            source_layout.addWidget(self.source_input)

            source_browse_btn = QPushButton("Browse")
            source_browse_btn.clicked.connect(self.browse_source)
            source_layout.addWidget(source_browse_btn)

            source_group.setLayout(source_layout)
            layout.addWidget(source_group)

            # Destination section
            dest_group = QGroupBox("Destination")
            dest_layout = QHBoxLayout()

            self.dest_input = QLineEdit()
            self.dest_input.setPlaceholderText("Select destination directory...")
            dest_layout.addWidget(self.dest_input)

            dest_browse_btn = QPushButton("Browse")
            dest_browse_btn.clicked.connect(self.browse_destination)
            dest_layout.addWidget(dest_browse_btn)

            dest_group.setLayout(dest_layout)
            layout.addWidget(dest_group)

            # Options section
            options_group = QGroupBox("Options")
            options_layout = QVBoxLayout()

            self.incremental_check = QCheckBox("Incremental Backup")
            self.incremental_check.setChecked(True)
            options_layout.addWidget(self.incremental_check)

            self.encrypt_check = QCheckBox("Encrypt Backup")
            options_layout.addWidget(self.encrypt_check)

            self.compress_check = QCheckBox("Compress Backup")
            self.compress_check.setChecked(True)
            options_layout.addWidget(self.compress_check)

            self.verify_check = QCheckBox("Verify Integrity")
            self.verify_check.setChecked(True)
            options_layout.addWidget(self.verify_check)

            options_group.setLayout(options_layout)
            layout.addWidget(options_group)

            # Progress section
            progress_group = QGroupBox("Progress")
            progress_layout = QVBoxLayout()

            self.progress_label = QLabel("Ready to start backup")
            progress_layout.addWidget(self.progress_label)

            self.progress_bar = QProgressBar()
            progress_layout.addWidget(self.progress_bar)

            self.log_text = QTextEdit()
            self.log_text.setReadOnly(True)
            self.log_text.setMaximumHeight(150)
            progress_layout.addWidget(self.log_text)

            progress_group.setLayout(progress_layout)
            layout.addWidget(progress_group)

            # Buttons
            button_layout = QHBoxLayout()

            self.start_backup_btn = QPushButton("Start Backup")
            self.start_backup_btn.clicked.connect(self.start_backup)
            button_layout.addWidget(self.start_backup_btn)

            self.stop_backup_btn = QPushButton("Stop")
            self.stop_backup_btn.setEnabled(False)
            button_layout.addWidget(self.stop_backup_btn)

            button_layout.addStretch()

            layout.addLayout(button_layout)

            return widget

        def create_restore_tab(self) -> QWidget:
            """Create restore tab."""
            widget = QWidget()
            layout = QVBoxLayout(widget)

            label = QLabel("Restore functionality coming soon!")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)

            return widget

        def create_schedule_tab(self) -> QWidget:
            """Create schedule tab."""
            widget = QWidget()
            layout = QVBoxLayout(widget)

            label = QLabel("Backup scheduling coming soon!")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)

            return widget

        def create_history_tab(self) -> QWidget:
            """Create history tab."""
            widget = QWidget()
            layout = QVBoxLayout(widget)

            # Table for backup history
            self.history_table = QTableWidget()
            self.history_table.setColumnCount(6)
            self.history_table.setHorizontalHeaderLabels([
                "Date", "Source", "Destination", "Files", "Size", "Status"
            ])

            layout.addWidget(self.history_table)

            # Refresh button
            refresh_btn = QPushButton("Refresh")
            refresh_btn.clicked.connect(self.refresh_history)
            layout.addWidget(refresh_btn)

            return widget

        def create_settings_tab(self) -> QWidget:
            """Create settings tab."""
            widget = QWidget()
            layout = QVBoxLayout(widget)

            # Performance settings
            perf_group = QGroupBox("Performance")
            perf_layout = QVBoxLayout()

            thread_layout = QHBoxLayout()
            thread_layout.addWidget(QLabel("Worker Threads:"))
            self.threads_spin = QSpinBox()
            self.threads_spin.setRange(1, 16)
            self.threads_spin.setValue(4)
            thread_layout.addWidget(self.threads_spin)
            thread_layout.addStretch()
            perf_layout.addLayout(thread_layout)

            perf_group.setLayout(perf_layout)
            layout.addWidget(perf_group)

            # Notification settings
            notif_group = QGroupBox("Notifications")
            notif_layout = QVBoxLayout()

            self.desktop_notif_check = QCheckBox("Desktop Notifications")
            self.desktop_notif_check.setChecked(True)
            notif_layout.addWidget(self.desktop_notif_check)

            notif_group.setLayout(notif_layout)
            layout.addWidget(notif_group)

            layout.addStretch()

            # Save button
            save_btn = QPushButton("Save Settings")
            layout.addWidget(save_btn)

            return widget

        def browse_source(self):
            """Browse for source directory."""
            directory = QFileDialog.getExistingDirectory(
                self,
                "Select Source Directory"
            )

            if directory:
                self.source_input.setText(directory)

        def browse_destination(self):
            """Browse for destination directory."""
            directory = QFileDialog.getExistingDirectory(
                self,
                "Select Destination Directory"
            )

            if directory:
                self.dest_input.setText(directory)

        def start_backup(self):
            """Start backup operation."""
            source = self.source_input.text()
            destination = self.dest_input.text()

            # Validate inputs
            if not source or not destination:
                QMessageBox.warning(
                    self,
                    "Invalid Input",
                    "Please select both source and destination directories."
                )
                return

            if not Path(source).exists():
                QMessageBox.warning(
                    self,
                    "Invalid Source",
                    "Source directory does not exist."
                )
                return

            # Prepare options
            options = {
                'incremental': self.incremental_check.isChecked(),
                'encrypt': self.encrypt_check.isChecked(),
                'compress': self.compress_check.isChecked(),
                'verify': self.verify_check.isChecked()
            }

            # Disable start button
            self.start_backup_btn.setEnabled(False)
            self.stop_backup_btn.setEnabled(True)

            # Clear log
            self.log_text.clear()
            self.log_text.append("Starting backup...")

            # Create and start worker
            self.backup_worker = BackupWorker(source, destination, options)
            self.backup_worker.progress.connect(self.on_backup_progress)
            self.backup_worker.finished.connect(self.on_backup_finished)
            self.backup_worker.error.connect(self.on_backup_error)
            self.backup_worker.start()

            self.statusBar().showMessage("Backup in progress...")

        def on_backup_progress(self, data: dict):
            """Handle backup progress update."""
            phase = data.get('phase', 'unknown')

            if phase == 'scanning':
                total_files = data.get('total_files', 0)
                self.progress_label.setText(f"Scanning... {total_files} files found")

            elif phase == 'backing_up':
                backed_up = data.get('backed_up_files', 0)
                total = data.get('total_files', 1)
                percentage = data.get('percentage', 0)

                self.progress_label.setText(
                    f"Backing up... {backed_up}/{total} files ({percentage:.1f}%)"
                )
                self.progress_bar.setValue(int(percentage))

                current_file = data.get('current_file', '')
                self.log_text.append(f"Backing up: {Path(current_file).name}")

        def on_backup_finished(self, stats: dict):
            """Handle backup completion."""
            self.start_backup_btn.setEnabled(True)
            self.stop_backup_btn.setEnabled(False)

            backed_up = stats.get('backed_up_files', 0)
            total = stats.get('total_files', 0)
            failed = stats.get('failed_files', 0)

            self.progress_label.setText(
                f"Backup completed! {backed_up}/{total} files backed up, {failed} failed"
            )
            self.progress_bar.setValue(100)

            self.log_text.append("\n=== Backup Completed ===")
            self.log_text.append(f"Total files: {total}")
            self.log_text.append(f"Backed up: {backed_up}")
            self.log_text.append(f"Failed: {failed}")

            self.statusBar().showMessage("Backup completed successfully")

            QMessageBox.information(
                self,
                "Backup Complete",
                f"Backup completed successfully!\n\n"
                f"Files backed up: {backed_up}/{total}"
            )

        def on_backup_error(self, error: str):
            """Handle backup error."""
            self.start_backup_btn.setEnabled(True)
            self.stop_backup_btn.setEnabled(False)

            self.progress_label.setText("Backup failed!")
            self.log_text.append(f"\nERROR: {error}")

            self.statusBar().showMessage("Backup failed")

            QMessageBox.critical(
                self,
                "Backup Error",
                f"Backup failed with error:\n\n{error}"
            )

        def refresh_history(self):
            """Refresh backup history table."""
            try:
                from app.utils.database import BackupDatabase

                with BackupDatabase() as db:
                    records = db.list_backup_records(limit=50)

                    self.history_table.setRowCount(len(records))

                    for i, record in enumerate(records):
                        self.history_table.setItem(i, 0, QTableWidgetItem(
                            record.started_at.strftime('%Y-%m-%d %H:%M') if record.started_at else ''
                        ))
                        self.history_table.setItem(i, 1, QTableWidgetItem(record.source))
                        self.history_table.setItem(i, 2, QTableWidgetItem(record.destination))
                        self.history_table.setItem(i, 3, QTableWidgetItem(str(record.backed_up_files)))
                        self.history_table.setItem(i, 4, QTableWidgetItem(
                            f"{record.transferred_size / (1024**3):.2f} GB"
                        ))
                        self.history_table.setItem(i, 5, QTableWidgetItem(record.status))

            except Exception as e:
                logger.error(f"Failed to refresh history: {e}")
