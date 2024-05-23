# Heasoft auto installer

This is a shell script which enables the user to automatically install heasoft in an ubuntu or any debian based operating system.

The instructions to install are as follows:
- Download heasoft from NASA's official website. To do so...
- - Go to the [heasoft download link](https://heasarc.gsfc.nasa.gov/docs/software/heasoft/download.html)
  - Select source code and select **PC - Linux - Ubuntu**. Do not select any pre-compiled binary distributions
  - Select the desired packages and click on **Submit**
- *heasoft-6.33.2src.tar.gz* will be downloaded. ***Note: This version is 6.33.2. It can be an older or an updated version. In that case, the filename would read as heasoft-\<version\>src.tar.gz***
- Go to the location where you downloaded the file and open a bash terminal from there.
- Make a new heasoft directory
  
  > ```console
  > mkdir heasoft
  > ```
- Move the heasoft file to this directory
  
  > ```console
  > mv heasoft-6.33.2src.tar.gz heasoft/.
  > ```
- Change your directory to the heasoft directory
  
  > ```console
  > cd heasoft
  > ```
- Download the script
  
  > ```console
  > git clone https://github.com/Anish-Sarkar-1001/heasoft-auto-installer
  > ```
- In case you don't have git installed, you can install it by

  > ```console
  > sudo apt-get install git
  > ```
- Copy the shell script to your heaosft tarball location

  > ```console
  > cp heasoft-auto-installer/install-heasoft.sh .
  > ```
- Delete the dowloaded github folder ####IMPORTANT

  > ```console
  > rm -r heasoft-auto-installer
  > ```
- Enable shell script execution

  > ```console
  > chmod u+x install-heasoft.sh
  > ```
- Run the shell script

  > ```console
  > ./install-heasoft.sh
  > ```
The script will ask for your sudo password as well as the name of the heasoft tarball file that you downloaded. Supply them when prompted

### NOTE: The diretory where you will be installing heasoft whould only coontain the downloaded heasoft tarball and the shell script before execution of the file.
#### This restriction will be lifted in future releases
