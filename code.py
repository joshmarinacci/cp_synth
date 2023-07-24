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




display = board.DISPLAY

# make a menu class
# takes a list of action dicts
# each action has a label field and a perform function

# pal = displayio.Palette(3)
# pal[0] = 0x000000
# pal[1] = 0xffffff
# pal[2] = 0xff0000

# bitmap = displayio.Bitmap(display.width,display.height,3)
# bitmap.fill(0)

# font = terminalio.FONT
# print("font is",font.get_bounding_box())
# width, height = font.get_bounding_box()
# print('width, height',width,height)
# print("glyph is", font.get_glyph(65))

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

def audio_demo_1():
    synth = synthio.Synthesizer(sample_rate=22050)
    mixer.voice[0].play(synth)

    note = 50
    synth.press(note) # midi note 65 = F4
    time.sleep(0.5)
    synth.release(note) # release the note we pressed
    time.sleep(0.5)

def demo_play_chord():
    synth = synthio.Synthesizer(sample_rate=22050)
    mixer.voice[0].play(synth)
    synth.press( (65,69,72) ) # midi notes 65,69,72  = F4, A4, C5
    time.sleep(0.5)
    synth.release( (65,69,72) )
    time.sleep(0.5)

def demo_with_adsr():
    synth = synthio.Synthesizer(sample_rate=22050)
    mixer.voice[0].play(synth)
    amp_env_slow = synthio.Envelope(attack_time=0.2, release_time=0.8, sustain_level=1.0)
    amp_env_fast = synthio.Envelope(attack_time=0.01, release_time=0.2, sustain_level=0.5)
    synth.envelope = amp_env_fast  # could also set in synth constructor
    synth.press( (65,69,72) ) # midi notes 65,69,72  = F4, A4, C5
    time.sleep(0.5)
    synth.release( (65,69,72) )
    time.sleep(0.5)

def demo_vibrato():
    synth = synthio.Synthesizer(sample_rate=22050)
    mixer.voice[0].play(synth)
    midi_note = 65
    lfo = synthio.LFO(rate=5, scale=0.05)  # 5 Hz lfo at 0.5%
    note = synthio.Note( synthio.midi_to_hz(midi_note), bend=lfo )
    synth.press(note)
    time.sleep(1)
    synth.release(note)

def demo_tremolo():
    midi_note = 65
    lfo_tremo3 = synthio.LFO(rate=3)  # 1 Hz for lower note
    synth = synthio.Synthesizer(sample_rate=22050)
    mixer.voice[0].play(synth)
    note1 = synthio.Note( synthio.midi_to_hz(midi_note), amplitude=lfo_tremo3)
    synth.press(note1)
    time.sleep(3)
    synth.release(note1)

def demo_sine_wave():
    synth = synthio.Synthesizer(sample_rate=22050)
    mixer.voice[0].play(synth)
    midi_note = 65
    SAMPLE_SIZE = 512
    SAMPLE_VOLUME = 32000  # 0-32767
    wave_sine = np.array(np.sin(np.linspace(0, 2*np.pi, SAMPLE_SIZE, endpoint=False)) * SAMPLE_VOLUME, dtype=np.int16)
    wave_saw = np.linspace(SAMPLE_VOLUME, -SAMPLE_VOLUME, num=SAMPLE_SIZE, dtype=np.int16)
    note = synthio.Note( synthio.midi_to_hz(midi_note), waveform=wave_saw)
    synth.press(note)
    time.sleep(1)
    synth.release(note)

def demo_fatsaw():
    synth = synthio.Synthesizer(sample_rate=22050)
    mixer.voice[0].play(synth)
    midi_note = 65
    SAMPLE_SIZE = 512
    SAMPLE_VOLUME = 32000  # 0-32767

    detune = 0.005  # how much to detune, 0.7% here
    # num_oscs = 1
    midi_note = 45
    for num_oscs in range(1,5):
        print("saw with ",num_oscs)
        notes = []  # holds note objs being pressed
        # simple detune, always detunes up
        for i in range(num_oscs):
            f = synthio.midi_to_hz(midi_note) * (1 + i*detune)
            notes.append( synthio.Note(frequency=f) )
        synth.press(notes)
        time.sleep(1)
        synth.release(notes)
        time.sleep(0.1)


