import subprocess
import os
import sys
import time
import webbrowser

def start_aurasnap():
    # Get the absolute path of the current directory
    root_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(root_dir, "aurasnap-ui")

    # Determine paths based on OS
    if os.name == 'nt':  # Windows
        venv_path = os.path.join(root_dir, "venv")
        venv_scripts = os.path.join(venv_path, "Scripts")
        python_exe = os.path.join(venv_scripts, "python.exe")
        npm_cmd = "npm.cmd"
        path_sep = ";"
    else:  # Unix/Linux/Mac
        venv_path = os.path.join(root_dir, "venv")
        venv_scripts = os.path.join(venv_path, "bin")
        python_exe = os.path.join(venv_scripts, "python")
        npm_cmd = "npm"
        path_sep = ":"

    # Check if we are already running in the venv
    if sys.executable != python_exe and os.path.exists(python_exe):
        print(f"Re-launching script inside virtual environment...")
        # Add venv/Scripts to PATH so sub-commands find the right tools
        os.environ["PATH"] = venv_scripts + path_sep + os.environ.get("PATH", "")
        os.environ["VIRTUAL_ENV"] = venv_path
        
        # Re-execute the script using the venv python
        try:
            subprocess.run([python_exe] + sys.argv)
        except KeyboardInterrupt:
            pass  # Ctrl+C from inner process is expected, suppress traceback
        return

    print("\nStarting AuraSnap v2.0 (Environment Activated)...")

    # 1. Start Python Backend (FastAPI)
    print("Launching Backend API (api.py)...")
    # Using the current sys.executable since we re-launched in venv
    backend_process = subprocess.Popen(
        [sys.executable, os.path.join(root_dir, "backend", "api.py")],
        cwd=os.path.join(root_dir, "backend"),
        env=os.environ.copy()
    )

    # 2. Start Frontend (Vite)
    print("Launching Frontend (npm run dev)...")
    frontend_process = subprocess.Popen(
        [npm_cmd, "run", "dev"],
        cwd=frontend_dir,
        shell=(os.name == 'nt'),
        env=os.environ.copy()
    )

    # 3. Wait and Open Browser
    time.sleep(4)
    print("\nServices are initializing.")
    print("Opening: http://localhost:5173")
    webbrowser.open("http://localhost:5173")

    print("\nPress Ctrl+C to stop both services.")

    try:
        while True:
            if backend_process.poll() is not None:
                print("Backend process terminated.")
                break
            if frontend_process.poll() is not None:
                print("Frontend process terminated.")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping AuraSnap...")
        backend_process.terminate()
        frontend_process.terminate()
        print("Done.")

if __name__ == "__main__":
    start_aurasnap()
