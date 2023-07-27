import displayio
import time
import adafruit_imageload
import ulab.numpy as np
import synthio
import random

# a bar is 4 whole notes
# there are 16 steps, each a quarter note
# four on the floor is every fourth note
# the are four starting instruments
# hi hat, snare, and kick drum. add a tom drum later (lower pitch?)

# so three rows and 16 spots. using 8x8 pixel tiles gives us 128x54 for the main grid
# the pygamer is a 160x128px screen
# use joypad to navigate the grid
# press a to toggle a cell on or off
# press b to toggle playing the sequence.
# draw bitmaps empty cell, selected cell, highlighted cell, selected highlighted cell

SAMPLE_SIZE = 200
SAMPLE_RATE = 22050
sinwave1 = np.array(np.sin(np.linspace(0, 2*np.pi, SAMPLE_SIZE, endpoint=False)) * 32767, dtype=np.int16)
sinwave2 = np.array(np.sin(np.linspace(np.pi/2, 2.5*np.pi, SAMPLE_SIZE, endpoint=False)) * 32767, dtype=np.int16)
downwave = np.linspace(32767, -32767, num=3, dtype=np.int16)
noisewave = np.array([random.randint(-32767, 32767) for i in range(SAMPLE_SIZE)], dtype=np.int16)
w1 = np.array( [int(max(min(sinwave1[i] + (noisewave[i]/2.0), 32767), -32767)) for i in range(SAMPLE_SIZE)], dtype=np.int16)
w2 = np.array( [int(max(min(sinwave2[i] + (noisewave[i]/2.0), 32767), -32767)) for i in range(SAMPLE_SIZE)], dtype=np.int16)

class Voice():
    def __init__(self, synth) -> None:
        self.synth = synth
        self.mute = False

    def trigger(self) -> None:
        print("trigger must be implemented")

class KickDrum(Voice):
    def __init__(self, synth) -> None:
        super().__init__(synth)
        # kick drum
        self.lfo = synthio.LFO(waveform=downwave)
        self.lfo.once = True
        self.lfo.offset=0.33
        self.lfo.scale = 0.3
        self.lfo.rate=20
    
        self.filter_fr = 2000
        self.lpf = self.synth.low_pass_filter(frequency=self.filter_fr)

        self.amp_env1 = synthio.Envelope(attack_time=0.0, decay_time=0.075, release_time=0, attack_level=1, sustain_level=0)
        self.note1 = synthio.Note(frequency=53, envelope=self.amp_env1, waveform=sinwave2, filter=self.lpf, bend=self.lfo)

        self.amp_env2 = synthio.Envelope(attack_time=0.0, decay_time=0.055, release_time=0, attack_level=1, sustain_level=0)
        self.note2 = synthio.Note(frequency=72, envelope=self.amp_env2, waveform=sinwave1, filter=self.lpf, bend=self.lfo)

        self.amp_env3 = synthio.Envelope(attack_time=0.0, decay_time=0.095, release_time=0, attack_level=1, sustain_level=0)
        self.note3 = synthio.Note(frequency=41, envelope=self.amp_env3, waveform=sinwave2, filter=self.lpf, bend=self.lfo)

    def trigger(self) -> None:
        self.lfo.retrigger()
        self.synth.press((self.note1, self.note2, self.note3))
    def end(self) -> None:
        self.synth.release((self.note1, self.note2, self.note3))

class SnareDrum(Voice):
    def __init__(self, synth) -> None:
        super().__init__(synth)

        # kick drum
        self.lfo = synthio.LFO(waveform=downwave)
        self.lfo.once = True
        self.lfo.offset=0.33
        self.lfo.scale = 0.3
        self.lfo.rate=20
    
        self.filter_fr = 9500
        self.lpf = self.synth.low_pass_filter(frequency=self.filter_fr)

        self.amp_env1 = synthio.Envelope(attack_time=0.0, decay_time=0.115, release_time=0, attack_level=1, sustain_level=0)
        self.note1 = synthio.Note(frequency=90, envelope=self.amp_env1, waveform=w1, filter=self.lpf, bend=self.lfo)

        self.amp_env2 = synthio.Envelope(attack_time=0.0, decay_time=0.095, release_time=0, attack_level=1, sustain_level=0)
        self.note2 = synthio.Note(frequency=135, envelope=self.amp_env2, waveform=w2, filter=self.lpf, bend=self.lfo)

        self.amp_env3 = synthio.Envelope(attack_time=0.0, decay_time=0.115, release_time=0, attack_level=1, sustain_level=0)
        self.note3 = synthio.Note(frequency=165, envelope=self.amp_env3, waveform=w2, filter=self.lpf, bend=self.lfo)


    def trigger(self) -> None:
        if not self.mute:
            self.lfo.retrigger()
            self.synth.press((self.note1, self.note2, self.note3))
    def end(self) -> None:
        if not self.mute:
            self.synth.release((self.note1, self.note2, self.note3))

