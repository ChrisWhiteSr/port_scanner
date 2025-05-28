@echo off
echo Starting Comcast Port Monitor...
cd /d "%~dp0"
start "" "dist\ComcastPortMonitor.exe"
echo Port Monitor started!
pause 