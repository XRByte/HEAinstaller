"""
Script Name: heainstaller.py
Description: 
    The script downloads and installs HEASoft for the current user.
    The heasoft installation packages can be configured from user.json
    It is recommended to have an active virtual or conda environment

Usage: 
    python3 heainstaller.py

Dependencies:
    - Python >= 3.8
    - Required libraries: tqdm

Author: XRByte
Email: sarkar.anish.1001@gmail.com
Date Created: 26-01-2025
Last Modified: 18-07-2025
Version: 2.25.07

Notes:
    Progress bars used are approximate measures of progress

"""

import os
import sys
import shutil
import platform
import subprocess
import tarfile
import glob
import stat
import time
import json
import readline
try:
    from tqdm import tqdm
except ImportError:
    print("tqdm not installed. Please install tqdm before proceeding.")
    sys.exit()


class Heainstall:
    def __init__(self):
        """Initializes a HeaInstaller object with system and configuration details.

        Attributes:
            platform (str): The name of the operating system.
            version (str): The version of the operating system.
            architecture (str): The machine architecture.
            script_dir (str): Directory from which heainstaller.py is run.
            set_flags (list): Flags to be set during installation.
            unset_flags (list): Flags to be unset during installation.
            positive (list): Supported positive responses from the user.
            negative (list): Supported negative responses from the user.
            def_shell (str): The default shell used by the system.
            shell_ext (str): The shell extension.
            shell_config (list): The path to the shell configuration files.
            shell_env (str): The command to configure the shell environment.
            shell_alias (str): The alias command for the shell being used.
            shell_src (str): The command to source a file.
            initializer (list): The initial command for setting up the environment based on the platform.
            compilers (list): A list of compilers required for heasoft installation.
            pm (str): The package manager being used.
            pm_update (list): The command to update the package manager.
            pm_upgrade (list): The command to upgrade packages.
            pm_packages (list): A list of necessary packages.
            pm_incmd (list): The command to install packages using the package manager.
            pm_link (str): The link modifier to send system metadata to heasoft server.
            py_lib (list): The list of Python libraries required for installation.
            py_incmd (list): The command to install Python libraries using the appropriate manager.
            url (str): The URL template for downloading HEAsoft source code.
            home_dir (str): The home directory of the user.
            hea_dir (str): The directory where HEAsoft will be installed.
            download (bool): A flag to indicate whether downloading is enabled (default is True).
            total_size (int): The total size of the file to be downloaded (in bytes).
            tcl_valid (int): The tclreadline installed flag.
            hea_file (str): The name of the HEAsoft tarball file to be downloaded."""

        # Loads system information
        self.platform = platform.system().lower()
        self.version = platform.release()
        self.architecture = platform.machine()
        self.script_dir = os.path.dirname(os.path.realpath(__file__))

        # Reads installation configuration files
        try:
            with open(
                os.path.join(self.script_dir, "config.json"), "r", encoding="utf-8"
            ) as fl:
                config = json.load(fl)
        except FileNotFoundError as e:
            print(f"config.json not found at {os.getcwd()}\nError: {e}")

        # Sets configuration variables
        if self.platform in config.keys():
            self.set_flags = config["set_flags"]
            self.unset_flags = config["unset_flags"]
            self.positive = config["positive_resp"]
            self.negative = config["negative_resp"]
            pacman_counter = 0
            shell = os.path.basename(os.environ.get("SHELL", ""))

            # Checks for valid shell and sets shell configuration variables
            if shell in config["shell"].keys():
                self.def_shell = shell
                self.shell_ext = config["shell"][shell]["extension"]
                self.shell_config = config["shell"][shell]["config_file"]
                self.shell_env = config["shell"][shell]["env_cmd"]
                self.shell_alias = config["shell"][shell]["alias"]
                self.shell_src = config["shell"][shell]["source"]
            else:
                print(
                    "No supported shell found for running heasoft.\n"
                    f"Supported shells: {config['shell'].keys()}\nHeasoft initialization"
                    f"lines will not be present in {shell}. Please add them manually to"
                    "a compatible shell"
                )

            # Gets necessary dependancy & package manager information
            ops = config[self.platform]
            self.compilers = ops["compilers"]

            # Checks for valid a package manager
            for pacman in ops["package_manager"].keys():
                if shutil.which(pacman):
                    self.pm = pacman
                    pacman_counter += 1
                    break
            if not pacman_counter:
                print(
                    "No supported package managers found\n"
                    f"Supported package managers: {ops['package-managers']}\nExiting..."
                )
                sys.exit()

            # Sets package manager specific commands and dependency variables
            pm = ops["package_manager"][self.pm]
            self.initializer = pm.get("initializer")
            self.pm_update = pm["update"].split()
            self.pm_upgrade = pm["upgrade"].split()
            self.pm_packages = pm["packages"]
            self.pm_incmd = pm["install_cmd"].split()
            self.pm_link = pm["link"]

            # Checks for an active python environment
            if os.environ.get("CONDA_PREFIX"):
                py_pm = ops["py_manager"]["conda"]
            else:
                py_pm = ops["py_manager"]["pip"]

            # Loads python libraries and installation commands
            self.py_lib = py_pm["libraries"]
            self.py_incmd = py_pm["install_cmd"].split()
        else:
            print(f"Incompatible OS: {self.platform}\nExiting...")
            sys.exit()

        # Sets dwonload url
        url = "https://heasarc.gsfc.nasa.gov/cgi-bin/Tools/tarit/tarit.pl?mode=download&arch=src&src_{}=Y&\
        src_other_specify="
        self.url = url.format(self.pm_link)

        # Loads user configuration
        with open(
            os.path.join(self.script_dir, "user.json"), "r", encoding="utf-8"
        ) as fl:
            u_config = json.load(fl)

        # Sets user configuration
        for param in ("mission", "general", "xanadu", "xstar"):
            keys = self.__get_keys(u_config[param], "yes")
            if keys:
                for key in keys:
                    self.url += f"&{param}={config[param][key]}"

        # Sets some other necessary variables
        self.home_dir = os.path.expandvars("$HOME")
        self.hea_dir = os.path.join(self.home_dir, ".local", "bin", "heasoft")
        self.download_dir = os.path.join(self.home_dir, ".cache")
        self.download = True
        self.total_size = 4_333_973_837
        self.hea_file = "heasoft.tar.gz"

        # Makes heasoft installation directory if not present
        os.makedirs(self.hea_dir, exist_ok=True)
        os.chdir(self.hea_dir)

        # Initializes log files
        for file in (
            "installer.log",
            "error.log",
            "config.log",
            "build.log",
            "config.log",
        ):
            with open(file, "w", encoding="utf-8") as f:
                f.write("Initializing")

        print(f"OS: {self.platform}")
        print(f"Kernel version: {self.version}")
        print(f"Architecture: {self.architecture}\n")

    def update_packages(self) -> None:
        """Updates package manager and system packages"""

        # Updates package manager

        self.__run_pipeloader(
            "installer.log",
            f"Updating {self.pm}",
            *self.pm_update,
        )

        # Updates system packages
        self.__run_pipeloader(
            "installer.log",
            "Updating system packages",
            *self.pm_upgrade,
        )

        return

    def install_dependencies(self) -> None:
        """Installs dependencies"""

        # Runs extra setup commands
        if self.initializer:
            self.__run_pipeloader(
                "installer.log",
                "Installing extra dependencies",
                *self.initializer.split(),
                stdout=sys.stdout,
            )

        # Installs system package dependencies
        for package in self.pm_packages:
            self.__run_pipeloader(
                "installer.log",
                f"Installing {package.split()[-1]}",
                *self.pm_incmd,
                *package.split(),
            )

        # Install python library dependencies
        self.py_incmd = os.environ.get("PIP_CMD", " ".join(self.py_incmd))
        for py_lib in self.py_lib:
            self.__run_pipeloader(
                "installer.log",
                f"Installing {py_lib.split()[0]}",
                *self.py_incmd.split(),
                *py_lib.split(),
            )
        print("\nAll dependencies installed")

        return

    def config_environ(self) -> None:
        """Sets environment variables required for installation"""

        # Sets compiler flags
        sys.stdout.write("Configuring environment")
        for flag, compiler in zip(self.set_flags, self.compilers):
            os.environ[flag] = shutil.which(compiler)
            if not os.environ[flag]:
                print(f"{compiler} compiler not found\nExiting")
                sys.exit()

        # Unsets library flags
        for u_flag in self.unset_flags:
            os.environ.pop(u_flag, None)
        path = os.path.expandvars("$PATH")

        # Updates path
        os.environ["PATH"] = f"/usr/bin:{path}"
        sys.stdout.write("\rConfiguring environment: Completed successfully\n")

        return

    def check_download(self) -> None:
        """Checks if heasoft is already downloaded"""

        # Checks for valid user response
        while True:
            response = (
                input("\nDo you already have heasoft downloaded? [y/n]: ")
                .strip()
                .lower()
            )
            if response in self.positive:
                self.download = False

                # Checks for correct downloaded file path and copies file to heasoft installation directory if found
                while True:
                    file = input(
                        "Enter absolute path to the download heasoft file: "
                    ).strip()
                    file = glob.glob(os.path.expanduser(os.path.expandvars(file)))[-1]
                    if os.path.exists(file):
                        self.hea_file = file
                        break
                    else:
                        print("Invalid path. Please try again.\n")

                break
            elif response in self.negative:
                break
            else:
                print("Invalid input. Please try again.\n")

        return

    def download_heasoft(self) -> None:
        """Downloads heasoft tarball"""

        if self.download:
            os.makedirs(self.download_dir, exist_ok=True)
            
            # Checks if file already exists
            file = self.hea_file
            if os.path.exists(os.path.join(self.download_dir, file)):
                os.remove(os.path.join(self.download_dir, file))

            # Downloads file
            print(
                "Proceeding to download heasoft\nThis might take more than 2 hours..."
            )
            self.__run_pipeline(
                self.total_size,
                "installer.log",
                os.path.join(self.download_dir, file),
                "Downloading",
                1,
                "Download",
                "file_size",
                "B",
                "aria2c",
                "-d",
                self.download_dir,
                "-q",
                "--log-level=error",
                "-x",
                "16",
                "-s",
                "16",
                "-c",
                self.url,
                "-o",
                file,
            )

        return

    def extract_targz(self, file: str) -> None:
        """Extracts tarball

        Args:
            file (str): file path
        """

        try:
            print("Initializing extraction")
            with tarfile.open(file) as f:
                members = f.getmembers()
                total = len(members)

                # Progress bar
                with tqdm(
                    total=total, desc="Extracting", unit=" files", leave=True
                ) as pbar:
                    for member in members:
                        try:
                            f.extract(member, filter="fully_trusted")
                        except TypeError:
                            f.extract(member)
                        pbar.update(1)
        except FileNotFoundError as e:
            print(f"Error encountered while extracting files: {e}")
            sys.exit()

        return

    def configure(self) -> None:
        """Configures heasoft installation"""

        # Changes file mode to read, write and execute
        os.chmod("configure", stat.S_IRWXU)

        # Runs configuration
        print("Configuring\nThis will take a few minutes ...")
        config_file = os.path.join(self.hea_dir, "config.log")
        self.__run_pipeline(
            3_146,
            config_file,
            config_file,
            "Configuring",
            0.1,
            "Configuration",
            "line_number",
            " ln",
            "./configure",
            "--without-lynx",
        )

        return

    def compile(self) -> None:
        """Compiles necessary files required for instaallation"""

        print("Compiling\nThis may take a few hours ...")
        build_file = os.path.join(self.hea_dir, "build.log")
        self.__run_pipeline(
            78_975,
            build_file,
            build_file,
            "Compiling",
            2,
            "Compilation",
            "line_number",
            " ln",
            "make",
        )

        return

    def install(self) -> None:
        """Installs compiled file"""

        print("Installing\nThis may take an hour ...")
        ins_file = os.path.join(self.hea_dir, "install.log")
        self.__run_pipeline(
            64_075,
            ins_file,
            ins_file,
            "Installing",
            0.5,
            "Installation",
            "line_number",
            " ln",
            "make",
            "install",
        )

        return

    def configure_shell(self) -> None:
        """Configures non-login/login shell to initialize with heainit command"""

        installdir = os.getcwd()
        config = 0

        # Loops through each specified shell initialization file
        for conf in self.shell_config:
            path = os.path.expandvars(os.path.join(*conf.split()))

            # Checks if shell configuration file is present and writes to file if present
            if os.path.exists(path):
                self.__write_script(path, installdir)
                config += 1
                break

        # Creates login configuration file if not present and writes there
        if not config:
            path = os.path.expandvars(os.path.join(*self.shell_config[-1].split()))
            os.makedirs(os.path.dirname(path), exist_ok=True)
            self.__write_script(path, installdir)
            print(
                f"\n{path} was not found. "
                f"{os.path.basename(path)} has been created and can be "
                f"found at {os.path.dirname(path)}. Make sure that {os.path.basename(path)} "
                f"is read by {self.def_shell} before execution"
            )

        return

    def test_installation(self) -> None:
        """Tests the successful installation of heasoft"""

        # Gets installation directory
        installdir = os.getcwd()
        if not os.path.exists(
            os.path.join(installdir, f"headas-init.{self.shell_ext}")
        ):
            print("Heasoft installation unsuccessful!")
            sys.exit()

        # Sets HEADAS environment variable
        os.environ["HEADAS"] = f"{installdir}"

        # Sets heasoft initialization file directory
        script_dir = os.path.join("$HEADAS", f"headas-init.{self.shell_ext}")
        readfl = self.shell_src.format(script_dir)

        # Runs fversion
        print("Heasoft version: ", end="", flush=True)
        self.__run_subprocess(
            f'$SHELL -i -c "{readfl} && fversion"', stdout=sys.stdout, shell=True
        )

        return

    def run(self) -> None:
        """Runs setup"""
            
        os.chdir(self.hea_dir)

        # Runs instructions
        self.update_packages()
        self.install_dependencies()
        self.config_environ()
        self.check_download()
        self.download_heasoft()
        download_file = os.path.join(self.home_dir, ".cache", self.hea_file)
        if not self.download:
            download_file = os.path.join(self.hea_file)
            
        self.extract_targz(download_file)

        # Checks for heasoft download directory
        try:
            base = [
                name
                for name in glob.glob("heasoft-[0-9].[0-9][0-9]*")
                if os.path.isdir(name)
            ][-1]
        except IndexError:
            print("\nHeasoft folder not found\nExiting ...")
            sys.exit()

        # Changes to heasoft build directory
        os.chdir(os.path.join(base, "BUILD_DIR"))
        self.configure()
        self.compile()
        self.install()

        # Changes to heasoft installation directory
        os.chdir(os.path.dirname(os.getcwd()))
        (install_dir,) = glob.glob(f"{self.architecture}-*")
        os.chdir(install_dir)
        self.configure_shell()
        self.test_installation()

        return

    def __get_keys(self, _dict: dict, val: str) -> list:
        """Gets dictionaty keys containing a particular value

        Args:
            _dict (dict): Dictionary to be checked
            val (str): value to be checked for

        Returns:
            list: Keys containing value
        """
        keys = [key for key, value in _dict.items() if value == val]

        return keys

    def __write_script(self, file: str, ins_dir: str) -> None:
        """Writes configuration information to non-login/login shell configuration file

        Args:
            file (str): file path
            ins_dir (str): heasoft installation path containing headas-init script
        """

        script_dir = os.path.join("$HEADAS", f"headas-init.{self.shell_ext}")

        # headas-init file read command
        readfl = self.shell_src.format(script_dir)

        # Set heainit command
        cmd = self.shell_alias.format(readfl)

        # Configures shell if file is found
        try:
            with open(file, "a", encoding="utf-8") as script:
                script.write("\n\n#heasoft initialization\n")
                script.write(f"{self.shell_env}\n".format(ins_dir))
                script.write(f"{cmd}\n")
        except FileNotFoundError as e:
            print(f"Unable to find {file}:\n{e}")

        return

    def __run_subprocess(self, *args, **kwargs) -> None:
        """Runs a subprocess with exception handelling and logging"""

        try:
            with open("installer.log", "a", encoding="utf-8") as outfile:
                with open("error.log", "a", encoding="utf-8") as errfile:
                    kwargs.setdefault("stdout", outfile)
                    kwargs.setdefault("stderr", errfile)
                    kwargs.setdefault("text", True)
                    result = subprocess.run(args, **kwargs, check=True)
            if not result.returncode == 0:
                print(f"Error executing {args}: {result.stderr}")
                sys.exit()
        except Exception as e:
            print(f"An error occurred: {e}")
            self.__write_errlog(e)

        return

    def __run_pipeline(
        self,
        total: int,
        output_file: str,
        file: str,
        proc: str,
        update_diff: float,
        message: str,
        loader: str,
        unit: str,
        *args,
        **kwargs,
    ) -> None:
        """Runs a subprocess with progress bar

        Args:
            total (int): Total number of units to be processed
            output_file (str): Path to log file
            file (str): File to be processed
            proc (str): Process description
            update_diff (float): Progress bar update interval
            message (str): Success message
            loader (str): Progress bar configuraton. Can be line_number/file_size
            unit (str): Progress unit

        Returns:
            None: None
        """

        processes = {
            "line_number": self.__track_lines,
            "file_size": self.__track_download,
        }
        error_file = os.path.join(self.hea_dir, "error.log")

        # Runs process with logging
        with open(output_file, "a", encoding="utf-8") as out_file:
            with open(error_file, "a", encoding="utf-8") as err_file:
                kwargs.setdefault("stdout", out_file)
                kwargs.setdefault("stderr", err_file)
                kwargs.setdefault("text", True)
                process = subprocess.Popen(args, **kwargs)

        # Runs progress bar while process runs
        with tqdm(
            total=total, desc=proc, unit=unit, leave=True, unit_scale=True
        ) as pbar:
            while process.poll() is None:
                processes.get(loader)(file, pbar)
                time.sleep(update_diff)
            processes.get(loader)(file, pbar, finished=True)

        process.communicate()

        # Checks for process success
        if process.returncode == 0:
            print(f"\n{message}: Completed successfully.")
        else:
            print(f"\n{message}: Failed with return code {process.returncode}.")

        return

    def __run_pipeloader(self, output_file: str, message: str, *args, **kwargs) -> None:
        """Runs subprocess with loading animation

        Args:
            output_file (str): Output log file
            message (str): Process description

        Returns:
            None: None
        """

        # Loading animation glyphs
        glyphs = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        error_file = os.path.join(self.hea_dir, "error.log")

        # Runs subprocess with logging
        with open(output_file, "a", encoding="utf-8") as out_file:
            with open(error_file, "a", encoding="utf-8") as err_file:
                kwargs.setdefault("stdout", out_file)
                kwargs.setdefault("stderr", err_file)
                kwargs.setdefault("text", True)
                process = subprocess.Popen(args, **kwargs)

            # Runs loading animation while process runs
            while process.poll() is None:
                for glyph in glyphs:
                    sys.stdout.write(f"\r{message} {glyph}")
                    sys.stdout.flush()
                    time.sleep(0.1)
                time.sleep(0.1)

            process.communicate()

            # Checks for process success
            if process.returncode == 0:
                sys.stdout.write(f"\r{message}: Completed successfully.\n")
            else:
                sys.stdout.write(
                    f"\r{message}: Failed with return code {process.returncode}.\n"
                )

        return

    def __install_tclreadline(self, tcl):
        """Install tclreadline using suplied package

        Args:
            tcl (dict): dictionary containing necessray packages and commands
        """

        # Installs necessary packages
        for package in tcl["packages"]:
            self.__run_pipeloader(
                "installer.log",
                f"Installing {package}",
                *self.pm_incmd,
                f"{package}",
            )

        # Runs configuration commands
        os.chdir(os.path.join(self.script_dir, "tclreadline-2.1.0"))
        _ = [
            self.__run_pipeloader("installer.log", f"Executing {' '.join(cmd)}", *cmd)
            for cmd in tcl["config_cmd"]
        ]

        # Installs tclreadline
        _ = [
            self.__run_pipeloader("installer.log", f"Executing {' '.join(cmd)}", *cmd)
            for cmd in tcl["install_cmd"]
        ]
        os.chdir(self.script_dir)

        return

    def __write_outlog(self, out) -> None:
        """Writes output to output log

        Args:
            out (any): Output
        """

        with open("installer.log", "a", encoding="utf-8") as log:
            log.write(f"{out}\n")

        return

    def __write_errlog(self, err) -> None:
        """Writes error to error log

        Args:
            err (any): Error
        """

        with open("error.log", "a", encoding="utf-8") as log:
            log.write(f"{err}\n")

        return

    def __track_lines(
        self, file: str, pbar: tqdm, finished: bool = False, **kwargs
    ) -> None:
        """Counts number of lines written to file to track progress

        Args:
            file (str): File path
            pbar (tqdm): tqdm progressbar object
            finished (bool, optional): Checks if process has finished. Defaults to False.
        """

        try:

            # Counts number of lines
            with open(file, "r", encoding="utf-8") as log:
                lines = sum(1 for _ in log)

            # Sets progress bar iteration count
            pbar.n = lines

            # Resets total count
            if finished:
                pbar.total = lines
            pbar.refresh()
        except FileNotFoundError:
            pass

        return

    def __track_download(
        self, file: str, pbar: tqdm, finished: bool = False, **kwargs
    ) -> None:
        """Reads file size to track download progress

        Args:
            file (str): File path
            pbar (tqdm): tqdm progressbar object
            finished (bool, optional): Checks if process has finished. Defaults to False.
        """

        try:
            # Gets file size and sets progress bar iteration count
            size = os.path.getsize(file)
            pbar.n = round(size, 2)

            # Resets total count
            if finished:
                pbar.total = size
            pbar.refresh()
        except FileNotFoundError:
            pass

        return


if __name__ == "__main__":
    subprocess.run(["sudo", "echo", "Initializing"], check=True)
    hea = Heainstall()
    hea.run()
