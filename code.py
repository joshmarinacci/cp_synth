import time
import board
import usb_cdc
import os
import array
import digitalio
import sys
import math
import random
import displayio
import terminalio
import bitmaptools
import keypad
import analogio
import synthio
import audiomixer
from audioio import AudioOut
from audiocore import RawSample
from menu import Menu, MenuNumberEditor, MenuItemAction, MenuHeader, SubMenu
import ulab.numpy as np
from drumstep import DrumSequencer
from joystick import JoystickEventManager
import adafruit_bitmapsaver
import traceback
import storage

display = board.DISPLAY

font = terminalio.FONT
# font glyphs are in a single very wide bitmap. 
# every glyph has the same pixel size
# every glyph has a tile index
# glyph.tile_index * font.get_bounding_box().width = start of glyph in bitmap
# this is true for the terminal io font. others might not be.

# def draw_text(bitmap,text,dx,dy):
# bitmaptools.fill_region(bitmap, 0,0, 40,40, 2)
# for c in text:
#     glyph = font.get_glyph(ord(c))
#     if not glyph:
#         continue
#     gx = width*glyph.tile_index
#     bitmaptools.rotozoom(
#         dest_bitmap=bitmap, 
#         ox=dx, oy=dy, 
#         dest_clip0=(dx,dy), dest_clip1=(dx+6,dy+12), 
#         source_bitmap=glyph.bitmap, 
#         source_clip0=(gx,0), source_clip1=(gx+6,12),
#         px=gx, py=0,
#         skip_index=0, # skip black, only draw white.
#         )
#     dx += glyph.shift_x

# group = displayio.Group()

# draw_text(bitmap,'hello',20,10)
# put the first text here
# grid = displayio.TileGrid(bitmap,pixel_shader=pal)
# group.append(grid)

# another way is to turn the font's bitmap into a tilegrid
# and set the tiles to the letters we want
# but this only works with a monospace font
# we can choose a color to draw in
# but we can't do a background, say, for inverted colors
# but we *can* make the background transparent, or the foreground
# so maybe if each row is a different tilegrid, then we can invert the selected one.

group = displayio.Group()
class DebugTextOverlay():
    def __init__(self, font, text) -> None:
        print('font bitmap is',font.bitmap.width, font.bitmap.height)
        pal = displayio.Palette(2)
        pal[0] = 0x000000
        pal[1] = 0x000000
        pal.make_transparent(1)
        self.grid = displayio.TileGrid(font.bitmap, pixel_shader=pal, width=28 , height=1, tile_width=6, tile_height=12, x=0, y=0)
    def setText(self, text):
        for x,c in enumerate(text):
            # print('x is',x,c,ord(c))
            if x < self.grid.width:
                self.grid[x,0] = ord(c)-32


# enable = digitalio.DigitalInOut(board.SPEAKER_ENABLE)
# enable.direction = digitalio.Direction.OUTPUT
# enable.value = True

# audio = AudioOut(board.SPEAKER, right_channel=board.A1)
# mixer = audiomixer.Mixer(sample_rate=22050, buffer_size=2048, channel_count=1)
# audio.play(mixer)
# mixer.voice[0].level = 0.5  # 25% volume might be better

volume = 0.5
def get_volume():
    print("getting the volume")
    return volume

def print_hello():
    print('hello')

def set_volume(val):
    global volume
    print('setting the volume')
    volume = val

menu = Menu([
    MenuHeader(title='MENU'),
    MenuItemAction(action=print_hello, title='print hello'),
    MenuNumberEditor(getter=get_volume, setter=set_volume, min=0, max=1.0, step=0.1),
    SubMenu([
        MenuItemAction(action=print_hello, title='print hello'),
        MenuItemAction(action=print_hello, title='print hello'),
        MenuItemAction(action=print_hello, title='print hello'),
    ], title='go to sub menu >')
], title='Main Menu')    
# menu = Menu([
    # {'label':'Play N50, default syn', 'action':audio_demo_1},
    # {'label':'Play Chord','action':demo_play_chord},
    # {'label':'Chord w/ ADSR', 'action':demo_with_adsr},
    # {'label':'vibrato','action':demo_vibrato},
    # {'label':'tremolo', 'action':demo_tremolo},
    # {'label':'saw wave', 'action':demo_sine_wave},
    # {'label':'fat saw wave', 'action':demo_fatsaw},
    # {'label':'kick drum', 'action':demo_kickdrum},
    # {'label':'snare drum', 'action':demo_snare},
    # {'label':'high hat', 'action':demo_highhat},
    # ],
    # bgcolor=0xff0000,
    # fgcolor=0xffffff)
group.append(menu)
# draw_text2(bitmap, 'hello', 20, 10)

# sequencer = DrumSequencer(mixer)
# group.append(sequencer)
display.root_group = group

k = keypad.ShiftRegisterKeys(
    clock=board.BUTTON_CLOCK,
    data=board.BUTTON_OUT,
    latch=board.BUTTON_LATCH,
    key_count=8,
    value_when_pressed=True,
)

joystick = JoystickEventManager()

KEY_START = 2
KEY_SELECT = 3
keys = {}

debug = DebugTextOverlay(terminalio.FONT, 'foo')
debug.grid.x = 0
debug.grid.y = 9*12 + 8
group.append(debug.grid)

debug.setText("")

def do_screenshot():
    print("doing a screenshot")
    debug.setText("screenshot")
    try:
        storage.remount("/", False)
        adafruit_bitmapsaver.save_pixels('/screenshot.bmp',pixel_source=display)
        print("saved the screenshot")
        debug.setText("saved screenshot")
    except BaseException as e:
        debug.setText("failed screenshot")
        print("couldnt take screenshot")
        print(''.join(traceback.format_exception(e)))

while True:
    key = k.events.get()
    if key:
        keys[key.key_number] = key.pressed
        if KEY_START in keys and KEY_SELECT in keys and keys[KEY_START] and keys[KEY_SELECT]:
            do_screenshot()
    joy = joystick.update()
    # sequencer.update(joy, key)
    menu.update(joy,key)
