#!/bin/bash

location=$(pwd)
read -p "Enter heasoft tarball name: " hea_file

echo "Updating packages..."
sudo apt update && sudo apt -y upgrade >> install.log
echo "Packages updated successfully"

echo "Installing required dependencies..."
echo "Installing libreadline-dev..."
sudo apt-get -y install libreadline-dev >> install.log
echo "libreadline-dev installed"

echo "Installing libncurses5-dev..."
sudo apt-get -y install libncurses5-dev >> install.log
echo "libncurses5-dev installed"

echo "Installing ncurses-dev..."
sudo apt-get -y install ncurses-dev >> install.log
echo "ncurses-dev installed"

echo "Installing curl..."
sudo apt-get -y install curl >> install.log
echo "curl installed"

echo "Installing libcurl4..."
sudo apt-get -y install libcurl4 >> install.log
echo "libcurl4 installed"

echo "Installing libcurl4-gnutls-dev..."
sudo apt-get -y install libcurl4-gnutls-dev >> install.log
echo "libcurl4-gnutls-dev installed"

echo "Installing xorg-dev..."
sudo apt-get -y install xorg-dev >> install.log
echo "xorg-dev installed"

echo "Installing make..."
sudo apt-get -y install make >> install.log
echo "make installed"

echo "Installing gcc g++ gfortran..."
sudo apt-get -y install gcc g++ gfortran >> install.log
echo "gcc g++ gfortran installed"

echo "Installing perl-modules..."
sudo apt-get -y install perl-modules >> install.log
echo "perl-modules installed"

echo "Installing python3-dev..."
sudo apt-get -y install python3-dev >> install.log
echo "python3-dev installed"

echo "Installing python3-pip..."
sudo apt-get -y install python3-pip >> install.log
echo "python3-pip installed"

echo "Installing python3-setuptools..."
sudo apt-get -y install python3-setuptools >> install.log
echo "python3-setuptools installed"

echo "Installing python3-astropy..."
sudo apt-get -y install python3-astropy >> install.log
echo "python3-astropy installed"

echo "Installing python3-numpy..."
sudo apt-get -y install python3-numpy >> install.log
echo "python3-numpy installed"

echo "Installing python3-scipy..."
sudo apt-get -y install python3-scipy >> install.log
echo "python3-scipy installed"

echo "Installing python3-matplotlib..."
sudo apt-get -y install python3-matplotlib >> install.log
echo "python3-matplotlib installed"

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
    return 1 2>/dev/null
fi

echo "Compiling files. This can take upto an hour depending on the system and much longer if you are using WSL..."
make >> $location/install.log 2>&1
compile_check=$(tail -n 1 $location/install.log)
echo $compile_check

if [ "$compile_check" = "Finished make all" ]; then
    echo "Compilation successful"
else
    echo "Compilation unsuccessful. Terminating..."
    return 1 2>/dev/null
fi

echo "Installing. This can take up to 30 minutes or more depending on the system and even more if you are using WSL..."
make install >> $location/install.log 2>&1
install_check=$(tail -n 1 $location/install.log)

if [ "$install_check" = "Finished make install" ]; then
    echo "Installation successful"
else
    echo "Installation unsuccessful. Terminating..."
    return 1 2>/dev/null
fi

cd ../x86_64*

echo "Making init shell script executable..."
chmod u+x headas-init.sh
headas_path=$(pwd)

echo "Modifying .bashrc..."
echo -e "\n#heasoft\n\nHEADAS=\"${headas_path}\"\n. \"\$HEADAS/headas-init.sh\"" >> ~/.bashrc
. ~/.bashrc

hea_version=$(fversion)
echo "Heasoft version: $hea_version installed"