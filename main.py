# these imports are all included with python
import argparse
import os
import sys
import shutil
import subprocess
import logging
import platform

try:
    info = platform.freedesktop_os_release()
    if info.get('ID') == 'ubuntu':
        print("You are using Ubuntu. This script was designed for Ubuntu, so it should work well for you!")
except:
    print("You must use Ubuntu!")
    sys.exit(1)

if sys.version_info.major < 3:
    raise Exception("Python 3 is required.")

LOG_LEVEL = logging.DEBUG

STORAGE_DIR = os.path.expanduser("~/.ytvm")
LOG_DIR = os.path.join(STORAGE_DIR, "logs")
FLAG_DIR = os.path.join(STORAGE_DIR, "flags")

def setup():
    if os.path.exists(os.path.join(FLAG_DIR, "SETUP_COMPLETE")):
        logging.error(f"{STORAGE_DIR} already exists. Please remove it before running setup. Run:")
        logging.error(f"{sys.executable} {sys.argv[0]} --uninstall")
        logging.error(f"If you need to reinstall due to an error, please copy the log files in {STORAGE_DIR}/logs before uninstalling.")
        sys.exit(1)
    
    open(os.path.join(FLAG_DIR, "SETUP_INPROGRESS"), "w").close()

    apt_dependencies = ["libvirt-dev", "pkg-config", "python3-dev"]
    pip_dependencies = ["libvirt-python"]

    os.makedirs(STORAGE_DIR, exist_ok=True)
    VENV_DIR = os.path.join(STORAGE_DIR, "venv")

    if os.path.abspath(os.path.join(VENV_DIR)) != os.path.abspath(sys.prefix): # check if we're already in our venv, if not, create one and restart the script in it
        logging.info("Creating venv at " + os.path.abspath(VENV_DIR))
        subprocess.run([sys.executable, "-m", "venv", VENV_DIR], check=True)
        logging.info("Restarting with venv at " + os.path.abspath(VENV_DIR))
        venv_executable = os.path.join(VENV_DIR, "bin", "python")
        os.execv(venv_executable, [venv_executable] + sys.argv)

    else:
        logging.info("In our venv, continuing with setup...")
        if apt_dependencies:
            logging.info("Installing dependencies (apt)...")
            logging.info("You may be prompted for your password to install dependencies using sudo apt.")
            for dep in apt_dependencies:
                logging.info(f"Installing {dep} via apt...")
                subprocess.run(["sudo", "apt-get", "install", "-y", dep], check=True)

        if pip_dependencies:
            logging.info("Installing dependencies (pip)...")
            for dep in pip_dependencies:
                logging.info(f"Installing {dep} via pip...")
                subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)

        logging.info("Setup complete.")
        os.remove(os.path.join(FLAG_DIR, "SETUP_INPROGRESS"))
        open(os.path.join(FLAG_DIR, "SETUP_COMPLETE"), "w").close()
        sys.exit(0)

def uninstall():
    logging.info(f"Removing {STORAGE_DIR} directory...")
    if storage_exists:
        shutil.rmtree(STORAGE_DIR)
    else:
        logging.warning(f"{STORAGE_DIR} does not exist, skipping removal.")
    logging.info("Uninstallation complete.")
    sys.exit(0)

def main():
    global storage_exists
    storage_exists = os.path.exists(STORAGE_DIR)

    # these will be needed later
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(FLAG_DIR, exist_ok=True)

    logging.basicConfig( # set up logging
        level=LOG_LEVEL,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(os.path.join(LOG_DIR, "log.log"), mode="a"),
            logging.StreamHandler()
        ]
    )

    logging.info("Started!")
    os.makedirs(LOG_DIR, exist_ok=True)
    
    parser = argparse.ArgumentParser()

    parser.add_argument("--setup", action="store_true", help="Install and setup necessary dependencies and environment")
    parser.add_argument("--uninstall", action="store_true", help="Uninstall the environment with dependencies and logs")

    args = parser.parse_args()

    if args.setup:
        setup()
    if args.uninstall:
        uninstall()
    if not storage_exists or os.path.exists(os.path.join(FLAG_DIR, "SETUP_INPROGRESS")):
        logging.info("Please run with the --setup flag")
        logging.info(f"{sys.executable} {sys.argv[0]} --setup")
        sys.exit(1)
    
    # TODO: add more functionality here, this is just the setup and uninstall code for now

if __name__ == "__main__":
    main()
else:  
    print("Usage: Please add the help flag for usage instructions:")
    print("python3 main.py --help")
    print("Please don't import this file, it's meant to be run as a script.")
    sys.exit(1)