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
from menu import Menu
import ulab.numpy as np
from drumstep import DrumSequencer
from joystick import JoystickEventManager
import adafruit_bitmapsaver
import traceback

display = board.DISPLAY

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
# def draw_text2(bitmap, text, dx, dy):
#     # bitmaptools.fill_region(bitmap, 0,0, 40,40, 2)
#     print('font bitmap is',font.bitmap.width, font.bitmap.height)
#     pal2 = displayio.Palette(2)
#     pal2[0] = 0x00ff00
#     pal2[1] = 0xff00ff
#     pal2.make_transparent(1)
#     grid2 = displayio.TileGrid(font.bitmap, pixel_shader=pal2, width=10 , height=1, tile_width=6, tile_height=12, x=0, y=0)
#     for x,c in enumerate(text):
#         print('x is',x,c,ord(c))
#         grid2[x,0] = ord(c)-32
#     group.append(grid2)

group = displayio.Group()


enable = digitalio.DigitalInOut(board.SPEAKER_ENABLE)
enable.direction = digitalio.Direction.OUTPUT
enable.value = True

audio = AudioOut(board.SPEAKER, right_channel=board.A1)
# audio = AudioOut(board.SPEAKER)

mixer = audiomixer.Mixer(sample_rate=22050, buffer_size=2048, channel_count=1)
audio.play(mixer)
mixer.voice[0].level = 0.5  # 25% volume might be better


# menu = Menu([
#     {'label':'Play N50, default syn', 'action':audio_demo_1},
#     {'label':'Play Chord','action':demo_play_chord},
#     {'label':'Chord w/ ADSR', 'action':demo_with_adsr},
#     {'label':'vibrato','action':demo_vibrato},
#     {'label':'tremolo', 'action':demo_tremolo},
#     {'label':'saw wave', 'action':demo_sine_wave},
#     {'label':'fat saw wave', 'action':demo_fatsaw},
#     {'label':'kick drum', 'action':demo_kickdrum},
#     {'label':'snare drum', 'action':demo_snare},
#     {'label':'high hat', 'action':demo_highhat},
#     ],
#     bgcolor=0xff0000,
#     fgcolor=0xffffff)
# group.append(menu.grids)
# draw_text2(bitmap, 'hello', 20, 10)

sequencer = DrumSequencer(mixer)
group.append(sequencer)
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


while True:
    key = k.events.get()
    if key:
        keys[key.key_number] = key.pressed
        if KEY_START in keys and KEY_SELECT in keys and keys[KEY_START] and keys[KEY_SELECT]:
            print("doing a screenshot")
            try:
                adafruit_bitmapsaver.save_pixels('/screenshot.bmp',pixel_source=display)
                print("saved the screenshot")
            except BaseException as e:
                print("couldnt take screenshot")
                print(''.join(traceback.format_exception(e)))
    sequencer.update(joystick.update(), key)
    pass
    # event = k.events.get()
    # if event:
    #     # print(event)
    #     if(event.key_number == 1 and event.pressed):
    #         menu.choose_active_item()
    # event = joystick.update()
    # if event:
    #     if event.pressed and event.key_number == 32:
    #         menu.goto_prev_item()
    #     if event.pressed and event.key_number == 34:
    #         menu.goto_next_item()

