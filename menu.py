import displayio
import terminalio
import adafruit_imageload
import vectorio
font = terminalio.FONT

UP = 32
RIGHT = 33
DOWN = 34
LEFT = 35
ACTION = 1
BACK = 0

menu_bitmap, menu_pal = adafruit_imageload.load("menu.bmp")
menu_pal.make_transparent(0)

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

class MenuTextItem(MenuItem):
    def __init__(self, title='title') -> None:
        super().__init__()
        self.title = title
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

class MenuHeader(MenuTextItem):
    def __init__(self, title='title') -> None:
        super().__init__(title=title)
    def update(self, joy, key):
        pass

class MenuItemBack(MenuTextItem):
    def __init__(self):
        super().__init__(title='< back')
    def update(self, joy, key):
        if key and key.pressed:
            if key.key_number == 1:
                self.parent_menu.pop_menu()
        
class MenuItemAction(MenuTextItem):
    def __init__(self, action, title='title') -> None:
        super().__init__(title=title)
        self.action = action
    def update(self, joy, key):
        if key and key.key_number == 1:
            if hasattr(self,'action'):
                self.action()

class SubMenu(MenuTextItem):
    def __init__(self, rows, title='submenu title' ):
        super().__init__(title=title)
        self.rows = rows
        self.rows.insert(0,MenuHeader(title='a sub menu'))
        self.rows.append(MenuItemBack())

    def update(self, joy, key):
        if key and key.pressed:
            if key.key_number == ACTION:
                self.nav_sub()

    def nav_sub(self):
        self.parent_menu.push_menu(self.rows, self.title)

class MenuNumberEditor(MenuItem):
    def __init__(self, target, prop, min=0, max=100, step=1, title='value', onInput=None, unit=' '):
        super().__init__()
        self.target = target
        self.prop = prop
        self.title = title
        self.min = min
        self.max = max
        self.step = step
        self.onInput = onInput
        self.unit = unit
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
        if active:
            self.label.pixel_shader.make_opaque(0)
        else:
            self.label.pixel_shader.make_transparent(0)

    def refresh(self):
        val = getattr(self.target,self.prop)
        for i in range(self.value.width):
            self.value[i] = 0
        text = str(val) + self.unit
        for i,ch in enumerate(text):
            self.value[i] = ord(ch)-32

        t = (val- self.min) / self.max - self.min
        for i in range(self.editor.width):
            if i >= (t * self.editor.width):
                self.editor[i] = 1
            else:
                self.editor[i] = 0


    def update(self, joy, key):
        if key:
            print(key)
        if joy and joy.pressed:
            if joy.key_number == LEFT:
                self.decrement()
            if joy.key_number == RIGHT:
                self.increment()
        if self.onInput:
            self.onInput(joy,key)

    def increment(self):
        val = getattr(self.target,self.prop)
        print("value was",val)
        val = val + self.step
        if val > self.max:
            val = self.max
        print("value is now",val)
        setattr(self.target,self.prop, val)
        self.refresh()

    def decrement(self):
        val = getattr(self.target,self.prop)
        print("value was",val)
        val = val - self.step
        if val < self.min:
            val = self.min
        print("value is now",val)
        setattr(self.target,self.prop, val)
        self.refresh()

class MenuBooleanEditor(MenuItem):
    def __init__(self, target, prop, title='value', onInput=None):
        super().__init__()
        self.target = target
        self.prop = prop
        self.title = title
        self.onInput = onInput
        pal2 = displayio.Palette(2)
        pal2[0] = self.bg_color
        pal2[1] = self.fg_color
        pal2.make_transparent(0)
        self.label = displayio.TileGrid(font.bitmap, pixel_shader=pal2, width=20, height=1, tile_width=6, tile_height=12)
        self.append(self.label)
        for i,ch in enumerate(title):
            self.label[i] = ord(ch)-32
        self.editor = displayio.TileGrid(menu_bitmap, pixel_shader=menu_pal, width=2, height=1, tile_width=6, tile_height=12, default_tile=2)
        self.editor.x = (len(title) + 1)*6
        self.append(self.editor)
        self.refresh()

    def set_active(self, active) -> None:
        super().set_active(active)
        self.label.pixel_shader[0] = self.bg_color
        self.label.pixel_shader[1] = self.fg_color
        if active:
            self.label.pixel_shader.make_opaque(0)
        else:
            self.label.pixel_shader.make_transparent(0)

    def refresh(self):
        val = getattr(self.target,self.prop)
        print("boolean value",val)
        if val == True:
            self.editor[0] = 2
            self.editor[1] = 3
        else:
            self.editor[0] = 4
            self.editor[1] = 5

    def update(self, joy, key):
        if key and key.key_number == ACTION and key.pressed:
            print(key)
            val = getattr(self.target, self.prop)
            val = not val
            setattr(self.target, self.prop, val)
            self.refresh()
        if self.onInput:
            self.onInput(joy,key)



class Menu(displayio.Group):
    def __init__(self, rows, bgcolor=0x000000, fgcolor=0xffffff, title='title') -> None:
        super().__init__()
        self.title = title
        self.rows = rows
        self.grids = displayio.Group()
        self.active = 0
        self.bg = bgcolor
        self.fg = fgcolor

        pal = displayio.Palette(1)
        pal[0] = 0xff0000
        self.backdrop = vectorio.Rectangle(pixel_shader=pal, width=160, height=120, x=0, y=0)
        self.append(self.backdrop)

        for j, row in enumerate(self.rows):
            row.parent_menu = self
            self.grids.append(row)
            row.y = j*12
            row.x = 0
        self.append(self.grids)
        self.subbed = False

    def shutdown(self):
        for j, row in enumerate(self.rows):
            self.grids.remove(row)
        self.remove(self.grids)

    def update(self, joy, key):
        if self.subbed:
            self.submenu.update(joy,key)
            return
        if key and key.pressed:
            if key.key_number == ACTION:
                self.grids[self.active].update(joy,key)
                return
            if key.key_number == BACK and hasattr(self,'parent_menu'):
                self.pop_menu()
                return
        if joy and joy.pressed:
            if joy.key_number == UP:
                self.goto_prev_item()
                return
            if joy.key_number == DOWN:
                self.goto_next_item()
                return
        self.grids[self.active].update(joy,key)

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
        if self.active > 0:
            self.active = (self.active - 1) % len(self.grids)
        self.grids[self.active].set_active(True)

    def goto_next_item(self):
        self.grids[self.active].set_active(False)
        if self.active + 1 < len(self.grids):
            self.active = (self.active + 1) % len(self.grids)
        self.grids[self.active].set_active(True)

    def push_menu(self,rows, title):
        self.subbed = True
        self.submenu = Menu(rows, title=title)
        self.submenu.parent_menu = self
        self.submenu.x = 0
        self.append(self.submenu)

    def pop_menu(self):
        self.parent_menu.remove(self)
        self.parent_menu.subbed = False
        self.shutdown()

