# RaspberryPiCamera

## Description
This is a project to make a Infrared light sensitive point and shoot camera using Raspberry Pi, microSD card, usb card reader, SPI display, a few switches and ofcourse a camera module (for my build I have used Arducam 16MP NoIR Camera).

## OS Installation
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

### Initial Software setup
 -  Configuring raspberry pi by running
```
sudo raspi-config
```
	Enable the following :
	- Enable legacy camera support
	- Enable SPI/I2C/1Wire
	- Expand Filesystem

 -  Reboot after the changes are done. After reboot update your Raspberry Pi by running below commands one by one :
```
sudo apt update
sudo apt upgrade
sudo apt autoremove
```

### Storage Setup
If you want to setup the camera to store the images in an external storage (I used microSD card), you can setup the raspberry pi to automatically mount it to a specific path. Follow the below steeps for the same :

 -  Plug in the storage device and list the devices on your Raspberry Pi running command "lsblk -fp"
```
  pi@rpi-camera:~ $ lsblk -fp
  NAME             FSTYPE FSVER LABEL  UUID                                 FSAVAIL FSUSE% MOUNTPOINTS
  /dev/sda                                                                                 
  └─/dev/sda1      vfat   FAT32 SD32GB 6439-B4D1                              28.2G     5% /mnt/data
  /dev/mmcblk0                                                                             
  ├─/dev/mmcblk0p1 vfat   FAT32 bootfs AAE0-77E1                             394.6M    23% /boot/firmware
  └─/dev/mmcblk0p2 ext4   1.0   rootfs ca2be9ef-61a4-4400-a5a1-dc17d7ea790d   23.6G    13% /
```
 -  If you want to mount card with label SD32GB (above) then run "sudo blkid /dev/sda1"
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
 -  Add below line to /etc/fstab file using "sudo nano /etc/fstab"
```
/dev/sda1 /mnt/data vfat defaults,nofail,noatime 0 0
```
 -  Reboot your Raspberry Pi and check if device is mounted on your desired location by running "df -h". As shown in below result /dev/sda1 is mounted on path /mnt/data
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

### Samba Fileshare Setup
If you want to access the images stored on your rpi-camera directly via any devices connect to same network as Raspberry Pi the you can follow below steps :

 - Install samba
```
sudo apt install samba samba-common-bin
```
 - Configure samba fileshare by appending the below lines to /etc/samba/smb.conf . Please note that I have set value of writable, browsable and public as yes as I am not having any highly secure data here. You can change this parameters as per your need/requirement
```
[rpi-camera]
  path = /mnt/data
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
