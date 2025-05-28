# Comcast Email Port Monitor

A Windows desktop application to monitor email server ports and detect potential ISP blocking.

## 🚀 Quick Start

### Option 1: Download Release (Recommended)
1. Go to the [Releases](../../releases) page
2. Download the latest `ComcastPortMonitor.exe`
3. Double-click to run (no installation required)

### Option 2: Build from Source
```bash
# Clone the repository
git clone https://github.com/yourusername/comcast-port-monitor.git
cd comcast-port-monitor

# Install dependencies
pip install -r requirements.txt

# Run from source
python main.py

# Or build executable
build_exe.bat
```

## 📋 Features

- **Real-time Port Monitoring** - Monitor email ports (25, 110, 143, 465, 587, 993, 995) and web ports (80, 443)
- **Scheduled Scanning** - Automatic hourly scans with randomization to avoid detection
- **Beautiful UI** - Navy blue theme with orange highlights
- **Data Visualization** - Charts showing port availability over time
- **Export Capabilities** - CSV data export and evidence reports for ISP disputes
- **Blocking Detection** - Automatic detection of suspicious port blocking patterns

## 🎯 How to Use

### Dashboard Tab
- **Start Monitoring** - Begin scheduled port scans
- **Stop Monitoring** - Stop scheduled scanning
- **Scan Now** - Perform immediate port scan
- View real-time port status and 24-hour statistics

### Configuration Tab
- **Server Address** - Default: mail.comcast.net
- **Scan Interval** - How often to scan (default: 60 minutes)
- **Port Selection** - Choose which ports to monitor
- **Save Configuration** - Apply and save settings

### History & Charts Tab
- **Time Range Buttons** - View data for 24 hours, 7 days, 30 days, or all time
- **Port Availability Timeline** - Line chart showing success rates over time
- **Availability Heatmap** - Color-coded view of port status by hour

### Export Tab
- **Export to CSV** - Save scan data for analysis
- **Generate Evidence Report** - Create detailed reports for ISP disputes
- **Export Log** - View real-time status messages

## 🔧 Technical Details

### File Structure
```
port tester/
├── dist/
│   └── ComcastPortMonitor.exe    # Standalone executable (69MB)
├── main.py                       # Main application
├── port_scanner.py              # Port scanning functionality
├── database.py                  # SQLite database management
├── scheduler.py                 # Automated monitoring
├── styles.py                    # UI styling
├── run_monitor.bat              # Easy launcher
└── port_monitor.db              # SQLite database (created on first run)
```

### System Requirements
- **Windows 10/11** (64-bit)
- **No Python installation required** for the executable
- **Internet connection** for port scanning

### Database
- Uses SQLite database (`port_monitor.db`)
- Stores scan results, configuration, and statistics
- Automatic cleanup of old data (configurable)

## 🎨 Color Scheme
- **Primary**: Navy Blue (#1e3a5f)
- **Secondary**: Dark Gray (#2d3748)
- **Accent**: Orange (#ff8c00)
- **Text**: White (#ffffff)
- **Status Colors**: Green (open), Red (closed), Orange (timeout), Purple (error)

## 📊 Port Monitoring

### Email Ports
- **25** - SMTP (Simple Mail Transfer Protocol)
- **465** - SMTP over SSL/TLS
- **587** - SMTP with STARTTLS
- **110** - POP3 (Post Office Protocol v3)
- **995** - POP3 over SSL/TLS
- **143** - IMAP (Internet Message Access Protocol)
- **993** - IMAP over SSL/TLS

### Web Ports
- **80** - HTTP (Hypertext Transfer Protocol)
- **443** - HTTPS (HTTP over SSL/TLS)

## 🚨 Blocking Detection

The application automatically detects potential port blocking when:
- 3 or more email ports are simultaneously blocked
- Patterns suggest time-based blocking
- Evidence reports can be generated for ISP disputes

## 📁 Data Export

### CSV Export
- Timestamped scan results
- Port status, response times, error messages
- Configurable date ranges

### Evidence Reports
- Detailed blocking analysis
- Time-based patterns
- Suitable for ISP dispute documentation

## 🔍 Troubleshooting

### Common Issues
1. **Antivirus Warning** - Some antivirus software may flag the executable. This is normal for PyInstaller-generated files.
2. **Firewall Blocking** - Ensure Windows Firewall allows the application to access the network.
3. **No Data in Charts** - Run some scans first to populate the database.

### Debug Mode
Run from command line to see debug output:
```bash
ComcastPortMonitor.exe
```

## 📝 License

This application is provided as-is for monitoring network connectivity. Use responsibly and in accordance with your ISP's terms of service.

## 🤝 Support

For issues or questions, check the console output for error messages and ensure your network connection is working properly. 