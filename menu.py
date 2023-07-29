import displayio
import terminalio
import adafruit_imageload
import vectorio
font = terminalio.FONT

UP = 32
RIGHT = 33
DOWN = 34
LEFT = 35

menu_bitmap, menu_pal = adafruit_imageload.load("menu.bmp")

class MenuItem(displayio.Group):
    def __init__(self):
        super().__init__()
        self.bg_color = 0x000000
        self.fg_color = 0xffffff
    def set_active(self, active):
        if active:
            self.bg_color = 0xffffff
            self.fg_color = 0x000000
        else:
            self.fg_color = 0xffffff
            self.bg_color = 0x000000
    def update(self, joy, key):
        print("menu item getting input")

class MenuHeader(MenuItem):
    def __init__(self, title='title') -> None:
        super().__init__()
        pal2 = displayio.Palette(2)
        pal2[0] = self.bg_color
        pal2[1] = self.fg_color
        pal2.make_transparent(0)
        self.grid = displayio.TileGrid(font.bitmap, pixel_shader=pal2, width=30, height=1, tile_width=6, tile_height=12)
        for i,ch in enumerate(title):
            self.grid[i,0] = ord(ch)-32
        self.append(self.grid)
    def set_active(self, active) -> None:
        super().set_active(active)
        self.grid.pixel_shader[0] = self.bg_color
        self.grid.pixel_shader[1] = self.fg_color
    def update(self, joy, key):
        pass

class MenuItemAction(MenuItem):
    def __init__(self, action, title='title') -> None:
        super().__init__()
        print('making menu item action')
        self.action = action
        pal2 = displayio.Palette(2)
        pal2[0] = self.bg_color
        pal2[1] = self.fg_color
        pal2.make_transparent(0)
        self.pal = pal2
        self.grid = displayio.TileGrid(font.bitmap, pixel_shader=pal2, width=30, height=1, tile_width=6, tile_height=12)
        for i,ch in enumerate(title):
            self.grid[i,0] = ord(ch)-32
        self.append(self.grid)
    def set_active(self, active) -> None:
        super().set_active(active)
        self.grid.pixel_shader[0] = self.bg_color
        self.grid.pixel_shader[1] = self.fg_color
        if active:
            self.grid.pixel_shader.make_opaque(0)
        else:
            self.grid.pixel_shader.make_transparent(0)
    def update(self, joy, key):
        if hasattr(self,'action'):
            self.action()

class SubMenu(MenuItem):
    def __init__(self, rows, title='submenu title' ):
        super().__init__()
        self.rows = rows
        print("making a sub menu")    
        pal2 = displayio.Palette(2)
        pal2[0] = self.bg_color
        pal2[1] = self.fg_color
        pal2.make_transparent(0)
        self.grid = displayio.TileGrid(font.bitmap, pixel_shader=pal2, width=30, height=1, tile_width=6, tile_height=12)
        for i,ch in enumerate(title):
            self.grid[i,0] = ord(ch)-32
        self.append(self.grid)

    def set_active(self, active) -> None:
        super().set_active(active)
        self.grid.pixel_shader[0] = self.bg_color
        self.grid.pixel_shader[1] = self.fg_color
        if active:
            self.grid.pixel_shader.make_opaque(0)
        else:
            self.grid.pixel_shader.make_transparent(0)

    def update(self, joy, key):
        if joy and joy.pressed:
            if joy.key_number == LEFT:
                self.nav_up()
            if joy.key_number == RIGHT:
                self.nav_sub()
    def nav_sub(self):
        self.parent_menu.push_menu(self.rows)
        
    def nav_up(self):
        print("going up")
        

