#!/usr/bin/env python3
"""
Stingray Detector GUI - Visual step-by-step directional scanning
"""

import sys
import os
import subprocess
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QProgressBar,
                             QTextEdit, QStackedWidget, QMessageBox, QDialog,
                             QDialogButtonBox, QDoubleSpinBox, QFormLayout,
                             QTabWidget, QGroupBox, QGridLayout, QTimeEdit,
                             QCheckBox, QSpinBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTime
from PyQt6.QtGui import QPixmap, QPainter, QPen, QFont, QColor
import json

class MonitorThread(QThread):
    """Background thread for running monitoring scans"""
    progress = pyqtSignal(str)  # status updates
    finished = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, duration_minutes, interval_seconds):
        super().__init__()
        self.duration_minutes = duration_minutes
        self.interval_seconds = interval_seconds
        
    def run(self):
        try:
            self.progress.emit(f"Starting {self.duration_minutes} minute monitoring...")
            
            # Kill any existing HackRF processes
            subprocess.run(['killall', 'hackrf_sweep'], stderr=subprocess.DEVNULL)
            subprocess.run(['killall', 'hackrf_info'], stderr=subprocess.DEVNULL)
            import time
            time.sleep(2)
            
            # Run tracking script
            result = subprocess.run(
                ['./track-movement.sh', str(self.duration_minutes), str(self.interval_seconds)],
                capture_output=True,
                text=True,
                cwd='/Users/meep/Documents/EpiRay'
            )
            
            if result.returncode == 0:
                self.finished.emit(True, "Monitoring completed successfully!")
            else:
                self.finished.emit(False, f"Monitoring failed: {result.stderr}")
                
        except Exception as e:
            self.finished.emit(False, str(e))

class ScanThread(QThread):
    """Background thread for running HackRF scans"""
    finished = pyqtSignal(str, str)  # direction, output
    error = pyqtSignal(str)
    
    def __init__(self, direction):
        super().__init__()
        self.direction = direction
        
    def run(self):
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"detection-logs/directional/{self.direction}_{timestamp}.csv"
            
            # Ensure directory exists
            os.makedirs("detection-logs/directional", exist_ok=True)
            
            # Run hackrf_sweep
            cmd = [
                'hackrf_sweep',
                '-f', '750:770',
                '-f', '850:860',
                '-a', '1',
                '-l', '32',
                '-g', '40',
                '-N', '50',
                '-r', output_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                   cwd='/Users/meep/Documents/EpiRay')
            
            if result.returncode == 0:
                self.finished.emit(self.direction, output_file)
            else:
                self.error.emit(f"Scan failed: {result.stderr}")
                
        except Exception as e:
            self.error.emit(str(e))

