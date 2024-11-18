#!/usr/bin/python
# -*- coding: UTF-8 -*-
#import chardet
import os
import sys 
import time
import logging
import random
import spidev as SPI
#sys.path.append("..")
import RPi.GPIO as GPIO
import shutil
import lib.LCD_2inch as LCD_2inch
from PIL import Image,ImageDraw,ImageFont

# Raspberry Pi pin configuration:
RST = 27
DC = 23
BL = 18
bus = 0 
device = 0 
#logging.basicConfig(level=logging.DEBUG)
width = 320
height = 240
disp = LCD_2inch.LCD_2inch()

# Variables for display/screen
brightness = 50
SPI_SPEED_MHZ = 80
exposure_time=["AUTO","1/1600","1/1250","1/1000","1/800","1/640","1/500","1/400","1/320","1/250","1/200","1/160","1/125","1/100","1/80","1/60","1/50","1/40","1/30","1/25","1/20","1/15","1/13","1/10","1/8","1/6","1/5","1/4","1/3","1/2.5","1/2","1/1.6","1/1.3",'1"','1.3"','1.6"','2"','2.5"','3"','4"','5"','6"','8"','10"','13"','15"','20"','25"','30"','60"']

image_h=[1600,2048,2464,3008,3264,3888,4000,4656]
image_w=[1200,1536,1632,2000,2448,2592,2800,3496]

noise_reduction_mode = ("OFF","FAST","QUALITY")
white_balance = ("AUTO","TUNGSTEN","RADIANT","INDOOR","DAYLIGHT","CLOUDY")
picture_control = ("Standard","Grayscale","Sepia","Technicolor")

# Define colors
RED=(200,0,0)
GREEN=(0,200,0)
BLUE=(0,0,255)
BLACK=(0,0,0)
GRAY=(120,120,120)
INFO=(200,200,175)
WHITE=(255,255,255)
YELLOW=(255,255,0)
SEPIA=(150,110,75)
MENU_SELECT=(200,200,200)
MENU_TEXT=(250,250,120)
MENU_TITLE=(128,255,10)

# Path for fonts
# Fonts used are taken from the waveshare LCD interface example code
# URL : https://www.waveshare.com/w/upload/a/a8/LCD_Module_RPI_code.7z
boot_screen = ImageFont.truetype("./font/Font01.ttf",50)
menu_icon_large = ImageFont.truetype("./font/Font02.ttf",30)
menu_icon = ImageFont.truetype("./font/Font02.ttf",24)
home_info = ImageFont.truetype("./font/Font02.ttf",19)
menu_title = ImageFont.truetype("./font/Font02.ttf",30)
menu_line = ImageFont.truetype("./font/Font02.ttf",24)