def demo_kickdrum():        
    SAMPLE_SIZE = 200
    sinwave1 = np.array(np.sin(np.linspace(0, 2*np.pi, SAMPLE_SIZE, endpoint=False)) * 32767, dtype=np.int16)
    sinwave2 = np.array(np.sin(np.linspace(np.pi/2, 2.5*np.pi, SAMPLE_SIZE, endpoint=False)) * 32767, dtype=np.int16)
    downwave = np.linspace(32767, -32767, num=3, dtype=np.int16)

    # noisewave = np.array([random.randint(-32767, 32767) for i in range(SAMPLE_SIZE)], dtype=np.int16)
    # w1 = np.array( [int(max(min(sinwave1[i] + (noisewave[i]/2.0), 32767), -32767)) for i in range(SAMPLE_SIZE)], dtype=np.int16)
    # w2 = np.array( [int(max(min(sinwave2[i] + (noisewave[i]/2.0), 32767), -32767)) for i in range(SAMPLE_SIZE)], dtype=np.int16)

    synth = synthio.Synthesizer(sample_rate=22050)
    mixer.voice[0].play(synth)

    lfo = synthio.LFO(waveform=downwave)
    lfo.once = True
    lfo.offset=0.33
    lfo.scale = 0.3
    lfo.rate=20
    
    filter_fr = 2000
    lpf = synth.low_pass_filter(frequency=filter_fr)

    amp_env1 = synthio.Envelope(attack_time=0.0, decay_time=0.075, release_time=0, attack_level=1, sustain_level=0)
    note1 = synthio.Note(frequency=53, envelope=amp_env1, waveform=sinwave2, filter=lpf, bend=lfo)

    amp_env2 = synthio.Envelope(attack_time=0.0, decay_time=0.055, release_time=0, attack_level=1, sustain_level=0)
    note2 = synthio.Note(frequency=72, envelope=amp_env2, waveform=sinwave1, filter=lpf, bend=lfo)

    amp_env3 = synthio.Envelope(attack_time=0.0, decay_time=0.095, release_time=0, attack_level=1, sustain_level=0)
    note3 = synthio.Note(frequency=41, envelope=amp_env3, waveform=sinwave2, filter=lpf, bend=lfo)

    for count in range(4):
        lfo.retrigger()
        print("triggering the kick")
        synth.press((note1, note2, note3))
        time.sleep(0.25)
        synth.release((note1, note2, note3))
        time.sleep(0.25)


def demo_snare():
    SAMPLE_SIZE = 200
    sinwave1 = np.array(np.sin(np.linspace(0, 2*np.pi, SAMPLE_SIZE, endpoint=False)) * 32767, dtype=np.int16)
    sinwave2 = np.array(np.sin(np.linspace(np.pi/2, 2.5*np.pi, SAMPLE_SIZE, endpoint=False)) * 32767, dtype=np.int16)
    downwave = np.linspace(32767, -32767, num=3, dtype=np.int16)
    noisewave = np.array([random.randint(-32767, 32767) for i in range(SAMPLE_SIZE)], dtype=np.int16)
    w1 = np.array( [int(max(min(sinwave1[i] + (noisewave[i]/2.0), 32767), -32767)) for i in range(SAMPLE_SIZE)], dtype=np.int16)
    w2 = np.array( [int(max(min(sinwave2[i] + (noisewave[i]/2.0), 32767), -32767)) for i in range(SAMPLE_SIZE)], dtype=np.int16)

    lfo = synthio.LFO(waveform=downwave)
    lfo.once = True
    lfo.offset=0.33
    lfo.scale = 0.3
    lfo.rate=20

    synth = synthio.Synthesizer(sample_rate=22050)
    mixer.voice[0].play(synth)
    filter_fr = 9500
    lpf = synth.low_pass_filter(filter_fr)

    amp_env1 = synthio.Envelope(attack_time=0.0, decay_time=0.115, release_time=0, attack_level=1, sustain_level=0)
    note1 = synthio.Note(frequency=90, envelope=amp_env1, waveform=w1, filter=lpf, bend=lfo)

    amp_env2 = synthio.Envelope(attack_time=0.0, decay_time=0.095, release_time=0, attack_level=1, sustain_level=0)
    note2 = synthio.Note(frequency=135, envelope=amp_env2, waveform=w2, filter=lpf, bend=lfo)

    amp_env3 = synthio.Envelope(attack_time=0.0, decay_time=0.115, release_time=0, attack_level=1, sustain_level=0)
    note3 = synthio.Note(frequency=165, envelope=amp_env3, waveform=w2, filter=lpf, bend=lfo)
    for count in range(4):
        lfo.retrigger()
        print("triggering the snare")
        synth.press((note1, note2, note3))
        time.sleep(0.25)
        synth.release((note1, note2, note3))
        time.sleep(0.25)


