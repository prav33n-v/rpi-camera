# RaspberryPiCamera

## Description
This is a project to make a Infrared light sensitive point and shoot camera using Raspberry Pi, microSD card, usb card reader, SPI display, a few switches and a camera module (for this build I have used Arducam 16MP NoIR Camera).

## Acknowledgment
To write the code for this project, I have referred and used the sample codes available online to understand how the hardware works. Below are the codes I referred and used to develop this project :
   - <b>Picamera2 datasheet</b> - https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf 
   - Documentation for <b>gpiozero</b> librar - https://readthedocs.org/projects/gpiozero/downloads/pdf/stable/
   - Copied LCD driver code(<b>lib/lcdconfig.py</b> and <b>lib/LCD_2inch.py</b>) and <b>fonts</b> from the Waveshare's LCD_Module_RPI_code - https://www.waveshare.com/w/upload/a/a8/LCD_Module_RPI_code.7z

## Installation & Setup
At the time of building this project, I have used Raspbian Pi OS (32bit) distro.
```
  pi@rpi-camera:~ $ cat /etc/*release
  PRETTY_NAME="Raspbian GNU/Linux 12 (bookworm)"
  NAME="Raspbian GNU/Linux"
  VERSION_ID="12"
  VERSION="12 (bookworm)"
  VERSION_CODENAME=bookworm
  ID=raspbian
  ID_LIKE=debian
  HOME_URL="http://www.raspbian.org/"
  SUPPORT_URL="http://www.raspbian.org/RaspbianForums"
  BUG_REPORT_URL="http://www.raspbian.org/RaspbianBugs"
```

### Software setup
 -  Configuring raspberry pi by running
```
sudo raspi-config
```
 -  Enable the following and save the settings :
    -  Enable SPI/I2C/1Wire
    -  Expand Filesystem

 -  Reboot after the changes are done. After reboot update your Raspberry Pi by running below commands one by one :
```
sudo apt update
sudo apt upgrade
sudo apt autoremove
```

### Storage Setup
If you want to setup the camera to store the images in an external storage (I used microSD card), you can setup the raspberry pi to automatically mount it to a specific path. Follow the below steps for the same :

 -  Plug in the storage device and list the devices on your Raspberry Pi running command <b>lsblk -fp</b>
```
  pi@rpi-camera:~ $ lsblk -fp
  NAME             FSTYPE FSVER LABEL  UUID                                 FSAVAIL FSUSE% MOUNTPOINTS
  /dev/sda                                                                                 
  └─/dev/sda1      vfat   FAT32 SD32GB 6439-B4D1                              28.2G     5% /media/pi
  /dev/mmcblk0                                                                             
  ├─/dev/mmcblk0p1 vfat   FAT32 bootfs AAE0-77E1                             394.6M    23% /boot/firmware
  └─/dev/mmcblk0p2 ext4   1.0   rootfs ca2be9ef-61a4-4400-a5a1-dc17d7ea790d   23.6G    13% /
```
 -  If you want to mount card with label SD32GB (above) then run <b>sudo blkid /dev/sda1</b>
```
  pi@rpi-camera:~ $ sudo blkid /dev/sda1
  /dev/sda1: LABEL_FATBOOT="SD32GB" LABEL="SD32GB" UUID="6439-B4D1" BLOCK_SIZE="512" TYPE="vfat" PARTUUID="dec9100f-0771-43f2-ab9f-e0866e25869f"
  pi@rpi-camera:~ $
```
 -  Create a directory where you want to mount the storage device.
```
  pi@rpi-camera:~ $ sudo mkdir /mnt/data
  pi@rpi-camera:~ $ sudo chown pi:pi /mnt/data
  pi@rpi-camera:~ $ sudo chmod 777 /mnt/
```
 -  Add below line to /etc/fstab file using <b>sudo nano /etc/fstab</b>
```
/dev/sda1 /mnt/data vfat auto,nofail,noatime,rw,users,uid=1000,gid=1000 0 0
```
 -  Reboot your Raspberry Pi and check if device is mounted on your desired location by running <b>df -h</b>. As shown in below result /dev/sda1 is mounted on path /mnt/data
```
  pi@rpi-camera:~ $ df -h
  Filesystem      Size  Used Avail Use% Mounted on
  udev            325M     0  325M   0% /dev
  tmpfs            93M  2.1M   91M   3% /run
  /dev/mmcblk0p2   29G  3.7G   24G  14% /
  tmpfs           461M     0  461M   0% /dev/shm
  tmpfs           5.0M   12K  5.0M   1% /run/lock
  /dev/mmcblk0p1  510M  116M  395M  23% /boot/firmware
  /dev/sda1        30G  1.5G   29G   5% /mnt/data
  tmpfs            93M   36K   93M   1% /run/user/1000
  pi@rpi-camera:~ $ 
```
 - Create a directory for storing images in your storage device
```
mkdir /mnt/data/rpi-camera
```

### Samba Fileshare Setup
If you want to access the images stored on your rpi-camera directly via any devices connect to same network as Raspberry Pi the you can follow below steps :

 - Install samba
```
sudo apt install samba samba-common-bin
```
 - Configure samba fileshare by appending the below lines to /etc/samba/smb.conf . Please note that I have set value of writable, browsable and public as yes as I am not having any highly secure data here. You can change this parameters as per your need/requirement
```
[rpi-camera]
  path = /mnt/data/rpi-camera
  writable = yes
  browsable = yes
  public = yes
```
 - Setup a user to access your Samba share by running below command (sudo smbpasswd -a <USERNAME>) and then setup password for the same
```
sudo smbpasswd -a pi
```
 - Restart Samba services
```
sudo systemctl restart smbd
```

### Run scripts for Arducam 16MP NoIR Camera module
If you are using any other camera module then you do not need to do this setup. If you are using the mentioned camera module then you can install the same by following up the instructions from camera module manufacturer.
 - For this project, a camera module with Sony IMX519 sensor is used. The documentation is availabe at https://docs.arducam.com/Raspberry-Pi-Camera/Native-camera/16MP-IMX519/#supported-platforms-and-os
 - Reboot your raspberry pi.
 - Once your camera is connected correctly, run command <b>libcamera-still -o test.jpeg</b> to check if you are able to capture image. 

### Display Setup
For this project, 2 inch LCD display from Waveshare is used with resolution of 240x320. The documentation is available at https://www.waveshare.com/wiki/2inch_LCD_Module
```
sudo apt-get update
sudo apt-get install python3-pip python3-pil python3-numpy
sudo pip3 install spidev
```
 - In case of you get <b>error: externally-managed-environment</b> , run below command and the try running the above command again.
```
sudo mv /usr/lib/python3.11/EXTERNALLY-MANAGED /usr/lib/python3.11/EXTERNALLY-MANAGED.old
```

## Setup crontab to automatically run the camera code
 - To start the program on boot, add the below line to your crontab by running <b> sudo crontab -e </b> after replacing the path with <location> to rpi_cam.py file
```
@reboot cd < location > ; python3 rpi_cam.py
```