# Custom icon for status display
def get_icon(icon_name,icon_color,camera_config):
    icon=Image.new("RGB",(28,28),color=GRAY)
    draw = ImageDraw.Draw(icon)
    if(icon_name == "sound"):
        draw.rectangle((4,4,24,24), WHITE)
        draw.rectangle((5,5,23,23), BLACK)
        draw.rectangle((7,11,11,18), icon_color)
        draw.rectangle((14,12,14,17), icon_color) 
        draw.rectangle((16,10,16,19), icon_color) 
        draw.rectangle((18,8,18,21), icon_color) 
        draw.rectangle((20,6,20,22), icon_color) 
    elif(icon_name == "Standard"):
        draw.rectangle((4,4,24,24), WHITE)
        draw.rectangle((5,5,23,23), BLACK)
        draw.rectangle((6,6,22,22), WHITE)
        draw.polygon([(6,6),(6,16),(16,6)], fill = RED)
        draw.polygon([(22,12),(12,22),(22,22)], fill = GREEN)
    elif(icon_name == "Grayscale"):
        draw.rectangle((4,4,24,24), WHITE)
        draw.rectangle((5,5,23,23), BLACK)
        draw.polygon([(6,6),(6,22),(22,6)], fill = WHITE)
    elif(icon_name == "Sepia"):
        draw.rectangle((4,4,24,24), WHITE)
        draw.rectangle((5,5,23,23), SEPIA)
        draw.polygon([(6,6),(6,22),(22,6)], fill = YELLOW)
    elif(icon_name == "Technicolor"):
        draw.rectangle((4,4,24,24), WHITE)
        draw.rectangle((5,5,23,23), BLACK)
        draw.rectangle((6,6,22,11), fill = RED)
        draw.rectangle((6,12,22,17), fill = GREEN)
        draw.rectangle((6,18,22,22), fill = BLUE)
    elif(icon_name == "pic"):
        draw.rectangle((4,4,24,24), WHITE)
        draw.rectangle((5,5,23,23), BLACK)
        if (camera_config["raw"]):
            draw.text((10,2),"R", fill = icon_color,font = home_info)
        else:
            draw.text((11,2),"J", fill = WHITE,font = home_info)
    elif(icon_name == "bkt"):
        draw.rectangle((6,6,26,26), WHITE)
        draw.rectangle((5,5,25,25), BLACK)
        draw.rectangle((4,4,24,24), WHITE)
        draw.rectangle((5,5,23,23), BLACK)
        if (camera_config["raw"]):
            draw.text((10,2),"R", fill = icon_color,font = home_info)
        else:
            draw.text((11,2),"J", fill = WHITE,font = home_info)
    elif(icon_name == "int"):
        draw.rectangle((6,6,26,26), WHITE)
        draw.rectangle((5,5,25,25), BLACK)
        draw.rectangle((4,4,24,24), WHITE)
        draw.rectangle((5,5,23,23), BLACK)
        if (camera_config["raw"]):
            draw.polygon([(7,11),(7,17),(11,21),(17,21),(21,17),(21,11),(17,7),(11,7)], fill = icon_color)
        else:
            draw.polygon([(7,11),(7,17),(11,21),(17,21),(21,17),(21,11),(17,7),(11,7)], fill = WHITE)
    elif(icon_name == "nr"):
        draw.rectangle((4,4,24,24), WHITE)
        draw.rectangle((5,5,23,23), BLACK)
        if (camera_config["noise_reduction"] == 1 ):
            draw.text((6,2),"NR", fill = RED,font = home_info)
        else:
            draw.text((6,2),"NR", fill = icon_color,font = home_info)
    return icon

# LCD : Show image_file on screen
def show_image(image):
    basewidth = width
    wpercent = (basewidth/float(image.size[0]))
    hsize = int((float(image.size[1])*float(wpercent)))
    image= image.resize((basewidth,hsize), resample=Image.BICUBIC)
    new_image=Image.new("RGB",(width,height),color='black')
    new_image.paste(image,(0,0))
    disp.ShowImage(new_image)

def draw_bar(image,value,background_color=GRAY,bar_fill_color=WHITE):
    draw = ImageDraw.Draw(image)
    # Draw a handy on-screen bar to show us the current brightness
    bar_width = int((305 / 100.0) * value)
    draw.rectangle((10,216,310,216), background_color)
    draw.rectangle((10,216,5+bar_width,216), bar_fill_color)
    # return the resulting image
    return image

