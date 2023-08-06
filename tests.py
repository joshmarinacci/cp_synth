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
from drums import HighHat

enable = digitalio.DigitalInOut(board.SPEAKER_ENABLE)
enable.direction = digitalio.Direction.OUTPUT
enable.value = True

SAMPLE_RATE = 22050*2

audio = AudioOut(board.SPEAKER, right_channel=board.A1)
mixer = audiomixer.Mixer(sample_rate=SAMPLE_RATE, buffer_size=2048, channel_count=1)
audio.play(mixer)
mixer.voice[0].level = 0.25  # 25% volume might be better

# synth = synthio.Synthesizer(sample_rate=SAMPLE_RATE)

SAMPLE_SIZE = 512
SAMPLE_VOLUME = 32000  # 0-32767
# downwave = np.linspace(32767, -32767, num=3, dtype=np.int16)
saw_down = np.linspace(SAMPLE_VOLUME, -SAMPLE_VOLUME, num=SAMPLE_SIZE, dtype=np.int16)
saw_up = np.linspace(-SAMPLE_VOLUME, SAMPLE_VOLUME, num=SAMPLE_SIZE, dtype=np.int16)

def make_square(per):
    waveform = np.linspace(-SAMPLE_VOLUME, -SAMPLE_VOLUME, num=SAMPLE_SIZE, dtype=np.int16)
    for i in range(int(SAMPLE_SIZE*per)):
        waveform[i] = SAMPLE_VOLUME
    return waveform


def lerp(a, b, t):  return (1-t)*a + t*b
def make_triangle():
    waveform = np.linspace(0,0,num=SAMPLE_SIZE, dtype=np.int16)
    for i in range(0,SAMPLE_SIZE/2):
        t = i/SAMPLE_SIZE/2
        waveform[i] = lerp(-SAMPLE_VOLUME,SAMPLE_VOLUME,t)
    for i in range(0,SAMPLE_SIZE/2):
        t = i/SAMPLE_SIZE/2
        waveform[i+SAMPLE_SIZE/2] = lerp(SAMPLE_VOLUME,-SAMPLE_VOLUME,t)
    return waveform


square_wav = make_square(0.5)
triangle_wav = make_triangle()
noisewave = np.array([random.randint(-32767, 32767) for i in range(SAMPLE_SIZE)], dtype=np.int16)
plain_saw = np.linspace(-SAMPLE_VOLUME, SAMPLE_VOLUME, num=SAMPLE_SIZE, dtype=np.int16)
noisy_saw = np.linspace(-SAMPLE_VOLUME, SAMPLE_VOLUME, num=SAMPLE_SIZE, dtype=np.int16)
for i in range(0,len(noisy_saw)):
    noisy_saw[i] = lerp(noisewave[i],plain_saw[i],0.75)
# noisy_saw = lerp(noisewave,plain_saw,0.9)

def play_with_waveform(wav):
    synth = synthio.Synthesizer(sample_rate=SAMPLE_RATE, waveform=wav)
    mixer.voice[0].play(synth)
    b = 72-8-8
    notes = [b, b-2, b, b-3, b-5, b-3, b-7, 1]
    speed = 0.20
    for n in notes:
        note = synthio.Note(synthio.midi_to_hz(n))
        synth.press(note)
        time.sleep(speed)
        synth.release(note)
        time.sleep(speed)

def popcorn():
    popcorn = synthio.Envelope(attack_time=0, release_time=0, sustain_level=0, decay_time=0.10)
    synth = synthio.Synthesizer(sample_rate=SAMPLE_RATE, envelope=popcorn)
    b = 72
    notes = [b, b-2, b, b-3, b-5, b-3, b-7, 20]
    speed = 0.10
    mixer.voice[0].play(synth)
    for c in range(4):
        for n in notes:
            # note = synthio.Note( synthio.midi_to_hz(n), bend=lfo )
            note = synthio.Note( 
                synthio.midi_to_hz(n), 
                # amplitude=lfo, 
                # waveform=wave_saw
                )
            synth.press(note)
            time.sleep(speed)
            synth.release(note)
            time.sleep(speed)

def deeda():
    lfo = synthio.LFO(rate=8, scale=0.2, waveform=saw_down)
    synth = synthio.Synthesizer(sample_rate=SAMPLE_RATE)
    mixer.voice[0].play(synth)
    b = 72
    notes = [b,b+1,b+2]
    speed = 1.0
    for n in notes:
        note = synthio.Note( 
            synthio.midi_to_hz(n), 
            bend=lfo,
            # amplitude=lfo, 
            # waveform=wave_saw
              )
        synth.press(note)
        time.sleep(speed)
        synth.release(note)
        time.sleep(speed)

