# GitHub Setup Guide

## 📋 Repository Setup

### 1. Create GitHub Repository
1. Go to [GitHub](https://github.com) and sign in
2. Click "New repository" or go to https://github.com/new
3. Repository settings:
   - **Name**: `comcast-port-monitor`
   - **Description**: `Windows desktop application for monitoring email server ports and detecting ISP blocking`
   - **Visibility**: Public (or Private if preferred)
   - **Initialize**: Don't initialize with README (we already have one)

### 2. Connect Local Repository
```bash
# Add GitHub remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/comcast-port-monitor.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### 3. Repository Topics (Optional)
Add these topics to your repository for better discoverability:
- `python`
- `pyqt6`
- `port-scanner`
- `network-monitoring`
- `email-server`
- `isp-blocking`
- `windows-desktop`
- `gui-application`

## 🚀 Creating Releases

### 1. Build the Executable
```bash
# Run the build script
build_exe.bat

# This creates: dist/ComcastPortMonitor.exe (69MB)
```

### 2. Create GitHub Release
1. Go to your repository on GitHub
2. Click "Releases" → "Create a new release"
3. Release settings:
   - **Tag**: `v1.0.0`
   - **Title**: `Comcast Port Monitor v1.0.0`
   - **Description**:
     ```
     ## 🎉 Initial Release
     
     Complete Windows desktop application for monitoring email server ports and detecting potential ISP blocking.
     
     ### ✨ Features
     - Real-time port monitoring with beautiful navy blue UI
     - Automated scheduled scanning with randomization
     - Data visualization with charts and heatmaps
     - CSV export and evidence report generation
     - Protocol-specific testing (SMTP, POP3, IMAP, HTTP/HTTPS)
     - Blocking pattern detection and alerting
     
     ### 📥 Download
     - **ComcastPortMonitor.exe** - Standalone executable (no installation required)
     - **Source code** - For developers who want to build from source
     
     ### 💻 System Requirements
     - Windows 10/11 (64-bit)
     - Internet connection for port scanning
     - No Python installation required for the executable
     
     ### 🚀 Quick Start
     1. Download `ComcastPortMonitor.exe`
     2. Double-click to run
     3. Click "Scan Now" to test connectivity
     4. Use "Start Monitoring" for continuous monitoring
     ```

### 3. Upload Executable
1. Drag and drop `dist/ComcastPortMonitor.exe` to the release assets
2. The file will be uploaded (may take a few minutes due to 69MB size)
3. Click "Publish release"

## 📁 File Structure for GitHub

```
comcast-port-monitor/
├── .gitignore              # Excludes large files and build artifacts
├── README.md               # Main documentation
├── requirements.txt        # Python dependencies
├── build_exe.bat          # Build script for creating executable
├── run_monitor.bat        # Easy launcher script
├── main.py                # Main application entry point
├── port_scanner.py        # Port scanning functionality
├── database.py            # SQLite database management
├── scheduler.py           # Automated monitoring scheduler
└── styles.py              # UI styling and themes
```

## 🔧 For Contributors

### Development Setup
```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/comcast-port-monitor.git
cd comcast-port-monitor

# Install dependencies
pip install -r requirements.txt

# Run from source
python main.py

# Build executable
build_exe.bat
```

### Making Changes
1. Create feature branch: `git checkout -b feature-name`
2. Make changes and test
3. Commit: `git commit -m "Description of changes"`
4. Push: `git push origin feature-name`
5. Create Pull Request on GitHub

## 📊 Repository Statistics

- **Language**: Python (PyQt6)
- **Size**: ~50KB source code (excluding executable)
- **Dependencies**: 6 main packages
- **Executable Size**: 69MB (includes all dependencies)
- **Target Platform**: Windows 10/11

## 🏷️ Suggested Labels

Create these labels in your GitHub repository:
- `bug` - Something isn't working
- `enhancement` - New feature or request
- `documentation` - Improvements or additions to docs
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention is needed
- `ui/ux` - User interface and experience
- `performance` - Performance improvements
- `security` - Security-related issues

## 📈 GitHub Actions (Optional)

You can set up automated builds with GitHub Actions by creating `.github/workflows/build.yml`:

```yaml
name: Build Executable

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: pip install -r requirements.txt
    
    - name: Build executable
      run: python -m PyInstaller --onefile --windowed --name "ComcastPortMonitor" main.py
    
    - name: Upload artifact
      uses: actions/upload-artifact@v3
      with:
        name: ComcastPortMonitor
        path: dist/ComcastPortMonitor.exe
```

This will automatically build the executable when you create a new release tag. 