def progress_bar(image_file,x,shoot_config,camera_config,display_config,background_color=GRAY,bar_fill_color=WHITE):
    basewidth = width
    image_count = 1
    image = Image.open(image_file)
    wpercent = (basewidth/float(image.size[0]))
    hsize = int((float(image.size[1])*float(wpercent)))
    preview_image= image.resize((288,216), resample=Image.BICUBIC)
    outline=Image.new("RGB",(320,240),color='red')
    outline.paste(preview_image,(1,23))
    image=Image.new("RGB",(width,height),color='black')
    image.paste(outline,(0,0))
    draw = ImageDraw.Draw(image)
    # Draw a handy on-screen bar to show us the current brightness
    info_color = MENU_TITLE
    draw.rectangle((290,23,318,238), GRAY)
    image.paste(get_icon(picture_control[camera_config["picture_control"]],BLACK,camera_config),(290,25))
    if( shoot_config["shoot_mode"] == 2 ):              # mode 2 - bracketing
        image_count = shoot_config["bkt_frame_count"]
        image.paste(get_icon("bkt",GREEN,camera_config),(290,55))
    elif( shoot_config["shoot_mode"] == 3 ):              # mode 3 - timelapse stills
        image_count = shoot_config["tlp_frame_count"]
        image.paste(get_icon("int",GREEN,camera_config),(290,55))
    elif( shoot_config["shoot_mode"] == 4 ):              # mode 4 - timelapse video
        image_count = shoot_config["tlv_frame_count"]
        image.paste(get_icon("tlv",GREEN,camera_config),(290,55))
    if(camera_config["noise_reduction"] != 0):
        image.paste(get_icon("nr",GREEN,camera_config),(290,85))
    if(display_config["sound"]):
        image.paste(get_icon("sound",RED,camera_config),(290,210))
    draw.rectangle((290,22,318,22), 'red')
    draw.rectangle((1,1,318,21), BLACK)
    draw.rectangle((1,1,70,21), GRAY)
    draw.text((2,0),("ISO "+str(int(camera_config["analogue_gain"] * 100))), fill = MENU_TEXT,font = home_info)
    draw.rectangle((73,1,145,21), GRAY)
    if(camera_config["exposure"] == 0):
        draw.text((75,0),exposure_time[camera_config["exposure"]],fill = MENU_TITLE, font = home_info)
    else:
        draw.text((75,0),exposure_time[camera_config["exposure"]],fill = MENU_TEXT, font = home_info)
    draw.rectangle((148,1,220,21), GRAY)
    if(camera_config["white_balance"] != 0 ):
        draw.text((150,0),"WB - "+(white_balance[camera_config["white_balance"]][0:3]), fill = MENU_TEXT,font = home_info)
    else:
        draw.text((150,0),"AWB", fill = MENU_TEXT,font = home_info)
    draw.rectangle((223,1,318,21), GRAY)
    draw.text((225,0),("CON "+str(float(camera_config["contrast"]))), fill = MENU_TEXT,font = home_info)
    draw.text((5,215),"Processing → "+str(x+1)+" / "+str(image_count), fill = YELLOW,font = home_info)

    value = int(((x+1)/image_count)*100)
    bar_width = int((278 / 100.0) * value)
    draw.rectangle((5,216,283,216), background_color)
    draw.rectangle((5,216,5+bar_width,216), bar_fill_color)
    disp.ShowImage(image)

#############################################################################
# Functions to print specific menu options for camera
#############################################################################

def boot_disp(file_name):
    # Initialize library.
    disp.Init()
    # Clear display.
    disp.clear()

    dir= "logo"
    camera_logo_file= os.path.join(os.getcwd(),dir,file_name)
    image=Image.open(camera_logo_file)
    image=image.resize((width,height), resample=Image.BICUBIC)
    draw = ImageDraw.Draw(image)
    disp.ShowImage(image)

def menu_display(header,menu_item,display_config,bar_value=0):
    item_number = display_config["menu"] % 10
    image=Image.new("RGB",(width,height),color='black')
    draw = ImageDraw.Draw(image)
    draw.text((0,5),header,fill = MENU_TITLE,font = menu_title)
    count = 0
    for item in menu_item:
        if(item_number == (count+1)):
            draw.rectangle([(310,(36+(25*(count+1)))),(10,(36+(25*count)))],fill = MENU_SELECT)
            draw.text((15,(33+(25*count))),item,fill = BLACK,font = menu_line)
        else:
            draw.text((15,(33+(25*count))),item,fill = MENU_TEXT,font = menu_line)
        count += 1
    if(display_config["menu"] == 31):
        disp.ShowImage(draw_bar(image,display_config["brightness"]))
    elif(display_config["menu"] == 42):
        if(bar_value < 50):
            COLOR = GREEN
        elif(bar_value >= 50 and bar_value <=75):
            COLOR = YELLOW
        else:
            COLOR = RED
        disp.ShowImage(draw_bar(image,bar_value,bar_fill_color=COLOR))
    disp.ShowImage(image)

