import time
import busio
import digitalio
from board import SCK, MOSI, MISO, CE0, CE1

from adafruit_rgb_display import color565
import adafruit_rgb_display.ili9341 as ili9341


# Configuration for CS and DC pins:
CS_PIN = D2
DC_PIN = D3

# Setup SPI bus using hardware SPI:
spi = busio.SPI(clock=SCK, MOSI=MOSI, MISO=MISO)

# Create the ILI9341 display:
disp = hx8357.HX8357(spi, rotation=180,                 
disp = hx8357.HX8357(spi, rotation=90,
                       cs=cs_pin, dc=dc_pin, rst=reset_pin, baudrate=BAUDRATE)          


# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image)
# Draw some shapes.
