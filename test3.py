
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import sys
import time
import json
import requests

#Import Blinka
import digitalio
import board

# Import Python Imaging Library
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.ili9341 as ili9341

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

# First define some constants to allow easy resizing of shapes.
BORDER = 20
FONTSIZE = 24
 
# Configuration for CS and DC pins (these are PiTFT defaults):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)
 
# Config for display baudrate (default max is 24mhz):
BAUDRATE = 64000000
 
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
	width=430, height=320, x_offset=53, y_offset=40
)
# pylint: enable=line-too-long
 
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
 
# Display image.
disp.image(image)