def camera_home(display_config,shoot_config,camera_config,preview_image):
    preview_image= preview_image.resize((288,216), resample=Image.BICUBIC)
    outline=Image.new("RGB",(320,240),color='white')
    outline.paste(preview_image,(1,23))
    image=Image.new("RGB",(width,height),color='black')
    image.paste(outline,(0,0))
    draw = ImageDraw.Draw(image)
    info_color = MENU_TITLE
    draw.rectangle((290,23,318,238), GRAY)
    image.paste(get_icon(picture_control[camera_config["picture_control"]],BLACK,camera_config),(290,25))
    if( shoot_config["shoot_mode"] == 1 ):                # mode 1 - stills
        image.paste(get_icon("pic",GREEN,camera_config),(290,55))
    elif( shoot_config["shoot_mode"] == 2 ):              # mode 2 - bracketing
        image.paste(get_icon("bkt",GREEN,camera_config),(290,55))
    elif( shoot_config["shoot_mode"] == 3 ):              # mode 3 - timelapse stills
        image.paste(get_icon("int",GREEN,camera_config),(290,55))
    if(camera_config["noise_reduction"] != 0):
        image.paste(get_icon("nr",GREEN,camera_config),(290,85))
    if(display_config["sound"]):
        image.paste(get_icon("sound",RED,camera_config),(290,210))
    draw.rectangle((290,22,318,22), 'white')
    draw.rectangle((1,1,318,21), BLACK)
    draw.rectangle((1,1,70,21), GRAY)
    draw.text((2,0),("ISO "+str(int(camera_config["analogue_gain"] * 100))), fill = MENU_TEXT,font = home_info)
    draw.rectangle((73,1,145,21), GRAY)
    if(camera_config["exposure"] == 0):
        draw.text((75,0),exposure_time[camera_config["exposure"]],fill = MENU_TITLE, font = home_info)
    else:
        draw.text((75,0),exposure_time[camera_config["exposure"]],fill = MENU_TEXT, font = home_info)
    draw.rectangle((148,1,220,21), GRAY)
    if(camera_config["white_balance"] != 0 ):
        draw.text((150,0),"WB - "+(white_balance[camera_config["white_balance"]][0:3]), fill = MENU_TEXT,font = home_info)
    else:
        draw.text((150,0),"AWB", fill = MENU_TEXT,font = home_info)
    draw.rectangle((223,1,318,21), GRAY)
    draw.text((225,0),("CON "+str(float(camera_config["contrast"]))), fill = MENU_TEXT,font = home_info)
    disp.ShowImage(image)

def get_disk_usage(shoot_config):
    # Disk space usage infod
    memory=shutil.disk_usage(shoot_config["storage_path"])
    usage=int((memory[1]/memory[0])*100)
    used=(memory[1]/1024)
    total=(memory[0]/1024)/1024
    if(used > 0 and used < 1024):
        value = str(round(used,2)) + "k /" + str(round((total/1024),2)) + "g"
    elif(used >= 1024 and used < 1048576): # and used < 1073741824):
        value = str(round((used/1024),2)) + "m /" + str(round((total/1024),2)) + "g"
    else:
        value = str(round(((used/1024)/1024),2)) + "g /" + str(round((total/1024),2)) + "g"
    return value,usage

