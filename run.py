import os
import sys
import subprocess

# List of required packages
REQUIRED_PACKAGES = [
    "streamlit",
    "supabase",
    "sentence-transformers",
    "textblob",
    "python-dotenv",
    "requests"
]

def install_packages():
    for package in REQUIRED_PACKAGES:
        try:
            __import__(package)
        except ImportError:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def run_app():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py", "--server.fileWatcherType", "none"])

if __name__ == "__main__":
    print("Checking dependencies...")
    install_packages()
    print("Starting CogniChat...")
    run_app()