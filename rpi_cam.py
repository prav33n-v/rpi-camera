#!/usr/bin/env python3

import os
import shutil
import time
import signal
import threading
import RPi.GPIO as GPIO
from gpiozero import Button
import lib.camera as camera
import lib.display as lcd
import lib.operations as operation

# Output
LED = 17
BUZZER = 9
# Input
UP=Button(13,hold_time=0.01)
DOWN=Button(12,hold_time=0.01)
LEFT=Button(16,hold_time=0.01)
RIGHT=Button(19,hold_time=0.01)
MENU=Button(26,hold_time=0.01)
SHUTTER=Button(6,hold_time=0.01)
BACK=Button(5,hold_time=0.01)

GPIO.setwarnings(False)
# Setup RPI.GPIO with "BCM" numbering scheme
GPIO.setmode(GPIO.BCM)
# We must set the backlight pin up as an output first
GPIO.setup(18, GPIO.OUT)
# Set up our pin as a PWM output at 500Hz
backlight = GPIO.PWM(18, 500)

# Notification LED 
GPIO.setup(LED, GPIO.OUT, initial=GPIO.LOW)
# Buzzer
GPIO.setup(BUZZER, GPIO.OUT, initial=GPIO.LOW)

# Exposure time OR Shutter Speed in microseconds
exposure_time=[0,625,800,1000,1250,1562,2000,2500,3125,4000,5000,6250,8000,10000,12500,16667,20000,25000,33333,40000,50000,66667,76923,100000,125000,166667,200000,250000,333333,400000,500000,625000,769231,1000000,1300000,1600000,2000000,2500000,3000000,4000000,5000000,6000000,8000000,10000000,13000000,15000000,20000000,25000000,30000000,60000000]
image_height=[1600,2048,2464,3008,3264,3888,4000,4656]
image_width=[1200,1536,1632,2000,2448,2592,2800,3496]
# Key input delay
wait = 0.5

def display_sleep(brightness,sleep):
    if(sleep):
        for x in range (brightness,-1,-1):
            backlight.ChangeDutyCycle(x)
            time.sleep(0.01)
    else:
        for x in range (0,brightness+1,1):
            backlight.ChangeDutyCycle(x)
            time.sleep(0.01)

def set_LED():
    if(display_config["status_led"]):
        GPIO.output(LED, GPIO.HIGH)

def reset_LED():
    GPIO.output(LED, GPIO.LOW)

def buzz():
    if(display_config["sound"]):
        GPIO.output(BUZZER, GPIO.HIGH)
        time.sleep(0.1)
    GPIO.output(BUZZER, GPIO.LOW)

def init(display_config,shoot_config,camera_config):
    backlight.start(1)
    set_LED()
    lcd.boot_disp("start.jpg")
    camera.initialize_camera(camera_config)
    display_sleep(display_config["brightness"],False)
    buzz()
    reset_LED()

def end_program(image_name="reboot.jpg"):
    lcd.boot_disp(image_name)
    camera.stop_camera()
    GPIO.cleanup()       # clean up GPIO on CTRL+C exit

def lcd_viewfinder():
    global display_config,shoot_config,camera_config
    while(True):	# Continuously show image preview on screen if busy flag is set to False
        if(display_config["menu"] == 0 and display_config["busy"] == False):
            lcd.camera_home(display_config,shoot_config,camera_config,camera.shoot_preview(camera_config))
        else:
            pass	# Do nothing
        time.sleep(camera_config["refresh_time"])

def key_input(input_value):
    global display_config,shoot_config,camera_config
    if(input_value == 0):                                                             # BACK key
        if(display_config["menu"] == -1):
            display_sleep(display_config["brightness"],False)
            display_config["busy"] = False
        display_config,shoot_config,camera_config = operation.back_button(display_config,shoot_config,camera_config)

    elif(input_value == 2):                                                           # Down key
        display_config,shoot_config,camera_config = operation.down_button(display_config,shoot_config,camera_config)

    elif(input_value == 4):                                                           # Left key being used as DECREMENT ( - )
        display_config,shoot_config,camera_config = operation.left_button(display_config,shoot_config,camera_config)
        if(display_config["menu"] == 31):
            backlight.ChangeDutyCycle(display_config["brightness"])

    elif(input_value == 5):                                                           # Right key being used as INCREMENT ( + )
        display_config,shoot_config,camera_config = operation.right_button(display_config,shoot_config,camera_config)
        if(display_config["menu"] == 31):
            backlight.ChangeDutyCycle(display_config["brightness"])

    elif(input_value == 3):                                                           # UP key
        display_config,shoot_config,camera_config = operation.up_button(display_config,shoot_config,camera_config)

    elif(input_value == 1):                                                           # MENU key
        if(display_config["menu"] == -1):
            display_sleep(display_config["brightness"],False)
        display_config,shoot_config,camera_config = operation.ok_menu_button(display_config,shoot_config,camera_config)
        if(((display_config["menu"] > 30) and (display_config["menu"] < 40)) or ((display_config["menu"] > 4000) and (display_config["menu"] < 5000))):
            backlight.ChangeDutyCycle(display_config["brightness"])
        if(display_config["menu"] == -2):
            display_config["menu"] = -1
            display_config["busy"] = True
            display_sleep(display_config["brightness"],True)
    else:										# SHUTTER KEY
        set_LED()
        display_config,shoot_config,camera_config = operation.shutter_button(display_config,shoot_config,camera_config)
        reset_LED()
        buzz()
        time.sleep(camera_config["wait_time"])
        display_config["busy"] = not display_config["busy"]

def down():
    key_input(2)

def up():
    key_input(3)

def left():
    key_input(4)

def right():
    key_input(5)

def shutter():
    key_input(7)

def back():
    key_input(0)

def menu():
    key_input(1)

def key_thread():
    try:
        UP.when_held = up
        DOWN.when_held = down
        LEFT.when_held = left
        RIGHT.when_held  = right
        SHUTTER.when_held = shutter
        BACK.when_held = back
        MENU.when_held = menu
        signal.pause()
    except:
        print("Keyboard interrupt detected")
        display_config["menu"] == 0
        operation.save_settings(display_config,shoot_config,camera_config,"auto_saved")
        print("Current settings saved")
        end_program("crashed.jpg")

###############################################################################################################
# main()
###############################################################################################################

def main():
    global display_config,shoot_config,camera_config,keypress
    display_config,shoot_config,camera_config = operation.load_settings("auto_saved")
    init(display_config,shoot_config,camera_config)
    viewfinder_thread = threading.Thread(target=lcd_viewfinder)
    key_input_thread =  threading.Thread(target=key_thread)
    try:
        lcd.camera_home(display_config,shoot_config,camera_config,camera.shoot_preview(camera_config))
        viewfinder_thread.start()
        time.sleep(1)
        key_input_thread.start()
    except KeyboardInterrupt:
        viewfinder_thread.join()
        key_input_thread.join()
        print("Keyboard interrupt detected")
        display_config["menu"] == 0
        operation.save_settings(display_config,shoot_config,camera_config,"auto_saved")
        print("Current settings saved")
        end_program("crashed.jpg")

if __name__ == '__main__':
    main()

