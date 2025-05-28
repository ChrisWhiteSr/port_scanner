"""
Stylesheet Module
Contains the styling for the Comcast Port Monitor application
Navy blue theme with orange and white highlights
"""

def get_application_stylesheet():
    """
    Returns the main application stylesheet with navy blue theme
    """
    return """
    /* Main Application Styling */
    QMainWindow {
        background-color: #1e3a5f;
        color: #ffffff;
    }
    
    /* Central Widget */
    QWidget {
        background-color: #1e3a5f;
        color: #ffffff;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 10pt;
    }
    
    /* Tab Widget */
    QTabWidget::pane {
        border: 2px solid #2c5282;
        background-color: #2d3748;
        border-radius: 8px;
    }
    
    QTabWidget::tab-bar {
        alignment: center;
    }
    
    QTabBar::tab {
        background-color: #2c5282;
        color: #ffffff;
        padding: 12px 20px;
        margin: 2px;
        border-radius: 6px 6px 0px 0px;
        font-weight: bold;
        min-width: 100px;
    }
    
    QTabBar::tab:selected {
        background-color: #ff8c00;
        color: #1e3a5f;
    }
    
    QTabBar::tab:hover {
        background-color: #3182ce;
        color: #ffffff;
    }
    
    /* Group Boxes */
    QGroupBox {
        font-weight: bold;
        font-size: 11pt;
        color: #ffffff;
        border: 2px solid #ff8c00;
        border-radius: 8px;
        margin-top: 10px;
        padding-top: 10px;
        background-color: #2d3748;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 8px 0 8px;
        color: #ff8c00;
        font-weight: bold;
    }
    
    /* Labels */
    QLabel {
        color: #ffffff;
        font-size: 10pt;
    }
    
    /* Buttons */
    QPushButton {
        background-color: #ff8c00;
        color: #1e3a5f;
        border: none;
        padding: 10px 20px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 10pt;
        min-height: 20px;
    }
    
    QPushButton:hover {
        background-color: #ff9500;
    }
    
    QPushButton:pressed {
        background-color: #e67e00;
    }
    
    QPushButton:disabled {
        background-color: #4a5568;
        color: #a0aec0;
    }
    
    /* Special button styling for Start/Stop */
    QPushButton#start_button {
        background-color: #38a169;
        color: #ffffff;
    }
    
    QPushButton#start_button:hover {
        background-color: #48bb78;
    }
    
    QPushButton#stop_button {
        background-color: #e53e3e;
        color: #ffffff;
    }
    
    QPushButton#stop_button:hover {
        background-color: #f56565;
    }
    
    /* Input Fields */
    QLineEdit {
        background-color: #4a5568;
        border: 2px solid #2c5282;
        border-radius: 4px;
        padding: 8px;
        color: #ffffff;
        font-size: 10pt;
    }
    
    QLineEdit:focus {
        border-color: #ff8c00;
        background-color: #2d3748;
    }
    
    QSpinBox {
        background-color: #4a5568;
        border: 2px solid #2c5282;
        border-radius: 4px;
        padding: 8px;
        color: #ffffff;
        font-size: 10pt;
    }
    
    QSpinBox:focus {
        border-color: #ff8c00;
        background-color: #2d3748;
    }
    
    QSpinBox::up-button, QSpinBox::down-button {
        background-color: #ff8c00;
        border: none;
        width: 20px;
        border-radius: 3px;
    }
    
    QSpinBox::up-button:hover, QSpinBox::down-button:hover {
        background-color: #ff9500;
    }
    
    /* Checkboxes */
    QCheckBox {
        color: #ffffff;
        font-size: 10pt;
        spacing: 8px;
    }
    
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        border-radius: 3px;
        border: 2px solid #2c5282;
        background-color: #4a5568;
    }
    
    QCheckBox::indicator:checked {
        background-color: #ff8c00;
        border-color: #ff8c00;
        image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDQuNUw0LjUgOEwxMSAxIiBzdHJva2U9IiMxZTNhNWYiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
    }
    
    QCheckBox::indicator:hover {
        border-color: #ff8c00;
    }
    
    /* Table Widget */
    QTableWidget {
        background-color: #2d3748;
        alternate-background-color: #4a5568;
        border: 2px solid #2c5282;
        border-radius: 6px;
        gridline-color: #2c5282;
        color: #ffffff;
        font-size: 10pt;
    }
    
    QTableWidget::item {
        padding: 8px;
        border-bottom: 1px solid #2c5282;
    }
    
    QTableWidget::item:selected {
        background-color: #ff8c00;
        color: #1e3a5f;
    }
    
    QHeaderView::section {
        background-color: #2c5282;
        color: #ffffff;
        padding: 10px;
        border: none;
        font-weight: bold;
        font-size: 10pt;
    }
    
    QHeaderView::section:hover {
        background-color: #3182ce;
    }
    
    /* Text Edit */
    QTextEdit {
        background-color: #2d3748;
        border: 2px solid #2c5282;
        border-radius: 6px;
        color: #ffffff;
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 9pt;
        padding: 8px;
    }
    
    QTextEdit:focus {
        border-color: #ff8c00;
    }
    
    /* Scroll Bars */
    QScrollBar:vertical {
        background-color: #2d3748;
        width: 12px;
        border-radius: 6px;
    }
    
    QScrollBar::handle:vertical {
        background-color: #ff8c00;
        border-radius: 6px;
        min-height: 20px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #ff9500;
    }
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        border: none;
        background: none;
    }
    
    QScrollBar:horizontal {
        background-color: #2d3748;
        height: 12px;
        border-radius: 6px;
    }
    
    QScrollBar::handle:horizontal {
        background-color: #ff8c00;
        border-radius: 6px;
        min-width: 20px;
    }
    
    QScrollBar::handle:horizontal:hover {
        background-color: #ff9500;
    }
    
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        border: none;
        background: none;
    }
    
    /* Status Labels with Special Colors */
    QLabel#monitoring_status {
        font-size: 14pt;
        font-weight: bold;
        color: #ff8c00;
        padding: 5px;
    }
    
    QLabel#server_label {
        color: #90cdf4;
        font-weight: bold;
    }
    
    /* Progress Bar (if needed) */
    QProgressBar {
        border: 2px solid #2c5282;
        border-radius: 6px;
        background-color: #2d3748;
        text-align: center;
        color: #ffffff;
        font-weight: bold;
    }
    
    QProgressBar::chunk {
        background-color: #ff8c00;
        border-radius: 4px;
    }
    
    /* Tooltips */
    QToolTip {
        background-color: #1e3a5f;
        color: #ffffff;
        border: 2px solid #ff8c00;
        border-radius: 4px;
        padding: 8px;
        font-size: 9pt;
    }
    
    /* Menu Bar (if added later) */
    QMenuBar {
        background-color: #1e3a5f;
        color: #ffffff;
        border-bottom: 2px solid #2c5282;
    }
    
    QMenuBar::item {
        background-color: transparent;
        padding: 8px 12px;
    }
    
    QMenuBar::item:selected {
        background-color: #ff8c00;
        color: #1e3a5f;
    }
    
    /* Status Bar (if added later) */
    QStatusBar {
        background-color: #2c5282;
        color: #ffffff;
        border-top: 1px solid #ff8c00;
    }
    """

def get_chart_style():
    """
    Returns matplotlib styling for charts to match the application theme
    """
    return {
        'figure.facecolor': '#2d3748',
        'axes.facecolor': '#2d3748',
        'axes.edgecolor': '#ff8c00',
        'axes.labelcolor': '#ffffff',
        'axes.axisbelow': True,
        'axes.grid': True,
        'axes.spines.left': True,
        'axes.spines.bottom': True,
        'axes.spines.top': False,
        'axes.spines.right': False,
        'xtick.color': '#ffffff',
        'ytick.color': '#ffffff',
        'grid.color': '#4a5568',
        'grid.linestyle': '-',
        'grid.linewidth': 0.5,
        'text.color': '#ffffff',
        'font.size': 10,
        'legend.facecolor': '#2d3748',
        'legend.edgecolor': '#ff8c00',
        'legend.fontsize': 9
    }

def get_port_status_colors():
    """
    Returns color mapping for port status indicators
    """
    return {
        'OPEN': '#38a169',      # Green
        'CLOSED': '#e53e3e',    # Red  
        'TIMEOUT': '#ed8936',   # Orange
        'ERROR': '#9f7aea',     # Purple
        'UNKNOWN': '#4a5568'    # Gray
    } 