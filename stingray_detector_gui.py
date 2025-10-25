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
                             QCheckBox, QSpinBox, QFileDialog, QLineEdit,
                             QScrollArea)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTime
from PyQt6.QtGui import QPixmap, QPainter, QPen, QFont, QColor
import json
import webbrowser
from PIL import Image, ImageDraw, ImageFont

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
                cwd=os.path.dirname(os.path.abspath(__file__))
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
                                   cwd=os.path.dirname(os.path.abspath(__file__)))
            
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
        title = QLabel(f"Point antenna toward the {self.direction}")
        title.setFont(QFont('Arial', 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #ffffff; background-color: #1a1a1a; padding: 10px;")
        layout.addWidget(title)
        
        # Diagram
        diagram = self.create_diagram()
        layout.addWidget(diagram)
        
        # Instructions at bottom
        instructions = QLabel(
            "1. Hold your HackRF with antenna pointing in the direction shown above"
        )
        instructions.setFont(QFont('Arial', 12))
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instructions.setStyleSheet("color: #ffffff; padding: 10px; background-color: #2b2b2b;")
        layout.addWidget(instructions)
        
        self.setLayout(layout)
        
    def create_diagram(self):
        """Create visual diagram showing antenna direction"""
        label = QLabel()
        pixmap = QPixmap(500, 300)
        pixmap.fill(QColor(43, 43, 43))  # Dark background
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw compass rose
        center_x, center_y = 250, 150
        
        # Draw circle
        painter.setPen(QPen(Qt.GlobalColor.white, 2))
        painter.drawEllipse(center_x - 100, center_y - 100, 200, 200)
        
        # Draw cardinal directions
        painter.setPen(QPen(Qt.GlobalColor.white))
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
        self.setGeometry(100, 100, 900, 530)
        
        # Apply dark mode stylesheet
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #3d3d3d;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
            QPushButton:pressed {
                background-color: #2d2d2d;
            }
            QTextEdit, QLineEdit, QSpinBox, QDoubleSpinBox, QTimeEdit {
                background-color: #3d3d3d;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 4px;
                border-radius: 3px;
            }
            QProgressBar {
                background-color: #3d3d3d;
                border: 1px solid #555555;
                border-radius: 3px;
                text-align: center;
                color: #ffffff;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
            QGroupBox {
                border: 1px solid #555555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QTabWidget::pane {
                border: 1px solid #555555;
                background-color: #2b2b2b;
            }
            QTabBar::tab {
                background-color: #3d3d3d;
                color: #ffffff;
                padding: 8px 16px;
                border: 1px solid #555555;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #2b2b2b;
                border-bottom: 1px solid #2b2b2b;
            }
            QCheckBox {
                color: #ffffff;
            }
            QScrollArea {
                background-color: #2b2b2b;
                border: none;
            }
        """)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # HackRF Status Bar
        status_bar = QWidget()
        status_layout = QHBoxLayout(status_bar)
        status_layout.setContentsMargins(10, 5, 10, 5)
        
        status_label = QLabel("HackRF Status:")
        status_label.setStyleSheet("font-weight: bold;")
        status_layout.addWidget(status_label)
        
        self.hackrf_indicator = QLabel("● Checking...")
        self.hackrf_indicator.setStyleSheet("color: orange; font-size: 16px; font-weight: bold;")
        status_layout.addWidget(self.hackrf_indicator)
        
        self.hackrf_detail = QLabel("")
        self.hackrf_detail.setStyleSheet("color: gray; font-size: 11px;")
        status_layout.addWidget(self.hackrf_detail)
        
        status_layout.addStretch()
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.check_hackrf_status)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 5px 15px;
                border-radius: 3px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        status_layout.addWidget(refresh_btn)
        
        status_bar.setStyleSheet("background-color: #f5f5f5; border-bottom: 1px solid #ddd;")
        layout.addWidget(status_bar)
        
        # Tab widget
        tabs = QTabWidget()
        
        # Directional Scanner Tab with scroll
        scanner_tab = self.create_scanner_tab()
        scanner_scroll = QScrollArea()
        scanner_scroll.setWidget(scanner_tab)
        scanner_scroll.setWidgetResizable(True)
        tabs.addTab(scanner_scroll, "📡 Directional Scanner")
        
        # Monitoring Tab with scroll
        monitor_tab = self.create_monitor_tab()
        monitor_scroll = QScrollArea()
        monitor_scroll.setWidget(monitor_tab)
        monitor_scroll.setWidgetResizable(True)
        tabs.addTab(monitor_scroll, "⏱️ Monitoring & Schedule")
        
        # Photo & Reporting Tab with scroll
        photo_tab = self.create_photo_tab()
        photo_scroll = QScrollArea()
        photo_scroll.setWidget(photo_tab)
        photo_scroll.setWidgetResizable(True)
        tabs.addTab(photo_scroll, "📸 Photo & Report")
        
        layout.addWidget(tabs)
        
        # Check HackRF status on startup
        self.check_hackrf_status()
        
    def check_hackrf_status(self):
        """Check if HackRF is connected and accessible"""
        try:
            result = subprocess.run(
                ['hackrf_info'],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            if 'Found HackRF' in result.stdout:
                if 'Access denied' in result.stdout or 'insufficient permissions' in result.stdout:
                    self.hackrf_indicator.setText("● Connected (Need Sudo)")
                    self.hackrf_indicator.setStyleSheet("color: orange; font-size: 16px; font-weight: bold;")
                    
                    # Extract serial number
                    for line in result.stdout.split('\n'):
                        if 'Serial number:' in line:
                            serial = line.split(':')[1].strip()
                            # Mask serial number for privacy (show only last 4 chars)
                            masked_serial = "XXXXXXXXXXXX" + serial[-4:] if len(serial) > 4 else "XXXX"
                            self.hackrf_detail.setText(f"Serial: {masked_serial} - Run scripts with sudo for access")
                            break
                else:
                    self.hackrf_indicator.setText("● Connected")
                    self.hackrf_indicator.setStyleSheet("color: #4caf50; font-size: 16px; font-weight: bold;")
                    
                    # Extract serial number
                    for line in result.stdout.split('\n'):
                        if 'Serial number:' in line:
                            serial = line.split(':')[1].strip()
                            # Mask serial number for privacy (show only last 4 chars)
                            masked_serial = "XXXXXXXXXXXX" + serial[-4:] if len(serial) > 4 else "XXXX"
                            self.hackrf_detail.setText(f"Serial: {masked_serial} - Ready to scan")
                            break
            else:
                self.hackrf_indicator.setText("● Not Found")
                self.hackrf_indicator.setStyleSheet("color: #f44336; font-size: 16px; font-weight: bold;")
                self.hackrf_detail.setText("Connect HackRF via USB and click Refresh")
                
        except subprocess.TimeoutExpired:
            self.hackrf_indicator.setText("● Timeout")
            self.hackrf_indicator.setStyleSheet("color: orange; font-size: 16px; font-weight: bold;")
            self.hackrf_detail.setText("HackRF not responding - check connection")
        except FileNotFoundError:
            self.hackrf_indicator.setText("● Not Installed")
            self.hackrf_indicator.setStyleSheet("color: #f44336; font-size: 16px; font-weight: bold;")
            self.hackrf_detail.setText("Install HackRF tools: brew install hackrf")
        except Exception as e:
            self.hackrf_indicator.setText("● Error")
            self.hackrf_indicator.setStyleSheet("color: #f44336; font-size: 16px; font-weight: bold;")
            self.hackrf_detail.setText(str(e))
        
    def create_scanner_tab(self):
        """Create the directional scanner tab"""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        
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
                dir_widget = DirectionWidget(direction, description, angle)
            else:
                # Special handling for up/down
                dir_widget = self.create_vertical_widget(direction, description)
            self.stack.addWidget(dir_widget)
        
        # Add results screen
        self.results_widget = self.create_results_widget()
        self.stack.addWidget(self.results_widget)
        
        # Horizontal layout for buttons (left) and visual (right)
        content_layout = QHBoxLayout()
        
        # Left side - Control buttons
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        self.prev_btn = QPushButton('← Previous')
        self.prev_btn.clicked.connect(self.previous_step)
        self.prev_btn.setEnabled(False)
        self.prev_btn.setMinimumHeight(50)
        left_layout.addWidget(self.prev_btn)
        
        self.scan_btn = QPushButton('Start Scan')
        self.scan_btn.clicked.connect(self.start_scan)
        self.scan_btn.setMinimumHeight(60)
        self.scan_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 18px;
                font-weight: bold;
                padding: 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #666666;
            }
        """)
        left_layout.addWidget(self.scan_btn)
        
        self.next_btn = QPushButton('Next →')
        self.next_btn.clicked.connect(self.next_step)
        self.next_btn.setEnabled(False)
        self.next_btn.setMinimumHeight(50)
        left_layout.addWidget(self.next_btn)
        
        left_layout.addStretch()
        
        # Status label
        self.status_label = QLabel('Ready to start scanning')
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont('Arial', 11))
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("padding: 10px; background-color: #3d3d3d; border-radius: 5px;")
        left_layout.addWidget(self.status_label)
        
        left_panel.setMaximumWidth(200)
        content_layout.addWidget(left_panel)
        
        # Right side - Visual
        content_layout.addWidget(self.stack, 1)
        
        layout.addLayout(content_layout)
        
        return tab_widget
        
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
    
    def create_photo_tab(self):
        """Create photo annotation and reporting tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Photo Annotation Section
        photo_group = QGroupBox("📸 Annotate Stingray Photo")
        photo_layout = QVBoxLayout()
        
        # Photo selection
        photo_select_layout = QHBoxLayout()
        self.photo_path_input = QLineEdit()
        self.photo_path_input.setPlaceholderText("Select a photo...")
        self.photo_path_input.setReadOnly(True)
        photo_select_layout.addWidget(self.photo_path_input)
        
        select_photo_btn = QPushButton("📁 Select Photo")
        select_photo_btn.clicked.connect(self.select_photo)
        photo_select_layout.addWidget(select_photo_btn)
        
        photo_layout.addLayout(photo_select_layout)
        
        # Measurement inputs
        measurements_layout = QFormLayout()
        
        self.species_input = QLineEdit()
        self.species_input.setPlaceholderText("e.g., LightPolaflag")
        measurements_layout.addRow("Species:", self.species_input)
        
        self.distance_input = QLineEdit()
        self.distance_input.setPlaceholderText("e.g., 12 feet")
        measurements_layout.addRow("Distance:", self.distance_input)
        
        self.direction_input = QLineEdit()
        self.direction_input.setPlaceholderText("e.g., Southwest")
        measurements_layout.addRow("Direction:", self.direction_input)
        
        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText("e.g., 10 feet above ground")
        measurements_layout.addRow("Height:", self.height_input)
        
        self.signal_input = QLineEdit()
        self.signal_input.setPlaceholderText("e.g., -15.5 dBm")
        measurements_layout.addRow("Signal Strength:", self.signal_input)
        
        photo_layout.addLayout(measurements_layout)
        
        # Annotate button
        annotate_btn = QPushButton("🎨 Annotate Photo")
        annotate_btn.clicked.connect(self.annotate_photo)
        annotate_btn.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                font-size: 16px;
                padding: 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
        """)
        photo_layout.addWidget(annotate_btn)
        
        # Preview area
        self.photo_preview = QLabel("Photo preview will appear here")
        self.photo_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.photo_preview.setMinimumHeight(300)
        self.photo_preview.setStyleSheet("border: 2px dashed #ccc; background: #f5f5f5;")
        
        scroll = QScrollArea()
        scroll.setWidget(self.photo_preview)
        scroll.setWidgetResizable(True)
        photo_layout.addWidget(scroll)
        
        photo_group.setLayout(photo_layout)
        layout.addWidget(photo_group)
        
        # GitHub Reporting Section
        github_group = QGroupBox("🌐 Share to Community")
        github_layout = QVBoxLayout()
        
        info = QLabel(
            "📤 Share your findings with the community!\n\n"
            "Your annotated photos and reports help others identify threats in their area.\n"
            "All submissions are public and help build a global Stingray detection database."
        )
        info.setWordWrap(True)
        info.setStyleSheet("padding: 10px; background: #e3f2fd; border-radius: 5px; color: #000000;")
        github_layout.addWidget(info)
        
        # GitHub sync button
        github_btn = QPushButton("📤 Upload to GitHub Community")
        github_btn.clicked.connect(self.upload_to_github)
        github_btn.setStyleSheet("""
            QPushButton {
                background-color: #24292e;
                color: white;
                font-size: 16px;
                padding: 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1b1f23;
            }
        """)
        github_layout.addWidget(github_btn)
        
        # View community button
        view_community_btn = QPushButton("👀 View Community Reports")
        view_community_btn.clicked.connect(self.view_community_reports)
        view_community_btn.setStyleSheet("""
            QPushButton {
                background-color: #0366d6;
                color: white;
                font-size: 14px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0256c7;
            }
        """)
        github_layout.addWidget(view_community_btn)
        
        github_group.setLayout(github_layout)
        layout.addWidget(github_group)
        
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
        instructions.setStyleSheet("color: #ffffff; padding: 10px; background-color: #2b2b2b;")
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
                cwd=os.path.dirname(os.path.abspath(__file__)),
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
                cwd=os.path.dirname(os.path.abspath(__file__)),
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
    
    def select_photo(self):
        """Open file dialog to select photo"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Stingray Photo",
            os.path.expanduser("~"),
            "Images (*.png *.jpg *.jpeg *.gif *.bmp)"
        )
        
        if file_path:
            self.photo_path_input.setText(file_path)
            
            # Show preview
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                # Scale to fit preview
                scaled = pixmap.scaled(800, 600, Qt.AspectRatioMode.KeepAspectRatio, 
                                      Qt.TransformationMode.SmoothTransformation)
                self.photo_preview.setPixmap(scaled)
    
    def annotate_photo(self):
        """Annotate the selected photo with measurements"""
        photo_path = self.photo_path_input.text()
        
        if not photo_path or not os.path.exists(photo_path):
            QMessageBox.warning(self, 'No Photo', 'Please select a photo first.')
            return
        
        # Get measurements
        measurements = {
            'species': self.species_input.text() or 'Unknown Stingray',
            'distance': self.distance_input.text(),
            'direction': self.direction_input.text(),
            'height': self.height_input.text(),
            'signal_strength': self.signal_input.text(),
            'show_scale': True
        }
        
        # Check if any measurements provided
        if not any([measurements['distance'], measurements['direction'], 
                   measurements['height'], measurements['signal_strength']]):
            QMessageBox.warning(self, 'No Measurements', 
                              'Please enter at least one measurement.')
            return
        
        try:
            # Generate output path
            base_name = os.path.splitext(photo_path)[0]
            output_path = f"{base_name}_annotated.jpg"
            
            # Annotate using PIL
            img = Image.open(photo_path)
            draw = ImageDraw.Draw(img)
            
            width, height = img.size
            
            # Load font
            try:
                title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
                label_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
                data_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 35)
            except:
                title_font = ImageFont.load_default()
                label_font = ImageFont.load_default()
                data_font = ImageFont.load_default()
            
            # Top overlay
            overlay = Image.new('RGBA', (width, 200), (0, 0, 0, 180))
            img.paste(overlay, (0, 0), overlay)
            
            # Title
            draw.text((20, 20), f"🎯 {measurements['species']}", 
                     fill=(255, 255, 255), font=title_font)
            
            # Measurements
            y = 90
            if measurements['distance']:
                draw.text((20, y), f"📏 Distance: {measurements['distance']}", 
                         fill=(255, 200, 0), font=label_font)
                y += 50
            
            if measurements['direction']:
                draw.text((20, y), f"🧭 Direction: {measurements['direction']}", 
                         fill=(255, 200, 0), font=label_font)
            
            # Bottom overlay
            info_overlay = Image.new('RGBA', (width, 150), (0, 0, 0, 180))
            img.paste(info_overlay, (0, height - 150), info_overlay)
            
            # Bottom info
            y_bottom = height - 130
            if measurements['height']:
                draw.text((20, y_bottom), f"📐 Height: {measurements['height']}", 
                         fill=(100, 200, 255), font=data_font)
                y_bottom += 45
            
            if measurements['signal_strength']:
                draw.text((20, y_bottom), f"📡 Signal: {measurements['signal_strength']}", 
                         fill=(255, 100, 100), font=data_font)
            
            # Save
            img.save(output_path, quality=95)
            
            # Show result
            QMessageBox.information(
                self,
                'Success!',
                f'Annotated photo saved to:\n{output_path}\n\n'
                f'You can now upload this to the community!'
            )
            
            # Update preview
            pixmap = QPixmap(output_path)
            scaled = pixmap.scaled(800, 600, Qt.AspectRatioMode.KeepAspectRatio,
                                  Qt.TransformationMode.SmoothTransformation)
            self.photo_preview.setPixmap(scaled)
            
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to annotate photo:\n{str(e)}')
    
    def upload_to_github(self):
        """Open GitHub to upload report"""
        msg = QMessageBox()
        msg.setWindowTitle('Upload to GitHub Community')
        msg.setText(
            '📤 Share Your Findings!\n\n'
            'To upload your report:\n\n'
            '1. Click "Open GitHub" below\n'
            '2. Navigate to the "community-reports" folder\n'
            '3. Click "Add file" → "Upload files"\n'
            '4. Drag your annotated photo and any scan data\n'
            '5. Add a description and commit\n\n'
            'Your contribution helps protect others!'
        )
        msg.setIcon(QMessageBox.Icon.Information)
        
        open_btn = msg.addButton('Open GitHub', QMessageBox.ButtonRole.AcceptRole)
        cancel_btn = msg.addButton('Cancel', QMessageBox.ButtonRole.RejectRole)
        
        msg.exec()
        
        if msg.clickedButton() == open_btn:
            webbrowser.open('https://github.com/aimarketingflow/stingray-detector-relative-positional-locator/tree/main/community-reports')
    
    def view_community_reports(self):
        """Open browser to view community reports"""
        webbrowser.open('https://github.com/aimarketingflow/stingray-detector-relative-positional-locator/tree/main/community-reports')

def main():
    app = QApplication(sys.argv)
    window = StingrayDetectorGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
