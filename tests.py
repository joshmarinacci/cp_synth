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

enable = digitalio.DigitalInOut(board.SPEAKER_ENABLE)
enable.direction = digitalio.Direction.OUTPUT
enable.value = True

audio = AudioOut(board.SPEAKER, right_channel=board.A1)
mixer = audiomixer.Mixer(sample_rate=22050, buffer_size=2048, channel_count=1)
audio.play(mixer)
mixer.voice[0].level = 0.1  # 25% volume might be better

print("hello")
SAMPLE_RATE = 22050

# synth = synthio.Synthesizer(sample_rate=SAMPLE_RATE)

SAMPLE_SIZE = 512
SAMPLE_VOLUME = 32000  # 0-32767
# downwave = np.linspace(32767, -32767, num=3, dtype=np.int16)
saw_down = np.linspace(SAMPLE_VOLUME, -SAMPLE_VOLUME, num=SAMPLE_SIZE, dtype=np.int16)
saw_up = np.linspace(-SAMPLE_VOLUME, SAMPLE_VOLUME, num=SAMPLE_SIZE, dtype=np.int16)

def popcorn():
    # amp_env_slow = synthio.Envelope(attack_time=0.2, release_time=1.0, sustain_level=1.0)
    popcorn = synthio.Envelope(attack_time=0, release_time=0, sustain_level=0, decay_time=0.10)
    synth = synthio.Synthesizer(sample_rate=SAMPLE_RATE, envelope=popcorn)
    b = 72
    notes = [b, b-2, b, b-3, b-5, b-3, b-7, 20]
    speed = 0.10
    mixer.voice[0].play(synth)
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
# lfo = synthio.LFO(rate=8)  # 5 Hz lfo at 0.5%

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
    synth = synthio.Synthesizer(sample_rate=SAMPLE_RATE, waveform=saw_up)
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

while True:
    # popcorn()
    # deeda()
    bladerunner()