def menu_control(display_config,shoot_config,camera_config):
    menu = display_config.get("menu")
    value,usage = get_disk_usage(shoot_config)
    if( menu >= 1 and menu <= 9):
        items=["Camera Control","Shooting Mode","UI Menu","System Menu","Power Options"]
        menu_display("Menu",items,display_config)

    elif( menu >= 11 and menu <= 19 ):        # Camera control settings
        items=["Exposure","ISO","Contrast","Sharpness","Noise Reduction","AWB","Picture Control","Size"]
        if(shoot_config["shoot_mode"] == 1):
            menu_page_title = "Photo Mode Setup"
        elif(shoot_config["shoot_mode"] == 2):
            menu_page_title = "Bracketing Mode Setup"
        elif(shoot_config["shoot_mode"] == 3):
            menu_page_title = "Interval Timer Setup"
        items[0] = items[0] + " → " + exposure_time[camera_config["exposure"]]
        items[1] = items[1] + " → " + str(int(camera_config["analogue_gain"] * 100))
        items[2] = items[2] + " → " + str(camera_config["contrast"])
        items[3] = items[3] + " → " + str(camera_config["sharpness"])
        items[4] = items[4] + " → " + noise_reduction_mode[camera_config["noise_reduction"]]
        items[5] = items[5] + " → " + white_balance[camera_config["white_balance"]]
        items[6] = items[6] + " → " + picture_control[camera_config["picture_control"]]
        items[7] = items[7] + " → " + str(image_h[camera_config["image_size"]]) +" X " + str(image_w[camera_config["image_size"]])
        menu_display(menu_page_title,items,display_config)

    elif( menu >= 21 and menu <= 29 ):        # Shooting mode
        items=["Photo","Bracketing","Interval Timer Shoot"]
        menu_display("Shooting Mode",items,display_config)

    elif( menu >= 222 and menu <= 229 ):      # Bracketing submenu
        items=["Photo","Bracketing","* Frames","Interval Timer Shoot"]
        items[2]=items[2] + " → " + str(shoot_config["bkt_frame_count"])
        menu_display("Shooting Mode",items,display_config)

    elif( menu >= 233 and menu <= 239 ):      # Timelapse photo submenu
        items=["Photo","Bracketing","Interval Timer Shoot","* Frames","* Interval"]
        items[3]=items[3] + " → " + str(shoot_config["tlp_frame_count"])
        items[4]=items[4] + " → " + str(shoot_config["tlp_interval"])
        menu_display("Shooting Mode",items,display_config)

    elif( menu >= 31 and menu <= 39 ):        # Image Setting Menu
        items=["Brightness","Sound","Status LED","Playback Time → "]
        if(menu == 31):                             # Brightness Control
            items[0] = items[0] + " → " + str(display_config["brightness"])
        if(display_config["sound"]):
            items[1] += " → On"
        else:
            items[1] += " → Off"
        if(display_config["status_led"]): 
            items[2] += " → On"
        else:
            items[2] += " → Off"
        items[3] += (str(camera_config["wait_time"]) + " Sec")
        menu_display("UI Menu",items,display_config)

    elif( menu >= 41 and menu <= 49 ):        # System Menu
        items=["Output File → JPG","Disk","Wipe Data","Save Settings","Load Settings","Reset Settings"]
        if(camera_config["raw"]):
            items[0] += " + RAW"
        items[1] = items[1] + " → " + value
        menu_display("System Menu",items,display_config,usage)

    elif( menu == 433 ):                            # Wipe data
        items=["Output File → JPG","Disk","Wipe Data → Sure ?","Save Settings","Load Settings","Reset Settings"]
        if(camera_config["raw"]):
            items[0] += " + RAW"
        items[1] = items[1] + " → " + value
        menu_display("System Menu",items,display_config)

    elif( menu == 4333 ):                           # Wipe data confirmation
        items=["Output File → JPG","Disk","Wipe Data → Done !","Save Settings","Load Settings","Reset Settings"]
        if(camera_config["raw"]):
            items[0] += " + RAW"
        items[1] = items[1] + " → " + value
        menu_display("System Menu",items,display_config)
        time.sleep(1)
        items[2] = "Wipe Data"
        menu_display("System Menu",items,display_config)

    elif( menu == 444 ):                            # Save settings
        items=["Output File → JPG","Disk","Wipe Data","Save Settings → Sure ?","Load Settings","Reset Settings"]
        if(camera_config["raw"]):
            items[0] += " + RAW"
        items[1] = items[1] + " → " + value
        menu_display("System Menu",items,display_config)

    elif( menu == 4444 ):                           # Save settings confirmation
        items=["Output File → JPG","Disk","Wipe Data","Save Settings → Done !","Load Settings","Reset Settings"]
        if(camera_config["raw"]):
            items[0] += " + RAW"
        items[1] = items[1] + " → " + value
        menu_display("System Menu",items,display_config)
        time.sleep(1)
        items[3] = "Save Settings"
        menu_display("System Menu",items,display_config)

    elif( menu == 455 ):                            # Load settings
        items=["Output File → JPG","Disk","Wipe Data","Save Settings","Load Settings → Sure ?","Reset Settings"]
        if(camera_config["raw"]):
            items[0] += " + RAW"
        items[1] = items[1] + " → " + value
        menu_display("System Menu",items,display_config)

    elif( menu == 4555 ):                           # Load settings confirmation
        items=["Output File → JPG","Disk","Wipe Data","Save Settings","Load Settings → Done !","Reset Settings"]
        if(camera_config["raw"]):
            items[0] += " + RAW"
        items[1] = items[1] + " → " + value
        menu_display("System Menu",items,display_config)
        time.sleep(1)
        items[4] = "Load Settings"
        menu_display("System Menu",items,display_config)

    elif( menu == 466 ):                            # Load settings
        items=["Output File → JPG","Disk","Wipe Data","Save Settings","Load Settings","Reset Settings → Sure ?"]
        if(camera_config["raw"]):
            items[0] += " + RAW"
        items[1] = items[1] + " → " + value
        menu_display("System Menu",items,display_config)

    elif( menu == 4666 ):                           # Load settings confirmation
        items=["Output File → JPG","Disk","Wipe Data","Save Settings","Load Settings","Reset Settings → Done !"]
        if(camera_config["raw"]):
            items[0] += " + RAW"
        items[1] = items[1] + " → " + value
        menu_display("System Menu",items,display_config)
        time.sleep(1)
        items[5] = "Reset Settings"
        menu_display("System Menu",items,display_config)

    elif( menu >= 51 and menu <= 59 ):              # Power Options
        items=["Power Saver","Reboot","Poweroff"]
        menu_display("Power Options",items,display_config)

    elif( menu == 511 ):
        items=["Power Saver → Sure ?","Reboot","Poweroff"]
        menu_display("Power Options",items,display_config)

    elif( menu == 522 ):
        items=["Power Saver","Reboot → Sure ?","Poweroff"]
        menu_display("Power Options",items,display_config)

    elif( menu == 5223 ):
        items=["Power Saver","Reboot","→ Configs saved","Poweroff"]
        menu_display("Power Options",items,display_config)

    elif( menu == 5224 ):
        items=["Power Saver","Reboot","→ Configs saved","→ Camera stopped","Poweroff"]
        menu_display("Power Options",items,display_config)

    elif( menu == 5225 ):
        items=["Power Saver","Reboot","→ Configs saved","→ Camera stopped","→ Rebooting now . . .","Poweroff"]
        menu_display("Power Options",items,display_config)

    elif( menu == 533 ):
        items=["Power Saver","Reboot","Poweroff → Sure ?"]
        menu_display("Power Options",items,display_config)

    elif( menu == 5334 ):
        items=["Power Saver","Reboot","Poweroff","→ Configs saved"]
        menu_display("Power Options",items,display_config)

    elif( menu == 5335 ):
        items=["Power Saver","Reboot","Poweroff","→ Configs saved","→ Camera stopped"]
        menu_display("Power Options",items,display_config)
    elif( menu == 5336 ):
        items=["Power Saver","Reboot","Poweroff","→ Configs saved","→ Camera stopped","→ Bye Bye !!!"]
        menu_display("Power Options",items,display_config)
