from kivy.uix.relativelayout import RelativeLayout


def keyboard_closed(self):
    self._keyboard.unbind(on_key_down=self._on_keyboard_down)
    self._keyboard.unbind(on_key_up=self._on_keyboard_up)
    self._keyboard = None


def on_keyboard_down(self, keyboard, keycode, text, modifiers):
    if keycode[1] == 'a' or keycode[1] == 'left':
        self.current_speed_x = self.speed_x
        print(keycode[1])
    elif keycode[1] == 'd' or keycode[1] == 'right':
        self.current_speed_x = -self.speed_x
        print(keycode[1])
    if keycode[1] == 'spacebar' or keycode[0] == 32 or keycode[1] == 'enter':
        print(keycode)
        print(self.state_game_started)
        if not self.state_game_started or self.state_game_over:
            self.on_menu_button_pressed()
    return True


def on_keyboard_up(self, keyboard, keycode):
    self.current_speed_x = 0
    print('Key Up')
    return True

def on_touch_down(self, touch):

    if self.state_game_started and not self.state_game_over:
        if touch.x < (self.width / 2):
            self.current_speed_x = self.speed_x
            # print('<-')
        else:
            # print('->')
            self.current_speed_x = -self.speed_x
    return super(RelativeLayout, self).on_touch_down(touch)

def on_touch_up(self, touch):
    # print('UP')
    self.current_speed_x = 0