# these imports are all included with python
import argparse
import os
import sys
import shutil
import subprocess

STORAGE_DIR = "~/.ytvm"
VENV_DIR = os.path.join(STORAGE_DIR, "venv")

pip_dependencies = ["libvirt"]
apt_dependencies = []

def setup():
    shutil.rmtree("~/.ytvm", ignore_errors=True)
    os.mkdir("~/.ytvm", exist_ok=True)

    for dep in pip_dependencies:
        cmd = [sys.executable, "-m", "pip", "install", dep]
        subprocess.run(cmd, check=True) 
    

def uninstall():
    shutil.rmtree("~/.ytvm")

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--setup", action="store_true", help="Set up the environment for ytvm")
    parser.add_argument("--uninstall", action="store_true", help="Uninstall the environment for ytvm")

    args = parser.parse_args()

    if args.setup:
        setup()
    elif args.uninstall:
        uninstall()
    else:
        if not os.path.exists("~/.ytvm"):
            print("Please run with the --setup flag")
            print("python3 main.py --setup")
            sys.exit(1)

        print("Attempting to start VM")

            
if __name__ == "__main__":
    main()
else:  
    print("Usage: python3 main.py [options]")
    print("Please don't import this file, it's meant to be run as a script.")
    sys.exit(1)