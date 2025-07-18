import os
import sys
import subprocess
import venv

env_dir = os.path.join(os.path.dirname(__file__), ".temp_env")

if os.name == "nt":
    print("Installer is not compatible with Windows! Exiting...")
    sys.exit()
else:
    pip_path = os.path.join(env_dir, "bin", "pip")
    python_path = os.path.join(env_dir, "bin", "python")

if not os.path.exists(python_path):
    builder = venv.EnvBuilder(with_pip=True)
    builder.create(env_dir)

packages = ["tqdm"]

try:
    subprocess.check_call([pip_path, "install"] + packages)
except subprocess.CalledProcessError:
    print(f"Unable to install {', '.join(packages)}. Please proceed manually.")
    
try:
    subprocess.check_call([python_path, "heainstaller.py"])
except subprocess.CalledProcessError:
    print("Unable to run heainstaller.py. Please run the script manually")
