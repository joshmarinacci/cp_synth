import analogio
import board
import keypad

joystick_x = analogio.AnalogIn(board.JOYSTICK_X)
joystick_y = analogio.AnalogIn(board.JOYSTICK_Y)

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
        if joystick_x.value >= 30000 and self.left_pressed:
            self.left_pressed = False
            return keypad.Event(self.up_number+3, pressed=False)
        return None
