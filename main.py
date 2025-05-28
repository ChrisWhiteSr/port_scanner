#!/usr/bin/env python3
"""
Comcast Email Port Monitor - Main Application
A Windows desktop application to monitor email server ports and detect potential blocking.
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt6.QtWidgets import QLabel, QPushButton, QTableWidget, QTableWidgetItem, QTabWidget
from PyQt6.QtWidgets import QLineEdit, QSpinBox, QCheckBox, QTextEdit, QProgressBar, QGroupBox
from PyQt6.QtCore import QTimer, QThread, pyqtSignal, Qt
from PyQt6.QtGui import QFont, QIcon, QColor
import sqlite3
import socket
import threading
import time
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
import schedule

from port_scanner import PortScanner
from database import DatabaseManager
from scheduler import MonitoringScheduler
from styles import get_application_stylesheet, get_chart_style, get_port_status_colors

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Comcast Email Port Monitor")
        self.setGeometry(100, 100, 1200, 800)
        
        # Apply styling
        self.setStyleSheet(get_application_stylesheet())
        
        # Get color scheme
        self.status_colors = get_port_status_colors()
        
        # Initialize components
        self.db_manager = DatabaseManager()
        self.port_scanner = PortScanner()
        self.scheduler = MonitoringScheduler(self.db_manager, self.port_scanner)
        
        # Setup scheduler callbacks
        self.scheduler.set_scan_complete_callback(self.on_scan_complete)
        self.scheduler.set_status_update_callback(self.on_status_update)
        
        # Setup UI
        self.setup_ui()
        self.setup_timers()
        
        # Load initial data
        self.load_server_config()
        self.update_status_display()
        
    def setup_ui(self):
        """Setup the main user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_configuration_tab()
        self.create_history_tab()
        self.create_export_tab()
        
        # Add status bar
        from PyQt6.QtWidgets import QStatusBar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready - Click 'Scan Now' to test port connectivity")
        
    def create_dashboard_tab(self):
        """Create the main dashboard tab"""
        dashboard = QWidget()
        layout = QVBoxLayout(dashboard)
        
        # Status section
        status_group = QGroupBox("Current Status")
        status_layout = QGridLayout(status_group)
        
        self.monitoring_status = QLabel("Monitoring: STOPPED")
        self.monitoring_status.setObjectName("monitoring_status")
        self.monitoring_status.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        status_layout.addWidget(self.monitoring_status, 0, 0)
        
        self.last_scan_label = QLabel("Last Scan: Never")
        status_layout.addWidget(self.last_scan_label, 0, 1)
        
        self.next_scan_label = QLabel("Next Scan: --")
        status_layout.addWidget(self.next_scan_label, 1, 0)
        
        self.server_label = QLabel("Server: mail.comcast.net")
        self.server_label.setObjectName("server_label")
        status_layout.addWidget(self.server_label, 1, 1)
        
        layout.addWidget(status_group)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start Monitoring")
        self.start_button.setObjectName("start_button")
        self.start_button.clicked.connect(self.start_monitoring)
        button_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop Monitoring")
        self.stop_button.setObjectName("stop_button")
        self.stop_button.clicked.connect(self.stop_monitoring)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        self.scan_now_button = QPushButton("Scan Now")
        self.scan_now_button.clicked.connect(self.scan_now)
        button_layout.addWidget(self.scan_now_button)
        
        layout.addLayout(button_layout)
        
        # Port status table
        ports_group = QGroupBox("Port Status")
        ports_layout = QVBoxLayout(ports_group)
        
        self.port_table = QTableWidget()
        self.port_table.setColumnCount(4)
        self.port_table.setHorizontalHeaderLabels(["Port", "Protocol", "Status", "Last Check"])
        
        # Set column widths
        self.port_table.setColumnWidth(0, 80)   # Port
        self.port_table.setColumnWidth(1, 120)  # Protocol
        self.port_table.setColumnWidth(2, 100)  # Status
        self.port_table.setColumnWidth(3, 180)  # Last Check
        
        # Enable alternating row colors and selection
        self.port_table.setAlternatingRowColors(True)
        self.port_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        ports_layout.addWidget(self.port_table)
        
        layout.addWidget(ports_group)
        
        # Quick stats
        stats_group = QGroupBox("24-Hour Statistics")
        stats_layout = QGridLayout(stats_group)
        
        self.total_scans_label = QLabel("Total Scans: 0")
        stats_layout.addWidget(self.total_scans_label, 0, 0)
        
        self.success_rate_label = QLabel("Success Rate: 0%")
        stats_layout.addWidget(self.success_rate_label, 0, 1)
        
        self.blocked_ports_label = QLabel("Blocked Ports: 0")
        stats_layout.addWidget(self.blocked_ports_label, 1, 0)
        
        self.avg_response_label = QLabel("Avg Response: 0ms")
        stats_layout.addWidget(self.avg_response_label, 1, 1)
        
        layout.addWidget(stats_group)
        
        self.tab_widget.addTab(dashboard, "Dashboard")
        
    def create_configuration_tab(self):
        """Create the configuration tab"""
        config = QWidget()
        layout = QVBoxLayout(config)
        
        # Server configuration
        server_group = QGroupBox("Server Configuration")
        server_layout = QGridLayout(server_group)
        
        server_layout.addWidget(QLabel("Server Address:"), 0, 0)
        self.server_input = QLineEdit("mail.comcast.net")
        server_layout.addWidget(self.server_input, 0, 1)
        
        server_layout.addWidget(QLabel("Scan Interval (minutes):"), 1, 0)
        self.interval_input = QSpinBox()
        self.interval_input.setRange(1, 1440)  # 1 minute to 24 hours
        self.interval_input.setValue(60)
        server_layout.addWidget(self.interval_input, 1, 1)
        
        layout.addWidget(server_group)
        
        # Port configuration
        ports_group = QGroupBox("Ports to Monitor")
        ports_layout = QVBoxLayout(ports_group)
        
        # Default ports
        self.port_checkboxes = {}
        default_ports = [
            (25, "SMTP"),
            (465, "SMTP SSL"),
            (587, "SMTP TLS"),
            (110, "POP3"),
            (995, "POP3 SSL"),
            (143, "IMAP"),
            (993, "IMAP SSL"),
            (80, "HTTP"),
            (443, "HTTPS")
        ]
        
        ports_grid = QGridLayout()
        for i, (port, protocol) in enumerate(default_ports):
            checkbox = QCheckBox(f"{port} ({protocol})")
            checkbox.setChecked(True)
            self.port_checkboxes[port] = checkbox
            ports_grid.addWidget(checkbox, i // 3, i % 3)
        
        ports_layout.addLayout(ports_grid)
        
        # Custom ports
        custom_layout = QHBoxLayout()
        custom_layout.addWidget(QLabel("Custom Port:"))
        self.custom_port_input = QLineEdit()
        custom_layout.addWidget(self.custom_port_input)
        
        add_port_button = QPushButton("Add Port")
        add_port_button.clicked.connect(self.add_custom_port)
        custom_layout.addWidget(add_port_button)
        
        ports_layout.addLayout(custom_layout)
        layout.addWidget(ports_group)
        
        # Save configuration
        save_button = QPushButton("Save Configuration")
        save_button.clicked.connect(self.save_configuration)
        layout.addWidget(save_button)
        
        self.tab_widget.addTab(config, "Configuration")
        
    def create_history_tab(self):
        """Create the history/charts tab"""
        history = QWidget()
        layout = QVBoxLayout(history)
        
        # Chart controls
        controls_layout = QHBoxLayout()
        
        time_buttons = ["24 Hours", "7 Days", "30 Days", "All Time"]
        for button_text in time_buttons:
            button = QPushButton(button_text)
            # Fix lambda closure issue
            button.clicked.connect(self.create_chart_callback(button_text))
            controls_layout.addWidget(button)
        
        layout.addLayout(controls_layout)
        
        # Chart area
        self.figure = Figure(figsize=(12, 8))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        self.tab_widget.addTab(history, "History & Charts")
        
    def create_export_tab(self):
        """Create the export tab"""
        export = QWidget()
        layout = QVBoxLayout(export)
        
        # Export options
        export_group = QGroupBox("Export Data")
        export_layout = QVBoxLayout(export_group)
        
        # Date range
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Export data from last:"))
        
        self.export_range = QSpinBox()
        self.export_range.setRange(1, 365)
        self.export_range.setValue(7)
        date_layout.addWidget(self.export_range)
        date_layout.addWidget(QLabel("days"))
        
        export_layout.addLayout(date_layout)
        
        # Export buttons
        button_layout = QHBoxLayout()
        
        csv_button = QPushButton("Export to CSV")
        csv_button.clicked.connect(self.export_csv)
        button_layout.addWidget(csv_button)
        
        pdf_button = QPushButton("Generate PDF Report")
        pdf_button.clicked.connect(self.export_pdf)
        button_layout.addWidget(pdf_button)
        
        export_layout.addLayout(button_layout)
        layout.addWidget(export_group)
        
        # Export log
        log_group = QGroupBox("Export Log")
        log_layout = QVBoxLayout(log_group)
        
        self.export_log = QTextEdit()
        self.export_log.setReadOnly(True)
        log_layout.addWidget(self.export_log)
        
        layout.addWidget(log_group)
        
        self.tab_widget.addTab(export, "Export")
        
    def setup_timers(self):
        """Setup timers for UI updates"""
        # Update timer for real-time display
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status_display)
        self.update_timer.start(1000)  # Update every second
        
    def start_monitoring(self):
        """Start the monitoring process"""
        print("Start monitoring button clicked!")  # Debug
        try:
            # Update configuration before starting
            self.update_scheduler_config()
            
            self.scheduler.start_monitoring()
            self.monitoring_status.setText("Monitoring: RUNNING")
            self.monitoring_status.setStyleSheet("color: #38a169; font-weight: bold;")  # Green
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            
            # Show status message
            self.on_status_update("Monitoring started successfully")
        except Exception as e:
            print(f"Error starting monitoring: {e}")  # Debug
            self.on_status_update(f"Failed to start monitoring: {str(e)}")
        
    def stop_monitoring(self):
        """Stop the monitoring process"""
        print("Stop monitoring button clicked!")  # Debug
        try:
            self.scheduler.stop_monitoring()
            self.monitoring_status.setText("Monitoring: STOPPED")
            self.monitoring_status.setStyleSheet("color: #e53e3e; font-weight: bold;")  # Red
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            
            # Show status message
            self.on_status_update("Monitoring stopped")
        except Exception as e:
            print(f"Error stopping monitoring: {e}")  # Debug
            self.on_status_update(f"Failed to stop monitoring: {str(e)}")
        
    def scan_now(self):
        """Perform an immediate scan"""
        print("Scan now button clicked!")  # Debug
        try:
            # Update configuration before scanning
            self.update_scheduler_config()
            
            # Disable button temporarily
            self.scan_now_button.setEnabled(False)
            self.scan_now_button.setText("Scanning...")
            
            self.on_status_update("Starting immediate scan...")
            self.scheduler.scan_now()
            self.update_status_display()
            
            # Re-enable button
            self.scan_now_button.setEnabled(True)
            self.scan_now_button.setText("Scan Now")
            
        except Exception as e:
            print(f"Error in scan now: {e}")  # Debug
            self.on_status_update(f"Scan failed: {str(e)}")
            # Re-enable button on error
            self.scan_now_button.setEnabled(True)
            self.scan_now_button.setText("Scan Now")
        
    def update_status_display(self):
        """Update the status display with current information"""
        # Update port table
        self.update_port_table()
        
        # Update statistics
        self.update_statistics()
        
        # Update next scan time
        if self.scheduler.is_running:
            next_scan = self.scheduler.get_next_scan_time()
            if next_scan:
                self.next_scan_label.setText(f"Next Scan: {next_scan.strftime('%H:%M:%S')}")
        
    def update_port_table(self):
        """Update the port status table"""
        recent_scans = self.db_manager.get_recent_scans(limit=50)
        
        # Group by port
        port_status = {}
        for scan in recent_scans:
            port = scan['port']
            if port not in port_status or scan['timestamp'] > port_status[port]['timestamp']:
                port_status[port] = scan
        
        self.port_table.setRowCount(len(port_status))
        
        for row, (port, scan) in enumerate(port_status.items()):
            self.port_table.setItem(row, 0, QTableWidgetItem(str(port)))
            self.port_table.setItem(row, 1, QTableWidgetItem(self.get_protocol_name(port)))
            
            status_item = QTableWidgetItem(scan['status'])
            status_color = self.status_colors.get(scan['status'], self.status_colors['UNKNOWN'])
            status_item.setBackground(QColor(status_color))
            
            # Set text color for better contrast
            if scan['status'] == 'OPEN':
                status_item.setForeground(QColor('#ffffff'))
            else:
                status_item.setForeground(QColor('#ffffff'))
            
            self.port_table.setItem(row, 2, status_item)
            
            # Format timestamp nicely
            try:
                timestamp = datetime.fromisoformat(scan['timestamp'])
                formatted_time = timestamp.strftime("%m/%d %H:%M:%S")
            except:
                formatted_time = scan['timestamp']
            
            self.port_table.setItem(row, 3, QTableWidgetItem(formatted_time))
        
    def update_statistics(self):
        """Update the 24-hour statistics"""
        stats = self.db_manager.get_24h_statistics()
        
        self.total_scans_label.setText(f"Total Scans: {stats['total_scans']}")
        self.success_rate_label.setText(f"Success Rate: {stats['success_rate']:.1f}%")
        self.blocked_ports_label.setText(f"Blocked Ports: {stats['blocked_ports']}")
        self.avg_response_label.setText(f"Avg Response: {stats['avg_response']:.0f}ms")
        
    def get_protocol_name(self, port):
        """Get protocol name for a port"""
        protocol_map = {
            25: "SMTP", 465: "SMTP SSL", 587: "SMTP TLS",
            110: "POP3", 995: "POP3 SSL",
            143: "IMAP", 993: "IMAP SSL",
            80: "HTTP", 443: "HTTPS"
        }
        return protocol_map.get(port, "Custom")
        
    def add_custom_port(self):
        """Add a custom port to monitor"""
        try:
            port_text = self.custom_port_input.text().strip()
            if not port_text:
                self.on_status_update("Please enter a port number")
                return
                
            port = int(port_text)
            if not (1 <= port <= 65535):
                self.on_status_update("Port must be between 1 and 65535")
                return
                
            if port in self.port_checkboxes:
                self.on_status_update(f"Port {port} is already in the list")
                return
                
            checkbox = QCheckBox(f"{port} (Custom)")
            checkbox.setChecked(True)
            self.port_checkboxes[port] = checkbox
            
            # For now, just add to the internal list - UI would need dynamic layout updates
            self.custom_port_input.clear()
            self.on_status_update(f"Added port {port} to monitoring list")
            
        except ValueError:
            self.on_status_update("Please enter a valid port number")
            
    def save_configuration(self):
        """Save the current configuration"""
        try:
            config = {
                'server': self.server_input.text(),
                'interval': self.interval_input.value(),
                'ports': [port for port, checkbox in self.port_checkboxes.items() if checkbox.isChecked()]
            }
            self.db_manager.save_configuration(config)
            
            # Update the scheduler with new config
            self.update_scheduler_config()
            
            # Update server label
            self.server_label.setText(f"Server: {config['server']}")
            
            self.on_status_update("Configuration saved successfully")
        except Exception as e:
            self.on_status_update(f"Failed to save configuration: {str(e)}")
    
    def update_scheduler_config(self):
        """Update scheduler configuration from UI"""
        try:
            host = self.server_input.text().strip()
            interval = self.interval_input.value()
            ports = [port for port, checkbox in self.port_checkboxes.items() if checkbox.isChecked()]
            
            if not host:
                host = "mail.comcast.net"
            
            if not ports:
                ports = self.port_scanner.get_default_ports()
            
            self.scheduler.update_configuration(host=host, interval=interval, ports=ports)
        except Exception as e:
            print(f"Error updating scheduler config: {e}")
    
    def on_scan_complete(self, results):
        """Callback when scan completes"""
        try:
            # Update the display
            self.update_status_display()
            
            # Update last scan time
            scan_time = datetime.now().strftime("%H:%M:%S")
            self.last_scan_label.setText(f"Last Scan: {scan_time}")
            
            # Count successful scans
            open_ports = len([r for r in results if r['status'] == 'OPEN'])
            total_ports = len(results)
            
            status_msg = f"Scan completed: {open_ports}/{total_ports} ports open"
            self.on_status_update(status_msg)
            
        except Exception as e:
            print(f"Error in scan complete callback: {e}")
    
    def on_status_update(self, message):
        """Callback for status updates"""
        try:
            # Update status bar
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage(message, 5000)  # Show for 5 seconds
                
            # Update status in export log (if visible)
            if hasattr(self, 'export_log'):
                timestamp = datetime.now().strftime("%H:%M:%S")
                self.export_log.append(f"[{timestamp}] {message}")
                
            # Print to console for debugging
            print(f"Status: {message}")
            
        except Exception as e:
            print(f"Error in status update: {e}")
    
    def create_chart_callback(self, time_range):
        """Create a callback function for chart buttons"""
        return lambda: self.update_chart(time_range)
        
    def load_server_config(self):
        """Load server configuration from database"""
        config = self.db_manager.get_configuration()
        if config:
            self.server_input.setText(config.get('server', 'mail.comcast.net'))
            self.interval_input.setValue(config.get('interval', 60))
            
    def update_chart(self, time_range):
        """Update the chart with specified time range"""
        print(f"Updating chart for time range: {time_range}")  # Debug
        self.on_status_update(f"Loading {time_range} chart data...")
        
        self.figure.clear()
        
        # Apply chart styling
        chart_style = get_chart_style()
        plt.rcParams.update(chart_style)
        
        # Set figure background
        self.figure.patch.set_facecolor('#2d3748')
        
        # Get data based on time range
        if time_range == "24 Hours":
            hours = 24
        elif time_range == "7 Days":
            hours = 24 * 7
        elif time_range == "30 Days":
            hours = 24 * 30
        else:
            hours = None
            
        data = self.db_manager.get_chart_data(hours)
        
        if data:
            # Create subplots
            ax1 = self.figure.add_subplot(2, 1, 1)
            ax2 = self.figure.add_subplot(2, 1, 2)
            
            # Set subplot backgrounds
            ax1.set_facecolor('#2d3748')
            ax2.set_facecolor('#2d3748')
            
            # Port availability timeline
            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Define colors for different ports
            port_colors = ['#ff8c00', '#38a169', '#e53e3e', '#3182ce', '#9f7aea', '#ed8936', '#48bb78', '#f56565', '#90cdf4']
            
            for i, port in enumerate(df['port'].unique()):
                port_data = df[df['port'] == port]
                success_rate = port_data.groupby(port_data['timestamp'].dt.hour)['status'].apply(
                    lambda x: (x == 'OPEN').mean() * 100
                )
                color = port_colors[i % len(port_colors)]
                ax1.plot(success_rate.index, success_rate.values, label=f"Port {port}", 
                        marker='o', color=color, linewidth=2, markersize=6)
            
            ax1.set_title('Port Availability Over Time', color='#ffffff', fontsize=12, fontweight='bold')
            ax1.set_xlabel('Hour of Day', color='#ffffff')
            ax1.set_ylabel('Success Rate (%)', color='#ffffff')
            ax1.legend(facecolor='#2d3748', edgecolor='#ff8c00', labelcolor='#ffffff')
            ax1.grid(True, color='#4a5568', alpha=0.3)
            
            # Heatmap of port status by hour
            pivot_data = df.pivot_table(
                values='status', 
                index='port', 
                columns=df['timestamp'].dt.hour,
                aggfunc=lambda x: (x == 'OPEN').mean()
            )
            
            # Custom colormap for our theme
            from matplotlib.colors import LinearSegmentedColormap
            colors = ['#e53e3e', '#ed8936', '#ff8c00', '#38a169']  # Red to Orange to Green
            n_bins = 100
            cmap = LinearSegmentedColormap.from_list('custom', colors, N=n_bins)
            
            im = ax2.imshow(pivot_data.values, cmap=cmap, aspect='auto')
            ax2.set_title('Port Availability Heatmap', color='#ffffff', fontsize=12, fontweight='bold')
            ax2.set_xlabel('Hour of Day', color='#ffffff')
            ax2.set_ylabel('Port', color='#ffffff')
            ax2.set_yticks(range(len(pivot_data.index)))
            ax2.set_yticklabels(pivot_data.index, color='#ffffff')
            ax2.set_xticks(range(0, 24, 4))
            ax2.set_xticklabels([f'{h:02d}:00' for h in range(0, 24, 4)], color='#ffffff')
            
            # Add colorbar with custom styling
            cbar = self.figure.colorbar(im, ax=ax2, label='Success Rate')
            cbar.set_label('Success Rate', color='#ffffff')
            cbar.ax.yaxis.set_tick_params(color='#ffffff')
            cbar.ax.yaxis.set_ticklabels([f'{x:.1f}' for x in cbar.get_ticks()], color='#ffffff')
        
        self.canvas.draw()
        self.on_status_update(f"Chart updated for {time_range}")
        
    def export_csv(self):
        """Export data to CSV"""
        try:
            days = self.export_range.value()
            filename = f"port_monitor_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            self.db_manager.export_to_csv(filename, days)
            self.export_log.append(f"✓ Exported {days} days of data to {filename}")
            self.on_status_update(f"Data exported to {filename}")
        except Exception as e:
            error_msg = f"✗ Export failed: {str(e)}"
            self.export_log.append(error_msg)
            self.on_status_update(error_msg)
            
    def export_pdf(self):
        """Generate PDF report"""
        try:
            days = self.export_range.value()
            filename = f"port_monitor_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            # Generate a text-based report for now (PDF would require additional libraries)
            self.scheduler.export_evidence_report(filename, days)
            self.export_log.append(f"✓ Generated evidence report: {filename}")
            self.on_status_update(f"Evidence report generated: {filename}")
        except Exception as e:
            error_msg = f"✗ Report generation failed: {str(e)}"
            self.export_log.append(error_msg)
            self.on_status_update(error_msg)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Comcast Port Monitor")
    
    # Set application-wide styling
    app.setStyleSheet(get_application_stylesheet())
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 