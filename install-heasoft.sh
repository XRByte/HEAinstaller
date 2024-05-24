#!/bin/bash

echo "Updating packages..."
sudo apt update && sudo apt -y upgrade >> install.log
echo "Packages updated successfully"

ubuntu_version=$(lsb_release -rs 2>/dev/null)
echo "Ubuntu version: ${ubuntu_version}"

ubuntu_version=$(echo "${ubuntu_version}" | bc -l)
flag_version=23.10

if [ -f "/proc/sys/fs/binfmt_misc/WSLInterop" ]
then
    echo "Operating system: Windows Subsystem for Linux detected"
    available_space=$(df -h /mnt/c | awk 'NR==2 {print $4}' | tr -d 'G')
    echo "Space available in C: ${available_space}"
    if [ ${available_space} -lt 10 ]
    then
        echo "Available space must be greater than 10 GB. Please clean up your storage and run the script again"
        exit 1 2>/dev/null
    else
        echo "Proceeding with installation..."
    fi
else
    echo "Operating system: Linux detected"
fi

if (( $(echo "${ubuntu_version} > ${flag_version}" | bc -l) ))
then
    sudo apt-get install libncurses-dev
    if dpkg -l | grep -q "libncurses-dev"
    then
        echo "libncurses-dev installed successfully"
    else
        echo "libncurses-dev installation unsucessful. Exiting..."
        exit 1 2>/dev/null
    fi
else
    sudo apt-get install libncurses5-dev
    if dpkg -l | grep -q "libncurses5-dev"
    then
        echo "libncurses5-dev installed successfully"
    else
        echo "libncurses5-dev installation unsucessful. Exiting..."
        exit 1 2>/dev/null
    fi
fi

packages=(libreadline-dev ncurses-dev curl libcurl4 libcurl4-gnutls-dev xorg-dev make gcc g++ gfortran perl-modules python3-dev python3-pip python3-setuptools python3-astropy python3-numpy python3-scipy python3-matplotlib)

echo "Installing required dependencies..."
for package in "${packages[@]}"
do
    echo "Installing ${package}..."
    sudo apt-get install -y "${package}"
    if dpkg -l | grep -q "${package}"
    then
        echo "${package} installed successfully"
    else
        echo "${package} installation unsucessful. Exiting..."
        exit 1 2>/dev/null
    fi
done

echo "Defining environment variables..."
export CC=/usr/bin/gcc
export CXX=/usr/bin/g++
export FC=/usr/bin/gfortran
export PERL=/usr/bin/perl
export PYTHON=/usr/bin/python3
echo "Environment variables defined"

mkdir ~/heasoft
if [ -d "${HOME}/heasoft" ]
then
    cd ~/heasoft
else
    echo "Fatal error! Unable to create heasoft directory"
    exit 1 2>/dev/null
fi
location=$(pwd)

while true
do
    wget "https://heasarc.gsfc.nasa.gov/cgi-bin/Tools/tarit/tarit.pl?mode=download&arch=src&src_pc_linux_ubuntu=Y&src_other_specify=&checkeverything=on&checkallmission=on&mission=asca&mission=einstein&mission=exosat&mission=gro&mission=heao1&mission=hitomi&mission=integral&mission=ixpe&mission=maxi&mission=nicer&mission=nustar&mission=oso8&mission=rosat&mission=suzaku&mission=swift&mission=vela5b&mission=xte&checkallgeneral=on&general=attitude&general=caltools&general=futils&general=fimage&general=heasarc&general=heasim&general=heasptools&general=heatools&general=heagen&general=fv&general=timepkg&checkallxanadu=on&xanadu=ximage&xanadu=xronos&xanadu=xspec&xstar=xstar" -O heasoft.tar.gz  && touch download.ok || touch download.bad
    if [[ $(ls | grep '\.ok$') ]]
    then
        break
    fi
done

echo "Unsetting required flags..."
unset CFLAGS CXXFLAGS FFLAGS LDFLAGS
echo "Flags unset"

if [[ $(ls | grep 'heasoft.tar.gz$') ]]
then
    echo "Extracting..."
    if tar -xvzf heasoft.tar.gz
    then
        hea_dir=$(tar -tzf "heasoft.tar.gz" | head -n 1 | cut -f1 -d'/')
        echo "Extraction successful"
    else
        echo "Fatal error! Unable to extract content"
        exit 1 2>/dev/null
    fi
fi

echo "Configuring heasoft..."
cd $hea_dir/BUILD_DIR/
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
echo -e "\n#heasoft\n\nexport HEADAS=\"${headas_path}\"\nsource \"\$HEADAS/headas-init.sh\"" >> ~/.bashrc
source ~/.bashrc

hea_version=$(fversion)
echo "Heasoft version: ${hea_version} installed successfully"
rm ~/heasoft/heasoft.tar.gz
