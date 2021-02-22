# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT
 
"""
This demo will draw a few rectangles onto the screen along with some text
on top of that.
 
This example is for use on (Linux) computers that are using CPython with
Adafruit Blinka to support CircuitPython libraries. CircuitPython does
not support PIL/pillow (python imaging library)!
 
Author(s): Melissa LeBlanc-Williams for Adafruit Industries
"""
 
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.ili9341 as ili9341
import adafruit_rgb_display.st7789 as st7789  # pylint: disable=unused-import
import adafruit_rgb_display.hx8357 as hx8357  # pylint: disable=unused-import
import adafruit_rgb_display.st7735 as st7735  # pylint: disable=unused-import
import adafruit_rgb_display.ssd1351 as ssd1351  # pylint: disable=unused-import
import adafruit_rgb_display.ssd1331 as ssd1331  # pylint: disable=unused-import
 
# First define some constants to allow easy resizing of shapes.
BORDER = 20
FONTSIZE = 24
 
# Configuration for CS and DC pins (these are PiTFT defaults):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)
 
# Config for display baudrate (default max is 24mhz):
BAUDRATE = 24000000
 
# Setup SPI bus using hardware SPI:
spi = board.SPI()
 
# pylint: disable=line-too-long
# Create the display:
# disp = st7789.ST7789(spi, rotation=90,                            # 2.0" ST7789
# disp = st7789.ST7789(spi, height=240, y_offset=80, rotation=180,  # 1.3", 1.54" ST7789
# disp = st7789.ST7789(spi, rotation=90, width=135, height=240, x_offset=53, y_offset=40, # 1.14" ST7789
# disp = hx8357.HX8357(spi, rotation=180,                           # 3.5" HX8357
# disp = st7735.ST7735R(spi, rotation=90,                           # 1.8" ST7735R
# disp = st7735.ST7735R(spi, rotation=270, height=128, x_offset=2, y_offset=3,   # 1.44" ST7735R
# disp = st7735.ST7735R(spi, rotation=90, bgr=True,                 # 0.96" MiniTFT ST7735R
# disp = ssd1351.SSD1351(spi, rotation=180,                         # 1.5" SSD1351
# disp = ssd1351.SSD1351(spi, height=96, y_offset=32, rotation=180, # 1.27" SSD1351
# disp = ssd1331.SSD1331(spi, rotation=180,                         # 0.96" SSD1331
disp = ili9341.ILI9341(
    spi,
    rotation=90,  # 2.2", 2.4", 2.8", 3.2" ILI9341
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
)
# pylint: enable=line-too-long
 
# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
if disp.rotation % 180 == 90:
    height = disp.width  # we swap height/width to rotate it to landscape!
    width = disp.height
else:
    width = disp.width  # we swap height/width to rotate it to landscape!
    height = disp.height
 
image = Image.new("RGB", (width, height))
 
# -*- coding: utf-8 -*-
import sys
import time
import json
import busio
import digitalio
import requests
from board import SCK, MOSI, MISO, D2, D3


#Import Blinka
import digitalio
import board

def get_ethermine_values(wallet):
    api_url = "https://api.ethermine.org/miner/{}/dashboard".format(wallet)
    r = requests.get(api_url)
    data = json.loads(r.text)
    ret_value = {}
    ret_value["unpaid"] = data["data"]["currentStatistics"]["unpaid"]/1000000000000000000
    ret_value["workers"] = data["data"]["currentStatistics"]["activeWorkers"]
    ret_value["reported_hashrate"] = data["data"]["currentStatistics"]["reportedHashrate"]/1000000
    ret_value["actual_hashrate"] = data["data"]["currentStatistics"]["currentHashrate"]/1000000
    ret_value["invalid_shares"] = data["data"]["currentStatistics"]["invalidShares"]
    ret_value["stale_shares"] = data["data"]["currentStatistics"]["staleShares"]
    return ret_value

