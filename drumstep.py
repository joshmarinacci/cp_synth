import displayio
import time
import adafruit_imageload
import ulab.numpy as np
import synthio
from menu import Menu, MenuHeader, MenuItemAction, MenuNumberEditor, SubMenu

from drums import SAMPLE_RATE, KickDrum, SnareDrum, HighHat

SAMPLE_SIZE = 512
SAMPLE_VOLUME = 32000  # 0-32767
wave_sine = np.array(np.sin(np.linspace(0, 2*np.pi, SAMPLE_SIZE, endpoint=False)) * SAMPLE_VOLUME, dtype=np.int16)
wave_saw = np.linspace(SAMPLE_VOLUME, -SAMPLE_VOLUME, num=SAMPLE_SIZE, dtype=np.int16)


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


UP = 32
RIGHT = 33
DOWN = 34
LEFT = 35
KEY_START = 2
KEY_SELECT = 3
KEY_BACK = 0


TOGGLE = 1
PLAY = 0

CELL_EMP = 0
CELL_SEL = 1

TILE_BLANK = 4
TILE_EMPTY = 0
TILE_SELECTED = 2
TILE_EMPTY_PLAYING = 11
TILE_SELECTED_PLAYING = 12

TILE_SNARE = 6
TILE_HIGHHAT = 7
TILE_KICKDRUM = 8

TILE_MUTE_OFF = 10
TILE_MUTE_ON = 9
TILE_WHOLE_NOTE_MARKER = 1
TILE_PLAY = 5
TILE_HIGHLIGHT = 13
TILE_CLEAR = 14

GRID_X_MIN = 2
GRID_X_MAX = 2+8
GRID_Y_MIN = 1
GRID_Y_MAX = 4

COLUMN_VOICE = 0
COLUMN_MUTE = 1

