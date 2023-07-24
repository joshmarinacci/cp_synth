import displayio
import terminalio

font = terminalio.FONT

class Menu():
    def __init__(self, rows, bgcolor=0x000000, fgcolor=0xffffff) -> None:
        print("making a menu with ",rows,'rows')
        self.rows = rows
        self.grids = displayio.Group()
        self.active = 0
        self.bg = bgcolor
        self.fg = fgcolor
        for j, row in enumerate(self.rows):
            print(j,row)
            pal2 = displayio.Palette(2)
            pal2[0] = self.bg
            pal2[1] = self.fg
            grid = displayio.TileGrid(font.bitmap, pixel_shader=pal2, width=30, height=1, tile_width=6, tile_height=12, x=0, y=j*12)
            for i,ch in enumerate(row['label']):
                grid[i,0] = ord(ch)-32
            self.grids.append(grid)
        self.update_colors()

    def update_colors(self):
        for j, grid in enumerate(self.grids):
            if(j == self.active):
                grid.pixel_shader[0] = self.fg
                grid.pixel_shader[1] = self.bg
            else:
                grid.pixel_shader[0] = self.bg
                grid.pixel_shader[1] = self.fg

    def goto_prev_item(self):
        self.active = (self.active - 1) % len(self.grids)
        print('selected',self.active)
        self.update_colors()

    def goto_next_item(self):
        self.active = (self.active + 1) % len(self.grids)
        print('selected',self.active)
        self.update_colors()

    def choose_active_item(self):
        print('going to do the action', self.active)
        print('doing',self.rows[self.active])
        self.rows[self.active]['action']()