class HighHat(Voice):
    def __init__(self, synth) -> None:
        super().__init__(synth)

        # kick drum
        self.lfo = synthio.LFO(waveform=downwave)
        self.lfo.once = True
        self.lfo.offset=0.33
        self.lfo.scale = 0.3
        self.lfo.rate=20
    
        t = 0.115
        self.filter_fr = 9500
        self.hpf = self.synth.high_pass_filter(frequency=self.filter_fr)

        self.amp_env1 = synthio.Envelope(attack_time=0.0, decay_time=t, release_time=0, attack_level=1, sustain_level=0)
        self.note1 = synthio.Note(frequency=90, envelope=self.amp_env1, waveform=noisewave, filter=self.hpf, bend=self.lfo)

        self.amp_env2 = synthio.Envelope(attack_time=0.0, decay_time=t-0.02, release_time=0, attack_level=1, sustain_level=0)
        self.note2 = synthio.Note(frequency=135, envelope=self.amp_env2, waveform=w2, filter=self.hpf, bend=self.lfo)

        self.amp_env3 = synthio.Envelope(attack_time=0.0, decay_time=t, release_time=0, attack_level=1, sustain_level=0)
        self.note3 = synthio.Note(frequency=165, envelope=self.amp_env3, waveform=noisewave, filter=self.hpf, bend=self.lfo)

    def trigger(self) -> None:
        if not self.mute:
            self.lfo.retrigger()
            self.synth.press((self.note1, self.note2, self.note3))
    def end(self) -> None:
        if not self.mute:
            self.synth.release((self.note1, self.note2, self.note3))

UP = 32
RIGHT = 33
DOWN = 34
LEFT = 35


TOGGLE = 1
PLAY = 0

CELL_EMP = 0
CELL_SEL = 1

TILE_BLANK = 4
TILE_EMPTY = 0
TILE_EMPTY_HIGHLIGHTED = 1
TILE_SELECTED = 2
TILE_SELECTED_HIGHLIGHTED = 3
TILE_EMPTY_PLAYING = 11
TILE_SELECTED_PLAYING = 12

TILE_SNARE = 6
TILE_HIGHHAT = 7
TILE_KICKDRUM = 8

TILE_MUTE_OFF = 10
TILE_MUTE_ON = 9
TILE_WHOLE_NOTE_MARKER = 13
TILE_PLAY = 5

GRID_X_MIN = 2
GRID_X_MAX = 2+8
GRID_Y_MIN = 1
GRID_Y_MAX = 4

