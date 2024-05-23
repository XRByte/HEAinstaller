#!/bin/bash

location=$(pwd)
read -p "Enter heasoft tarball name: " hea_file 
if [ "${hea_file}" == "" ]
then
    echo "File name cannot be blank"
    exit 1 2>/dev/null
fi

if [ "${hea_file}" != "*.tar.gz" ]
then
    hea_file="${hea_file}.tar.gz"
fi

packages=(libreadline-dev libncurses5-dev ncurses-dev curl libcurl4 libcurl4-gnutls-dev xorg-dev make gcc g++ gfortran perl-modules python3-dev python3-pip python3-setuptools python3-astropy python3-numpy python3-scipy python3-matplotlib)

echo "Updating packages..."
sudo apt update && sudo apt -y upgrade >> install.log
echo "Packages updated successfully"

echo "Installing required dependencies..."
for package in "${packages[@]}"
do
    echo "Installing ${package}..."
    sudo apt-get install -y "${package}"
    echo "${package} installed"
done

echo "Defining environment variables..."
export CC=/usr/bin/gcc
export CXX=/usr/bin/g++
export FC=/usr/bin/gfortran
export PERL=/usr/bin/perl
export PYTHON=/usr/bin/python3
echo "Environment variables defined"

echo "Unsetting required flags..."
unset CFLAGS CXXFLAGS FFLAGS LDFLAGS
echo "Flags unset"
tar -xvzf $hea_file
hea_folder=$(ls -d */) # Initially directory must be empty

echo "Configuring heasoft..."
cd $hea_folder/BUILD_DIR/
./configure >> $location/install.log 2>&1
configure_check=$(tail -n 1 $location/install.log)

if [ "$configure_check" = "Finished" ]; then
    echo "Configuration successful"
else
    echo "Configuration unsuccessful. Terminating..."
    exit 1 2>/dev/null
fi

echo "Compiling files. This can take upto an hour depending on the system and much longer if you are using WSL..."
make >> $location/install.log 2>&1
compile_check=$(tail -n 1 $location/install.log)
echo $compile_check

if [ "$compile_check" = "Finished make all" ]; then
    echo "Compilation successful"
else
    echo "Compilation unsuccessful. Terminating..."
    exit 1 2>/dev/null
fi

echo "Installing. This can take up to 30 minutes or more depending on the system and even more if you are using WSL..."
make install >> $location/install.log 2>&1
install_check=$(tail -n 1 $location/install.log)

if [ "$install_check" = "Finished make install" ]; then
    echo "Installation successful"
else
    echo "Installation unsuccessful. Terminating..."
    exit 1 2>/dev/null
fi

cd ../x86_64*

echo "Making init shell script executable..."
chmod u+x headas-init.sh
headas_path=$(pwd)

echo "Modifying .bashrc..."
echo -e "\n#heasoft\n\nexport HEADAS=\"${headas_path}\"\n. \"\$HEADAS/headas-init.sh\"" >> ~/.bashrc
. ~/.bashrc

hea_version=$(fversion)
echo "Heasoft version: $hea_version installed"
