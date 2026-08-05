"""
PyInstaller Build Script for Auto Job Applier LinkedIn
Compiles app_gui.py into a self-contained, standalone Windows executable.
"""

import os
import sys
import shutil
import subprocess

def build():
    workspace_dir = os.path.dirname(os.path.abspath(__file__))
    venv_pyinstaller = os.path.join(workspace_dir, ".venv", "Scripts", "pyinstaller.exe")
    if not os.path.exists(venv_pyinstaller):
        venv_pyinstaller = "pyinstaller"

    print("--> Starting PyInstaller build process for AutoJobApplier...")

    # PyInstaller arguments
    cmd = [
        venv_pyinstaller,
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name=AutoJobApplier",
        "--collect-all=customtkinter",
        "--add-data=config;config",
        "--add-data=modules;modules",
        "--add-data=templates;templates",
        "--add-data=all excels;all excels",
        os.path.join(workspace_dir, "app_gui.py")
    ]

    result = subprocess.run(cmd, cwd=workspace_dir)

    if result.returncode == 0:
        dist_dir = os.path.join(workspace_dir, "dist", "AutoJobApplier")
        print(f"\n[SUCCESS] Standalone package created at: {dist_dir}")

        # Ensure required runtime folders exist inside dist/AutoJobApplier/
        for folder in ["config", "modules", "logs", "all excels", "all resumes"]:
            os.makedirs(os.path.join(dist_dir, folder), exist_ok=True)

        # Create double-click launcher inside dist folder
        launcher_path = os.path.join(dist_dir, "Launch_Auto_Job_Applier.bat")
        with open(launcher_path, "w", encoding="utf-8") as f:
            f.write('@echo off\ncd /d "%~dp0"\nstart "" "AutoJobApplier.exe"\n')

        print(f"[SUCCESS] Created double-click launcher: {launcher_path}")
    else:
        print(f"\n❌ PyInstaller build failed with exit code {result.returncode}")

if __name__ == "__main__":
    build()