class MenuNumberEditor(MenuItem):
    def __init__(self, getter, setter, min=0, max=100, step=1, title='value'):
        super().__init__()
        print("making menu number editor")
        self.getter = getter
        self.setter = setter
        self.title = title
        self.min = min
        self.max = max
        self.step = step
        pal2 = displayio.Palette(2)
        pal2[0] = self.bg_color
        pal2[1] = self.fg_color
        pal2.make_transparent(0)
        self.label = displayio.TileGrid(font.bitmap, pixel_shader=pal2, width=20, height=1, tile_width=6, tile_height=12)
        self.append(self.label)
        for i,ch in enumerate(title):
            self.label[i] = ord(ch)-32
        self.editor = displayio.TileGrid(menu_bitmap, pixel_shader=menu_pal, width=10, height=1, tile_width=6, tile_height=12, default_tile=3)
        self.editor.x = (len(title) + 1)*6
        self.append(self.editor)

        self.value = displayio.TileGrid(font.bitmap, pixel_shader=pal2, width=20, height=1, tile_width=6, tile_height=12)
        self.append(self.value)
        self.value.x = self.editor.x + (self.editor.width + 1) * self.editor.tile_width
        self.refresh()

    def set_active(self, active) -> None:
        super().set_active(active)
        self.label.pixel_shader[0] = self.bg_color
        self.label.pixel_shader[1] = self.fg_color

    def refresh(self):
        val = self.getter()
        for i in range(self.value.width):
            self.value[i] = 0
        text = str(val)
        for i,ch in enumerate(text):
            self.value[i] = ord(ch)-32

        t = (val- self.min) / self.max - self.min
        for i in range(self.editor.width):
            if i >= (t * self.editor.width):
                self.editor[i] = 3
            else:
                self.editor[i] = 2


    def update(self, joy, key):
        if joy and joy.pressed:
            if joy.key_number == LEFT:
                self.decrement()
            if joy.key_number == RIGHT:
                self.increment()

    def increment(self):
        val = self.getter()
        print("value was",val)
        val = val + self.step
        if val > self.max:
            val = self.max
        print("value is now",val)
        self.setter(val)
        self.refresh()

    def decrement(self):
        val = self.getter()
        print("value was",val)
        val = val - self.step
        if val < self.min:
            val = self.min
        print("value is now",val)
        self.setter(val)
        self.refresh()


class Menu(displayio.Group):
    def __init__(self, rows, bgcolor=0x000000, fgcolor=0xffffff, title='title') -> None:
        super().__init__()
        print("making",title,"a menu with",len(rows),'rows')
        self.title = title
        self.rows = rows
        self.grids = displayio.Group()
        self.active = 0
        self.bg = bgcolor
        self.fg = fgcolor

        pal = displayio.Palette(1)
        pal[0] = 0xff0000
        self.backdrop = vectorio.Rectangle(pixel_shader=pal, width=160, height=80, x=0, y=0)
        self.append(self.backdrop)

        for j, row in enumerate(self.rows):
            # print(j,row)
            row.parent_menu = self
            self.grids.append(row)
            row.y = j*12
            row.x = 0
        self.append(self.grids)
        self.subbed = False

    def update(self, joy, key):
        if self.subbed:
            self.submenu.update(joy,key)
            return
        if joy and joy.pressed:
            if joy.key_number == LEFT:
                print("i am",self.title)
                if hasattr(self, 'parent_menu'):
                    print("going back up")
                    self.parent_menu.pop_menu(self)
                    return
                self.grids[self.active].update(joy,key)
            if joy.key_number == RIGHT:
                self.grids[self.active].update(joy,key)
            if joy.key_number == UP:
                self.goto_prev_item()
            if joy.key_number == DOWN:
                self.goto_next_item()

    def update_colors(self):
        for j, grid in enumerate(self.grids):
            if(j == self.active):
                grid.pixel_shader[0] = self.fg
                grid.pixel_shader[1] = self.bg
            else:
                grid.pixel_shader[0] = self.bg
                grid.pixel_shader[1] = self.fg

    def goto_prev_item(self):
        self.grids[self.active].set_active(False)
        self.active = (self.active - 1) % len(self.grids)
        self.grids[self.active].set_active(True)

    def goto_next_item(self):
        self.grids[self.active].set_active(False)
        self.active = (self.active + 1) % len(self.grids)
        self.grids[self.active].set_active(True)

    def choose_active_item(self):
        print('going to do the action', self.active)
        print('doing',self.rows[self.active])
        self.rows[self.active]['action']()
    def push_menu(self,rows):
        self.subbed = True
        self.submenu = Menu(rows)
        self.submenu.parent_menu = self
        self.submenu.x = 0
        self.append(self.submenu)
    def pop_menu(self, menu):
        self.subbed = False
        self.remove(menu)

