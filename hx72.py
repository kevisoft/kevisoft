# -*- coding: utf-8 -*-
import sys
import time
import json
import requests

#Import Blinka
import digitalio
import board
# Import Python Imaging Library
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.hx8357 as hx8357

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
    ret_value["unpaid"] = data["result"]/1000000000000000000

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

def get_hiveon_values(wallet):
    base_api_url = "https://hiveon.net/api/v1/stats/"
    ret_value = {}
    wallet = wallet.lower()

    # Get unpaid
    r = requests.get(base_api_url+"miner/"+wallet+"/ETH/billing-acc")
    data = json.loads(r.text)
    ret_value["unpaid"] = data["totalUnpaid"]

    # Get workers
    r = requests.get(base_api_url+"workers-count?minerAddress="+wallet+"&coin=ETH&window=10m&limit=1")
    data = json.loads(r.text)
    ret_value["workers"] = int(data["items"][0]["count"])

    # Get hashrate stats
    r = requests.get(base_api_url+"hashrates?minerAddress="+wallet+"&coin=ETH&limit=1")
    data = json.loads(r.text)
    ret_value["reported_hashrate"] = int(data["items"][0]["reportedHashrate"])/1000000
    ret_value["actual_hashrate"] = int(data["items"][0]["hashrate"])/1000000
    
    # Get shares stats
    r = requests.get(base_api_url+"shares?minerAddress="+wallet+"&coin=ETH&window=10m&limit=144")
    data = json.loads(r.text)
    invalid_shares, stale_shares = 0, 0
    for item in data["items"]:
        stale_shares += int(item["staleCount"]) if "staleCount" in item else 0
        invalid_shares += int(item["invalidCount"]) if "invalidCount" in item else 0
    ret_value["invalid_shares"] = invalid_shares
    ret_value["stale_shares"] = stale_shares
    return ret_value

if len(sys.argv) != 3 or (sys.argv[1] != "ethermine" and sys.argv[1] != "flexpool" and sys.argv[1] != "hiveon"):
    print("Usage: sudo python3 miner.py ethermine|flexpool|hiveon wallet")
    exit

pool = sys.argv[1]
wallet = sys.argv[2]
if wallet.startswith("0x"):
    wallet = wallet[2:]

value_api_url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"

# Configuration for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.CE1)
reset_pin = None

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 16000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# Create the ST7789 display:
disp = hx8357.HX8357(spi, cs=cs_pin, dc=dc_pin, rst=reset_pin, baudrate=BAUDRATE,
                     width=480, height=320)

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
height = disp.width   # we swap height/width to rotate it to landscape!
width = disp.height
image = Image.new('RGB', (width, height))
rotation = 90

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), fill=(0,0,0))
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
big_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 30)
small_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18)

font_height = font.getsize("a")[1]
big_font = big_font.getsize("a")[1]

red = "#FF0000"
green = "#FFF74C"
blue = "#0000FF"
yellow = "#FFFF00"
purple = "#006600"

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D26)
backlight.switch_to_output()
backlight.value = True

duration = 10
counter = duration

    # Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), fill=(0,0,0))

if counter == duration:
        try:
            miner_data = get_ethermine_values(wallet) if pool == "ethermine" else get_flexpool_values(wallet) if pool == "flexpool" else get_hiveon_values(wallet)
            r = requests.get(value_api_url)
            data = json.loads(r.text)
            eth_value = data["ethereum"]["usd"]
            y = top
            draw.text((x+font.getsize("Unpaid Amount:  ")[0],25), "{:.5f}".format(miner_data["unpaid"]), font=font, fill=green)
            y += font_height
            draw.text((x,100),"Earned/ETH Value: ", font=font, fill=purple)
            draw.text((x+font.getsize("Value: ")[0],90), "${:.2f} ${:.2f}".format(eth_value*miner_data["unpaid"], eth_value), font=big_font, fill=green)
            y += font_height
            draw.text((x,100),"Efficiency (Mh/s):", font=big_font, fill=blue)
            draw.text((x+font.getsize("{} - {:.1f} / ".format(miner_data["workers"], miner_data["reported_hashrate"]))[0],125), "{:.1f}".format(miner_data["actual_hashrate"]), font=big_font, fill=green if miner_data["actual_hashrate"] >= miner_data["reported_hashrate"] else yellow)
            y += font_height
            draw.text((x,140),"Hashrate (Mh/s):", font=big_font, fill=blue)
            y += font_height
            draw.text((x,250), "{}: {:.1f} / ".format(miner_data["workers"], miner_data["reported_hashrate"]), font=big_font, fill=green)
            draw.text((x,350),"Stale / Invalid: ", font=big_font, fill=blue)
            draw.text((x+font.getsize("Stale / Invalid: {} / ".format(miner_data["stale_shares"]))[0],380),str(miner_data["invalid_shares"]), font=big_font, align="center", fill=green if miner_data["invalid_shares"] == 0 else red)
            y += font_height
            draw.text((x+font.getsize("Refreshing in: ")[475],0), str(counter), font=small_font, fill=purple)

        except:
            y = top
            draw.text((x,y),"ERROR LOADING DATA", font=font, fill=red)
            print("error")
            time.sleep(60)

    # Display image.
disp.image(image, rotation)
counter = duration
time.sleep(10)
