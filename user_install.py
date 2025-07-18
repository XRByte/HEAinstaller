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
    os.environ["PIP_CMD"] = f"{pip_path} install"
    activate_scripts = [os.path.join(env_dir, "bin", "activate"), os.path.join(env_dir, "bin", "activate.csh")]

if not os.path.exists(python_path):
    builder = venv.EnvBuilder(with_pip=True)
    builder.create(env_dir)

packages = ["tqdm"]

try:
    subprocess.check_call([pip_path, "install"] + packages)
except subprocess.CalledProcessError:
    print(f"Unable to install {', '.join(packages)}. Please proceed manually.")
    sys.exit()
    
shell = os.environ.get("SHELL", "bash")
for activate in activate_scripts:
    try:
        print([shell, "-c", f"'source {activate}'", "&&", "python3", "heainstaller.py"])
        subprocess.run([shell, "-c", f"source {activate}  && python3 heainstaller.py"], check=True )
        break
    except:
        print(f"Unable to activate venv or run script. Exiting")
        sys.exit()