class VoiceSettings():
    def __init__(self, voice, synth, seq) -> None:
        self.voice = voice
        self.freq = 50
        self.synth = synth
        self.seq = seq

        self.attack_time   = 50
        self.decay_time    = 100
        self.release_time  = 200
        
        self.attack_level  = 100
        self.sustain_level = 80

        self.lpf_freq = 2000
        self.lpf_q = 1.5
        self.menu = Menu([
            MenuHeader(title='Voice Settings '),
            MenuHeader(title=voice.title),
            SubMenu([
                MenuNumberEditor(title='A level', target=self, prop='attack_level',  min=0, max=100, step=5,  onInput=self.play_tone, unit='%'),
                MenuNumberEditor(title='A time ', target=self, prop='attack_time',   min=0, max=500, step=10, onInput=self.play_tone, unit='ms'),
                MenuNumberEditor(title='D time ', target=self, prop='decay_time',    min=0, max=500, step=10, onInput=self.play_tone, unit='ms'),
                MenuNumberEditor(title='S level', target=self, prop='sustain_level', min=0, max=100, step=5,  onInput=self.play_tone, unit='%'),
                MenuNumberEditor(title='R time ', target=self, prop='release_time',  min=0, max=500, step=10, onInput=self.play_tone, unit='ms'),
            ], title='Amplitude ADSR >'),
            MenuNumberEditor(title='lpf freq', target=self, prop='lpf_freq',  min=0, max=10000, step=1000, onInput=self.play_tone, unit='hz'),
            MenuNumberEditor(title='lpf q   ', target=self, prop='lpf_q',     min=0, max=5, step=0.25,  onInput=self.play_tone, unit=''),
            MenuItemAction(title='^ done', action=self.close),
            # MenuItemAction(title='waveform', action=self.choose_waveform),
        ])
    def close(self):
        self.seq.close_voice_menu()

    def play_tone(self, joy, key):
        if key and key.key_number == KEY_BACK:
            print("doing a key back")
        if key and (key.key_number == 2 or key.key_number == 1):
            if key.pressed:
                adsr = synthio.Envelope(
                    attack_time=self.attack_time/500,
                    decay_time=self.decay_time/500,
                    release_time=self.release_time/500,
                    attack_level=self.attack_level/100,
                    sustain_level=self.sustain_level/100,
                )
                midi_note = 65
                lpf = self.synth.low_pass_filter(self.lpf_freq,self.lpf_q)
                self.test_note = synthio.Note(synthio.midi_to_hz(midi_note), waveform=wave_saw, envelope=adsr, filter=lpf)
                self.synth.press(self.test_note)
            if key.released:
                self.synth.release(self.test_note)

    def choose_waveform(self):
        print("choosing the waveform")
    


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
        self.tiles_pal.make_transparent(0)
        self.overlay = displayio.TileGrid(self.tiles, pixel_shader=self.tiles_pal,
                                          width=12, height=8,
                                          tile_height=16, tile_width=16,
                                          default_tile=TILE_CLEAR
                                          )
        self.append(self.overlay)

        self.cells = []
        for j in range(0, GRID_Y_MAX-GRID_Y_MIN):
            self.cells.append([])
            for i in range(0, GRID_X_MAX-GRID_X_MIN):
                self.cells[j].append(CELL_EMP)
        self.playing_column = -1

        # first column
        self.grid[(COLUMN_VOICE,1)] = TILE_HIGHHAT
        self.grid[(COLUMN_VOICE,2)] = TILE_SNARE
        self.grid[(COLUMN_VOICE,3)] = TILE_KICKDRUM
        # second column
        self.grid[(COLUMN_MUTE,1)] = TILE_MUTE_OFF
        self.grid[(COLUMN_MUTE,2)] = TILE_MUTE_ON
        self.grid[(COLUMN_MUTE,3)] = TILE_MUTE_OFF

        # top whole note markers
        for col in range(GRID_X_MIN, GRID_X_MAX+1, 4):
            self.grid[(col,0)] = TILE_WHOLE_NOTE_MARKER
        # the grid cells
        for j in range(GRID_Y_MIN,GRID_Y_MAX):
            for i in range(GRID_X_MIN,GRID_X_MAX):
                self.grid[(i,j)] = TILE_EMPTY

        self.highlighted = (2,1)
        self.overlay[(2,1)] = TILE_HIGHLIGHT
        self.refresh()

        self.menu_showing = False

    def refresh(self):
        for j in range(GRID_Y_MIN, GRID_Y_MAX):
            for i in range(GRID_X_MIN, GRID_X_MAX):
                y = j - GRID_Y_MIN
                x = i - GRID_X_MIN
                val = self.cells[y][x]
                tile = TILE_EMPTY
                playing = self.playing_column == x
                if val == CELL_SEL:
                    tile = TILE_SELECTED
                    if playing:
                        tile = TILE_SELECTED_PLAYING
                else:
                    tile = TILE_EMPTY
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
        if newhi[0] >= 0 and newhi[0] < GRID_X_MAX:
            if newhi[1] >= GRID_Y_MIN and newhi[1] < GRID_Y_MAX: 
                self.overlay[self.highlighted] = TILE_CLEAR
                self.highlighted = newhi
                self.overlay[self.highlighted] = TILE_HIGHLIGHT

    def get_at(self, xy):
        return self.cells[xy[1]-GRID_Y_MIN][xy[0]-GRID_X_MIN]
    
    def set_at(self, xy, val):
        self.cells[xy[1]-GRID_Y_MIN][xy[0]-GRID_X_MIN] = val

    def set_playing_column(self, col):
        self.playing_column = col
        self.refresh()

    def toggle(self):
        if(self.highlighted[0] == COLUMN_VOICE):
            voice = self.voices[self.highlighted[1]-GRID_Y_MIN]
            self.open_voice_menu(voice)
            return
        if(self.highlighted[0] == COLUMN_MUTE):
            voice = self.voices[self.highlighted[1]-GRID_Y_MIN]
            voice.mute = not voice.mute
            self.refresh()
            return
        curr = self.get_at(self.highlighted)
        if(curr == CELL_EMP):
            self.set_at(self.highlighted,CELL_SEL)
            voice = self.voices[self.highlighted[1] - GRID_Y_MIN]
            voice.trigger()
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
            time.sleep(0.4)
            self.set_playing_column(col)
        self.set_playing_column(-1)

    def update(self, joy, key):
        for voice in self.voices:
            voice.update()
        if self.menu_showing:
            self.settings.menu.update(joy,key)
            return
        if joy:
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
            if key.pressed and key.key_number == TOGGLE:
                self.toggle()
            if key.pressed and key.key_number == PLAY:
                self.playFromStart()

    def open_voice_menu(self, voice):
        self.settings = VoiceSettings(voice,self.synth,self)
        self.append(self.settings.menu)
        self.menu_showing = True
    def close_voice_menu(self):
        self.remove(self.settings.menu)
        self.settings = None
        self.menu_showing = False


