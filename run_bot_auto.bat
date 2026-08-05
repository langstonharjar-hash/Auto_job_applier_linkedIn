@echo off
title Auto Job Applier LinkedIn (Auto Mode)
cd /d "%~dp0"
echo Starting Auto Job Applier LinkedIn in Auto Mode (No confirmation, random delays under 30s)...
".venv\Scripts\python.exe" "run.py" --auto
pause