class DirectionWidget(QWidget):
    """Widget showing antenna direction with visual diagram"""
    
    def __init__(self, direction, description, angle):
        super().__init__()
        self.direction = direction
        self.description = description
        self.angle = angle
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel(f"Point Antenna: {self.direction.upper()}")
        title.setFont(QFont('Arial', 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Description
        desc = QLabel(self.description)
        desc.setFont(QFont('Arial', 14))
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Diagram
        diagram = self.create_diagram()
        layout.addWidget(diagram)
        
        # Instructions
        instructions = QLabel(
            "1. Hold your HackRF with antenna pointing in the direction shown\n"
            "2. Keep antenna steady and away from your body\n"
            "3. Click 'Start Scan' when ready"
        )
        instructions.setFont(QFont('Arial', 12))
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(instructions)
        
        self.setLayout(layout)
        
    def create_diagram(self):
        """Create visual diagram showing antenna direction"""
        label = QLabel()
        pixmap = QPixmap(600, 400)
        pixmap.fill(Qt.GlobalColor.white)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw compass rose
        center_x, center_y = 300, 200
        
        # Draw circle
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.drawEllipse(center_x - 100, center_y - 100, 200, 200)
        
        # Draw cardinal directions
        painter.setFont(QFont('Arial', 14, QFont.Weight.Bold))
        painter.drawText(center_x - 10, center_y - 110, "N")
        painter.drawText(center_x - 10, center_y + 125, "S")
        painter.drawText(center_x + 110, center_y + 5, "E")
        painter.drawText(center_x - 125, center_y + 5, "W")
        
        # Draw intercardinal directions
        painter.setFont(QFont('Arial', 12))
        painter.drawText(center_x + 75, center_y - 75, "NE")
        painter.drawText(center_x + 75, center_y + 85, "SE")
        painter.drawText(center_x - 95, center_y + 85, "SW")
        painter.drawText(center_x - 95, center_y - 75, "NW")
        
        # Draw HackRF (rectangle in center)
        hackrf_width, hackrf_height = 60, 40
        painter.setBrush(QColor(100, 100, 200))
        painter.drawRect(center_x - hackrf_width//2, center_y - hackrf_height//2, 
                        hackrf_width, hackrf_height)
        
        # Draw antenna direction arrow
        painter.setPen(QPen(Qt.GlobalColor.red, 4))
        painter.setBrush(Qt.GlobalColor.red)
        
        # Calculate arrow endpoint based on direction
        import math
        arrow_length = 80
        angle_rad = math.radians(self.angle)
        end_x = center_x + arrow_length * math.sin(angle_rad)
        end_y = center_y - arrow_length * math.cos(angle_rad)
        
        # Draw arrow line
        painter.drawLine(center_x, center_y, int(end_x), int(end_y))
        
        # Draw arrowhead
        arrow_size = 15
        angle1 = angle_rad + math.radians(150)
        angle2 = angle_rad - math.radians(150)
        
        point1_x = end_x + arrow_size * math.cos(angle1)
        point1_y = end_y + arrow_size * math.sin(angle1)
        point2_x = end_x + arrow_size * math.cos(angle2)
        point2_y = end_y + arrow_size * math.sin(angle2)
        
        from PyQt6.QtGui import QPolygon
        from PyQt6.QtCore import QPoint
        
        arrow_head = QPolygon([
            QPoint(int(end_x), int(end_y)),
            QPoint(int(point1_x), int(point1_y)),
            QPoint(int(point2_x), int(point2_y))
        ])
        painter.drawPolygon(arrow_head)
        
        # Label
        painter.setPen(QPen(Qt.GlobalColor.red, 2))
        painter.setFont(QFont('Arial', 16, QFont.Weight.Bold))
        painter.drawText(int(end_x) - 30, int(end_y) - 10, 
                        self.direction.upper())
        
        painter.end()
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        return label

class HeightDialog(QDialog):
    """Dialog to input antenna height"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Antenna Height')
        self.setup_ui()
        
    def setup_ui(self):
        layout = QFormLayout()
        
        # Info label
        info = QLabel('Enter the approximate height of your antenna above ground:')
        info.setWordWrap(True)
        layout.addRow(info)
        
        # Height input
        self.height_input = QDoubleSpinBox()
        self.height_input.setMinimum(0.5)
        self.height_input.setMaximum(100.0)
        self.height_input.setValue(12.0)
        self.height_input.setSuffix(' feet')
        self.height_input.setDecimals(1)
        layout.addRow('Antenna Height:', self.height_input)
        
        # Examples
        examples = QLabel(
            'Examples:\n'
            '• Ground floor: 2-4 feet\n'
            '• Second floor: 10-14 feet\n'
            '• Third floor: 20-24 feet'
        )
        examples.setStyleSheet('color: gray; font-size: 11px;')
        layout.addRow(examples)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        self.setLayout(layout)
        
    def get_height(self):
        return self.height_input.value()

class StingrayDetectorGUI(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.current_step = 0
        self.scan_results = {}
        self.antenna_height = 12.0  # Default height
        self.directions = [
            ('north', 'Point antenna toward the north', 0),
            ('south', 'Point antenna toward the south', 180),
            ('east', 'Point antenna toward the east', 90),
            ('west', 'Point antenna toward the west', 270),
            ('southwest', 'Point antenna toward the southwest (lightpole direction)', 225),
            ('northeast', 'Point antenna toward the northeast (building direction)', 45),
            ('up', 'Point antenna upward toward the sky', None),
            ('down', 'Point antenna downward toward the ground', None),
        ]
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle('Stingray Detector')
        self.setGeometry(100, 100, 900, 750)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Tab widget
        tabs = QTabWidget()
        
        # Directional Scanner Tab
        scanner_tab = self.create_scanner_tab()
        tabs.addTab(scanner_tab, "📡 Directional Scanner")
        
        # Monitoring Tab
        monitor_tab = self.create_monitor_tab()
        tabs.addTab(monitor_tab, "⏱️ Monitoring & Schedule")
        
        layout.addWidget(tabs)
        
    def create_scanner_tab(self):
        """Create the directional scanner tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setMaximum(len(self.directions))
        self.progress.setValue(0)
        layout.addWidget(self.progress)
        
        # Stacked widget for direction screens
        self.stack = QStackedWidget()
        
        # Add direction widgets
        for direction, description, angle in self.directions:
            if angle is not None:
                widget = DirectionWidget(direction, description, angle)
            else:
                # Special handling for up/down
                widget = self.create_vertical_widget(direction, description)
            self.stack.addWidget(widget)
        
        # Add results screen
        self.results_widget = self.create_results_widget()
        self.stack.addWidget(self.results_widget)
        
        layout.addWidget(self.stack)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.prev_btn = QPushButton('← Previous')
        self.prev_btn.clicked.connect(self.previous_step)
        self.prev_btn.setEnabled(False)
        button_layout.addWidget(self.prev_btn)
        
        self.scan_btn = QPushButton('Start Scan')
        self.scan_btn.clicked.connect(self.start_scan)
        self.scan_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        button_layout.addWidget(self.scan_btn)
        
        self.next_btn = QPushButton('Next →')
        self.next_btn.clicked.connect(self.next_step)
        self.next_btn.setEnabled(False)
        button_layout.addWidget(self.next_btn)
        
        layout.addLayout(button_layout)
        
        # Status label
        self.status_label = QLabel('Ready to start scanning')
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont('Arial', 12))
        layout.addWidget(self.status_label)
        
        return widget
        
    def create_monitor_tab(self):
        """Create the monitoring and scheduling tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Quick Test Plans
        test_group = QGroupBox("Quick Monitoring Tests")
        test_layout = QGridLayout()
        
        test_plans = [
            ("5 Minutes", 5, 30),
            ("10 Minutes", 10, 60),
            ("30 Minutes", 30, 120),
            ("1 Hour", 60, 120),
            ("2 Hours", 120, 180),
        ]
        
        for i, (label, duration, interval) in enumerate(test_plans):
            btn = QPushButton(f"▶️ {label}\n({interval}s intervals)")
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    font-size: 14px;
                    padding: 15px;
                    border-radius: 5px;
                    min-height: 60px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
                QPushButton:disabled {
                    background-color: #cccccc;
                }
            """)
            btn.clicked.connect(lambda checked, d=duration, i=interval: self.start_monitoring(d, i))
            test_layout.addWidget(btn, i // 3, i % 3)
        
        test_group.setLayout(test_layout)
        layout.addWidget(test_group)
        
        # Scheduling
        schedule_group = QGroupBox("Automated Daily Schedule")
        schedule_layout = QFormLayout()
        
        # Enable checkbox
        self.schedule_enabled = QCheckBox("Enable daily automated monitoring")
        schedule_layout.addRow(self.schedule_enabled)
        
        # Time picker
        self.schedule_time = QTimeEdit()
        self.schedule_time.setTime(QTime(20, 0))  # 8 PM default
        self.schedule_time.setDisplayFormat("hh:mm AP")
        schedule_layout.addRow("Daily run time:", self.schedule_time)
        
        # Duration
        self.schedule_duration = QSpinBox()
        self.schedule_duration.setMinimum(5)
        self.schedule_duration.setMaximum(480)
        self.schedule_duration.setValue(60)
        self.schedule_duration.setSuffix(" minutes")
        schedule_layout.addRow("Duration:", self.schedule_duration)
        
        # Interval
        self.schedule_interval = QSpinBox()
        self.schedule_interval.setMinimum(30)
        self.schedule_interval.setMaximum(600)
        self.schedule_interval.setValue(120)
        self.schedule_interval.setSuffix(" seconds")
        schedule_layout.addRow("Scan interval:", self.schedule_interval)
        
        # Save button
        save_schedule_btn = QPushButton("💾 Save Schedule")
        save_schedule_btn.clicked.connect(self.save_schedule)
        save_schedule_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-size: 14px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        schedule_layout.addRow(save_schedule_btn)
        
        # Info label
        info = QLabel(
            "ℹ️ Scheduled monitoring will:\n"
            "• Run automatically at the specified time each day\n"
            "• Kill any running HackRF processes to take control\n"
            "• Run even if you missed the scheduled time (when HackRF is detected)\n"
            "• Save results to detection-logs/tracking/"
        )
        info.setStyleSheet("color: gray; font-size: 11px; padding: 10px;")
        info.setWordWrap(True)
        schedule_layout.addRow(info)
        
        schedule_group.setLayout(schedule_layout)
        layout.addWidget(schedule_group)
        
        # Monitoring status
        self.monitor_status = QTextEdit()
        self.monitor_status.setReadOnly(True)
        self.monitor_status.setMaximumHeight(150)
        self.monitor_status.setPlaceholderText("Monitoring status will appear here...")
        layout.addWidget(self.monitor_status)
        
        # Stop button
        self.stop_monitor_btn = QPushButton("⏹️ Stop Monitoring")
        self.stop_monitor_btn.clicked.connect(self.stop_monitoring)
        self.stop_monitor_btn.setEnabled(False)
        self.stop_monitor_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-size: 14px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        layout.addWidget(self.stop_monitor_btn)
        
        # Load current schedule
        self.load_schedule()
        
        return widget
        
    def create_vertical_widget(self, direction, description):
        """Create widget for up/down directions"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Title
        title = QLabel(f"Point Antenna: {direction.upper()}")
        title.setFont(QFont('Arial', 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Description
        desc = QLabel(description)
        desc.setFont(QFont('Arial', 14))
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)
        
        # Simple diagram
        diagram_label = QLabel()
        pixmap = QPixmap(600, 300)
        pixmap.fill(Qt.GlobalColor.white)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        center_x, center_y = 300, 150
        
        # Draw HackRF
        painter.setBrush(QColor(100, 100, 200))
        painter.drawRect(center_x - 30, center_y - 20, 60, 40)
        
        # Draw arrow
        painter.setPen(QPen(Qt.GlobalColor.red, 4))
        painter.setBrush(Qt.GlobalColor.red)
        
        if direction == 'up':
            # Arrow pointing up
            painter.drawLine(center_x, center_y, center_x, center_y - 80)
            from PyQt6.QtGui import QPolygon
            from PyQt6.QtCore import QPoint
            arrow = QPolygon([
                QPoint(center_x, center_y - 80),
                QPoint(center_x - 15, center_y - 65),
                QPoint(center_x + 15, center_y - 65)
            ])
            painter.drawPolygon(arrow)
        else:
            # Arrow pointing down
            painter.drawLine(center_x, center_y, center_x, center_y + 80)
            from PyQt6.QtGui import QPolygon
            from PyQt6.QtCore import QPoint
            arrow = QPolygon([
                QPoint(center_x, center_y + 80),
                QPoint(center_x - 15, center_y + 65),
                QPoint(center_x + 15, center_y + 65)
            ])
            painter.drawPolygon(arrow)
        
        painter.end()
        diagram_label.setPixmap(pixmap)
        diagram_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(diagram_label)
        
        # Instructions
        instructions = QLabel(
            "1. Hold your HackRF with antenna pointing in the direction shown\n"
            "2. Keep antenna steady\n"
            "3. Click 'Start Scan' when ready"
        )
        instructions.setFont(QFont('Arial', 12))
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(instructions)
        
        widget.setLayout(layout)
        return widget
        
    def create_results_widget(self):
        """Create final results display"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel('Scan Complete!')
        title.setFont(QFont('Arial', 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setFont(QFont('Courier', 11))
        layout.addWidget(self.results_text)
        
        # Button layout
        btn_layout = QHBoxLayout()
        
        # Set height button
        height_btn = QPushButton('Set Antenna Height')
        height_btn.clicked.connect(self.set_antenna_height)
        height_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                font-size: 14px;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        btn_layout.addWidget(height_btn)
        
        # Analyze button
        analyze_btn = QPushButton('Analyze Results')
        analyze_btn.clicked.connect(self.analyze_results)
        analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        btn_layout.addWidget(analyze_btn)
        
        layout.addLayout(btn_layout)
        
        widget.setLayout(layout)
        return widget
        
    def start_scan(self):
        """Start scanning current direction"""
        self.scan_btn.setEnabled(False)
        self.prev_btn.setEnabled(False)
        self.next_btn.setEnabled(False)
        
        direction = self.directions[self.current_step][0]
        self.status_label.setText(f'Scanning {direction}... Please wait...')
        
        # Start scan thread
        self.scan_thread = ScanThread(direction)
        self.scan_thread.finished.connect(self.scan_finished)
        self.scan_thread.error.connect(self.scan_error)
        self.scan_thread.start()
        
    def scan_finished(self, direction, output_file):
        """Handle scan completion"""
        self.scan_results[direction] = output_file
        self.status_label.setText(f'✅ {direction.upper()} scan complete!')
        self.next_btn.setEnabled(True)
        self.scan_btn.setEnabled(False)
        
        # Auto-advance after 1 second
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(1000, self.next_step)
        
    def scan_error(self, error_msg):
        """Handle scan error"""
        self.status_label.setText(f'❌ Error: {error_msg}')
        self.scan_btn.setEnabled(True)
        self.prev_btn.setEnabled(self.current_step > 0)
        QMessageBox.critical(self, 'Scan Error', f'Failed to scan:\n{error_msg}')
        
    def next_step(self):
        """Move to next direction"""
        if self.current_step < len(self.directions) - 1:
            self.current_step += 1
            self.stack.setCurrentIndex(self.current_step)
            self.progress.setValue(self.current_step)
            self.prev_btn.setEnabled(True)
            self.scan_btn.setEnabled(True)
            self.next_btn.setEnabled(False)
            
            direction = self.directions[self.current_step][0]
            self.status_label.setText(f'Ready to scan {direction}')
        else:
            # All scans complete, show results
            self.current_step += 1
            self.stack.setCurrentIndex(len(self.directions))
            self.progress.setValue(len(self.directions))
            self.prev_btn.setEnabled(True)
            self.next_btn.setEnabled(False)
            self.scan_btn.setEnabled(False)
            self.status_label.setText('All scans complete!')
            self.show_results_summary()
            
    def previous_step(self):
        """Move to previous direction"""
        if self.current_step > 0:
            self.current_step -= 1
            self.stack.setCurrentIndex(self.current_step)
            self.progress.setValue(self.current_step)
            self.prev_btn.setEnabled(self.current_step > 0)
            self.next_btn.setEnabled(True)
            self.scan_btn.setEnabled(True)
            
            direction = self.directions[self.current_step][0]
            self.status_label.setText(f'Ready to scan {direction}')
            
    def set_antenna_height(self):
        """Open dialog to set antenna height"""
        dialog = HeightDialog(self)
        dialog.height_input.setValue(self.antenna_height)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.antenna_height = dialog.get_height()
            QMessageBox.information(
                self,
                'Height Set',
                f'Antenna height set to {self.antenna_height:.1f} feet'
            )
    
    def show_results_summary(self):
        """Display summary of all scans"""
        summary = "=== Directional Scan Summary ===\n\n"
        summary += f"Total scans completed: {len(self.scan_results)}\n"
        summary += f"Antenna height: {self.antenna_height:.1f} feet\n\n"
        
        for direction, filepath in self.scan_results.items():
            summary += f"✅ {direction.upper()}: {filepath}\n"
        
        summary += "\n\nClick 'Set Antenna Height' to adjust height if needed."
        summary += "\nClick 'Analyze Results' to run full analysis and triangulation."
        
        self.results_text.setText(summary)
        
    def analyze_results(self):
        """Run analysis scripts on collected data"""
        if len(self.scan_results) < 4:
            QMessageBox.warning(
                self,
                'Insufficient Data',
                'Please complete at least 4 directional scans before analyzing.'
            )
            return
        
        self.results_text.append("\n\n=== Running Analysis ===\n")
        self.results_text.append(f"Using antenna height: {self.antenna_height:.1f} feet\n\n")
        QApplication.processEvents()
        
        try:
            # Run comparison script
            self.results_text.append("Running directional comparison...\n")
            QApplication.processEvents()
            
            result = subprocess.run(
                ['python3', 'scripts/compare-directions.py', 'detection-logs/directional/'],
                capture_output=True,
                text=True,
                cwd='/Users/meep/Documents/EpiRay',
                timeout=30
            )
            
            if result.returncode == 0:
                self.results_text.append(result.stdout)
            else:
                self.results_text.append(f"⚠️ Comparison script error:\n{result.stderr}\n")
            
            # Run position estimation
            self.results_text.append("\n\n=== Position Estimation ===\n")
            QApplication.processEvents()
            
            result = subprocess.run(
                ['python3', 'scripts/estimate-position.py', 
                 'detection-logs/directional/', str(self.antenna_height)],
                capture_output=True,
                text=True,
                cwd='/Users/meep/Documents/EpiRay',
                timeout=30
            )
            
            if result.returncode == 0:
                self.results_text.append(result.stdout)
                self.status_label.setText('✅ Analysis complete!')
                QMessageBox.information(
                    self,
                    'Analysis Complete',
                    'Directional analysis and position estimation complete!\n\n'
                    'Check the results above for signal source location.'
                )
            else:
                self.results_text.append(f"⚠️ Position estimation error:\n{result.stderr}\n")
                self.status_label.setText('⚠️ Analysis completed with warnings')
            
        except subprocess.TimeoutExpired:
            self.results_text.append("\n\n❌ Error: Analysis timed out (took longer than 30 seconds)")
            self.status_label.setText('❌ Analysis timed out')
            QMessageBox.critical(
                self,
                'Timeout Error',
                'Analysis took too long and was cancelled.\n\n'
                'This may indicate an issue with the scan data or analysis scripts.'
            )
        except FileNotFoundError as e:
            self.results_text.append(f"\n\n❌ Error: Required file not found\n{str(e)}")
            self.status_label.setText('❌ Analysis failed')
            QMessageBox.critical(
                self,
                'File Error',
                f'Could not find required files:\n{str(e)}\n\n'
                'Make sure all scan files are in detection-logs/directional/'
            )
        except Exception as e:
            self.results_text.append(f"\n\n❌ Unexpected error: {str(e)}\n")
            self.status_label.setText('❌ Analysis failed')
            QMessageBox.critical(
                self,
                'Error',
                f'An error occurred during analysis:\n{str(e)}'
            )

    def start_monitoring(self, duration_minutes, interval_seconds):
        """Start monitoring test"""
        self.monitor_status.append(f"\n[{datetime.now().strftime('%H:%M:%S')}] Starting {duration_minutes} minute monitoring...")
        self.stop_monitor_btn.setEnabled(True)
        
        # Disable test buttons
        for btn in self.findChildren(QPushButton):
            if "▶️" in btn.text():
                btn.setEnabled(False)
        
        # Start monitoring thread
        self.monitor_thread = MonitorThread(duration_minutes, interval_seconds)
        self.monitor_thread.progress.connect(self.monitor_progress)
        self.monitor_thread.finished.connect(self.monitor_finished)
        self.monitor_thread.start()
        
    def monitor_progress(self, message):
        """Update monitoring progress"""
        self.monitor_status.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        
    def monitor_finished(self, success, message):
        """Handle monitoring completion"""
        if success:
            self.monitor_status.append(f"\n✅ [{datetime.now().strftime('%H:%M:%S')}] {message}")
            QMessageBox.information(self, 'Monitoring Complete', message)
        else:
            self.monitor_status.append(f"\n❌ [{datetime.now().strftime('%H:%M:%S')}] {message}")
            QMessageBox.warning(self, 'Monitoring Failed', message)
        
        self.stop_monitor_btn.setEnabled(False)
        
        # Re-enable test buttons
        for btn in self.findChildren(QPushButton):
            if "▶️" in btn.text():
                btn.setEnabled(True)
                
    def stop_monitoring(self):
        """Stop current monitoring"""
        if hasattr(self, 'monitor_thread') and self.monitor_thread.isRunning():
            # Kill HackRF processes
            subprocess.run(['killall', 'hackrf_sweep'], stderr=subprocess.DEVNULL)
            subprocess.run(['killall', 'track-movement.sh'], stderr=subprocess.DEVNULL)
            self.monitor_thread.terminate()
            self.monitor_thread.wait()
            self.monitor_status.append(f"\n⏹️ [{datetime.now().strftime('%H:%M:%S')}] Monitoring stopped by user")
            self.stop_monitor_btn.setEnabled(False)
            
            # Re-enable test buttons
            for btn in self.findChildren(QPushButton):
                if "▶️" in btn.text():
                    btn.setEnabled(True)
                    
    def load_schedule(self):
        """Load schedule from file"""
        schedule_file = os.path.expanduser('~/Library/Application Support/EpiRay/schedule.json')
        if os.path.exists(schedule_file):
            try:
                with open(schedule_file, 'r') as f:
                    schedule = json.load(f)
                    self.schedule_enabled.setChecked(schedule.get('enabled', False))
                    
                    # Parse time
                    time_str = schedule.get('daily_time', '20:00')
                    hour, minute = map(int, time_str.split(':'))
                    self.schedule_time.setTime(QTime(hour, minute))
                    
                    self.schedule_duration.setValue(schedule.get('duration_minutes', 60))
                    self.schedule_interval.setValue(schedule.get('interval_seconds', 120))
            except Exception as e:
                print(f"Error loading schedule: {e}")
                
    def save_schedule(self):
        """Save schedule to file"""
        schedule = {
            'enabled': self.schedule_enabled.isChecked(),
            'daily_time': self.schedule_time.time().toString('HH:mm'),
            'duration_minutes': self.schedule_duration.value(),
            'interval_seconds': self.schedule_interval.value()
        }
        
        schedule_file = os.path.expanduser('~/Library/Application Support/EpiRay/schedule.json')
        os.makedirs(os.path.dirname(schedule_file), exist_ok=True)
        
        try:
            with open(schedule_file, 'w') as f:
                json.dump(schedule, f, indent=2)
            
            QMessageBox.information(
                self,
                'Schedule Saved',
                f"Schedule saved successfully!\n\n"
                f"{'Enabled' if schedule['enabled'] else 'Disabled'}\n"
                f"Daily run time: {schedule['daily_time']}\n"
                f"Duration: {schedule['duration_minutes']} minutes\n"
                f"Interval: {schedule['interval_seconds']} seconds\n\n"
                f"The scheduler daemon will run this automatically."
            )
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to save schedule:\n{str(e)}')

def main():
    app = QApplication(sys.argv)
    window = StingrayDetectorGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