def get_flexpool_values(wallet):
    base_api_url = "https://flexpool.io/api/v1/miner/" + '0x' + wallet
    ret_value = {}

    # Get unpaid
    r = requests.get(base_api_url+"/balance")
    data = json.loads(r.text)
    ret_value["unpaid"] = data["result"]

    # Get unpaid
    r = requests.get(base_api_url+"/workerCount")
    data = json.loads(r.text)
    ret_value["workers"] = data["result"]["online"]

    # Get other stats
    r = requests.get(base_api_url+"/stats")
    data = json.loads(r.text)
    ret_value["reported_hashrate"] = data["result"]["current"]["reported_hashrate"]/1000000
    ret_value["actual_hashrate"] = data["result"]["current"]["effective_hashrate"]/1000000
    ret_value["invalid_shares"] = data["result"]["daily"]["invalid_shares"]
    ret_value["stale_shares"] = data["result"]["daily"]["stale_shares"]
    return ret_value

if len(sys.argv) != 3 or (sys.argv[1] != "ethermine" and sys.argv[1] != "flexpool"):
    print("Usage: sudo python3 miner.py ethermine|flexpool wallet")
    exit

pool = sys.argv[1]
wallet = sys.argv[2]
if wallet.startswith("0x"):
    wallet = wallet[2:]

value_api_url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"

# Configuration for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 64000000


# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
height = disp.width   # we swap height/width to rotate it to landscape!
width = disp.height
image = Image.new('RGB', (width, height))
rotation = 90

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image, rotation)
# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0
# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 24)
big_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 48)
small_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18)

font_height = font.getsize("a")[1]
big_font_height = big_font.getsize("a")[1]

red = "#FF0000"
green = "#00FF00"
blue = "#0000FF"
yellow = "#FFFF00"

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    if counter == duration:
        try:
            miner_data = get_ethermine_values(wallet) if pool == "ethermine" else get_flexpool_values(wallet)
            r = requests.get(value_api_url)
            data = json.loads(r.text)
            eth_value = data["ethereum"]["usd"]
        except:
            y = top
            draw.text((x,y),"ERROR LOADING DATA", font=font, fill=red)
            print("error")
            time.sleep(60)
            continue

    y = top

    if not buttonA.value:
        state = 1 if state == 0 else 0

    if state == 0:
        draw.text((x,y),"{:.5f}".format(miner_data["unpaid"]),font=big_font, fill=green if miner_data["workers"] >= 2 and miner_data["invalid_shares"] < 3 else red)
        y += big_font_height
        draw.text((x,y),"${:.2f}".format(miner_data["unpaid"]*eth_value), font=big_font, fill=green)
        y += big_font_height
        draw.text((x,y),"${:.2f}".format(eth_value), font=big_font, fill=green)
        draw.text((width-40,0), str(counter), font=small_font, fill=yellow)
    else:
        draw.text((x,y),"Unpaid: ", font=font, fill=blue)
        draw.text((x+font.getsize("Unpaid: ")[0],y), "{:.5f}".format(miner_data["unpaid"]), font=font, fill=green)
        y += font_height
        draw.text((x,y),"Value: ", font=font, fill=blue)
        draw.text((x+font.getsize("Value: ")[0],y+5), "${:.2f} ${:.2f}".format(eth_value*miner_data["unpaid"], eth_value), font=small_font, fill=green)
        y += font_height
        draw.text((x,y),"Workers: Mh/s (R/A):", font=font, fill=blue)
        y += font_height
        draw.text((x,y), "{}: {:.1f} / ".format(miner_data["workers"], miner_data["reported_hashrate"]), font=font, fill=green)
        draw.text((x+font.getsize("{} - {:.1f} / ".format(miner_data["workers"], miner_data["reported_hashrate"]))[0],y), "{:.1f}".format(miner_data["actual_hashrate"]), font=font, fill=green if miner_data["actual_hashrate"] >= miner_data["reported_hashrate"] else yellow)
        y += font_height
        draw.text((x,y),"Stale / Invalid: ", font=font, fill=blue)
        draw.text((x+font.getsize("Stale / Invalid: ")[0],y), str(miner_data["stale_shares"]), font=font, fill=green)
        draw.text((x+font.getsize("Stale / Invalid: {}".format(miner_data["stale_shares"]))[0],y), " / ", font=font, fill=blue)
        draw.text((x+font.getsize("Stale / Invalid: {} / ".format(miner_data["stale_shares"]))[0],y),str(miner_data["invalid_shares"]), font=font, fill=green if miner_data["invalid_shares"] == 0 else red)
        y += font_height
        draw.text((x,y), str(counter), font=small_font, fill=yellow)

    # Display image.
    disp.image(image, rotation)
    counter -= 1
    
    if counter == 0:
        counter = duration
    time.sleep(1)