def bladerunner():
    b = 76
    lfo = synthio.LFO(rate=0.1, offset=4000,scale=4000, waveform=saw_up)
    envelope = synthio.Envelope(attack_time=1.0, release_time=1.0, sustain_level=1.0, decay_time=0.1)
    synth = synthio.Synthesizer(sample_rate=SAMPLE_RATE, waveform=noisy_saw)
    synth.blocks.append(lfo)
    mixer.voice[0].play(synth)
    mixer.voice[0].level = 0.25  # 25% volume might be better

    def play_note(f):
        lfo.retrigger()
        keys =[]
        keys.append(synthio.Note(frequency=synthio.midi_to_hz(f) + 0.010, envelope=envelope))
        keys.append(synthio.Note(frequency=synthio.midi_to_hz(f) + 0, envelope=envelope))
        keys.append(synthio.Note(frequency=synthio.midi_to_hz(f) - 0.010, envelope=envelope))
        synth.press(keys)
        for n in range(3000):
            for note in keys:
                note.filter = synth.low_pass_filter(lfo.value,1.5)
            time.sleep(0.001)
        synth.release(keys)
        time.sleep(2)
    play_note(b)
    play_note(b+2)
    play_note(b-2)
    play_note(b)

def tubeway():
    env = synthio.Envelope(attack_time=0.05, decay_time=0.05)
    synth = synthio.Synthesizer(sample_rate=SAMPLE_RATE, waveform=noisy_saw, envelope=env)
    mixer.voice[0].play(synth)
    b = 72-8-8
    notes = [b, b+7, b-2, b+5]
    speed = 0.40

    synth2 = synthio.Synthesizer(sample_rate=SAMPLE_RATE)
    hihat = HighHat(synth2)
    mixer.voice[1].play(synth2)
    start = time.monotonic()
    ni = 0
    cur_note = None
    count = 0
    while count < 8:
        diff = time.monotonic() - start
        if diff > 0.5:
            if cur_note:
                synth.release(cur_note)
                cur_note = None
                hihat.trigger()
                count += 1
            else:
                n = notes[ni]
                cur_note = synthio.Note(synthio.midi_to_hz(n))
                ni = (ni + 1) % len(notes)
                synth.press(cur_note)
                hihat.trigger()
            start = time.monotonic()
        hihat.update()

def square_test():
    play_with_waveform(square_wav)
def triangle_test():
    play_with_waveform(triangle_wav)
def saw_test():
    play_with_waveform(saw_down)
def noisy_saw_test():    
    play_with_waveform(noisy_saw)

def tremolo_test():
    synth = synthio.Synthesizer(sample_rate=SAMPLE_RATE, waveform=triangle_wav)
    mixer.voice[0].play(synth)
    b = 72-8-8
    notes = [b, b-2, b, b-3, b-5, b-3, b-7, 1]
    speed = 0.80
    lfo = synthio.LFO(rate=8)
    for n in notes:
        note = synthio.Note(synthio.midi_to_hz(n), amplitude=lfo)
        synth.press(note)
        time.sleep(speed)
        synth.release(note)
        time.sleep(speed)

def vibrato_test():
    synth = synthio.Synthesizer(sample_rate=SAMPLE_RATE, waveform=triangle_wav)
    mixer.voice[0].play(synth)
    b = 72-8-8
    notes = [b, b-2, b, b-3, b-5, b-3, b-7, 1]
    speed = 0.80
    lfo = synthio.LFO(rate=4, scale=1/12)
    for n in notes:
        note = synthio.Note(synthio.midi_to_hz(n), bend=lfo)
        synth.press(note)
        time.sleep(speed)
        synth.release(note)
        time.sleep(speed)

menu = Menu([
    MenuHeader(title='Synth Tests '),
    # MenuItemAction(title='square wave', action=square_test),
    # MenuItemAction(title='triangle wave', action=triangle_test),
    MenuItemAction(title='saw wave', action=saw_test),
    MenuItemAction(title='noisy saw wave', action=noisy_saw_test),
    MenuItemAction(title='tubeway', action=tubeway),
    MenuItemAction(title='popcorn', action=popcorn),
    MenuItemAction(title='laser effect', action=deeda),
    MenuItemAction(title='bladerunner', action=bladerunner),
    MenuItemAction(title='tremolo', action=tremolo_test),
    MenuItemAction(title='vibrato', action=vibrato_test),
])

display = board.DISPLAY
display.root_group = menu

joystick = JoystickEventManager()
k = keypad.ShiftRegisterKeys(
    clock=board.BUTTON_CLOCK,
    data=board.BUTTON_OUT,
    latch=board.BUTTON_LATCH,
    key_count=8,
    value_when_pressed=True,
)

KEY_START = 2
KEY_SELECT = 3
keys = {}


while True:
    key = k.events.get()
    if key:
        keys[key.key_number] = key.pressed
        # if KEY_START in keys and KEY_SELECT in keys and keys[KEY_START] and keys[KEY_SELECT]:
            # do_screenshot()
    joy = joystick.update()
    menu.update(joy, key)