def demo_highhat():
    SAMPLE_SIZE = 200
    sinwave1 = np.array(np.sin(np.linspace(0, 2*np.pi, SAMPLE_SIZE, endpoint=False)) * 32767, dtype=np.int16)
    sinwave2 = np.array(np.sin(np.linspace(np.pi/2, 2.5*np.pi, SAMPLE_SIZE, endpoint=False)) * 32767, dtype=np.int16)
    downwave = np.linspace(32767, -32767, num=3, dtype=np.int16)
    noisewave = np.array([random.randint(-32767, 32767) for i in range(SAMPLE_SIZE)], dtype=np.int16)
    w1 = np.array( [int(max(min(sinwave1[i] + (noisewave[i]/2.0), 32767), -32767)) for i in range(SAMPLE_SIZE)], dtype=np.int16)
    w2 = np.array( [int(max(min(sinwave2[i] + (noisewave[i]/2.0), 32767), -32767)) for i in range(SAMPLE_SIZE)], dtype=np.int16)


    lfo = synthio.LFO(waveform=downwave)
    lfo.once = True
    lfo.offset=0.33
    lfo.scale = 0.3
    lfo.rate=20
    
    synth = synthio.Synthesizer(sample_rate=22050)
    mixer.voice[0].play(synth)
    t = 0.115
    filter_fr = 9500
    hpf = synth.high_pass_filter(filter_fr)

    amp_env1 = synthio.Envelope(attack_time=0.0, decay_time=t, release_time=0, attack_level=1, sustain_level=0)
    note1 = synthio.Note(frequency=90, envelope=amp_env1, waveform=noisewave, filter=hpf, bend=lfo)

    amp_env2 = synthio.Envelope(attack_time=0.0, decay_time=t-0.02, release_time=0, attack_level=1, sustain_level=0)
    note2 = synthio.Note(frequency=135, envelope=amp_env2, waveform=noisewave, filter=hpf, bend=lfo)

    amp_env3 = synthio.Envelope(attack_time=0.0, decay_time=t, release_time=0, attack_level=1, sustain_level=0)
    note3 = synthio.Note(frequency=165, envelope=amp_env3, waveform=noisewave, filter=hpf, bend=lfo)

    for count in range(4):
        lfo.retrigger()
        print("triggering the kick")
        synth.press((note1, note2, note3))
        time.sleep(0.25)
        synth.release((note1, note2, note3))
        time.sleep(0.25)



menu = Menu([
    {'label':'Play N50, default syn', 'action':audio_demo_1},
    {'label':'Play Chord','action':demo_play_chord},
    {'label':'Chord w/ ADSR', 'action':demo_with_adsr},
    {'label':'vibrato','action':demo_vibrato},
    {'label':'tremolo', 'action':demo_tremolo},
    {'label':'saw wave', 'action':demo_sine_wave},
    {'label':'fat saw wave', 'action':demo_fatsaw},
    {'label':'kick drum', 'action':demo_kickdrum},
    {'label':'snare drum', 'action':demo_snare},
    {'label':'high hat', 'action':demo_highhat},
    ],
    bgcolor=0xff0000,
    fgcolor=0xffffff)
group.append(menu.grids)
# draw_text2(bitmap, 'hello', 20, 10)

display.root_group = group

joystick_x = analogio.AnalogIn(board.JOYSTICK_X)
joystick_y = analogio.AnalogIn(board.JOYSTICK_Y)

k = keypad.ShiftRegisterKeys(
    clock=board.BUTTON_CLOCK,
    data=board.BUTTON_OUT,
    latch=board.BUTTON_LATCH,
    key_count=8,
    value_when_pressed=True,
)

class JoystickEventManager():
    def __init__(self, up_number=32) -> None:
        self.up_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        self.down_pressed = False
        self.up_number=32
        pass
    def update(self):
        # print("joystick updating", joystick_x.value, joystick_y.value)
        if joystick_y.value < 30000 and not self.up_pressed:
            self.up_pressed = True
            return keypad.Event(self.up_number+0, pressed=True)
        if joystick_y.value >= 30000 and self.up_pressed:
            self.up_pressed = False
            return keypad.Event(self.up_number+0, pressed=False)
        if joystick_x.value > 35000 and not self.right_pressed:
            self.right_pressed = True
            return keypad.Event(self.up_number+1, pressed=True)
        if joystick_x.value <= 35000 and self.right_pressed:
            self.right_pressed = False
            return keypad.Event(self.up_number+1, pressed=False)
        if joystick_y.value > 35000 and not self.down_pressed:
            self.down_pressed = True
            return keypad.Event(self.up_number+2, pressed=True)
        if joystick_y.value <= 35000 and self.down_pressed:
            self.down_pressed = False
            return keypad.Event(self.up_number+2, pressed=False)
        if joystick_x.value < 30000 and not self.left_pressed:
            self.left_pressed = True
            return keypad.Event(self.up_number+3, pressed=True)
        if joystick_x.value <= 30000 and self.left_pressed:
            self.left_pressed = True
            return keypad.Event(self.up_number+3, pressed=False)
        return None

joystick = JoystickEventManager()
while True:
    event = k.events.get()
    if event:
        # print(event)
        if(event.key_number == 1 and event.pressed):
            menu.choose_active_item()
    event = joystick.update()
    if event:
        if event.pressed and event.key_number == 32:
            menu.goto_prev_item()
        if event.pressed and event.key_number == 34:
            menu.goto_next_item()