class DrumSequencer(displayio.Group):
    def __init__(self, mixer) -> None:
        super().__init__()


        self.synth = synthio.Synthesizer(sample_rate=SAMPLE_RATE)
        mixer.voice[0].play(self.synth)

        self.kick = KickDrum(self.synth)
        self.snare = SnareDrum(self.synth)
        self.hihat = HighHat(self.synth)
        self.voices = [self.kick, self.snare, self.hihat]

        self.tiles, self.tiles_pal = adafruit_imageload.load("tiles.bmp")
        self.grid = displayio.TileGrid(self.tiles, pixel_shader=self.tiles_pal,
                                            width=12, height=8,
                                            tile_width=16, tile_height=16,
                                            default_tile=TILE_BLANK
                                            )
        self.append(self.grid)

        self.cells = []
        for j in range(0, GRID_Y_MAX-GRID_Y_MIN):
            self.cells.append([])
            for i in range(0, GRID_X_MAX-GRID_X_MIN):
                self.cells[j].append(CELL_EMP)
        self.playing_column = -1

        # first column
        self.grid[(0,1)] = TILE_HIGHHAT
        self.grid[(0,2)] = TILE_SNARE
        self.grid[(0,3)] = TILE_KICKDRUM
        # second column
        self.grid[(1,1)] = TILE_MUTE_OFF
        self.grid[(1,2)] = TILE_MUTE_ON
        self.grid[(1,3)] = TILE_MUTE_OFF

        # top whole note markers
        for col in range(GRID_X_MIN, GRID_X_MAX+1, 4):
            self.grid[(col,0)] = TILE_WHOLE_NOTE_MARKER
        # the grid cells   
        for j in range(GRID_Y_MIN,GRID_Y_MAX):
            for i in range(GRID_X_MIN,GRID_X_MAX):
                self.grid[(i,j)] = TILE_EMPTY

        self.highlighted = (5,2)

        # bottom status bar
        self.grid[(0,7)] = TILE_PLAY
        self.refresh()

    def refresh(self):
        for j in range(GRID_Y_MIN, GRID_Y_MAX):
            for i in range(GRID_X_MIN, GRID_X_MAX):
                y = j - GRID_Y_MIN
                x = i - GRID_X_MIN
                val = self.cells[y][x]
                high = self.highlighted == (i,j)
                tile = TILE_EMPTY
                playing = self.playing_column == x
                if val == CELL_SEL:
                    tile = TILE_SELECTED
                    if high:
                        tile = TILE_SELECTED_HIGHLIGHTED
                    if playing:
                        tile = TILE_SELECTED_PLAYING
                    
                else:
                    tile = TILE_EMPTY
                    if high:
                        tile = TILE_EMPTY_HIGHLIGHTED
                    if playing:
                        tile = TILE_EMPTY_PLAYING
                self.grid[(i,j)] = tile
        for j in range(GRID_Y_MIN, GRID_Y_MAX):
            voice = self.voices[j-GRID_Y_MIN]
            if voice.mute:
                self.grid[(1,j)] = TILE_MUTE_ON
            else:
                self.grid[(1,j)] = TILE_MUTE_OFF


    def nav(self, d):
        newhi = (self.highlighted[0]+d[0], self.highlighted[1]+d[1])
        if newhi[0] >= 1 and newhi[0] < GRID_X_MAX:
            if newhi[1] >= GRID_Y_MIN and newhi[1] < GRID_Y_MAX: 
                self.highlighted = newhi
        self.refresh()

    def get_at(self, xy):
        return self.cells[xy[1]-GRID_Y_MIN][xy[0]-GRID_X_MIN]
    
    def set_at(self, xy, val):
        self.cells[xy[1]-GRID_Y_MIN][xy[0]-GRID_X_MIN] = val

    def set_playing_column(self, col):
        self.playing_column = col
        self.refresh()

    def toggle(self):
        if(self.highlighted[0] == 1):
            voice = self.voices[self.highlighted[1]-GRID_Y_MIN]
            voice.mute = not voice.mute
            self.refresh()
            return
        curr = self.get_at(self.highlighted)
        if(curr == CELL_EMP):
            self.set_at(self.highlighted,CELL_SEL)
        else:
            self.set_at(self.highlighted,CELL_EMP)
        self.refresh()

    def playFromStart(self):
        for col in range(0,GRID_X_MAX-GRID_X_MIN):
            self.set_playing_column(col)
            if self.cells[0][col] == CELL_SEL:
                self.kick.trigger()
            if self.cells[1][col] == CELL_SEL:
                self.snare.trigger()
            if self.cells[2][col] == CELL_SEL:
                self.hihat.trigger()
            time.sleep(0.2)
            if self.cells[0][col] == CELL_SEL:
                self.kick.end()
            if self.cells[1][col] == CELL_SEL:
                self.snare.end()
            if self.cells[2][col] == CELL_SEL:
                self.hihat.end()
            time.sleep(0.2)
            self.set_playing_column(col)
        self.set_playing_column(-1)



    def update(self, joy, key):
        # print("updating sequencer")
        if joy:
            print(joy)
            if joy.pressed:
                if joy.key_number == LEFT:
                    self.nav((-1,0))
                if joy.key_number == RIGHT:
                    self.nav((1,0))
                if joy.key_number == UP:
                    self.nav((0,-1))
                if joy.key_number == DOWN:
                    self.nav((0,1))
        if key:
            print(key)
            if key.pressed and key.key_number == TOGGLE:
                self.toggle()
            if key.pressed and key.key_number == PLAY:
                self.playFromStart()



