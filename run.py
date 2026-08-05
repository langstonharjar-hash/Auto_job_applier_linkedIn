"""
Launcher script for Auto Job Applier LinkedIn.
Opening this file and clicking the ▶ Play button at the top will automatically
use the project's virtual environment (.venv) and launch the application.
"""
import sys
import os
import subprocess

def main():
    workspace_dir = os.path.dirname(os.path.abspath(__file__))
    venv_python = os.path.join(workspace_dir, ".venv", "Scripts", "python.exe")
    
    if not os.path.exists(venv_python):
        venv_python = os.path.join(workspace_dir, ".venv", "bin", "python")

    run_bot_script = os.path.join(workspace_dir, "runAiBot.py")

    # If not running inside .venv, re-execute with .venv python
    if os.path.exists(venv_python) and os.path.abspath(sys.executable) != os.path.abspath(venv_python):
        print(f"--> Automatically launching with virtual environment (.venv)...")
        result = subprocess.run([venv_python, run_bot_script] + sys.argv[1:])
        sys.exit(result.returncode)
    else:
        import runAiBot
        runAiBot.main()

if __name__ == "__main__":
    main()
