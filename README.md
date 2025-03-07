# HEAinstaller

## Version 2.25.03 (Latest)

**HEAinstaller** is a Python script that automates the installation of [HEASoft](https://heasarc.gsfc.nasa.gov/docs/software/heasoft/) on any supported platform *(WSL/Linux/Darwin)* that is based on the *glibc* library package.

---

## Requirements

- **Python** ≥ 3.8
- An active **Conda/Virtual Environment**
- **tqdm** installed in the environment
  
  > ```console
  > pip install tqdm
  > ```
- A **display server** like *Xorg (X11) / Wayland* for GUI-based tools (Ensure that the `$DISPLAY` environment variable is initialized)

### Setting Up an Environment
- Follow this [Virtual Environment Setup Guide](https://docs.python.org/3/library/venv.html) to create and activate a virtual environment.
- Alternatively, follow this [Conda Environment Setup Guide](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html) to create a Conda environment. The base environment will also work.

> **Note:** If no active Conda/Virtual environment is detected, the script will use `pip` to install Python libraries. However, most distributions recommend using a Virtual/Conda environment instead of modifying the base Python build. Hence, using an active environment is preferred.

---

## Installation Guide

Run the following commands to install HEASoft:

```console
 git clone https://github.com/Anish-Sarkar-1001/HEAinstaller.git
 cd HEAinstaller
 python3 heainstaller.py
```

> **Note:** You will be prompted for your superuser password and asked to provide the `heasoft-x.xx.x.tar.gz` path if you have already downloaded it.

Once the installation is complete, the installed HEASoft version will be displayed.

To initialize HEASoft after installation, use:

```console
 heainit
```

---

## Important Notes

- The script uses `sudo`, which may not be available by default in some distributions like Alpine Linux. Install `sudo` as root if required.
- The configuration is done **without `lynx`**, as some distributions report errors during setup. This does not impact functionality.

---

## Customization & Additional Information

- By default, all HEASoft packages are installed. This behavior can be modified by editing the **`user.json`** file and changing specific fields from `yes` to `no`. **Modify carefully**, as some packages have dependencies.
- Refer to the [HEASoft website](https://heasarc.gsfc.nasa.gov/docs/software/lheasoft/download-go.html) to check package dependencies.
- Progress bars displayed during installation are approximate and may vary by a margin of 1%.
- The software is installed at: `~/bin/heasoft/heasoft-x.xx`
- If the HEASoft tarball is downloaded, it will be stored at: `~/bin/heasoft`
- Log files for **configuration, build, installation, and errors** can be found in: `~/bin/heasoft`

---

## Tested Platforms

### **MacOS (Darwin):**
- MacOS Sequoia
- MacOS Sonoma
- MacOS Ventura

### **Linux:**
- Ubuntu
- OpenSUSE
- Arch
- Void (glibc)
- Gentoo (glibc)
- Debian
- Deepin
- Kali
- Oracle
- CentOS
- AlmaLinux
- Manjaro

### **WSL:**
- All the above Linux distributions

---

## Supported Shells
- `bash`
- `zsh`
- `ksh`
- `dash`
- `ash`
- `elvish`
- `csh`
- `tcsh`
- `fish`

---

## Unsupported Platforms

### **Linux:**
- Slackware
- Any distribution using `musl`

---

