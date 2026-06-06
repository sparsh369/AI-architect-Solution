"""
Convenience launcher.

    python run.py            # launch the Streamlit UI (default)
    python run.py ui         # same as above
    python run.py api        # launch the FastAPI backend on :8000

The Streamlit UI is fully self-contained — it calls the agent pipeline
directly and does NOT require the API to be running.
"""
import subprocess
import sys


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "ui"

    if target == "api":
        cmd = [sys.executable, "-m", "uvicorn", "backend.main:app",
               "--reload", "--port", "8000"]
    else:  # ui
        cmd = [sys.executable, "-m", "streamlit", "run", "app.py"]

    print("Launching:", " ".join(cmd))
    subprocess.run(cmd)


if __name__ == "__main__":
    main()
