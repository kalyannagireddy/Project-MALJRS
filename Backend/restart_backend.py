import os
import signal
import subprocess
import time
import sys

def restart_backend():
    print("🔄 Finding running backend process...")
    try:
        # Find process using port 8000
        result = subprocess.check_output("netstat -ano | findstr :8000", shell=True).decode()
        if result:
            lines = result.strip().split('\n')
            for line in lines:
                if "LISTENING" in line:
                    parts = line.split()
                    pid = parts[-1]
                    print(f"⚠️  Killing existing backend process (PID: {pid})...")
                    subprocess.run(f"taskkill /F /PID {pid}", shell=True)
                    time.sleep(2)
    except subprocess.CalledProcessError:
        print("✅ No existing backend process found on port 8000.")

    print("\n🚀 Starting Backend with new configuration...")
    # Start backend in a new independent process 
    # using shell=True and creationflags to detach might be needed but simple Popen is usually enough for test scripts
    # However, to keep it running for the user, we should probably just notify them to restart it, 
    # OR start it in background. 
    # Since I cannot easily "replace" the user's running terminal content, 
    # I will just kill it and let the user know, OR start a background one for testing.
    # actually, the user said "Run terminal commands: python -m uvicorn api.app:app ...".
    # I can't restart THAT specific terminal.
    # But I can kill it and start a new one, or just ask the user to restart.
    # BUT, I need to verify it WORKS. So I will start a temporary background process for testing.
    
    env = os.environ.copy()
    # Force reload env vars in the subprocess by not inheriting everything blindly or just relying on .env loading in app
    
    print("⏳ Starting uvicorn...")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd=r"c:\Users\sains\OneDrive\Desktop\Project-MALJRS\Backend",
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    print("Waiting for startup...")
    time.sleep(10)
    if proc.poll() is None:
        print("✅ Backend started successfully (PID: {})".format(proc.pid))
    else:
        print("❌ Backend failed to start.")
        print(proc.stderr.read().decode())

if __name__ == "__main__":
    restart_backend()
