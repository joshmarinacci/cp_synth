import displayio
import adafruit_imageload
import ulab.numpy as np

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
sinwave1 = np.array(np.sin(np.linspace(0, 2*np.pi, SAMPLE_SIZE, endpoint=False)) * 32767, dtype=np.int16)
sinwave2 = np.array(np.sin(np.linspace(np.pi/2, 2.5*np.pi, SAMPLE_SIZE, endpoint=False)) * 32767, dtype=np.int16)
downwave = np.linspace(32767, -32767, num=3, dtype=np.int16)
noisewave = np.array([random.randint(-32767, 32767) for i in range(SAMPLE_SIZE)], dtype=np.int16)
w1 = np.array( [int(max(min(sinwave1[i] + (noisewave[i]/2.0), 32767), -32767)) for i in range(SAMPLE_SIZE)], dtype=np.int16)
w2 = np.array( [int(max(min(sinwave2[i] + (noisewave[i]/2.0), 32767), -32767)) for i in range(SAMPLE_SIZE)], dtype=np.int16)

class Drums():
    def __init__(self) -> None:
        print("made drums")

UP = 32
RIGHT = 33
DOWN = 34
LEFT = 35


TOGGLE = 1
PLAY = 0

CELL_EMP = 0
CELL_SEL = 1
CELL_EMP_NO = 0
CELL_EMP_YES = 1
CELL_SEL_NO = 2
CELL_SEL_YES = 3

class DrumSequencer():
    def __init__(self) -> None:
        print("loading tile image")
        self.bitmap, self.palette = adafruit_imageload.load(
            "tiles.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette
        )
        self.cells = [[0 for j in range(16)] for i in range(3)]

        self.grid = displayio.TileGrid(self.bitmap, pixel_shader=self.palette, 
                                  width=16, height=3, 
                                  tile_width=8, tile_height=8)
        self.highlighted = (1,2)
        self.set_at(self.highlighted,CELL_SEL)

    def nav(self, d):
        newhi = (self.highlighted[0]+d[0], self.highlighted[1]+d[1])
        if newhi[0] >= 0 and newhi[0] < 16:
            if newhi[1] >= 0 and newhi[1] < 3: 
                if self.get_at(self.highlighted) == CELL_SEL:
                    self.grid[self.highlighted] = CELL_SEL_NO
                else:
                    self.grid[self.highlighted] = CELL_EMP_NO
                self.highlighted = newhi
                if self.get_at(self.highlighted) == CELL_SEL:
                    self.grid[self.highlighted] = CELL_SEL_YES
                else:
                    self.grid[self.highlighted] = CELL_EMP_YES

    def get_at(self, xy):
        print('getting at',xy)
        return self.cells[xy[1]][xy[0]]
    
    def set_at(self, xy, val):
        print('setting',xy,val,'hi',self.highlighted)
        self.cells[xy[1]][xy[0]] = val
        if val == CELL_SEL:
            if self.highlighted == xy:
                self.grid[xy] = CELL_SEL_YES
            else:
                self.grid[xy] = CELL_SEL_NO
        else:
            if self.highlighted == xy:
                self.grid[xy] = CELL_EMP_YES
            else:
                self.grid[xy] = CELL_EMP_NO

    def toggle(self):
        curr = self.get_at(self.highlighted)
        if(curr == CELL_EMP):
            self.set_at(self.highlighted,CELL_SEL)
        else:
            self.set_at(self.highlighted,CELL_EMP)

    def playFromStart(self):
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



