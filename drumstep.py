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

class KickDrum():
    def __init__(self) -> None:
        print("made drums")

        self.synth = synthio.Synthesizer(sample_rate=SAMPLE_RATE)

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
        print("playing")
        self.lfo.retrigger()
        self.synth.press((self.note1, self.note2, self.note3))
        time.sleep(0.25)
        self.synth.release((self.note1, self.note2, self.note3))



UP = 32
RIGHT = 33
DOWN = 34
LEFT = 35


TOGGLE = 1
PLAY = 0

CELL_EMP = 0
CELL_SEL = 1
TILE_EMPTY = 6
TILE_EMPTY_HIGHLIGHTED = 7
TILE_SELECTED = 9
TILE_SELECTED_HIGHLIGHTED = 10

TILE_HIGHHAT = 4
TILE_SNARE = 3
TILE_KICKDRUM = 5
TILE_MUTE_OFF = 2
TILE_MUTE_ON = 8

TILE_WHOLE_NOTE_MARKER = 12
TILE_PLAY = 0

GRID_X_MIN = 2
GRID_X_MAX = 2+8
GRID_Y_MIN = 1
GRID_Y_MAX = 4

class DrumSequencer(displayio.Group):
    def __init__(self, mixer) -> None:
        super().__init__()


        self.drums = KickDrum()
        mixer.voice[0].play(self.drums.synth)
        print("loading tile image")
        self.tiles, self.tiles_pal = adafruit_imageload.load("tiles.bmp")
        self.grid = displayio.TileGrid(self.tiles, pixel_shader=self.tiles_pal,
                                            width=16, height=13,
                                            tile_width=10, tile_height=10,
                                            default_tile=11
                                            )
        self.append(self.grid)

        self.cells = []
        for j in range(0, GRID_Y_MAX-GRID_Y_MIN):
            self.cells.append([])
            for i in range(0, GRID_X_MAX-GRID_X_MIN):
                print("making",j,i)
                self.cells[j].append(CELL_EMP)

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
        self.set_at(self.highlighted,CELL_SEL)



        # bottom status bar
        self.grid[(0,11)] = TILE_PLAY

    def nav(self, d):
        newhi = (self.highlighted[0]+d[0], self.highlighted[1]+d[1])
        if newhi[0] >= GRID_X_MIN and newhi[0] < GRID_X_MAX:
            if newhi[1] >= GRID_Y_MIN and newhi[1] < GRID_Y_MAX: 
                if self.get_at(self.highlighted) == CELL_SEL:
                    self.grid[self.highlighted] = TILE_SELECTED
                else:
                    self.grid[self.highlighted] = TILE_EMPTY
                self.highlighted = newhi
                if self.get_at(self.highlighted) == CELL_SEL:
                    self.grid[self.highlighted] = TILE_SELECTED_HIGHLIGHTED
                else:
                    self.grid[self.highlighted] = TILE_EMPTY_HIGHLIGHTED

    def get_at(self, xy):
        print('getting at',xy)
        return self.cells[xy[1]-GRID_Y_MIN][xy[0]-GRID_X_MIN]
    
    def set_at(self, xy, val):
        print('setting',xy,val,self.highlighted,)
        self.cells[xy[1]-GRID_Y_MIN][xy[0]-GRID_X_MIN] = val
        print(self.cells)
        if val == CELL_SEL:
            if self.highlighted == xy:
                self.grid[xy] = TILE_SELECTED_HIGHLIGHTED
            else:
                self.grid[xy] = TILE_SELECTED
        else:
            if self.highlighted == xy:
                self.grid[xy] = TILE_EMPTY_HIGHLIGHTED
            else:
                self.grid[xy] = TILE_EMPTY

    def toggle(self):
        curr = self.get_at(self.highlighted)
        if(curr == CELL_EMP):
            self.set_at(self.highlighted,CELL_SEL)
        else:
            self.set_at(self.highlighted,CELL_EMP)

    def playFromStart(self):
        for col in range(0,GRID_X_MAX-GRID_X_MIN):
            note = self.cells[0][col]
            print("note",note)
            if note == CELL_SEL:
                self.drums.trigger()
            time.sleep(0.2)


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



