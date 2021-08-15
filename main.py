from kivy.config import Config

Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '400')

from kivy.core.audio import SoundLoader

from kivy.lang import Builder
import random
from kivy.uix.relativelayout import RelativeLayout
from kivy import platform
from kivy.core.window import Window
from kivy.app import App
from kivy.graphics import Line, Color, Quad, Triangle
from kivy.properties import NumericProperty, Clock, ObjectProperty, StringProperty

Builder.load_file("menu.kv")

class MainWidget(RelativeLayout):
    from transforms import transform, transform_2D, transform_perspective
    from user_actions import keyboard_closed, on_keyboard_up, on_keyboard_down, on_touch_down, on_touch_up

    menu_widget = ObjectProperty()
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)
    menu_title = StringProperty('G  A  L  A  X  Y')
    menu_button_title = StringProperty('START')
    score = StringProperty()

    vertical_lines = list()
    V_NB_LINES = 8
    V_LINES_SPACING = .4  # in percentage screen width

    H_NB_LINES = 15
    H_LINES_SPACING = .1  # in percentage screen height
    horizontal_lines = list()

    current_offset_y = 0
    MIN_SPEED = .5
    SPEED = .5
    MAX_SPEED = 1.3
    current_y_loop = 0

    current_speed_x = 0
    current_offset_x = 1
    min_speed_x = 1.5
    speed_x = 1.5
    max_speed_x = 3.5


    NB_TILES = 16
    tiles = []
    tiles_coordinates = []

    SHIP_WIDTH = .1
    SHIP_HEIGHT = 0.035
    SHIE_BASE_Y = 0.04
    ship = None
    ship_coordinates = [(0, 0), (0, 0), (0, 0)]

    state_game_over = False
    state_game_started = False

    begin_sound = None
    galaxy_sound = None
    gameover_impact_sound = None
    gameover_voice_sound = None
    music_sound = None
    restart_sound = None

    game_onver_clock_event = None

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.init_audio()
        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.init_tiles()
        self.init_ship()
        self.reset_game()

        if self.is_desktop():
            self._keyboard = Window.request_keyboard(self.keyboard_closed, self)
            self._keyboard.bind(on_key_down=self.on_keyboard_down)
            self._keyboard.bind(on_key_up=self.on_keyboard_up)

        Clock.schedule_interval(self.update, 1 / 60)
        self.galaxy_sound.play()

    def init_audio(self):
        self.begin_sound = SoundLoader.load('audio/begin.wav')
        self.galaxy_sound = SoundLoader.load('audio/galaxy.wav')
        self.gameover_impact_sound = SoundLoader.load('audio/gameover_impact.wav')
        self.gameover_voice_sound = SoundLoader.load('audio/gameover_voice.wav')
        self.music_sound = SoundLoader.load('audio/music1.wav')
        self.restart_sound = SoundLoader.load('audio/restart.wav')

        self.music_sound.volume = 1
        self.galaxy_sound.volume = .25
        self.begin_sound.volume = .25
        self.gameover_voice_sound.volume = .25
        self.restart_sound.volume = .25
        self.gameover_impact_sound.volume = .6


    def reset_game(self):
        self.current_offset_y = 0
        self.current_y_loop = 0
        self.current_speed_x = 0
        self.current_offset_x = 0
        self.SPEED = .5
        self.speed_x = 1.5
        self.score = 'SCORE: 0'
        self.tiles_coordinates = []
        self.pre_fill_tiles_coordinates()
        self.generate_tile_coordinates()

        self.state_game_over = False


    def is_desktop(self):
        if platform in ('linux', 'win', 'macosx'):
            return True
        else:
            return False

    def check_ship_collision(self):
        for i in range(0, len(self.tiles_coordinates)):
            ti_x, ti_y = self.tiles_coordinates[i]
            if ti_y > self.current_y_loop + 1:
                return False
            if self.check_ship_collision_with_tile(ti_x, ti_y):
                return True
        return False

    def check_ship_collision_with_tile(self, ti_x, ti_y):
        xmin, ymin = self.get_tile_coordinates(ti_x, ti_y)
        xmax, ymax = self.get_tile_coordinates(ti_x + 1, ti_y + 1)
        for i in range(0, 3):
            px, py = self.ship_coordinates[i]
            if xmin <= px <= xmax and ymin <= py <= ymax:
                return True
        return False

    def init_tiles(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(self.NB_TILES):
                self.tiles.append(Quad())

    def init_ship(self):
        with self.canvas:
            Color(0, 0, 0)
            self.ship = Triangle()

    def update_ship(self):
        center_x = self.width / 2
        base_y = self.SHIE_BASE_Y * self.height
        ship_half_width = self.SHIP_WIDTH * self.width / 2
        ship_height = self.SHIP_HEIGHT * self.height

        self.ship_coordinates[0] = (center_x - ship_half_width, base_y)
        self.ship_coordinates[1] = (center_x, base_y + ship_height)
        self.ship_coordinates[2] = (center_x + ship_half_width, base_y)

        x1, y1 = self.transform(*self.ship_coordinates[0])
        x2, y2 = self.transform(*self.ship_coordinates[1])
        x3, y3 = self.transform(*self.ship_coordinates[2])
        self.ship.points = [x1, y1, x2, y2, x3, y3]

    def pre_fill_tiles_coordinates(self):
        # 10 tiles in a straight line
        for i in range(0, 10):
            self.tiles_coordinates.append((0, i))

    def generate_tile_coordinates(self):
        last_x = 0
        last_y = 0

        for i in range(len(self.tiles_coordinates) - 1, -1, -1):
            if self.tiles_coordinates[i][1] < self.current_y_loop:
                del self.tiles_coordinates[i]

        if len(self.tiles_coordinates) > 0:
            last_coordinates = self.tiles_coordinates[-1]
            last_x = last_coordinates[0]
            last_y = last_coordinates[1] + 1

        for i in range(len(self.tiles_coordinates), self.NB_TILES):
            r = random.randint(0, 2)
            # 0 -> straight
            # 1 -> right
            # 2 -> left
            start_index = -int(self.V_NB_LINES / 2) + 1
            end_index = start_index + self.V_NB_LINES - 1
            if last_x <= start_index:
                r = 1
            if last_x >= end_index:
                r = 2

            self.tiles_coordinates.append((last_x, last_y))
            if r == 1:
                last_x += 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))
            elif r == 2:
                last_x -= 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))

            last_y += 1

    def init_vertical_lines(self):
        with self.canvas:
            Color(1, 1, 1, .5)
            for i in range(self.V_NB_LINES):
                self.vertical_lines.append(Line())

    def get_line_x_from_index(self, index):
        central_line_x = int(self.width / 2)
        spacing = self.V_LINES_SPACING * self.width
        offset = index - 0.5
        line_x = central_line_x + offset * spacing + self.current_offset_x
        return line_x

    def get_line_y_from_index(self, index):
        spacing_y = self.H_LINES_SPACING * self.height
        line_y = index * spacing_y - self.current_offset_y
        return line_y

    def get_tile_coordinates(self, ti_x, ti_y):
        ti_y -= self.current_y_loop
        x = self.get_line_x_from_index(ti_x)
        y = self.get_line_y_from_index(ti_y)
        return x, y

    def update_tiles(self):
        for i in range(self.NB_TILES):
            tile = self.tiles[i]
            tile_coor_x, tile_coor_y = self.tiles_coordinates[i]
            xmin, ymin = self.get_tile_coordinates(tile_coor_x, tile_coor_y)
            xmax, ymax = self.get_tile_coordinates(tile_coor_x + 1, tile_coor_y + 1)

            x1, y1 = self.transform(xmin, ymin)
            x2, y2 = self.transform(xmin, ymax)
            x3, y3 = self.transform(xmax, ymax)
            x4, y4 = self.transform(xmax, ymin)

            tile.points = [x1, y1, x2, y2, x3, y3, x4, y4]

    def update_vertical_lines(self):
        start_index = -int(self.V_NB_LINES / 2) + 1
        for i in range(start_index, start_index + self.V_NB_LINES):
            line_x = self.get_line_x_from_index(i)
            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)
            self.vertical_lines[i].points = [x1, y1, x2, y2]

    def init_horizontal_lines(self):
        with self.canvas:
            Color(1, 1, 1, .5)
            for i in range(self.H_NB_LINES):
                self.horizontal_lines.append(Line())

    def update_horizontal_lines(self):
        start_index = -int(self.V_NB_LINES / 2) + 1
        end_index = start_index + self.V_NB_LINES - 1
        xmin = self.get_line_x_from_index(start_index)
        xmax = self.get_line_x_from_index(end_index)
        for i in range(self.H_NB_LINES):
            line_y = self.get_line_y_from_index(i)
            x1, y1 = self.transform(xmin, line_y)
            x2, y2 = self.transform(xmax, line_y)
            self.horizontal_lines[i].points = [x1, y1, x2, y2]

    def update(self, dt):
        time_factor = dt * 60
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tiles()
        self.update_ship()

        if not self.state_game_over and self.state_game_started:
            speed_y = self.SPEED * self.height / 100
            self.current_offset_y += speed_y * time_factor

            spacing_y = self.H_LINES_SPACING * self.height
            while self.current_offset_y >= spacing_y:
                self.current_offset_y -= spacing_y
                self.current_y_loop += 1
                self.score = 'SCORE: ' + str(self.current_y_loop)
                self.generate_tile_coordinates()
                print('loop:', self.current_y_loop)

            speed_x = self.current_speed_x * self.width / 100
            self.current_offset_x += speed_x * time_factor

        # Increase the SPEED according to the socre
        self.SPEED = min(self.MIN_SPEED + (self.current_y_loop / 500), self.MAX_SPEED)

        # Increase the Ship Side Movements
        self.speed_x = min(self.min_speed_x + (self.current_y_loop / 500), self.max_speed_x)

        if not self.check_ship_collision() and not self.state_game_over:
            self.state_game_over = True
            self.music_sound.stop()
            self.gameover_impact_sound.play()
            self.game_onver_clock_event = Clock.schedule_once(self.play_gameover_sound, 2)
            self.menu_widget.opacity = 1
            self.menu_title = 'G  A  M  E    O  V  E  R'
            self.menu_button_title = 'RESTART'
            print('Game Over')

    def play_gameover_sound(self, dt):
        if self.state_game_over:
            self.gameover_voice_sound.play()

    def on_menu_button_pressed(self):
        if self.state_game_over:
            self.restart_sound.play()
            self.game_onver_clock_event.cancel()
        else:
            self.begin_sound.play()
        self.music_sound.play()
        self.reset_game()
        print('Button')
        self.state_game_started = True
        self.menu_widget.opacity = 0

class GalaxyApp(App):
    pass


GalaxyApp().run()
