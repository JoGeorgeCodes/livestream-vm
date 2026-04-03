import sys
if sys.version_info.major < 3:
    raise Exception("Please run with Python3")

# these imports are all included with python including above sys
import argparse
import os
import shutil
import subprocess
import logging
import platform
import time

try:
    info = platform.freedesktop_os_release()
    if info.get('ID') == 'ubuntu':
        print("You are using Ubuntu. This script was designed for Ubuntu, so it should work well for you!")
    else:
        print("Please try to use Ubuntu if you can, but it might work on other Debian-based distros as well. If it is not Debian-based, please quit now. Any non-Debian-based system will not work, including Windows and MacOS\nWaiting 5 seconds...")
        time.sleep(5)
except:
    print("Please try to use Ubuntu if you can, but it might work on other Debian-based distros as well. If it is not Debian-based, please quit now. Any non-Debian-based system will not work, including Windows and MacOS\nWaiting 5 seconds...")
    time.sleep(5)

LOG_LEVEL = logging.DEBUG

STORAGE_DIR = os.path.expanduser("~/.ytvm")
LOG_DIR = os.path.join(STORAGE_DIR, "logs")
FLAG_DIR = os.path.join(STORAGE_DIR, "flags")
VENV_DIR = os.path.join(STORAGE_DIR, "venv")

SETTINGS_DIR = os.path.join(STORAGE_DIR, "settings")
SETTINGS_VM = os.path.join(SETTINGS_DIR, "vm.json")
SETTINGS_ISOS = os.path.join(SETTINGS_DIR, "isos.json")

def install():
    if os.path.exists(os.path.join(FLAG_DIR, "SETUP_COMPLETE")):
        logging.error(f"{STORAGE_DIR} already exists. Please remove it before running setup. Run:")
        logging.error(f"{sys.executable} {sys.argv[0]} --uninstall")
        logging.error(f"If you need to reinstall due to an error, please copy the log files in {STORAGE_DIR}/logs before uninstalling.")
        sys.exit(1)
    
    open(os.path.join(FLAG_DIR, "SETUP_INPROGRESS"), "w").close()

    apt_dependencies = ["libvirt-dev", "pkg-config", "python3-dev"]
    pip_dependencies = ["libvirt-python"]

    os.makedirs(STORAGE_DIR, exist_ok=True)

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

def add_iso():
    logging.info("Adding iso to collection...")
    args.iso = os.path.abspath(args.iso)
    if not os.path.exists(args.iso):
        logging.error(f"Iso file {args.iso} does not exist.")
        sys.exit(1)
    args.name = args.name.strip()
    if not args.name:
        logging.error("Name cannot be empty.")
        sys.exit(1)

def main():
    global storage_exists
    storage_exists = os.path.exists(STORAGE_DIR)

    # these will be needed later
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(FLAG_DIR, exist_ok=True)
    os.makedirs(SETTINGS_DIR, exist_ok=True)
    os.makedirs(SETTINGS_ISOS, exist_ok=True)
    os.makedirs(SETTINGS_VM, exist_ok=True)

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

    parser.add_argument("--install", action="store_true", help="Install and setup necessary dependencies and environment")
    parser.add_argument("--uninstall", action="store_true", help="Uninstall the environment with dependencies and logs")
    parser.add_argument("--memory", type=int, default=4096, help="Amount of memory to allocate to the VM in MB (default: 4096)")
    parser.add_argument("--vcpu", type=int, default=2, help="Number of virtual CPUs to allocate to the VM (default: 2)")

    subparser = parser.add_subparsers(dest="command", help="Available commands")
    add_parser = subparser.add_parser("add", help="Add isos to the collection")

    add_parser.add_argument("--iso", type=str, required=True, help="Path to the iso file to add to the collection")
    add_parser.add_argument("--name", type=str, required=True, help="Human-readable name to give the iso in the collection, used for switching isos")

    global args
    args = parser.parse_args()
    if args.install: install()
    if args.uninstall: uninstall()
    if args.command == "add": add_iso()

    if not storage_exists or os.path.exists(os.path.join(FLAG_DIR, "SETUP_INPROGRESS")):
        logging.info("Please run with the --install flag")
        logging.info(f"{sys.executable} {sys.argv[0]} --install")
        sys.exit(1)
    
    if os.path.abspath(os.path.join(VENV_DIR)) != os.path.abspath(sys.prefix): # check if we're already in our venv, if not, restart the script in it
        logging.info("Restarting with venv at " + os.path.abspath(VENV_DIR))
        venv_executable = os.path.join(VENV_DIR, "bin", "python")
        os.execv(venv_executable, [venv_executable] + sys.argv)

    # 

if __name__ == "__main__":
    main()
else:
    print("Please don't import this file, it's meant to be run as a script.")
    print("Please add the help flag for usage instructions:")
    print("python3 main.py --help")
    sys.exit(1)