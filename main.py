from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.graphics import Rectangle, Color, Ellipse
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.slider import Slider
from kivy.core.audio import SoundLoader
from kivy.uix.image import Image

class Paddle(Widget):
    def __init__(self, image_source, **kwargs):
        super().__init__(**kwargs)
        self.size = (100, 150)
        self.velocity = Vector(0, 0)
        self.gravity = -0.5
        self.jump_strength = 10
        self.speed = 7  # ความเร็วของผู้เล่น
        with self.canvas:
            self.image = Image(source=image_source, size=self.size, pos=self.pos)
        self.bind(pos=self.update_graphics_pos, size=self.update_graphics_pos)

    def update_graphics_pos(self, *args):
        self.image.pos = self.pos
        self.image.size = self.size

    def move(self):
        self.velocity.y += self.gravity
        self.y += self.velocity.y
        if self.y < 0:
            self.y = 0
            self.velocity.y = 0

    def jump(self):
        if self.y == 0:
            self.velocity.y = self.jump_strength

    def move_left(self):
        if self.x - self.speed >= 0:  # ป้องกันไม่ให้เคลื่อนที่ออกนอกขอบด้านซ้าย
            self.x -= self.speed

    def move_right(self):
        if self.right + self.speed <= self.parent.width:  # ป้องกันไม่ให้เคลื่อนที่ออกนอกขอบด้านขวา
            self.x += self.speed

class Ball(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.velocity = Vector(6, 6)
        self.size = (30, 30)
        with self.canvas:
            Color(1, 1, 0)
            self.ellipse = Ellipse(size=self.size, pos=self.pos)
        self.bind(pos=self.update_graphics_pos, size=self.update_graphics_pos)

    def update_graphics_pos(self, *args):
        self.ellipse.pos = self.pos
        self.ellipse.size = self.size

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos

    def increase_speed(self, factor=1.001):
        self.velocity = self.velocity * factor

class Net(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = 180  # ความสูงของตาข่าย
        self.thickness = 10  # ความหนาของตาข่าย
        with self.canvas:
            Color(0, 0, 0)
            self.rect = Rectangle(size=(self.thickness, self.height), pos=self.pos)
        self.bind(pos=self.update_graphics_pos, size=self.update_graphics_pos)

    def update_graphics_pos(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def set_height(self, height):
        self.height = height
        self.size = (self.thickness, self.height)
        self.update_graphics_pos()

    def set_thickness(self, thickness):
        self.thickness = thickness
        self.size = (self.thickness, self.height)
        self.update_graphics_pos()

class VolleyballGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(0.5, 0.5, 0.5, 1) 
            self.platform = Rectangle(size=(self.width, 50), pos=(0, 0))
            self.bind(size=self._update_rect, pos=self._update_rect)
        with self.canvas.before:
            self.bg_image = Image(source='assets/bg.png', allow_stretch=True, keep_ratio=False)
            self.bg = Rectangle(size=self.size, pos=self.pos)
            self.canvas.add(self.bg_image.canvas)

        self.player1 = Paddle(image_source='assets/player1.png', pos=(50, self.height / 2))
        self.add_widget(self.player1)

        self.player2 = Paddle(image_source='assets/player2.png', pos=(self.width - 100, self.height / 2))
        self.add_widget(self.player2)

        self.ball = Ball(center=self.center)
        self.add_widget(self.ball)

        self.net = Net(pos=(self.width / 2 - 5, 0))
        self.add_widget(self.net)

        self.player1_score = 0
        self.player2_score = 0

        self.score_label = Label(
            text="Player 1: 0 | Player 2: 0",
            size_hint=(None, None),
            size=(200, 50),
            pos=(self.width / 2 - 100, self.height - 50),  # ตำแหน่งคะแนน
        )
        self.add_widget(self.score_label)

        self.win_label = Label(
            text="",
            size_hint=(None, None),
            size=(200, 50),
            pos=(self.width / 2 - 100, self.height / 2),  # ตำแหน่งข้อความชนะ
        )
        self.add_widget(self.win_label)

        self.replay_button = Button(
            text="Replay",
            size_hint=(None, None),
            size=(100, 50),
            pos=(self.width / 2 - 50, self.height / 2 - 100),
            on_press=self.replay_game,
        )
        self.replay_button.opacity = 0  # ซ่อนปุ่มในตอนแรก
        self.add_widget(self.replay_button)

        self.back_to_menu_button = Button(
            text="Back to Main Menu",
            size_hint=(None, None),
            size=(200, 50),
            pos=(self.width / 2 - 100, self.height / 2 - 160),
            on_press=self.back_to_main_menu,
        )
        self.back_to_menu_button.opacity = 0  # ซ่อนปุ่มในตอนแรก
        self.add_widget(self.back_to_menu_button)

        self.bind(size=self._update_bg, pos=self._update_bg)
        self.bind(size=self._update_positions)

        Window.bind(on_key_down=self.on_key_down)
        Window.bind(on_key_up=self.on_key_up)

        self.keys_pressed = set()
        self.serving_player = 1  # ผู้ที่จะเริ่มเสิร์ฟ
    def _update_rect(self, *args):
        self.platform.size = (self.width, 50)
        self.platform.pos = (0, 0)

    def _update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos
        self.bg_image.size = self.size
        self.bg_image.pos = self.pos

    def _update_positions(self, *args):
        self.player1.pos = (50, self.height / 2)
        self.player2.pos = (self.width - 100, self.height / 2)
        self.ball.center = self.center
        self.score_label.pos = (self.width / 2 - 100, self.height - 50)  
        self.win_label.pos = (self.width / 2 - 100, self.height / 2) 
        self.replay_button.pos = (self.width / 2 - 50, self.height / 2 - 100)
        self.back_to_menu_button.pos = (self.width / 2 - 100, self.height / 2 - 160)
        self.net.pos = (self.width / 2 - self.net.thickness / 2, 0)
        self.net.set_height(self.height * 2 / 5)  #ความสูงของตาข่ายเป็น 2/5 ของความสูงหน้าจอ

    def serve_ball(self, velocity=(6, 6)):#การสลับกันเสิร์ฟ
        if self.serving_player == 1:
            self.ball.center = (self.player1.center_x, self.player1.top + self.ball.height)
            self.ball.velocity = Vector(*velocity)
            self.serving_player = 2  #เสิร์ฟครั้งต่อไปจะเป็นผู้เล่น 2
        else:
            self.ball.center = (self.player2.center_x, self.player2.top + self.ball.height)
            self.ball.velocity = Vector(-velocity[0], velocity[1])
            self.serving_player = 1  #เสิร์ฟครั้งต่อไปจะเป็นผู้เล่น 1
        print(f"Ball served at {self.ball.center} with velocity {self.ball.velocity}")

    def update(self, dt):
        self.ball.move()
        self.player1.move()
        self.player2.move()

        # เพิ่มความเร็วของลูกบอล
        self.ball.increase_speed()

        # การชนของลูกบอลกับด้านบน
        if self.ball.top > self.height:
            self.ball.velocity.y *= -1
            App.get_running_app().ball_hit_sound.play()

        # ลูกบอลชนกับด้านซ้ายและขวา
        if self.ball.x < 0 or self.ball.right > self.width:
            self.ball.velocity.x *= -1
            App.get_running_app().ball_hit_sound.play()

        # ลูกบอลชนกับด้านล่าง
        if self.ball.y < 0:
            if self.ball.center_x < self.width / 2:
                self.player2_score += 1
            else:
                self.player1_score += 1
            self.serve_ball(velocity=(6, 6))

        # ตรวจสอบเงื่อนไขการชนะ
        if self.player1_score >= 7:
            self.win_label.text = "Player 1 Wins!"
            self.replay_button.opacity = 1  # แสดงปุ่ม replay
            self.back_to_menu_button.opacity = 1  # แสดงปุ่ม back to menu
            Clock.unschedule(self.update)  # หยุดเกม
        elif self.player2_score >= 7:
            self.win_label.text = "Player 2 Wins!"
            self.replay_button.opacity = 1  # แสดงปุ่ม replay
            self.back_to_menu_button.opacity = 1  # แสดงปุ่ม back to menu
            Clock.unschedule(self.update)  # หยุดเกม

        # การชนของลูกบอลกับผู้เล่น
        if self.ball.collide_widget(self.player1):
            if self.ball.center_x < self.player1.center_x:
                self.ball.velocity.x = -abs(self.ball.velocity.x)  # ทำให้ลูกบอลกระเด็นไปทางซ้าย
                self.ball.right = self.player1.x  # ปรับตำแหน่งลูกบอลไปทางซ้ายของผู้เล่น
            else:
                self.ball.velocity.x = abs(self.ball.velocity.x)  # ทำให้ลูกบอลกระเด็นไปทางขวา
                self.ball.x = self.player1.right  # ปรับตำแหน่งลูกบอลไปทางขวาของผู้เล่น
            self.ball.velocity.y = abs(self.ball.velocity.y)  # ทำให้ลูกบอลกระเด็นขึ้น
            App.get_running_app().ball_hit_sound.play()       
        elif self.ball.collide_widget(self.player2):
            if self.ball.center_x < self.player2.center_x:
                self.ball.velocity.x = -abs(self.ball.velocity.x)  # ทำให้ลูกบอลกระเด็นไปทางซ้าย
                self.ball.right = self.player2.x  # ปรับตำแหน่งลูกบอลไปทางซ้ายของผู้เล่น
            else:
                self.ball.velocity.x = abs(self.ball.velocity.x)  # ทำให้ลูกบอลกระเด็นไปทางขวา
                self.ball.x = self.player2.right  # ปรับตำแหน่งลูกบอลไปทางขวาของผู้เล่น
            self.ball.velocity.y = abs(self.ball.velocity.y)  # ทำให้ลูกบอลกระเด็นขึ้น
            App.get_running_app().ball_hit_sound.play()

        # การชนของลูกบอลกับตาข่าย
        if self.ball.collide_widget(self.net):
            self.ball.velocity.x *= -1  # กลับทิศทางของความเร็วในแนว x ของลูกบอล
            App.get_running_app().ball_hit_sound.play()
        self.score_label.text = f"Player 1: {self.player1_score} | Player 2: {self.player2_score}"

        # ทำให้ผู้เล่นผ่านตาข่ายไม่ได้
        if self.player1.collide_widget(self.net):
            self.player1.x = self.net.x - self.player1.width
        if self.player2.collide_widget(self.net):
            self.player2.x = self.net.right

        # อัปเดตการเคลื่อนไหวของผู้เล่นตามปุ่มที่กด
        if 'w' in self.keys_pressed:
            self.player1.jump()
        if 'a' in self.keys_pressed:
            self.player1.move_left()
        if 'd' in self.keys_pressed:
            self.player1.move_right()
        if 'up' in self.keys_pressed:
            self.player2.jump()
        if 'left' in self.keys_pressed:
            self.player2.move_left()
        if 'right' in self.keys_pressed:
            self.player2.move_right()

    def on_key_down(self, window, key, *args):
        if key == 119:  # ปุ่ม W
            self.keys_pressed.add('w')
        elif key == 97:  # ปุ่ม A
            self.keys_pressed.add('a')
        elif key == 100:  # ปุ่ม D
            self.keys_pressed.add('d')
        elif key == 273:  # ปุ่มลูกศรขึ้น
            self.keys_pressed.add('up')
        elif key == 276:  # ปุ่มลูกศรซ้าย
            self.keys_pressed.add('left')
        elif key == 275:  # ปุ่มลูกศรขวา
            self.keys_pressed.add('right')

    def on_key_up(self, window, key, *args):
        if key == 119:  # ปุ่ม W
            self.keys_pressed.discard('w')
        elif key == 97:  # ปุ่ม A
            self.keys_pressed.discard('a')
        elif key == 100:  # ปุ่ม D
            self.keys_pressed.discard('d')
        elif key == 273:  # ปุ่มลูกศรขึ้น
            self.keys_pressed.discard('up')
        elif key == 276:  # ปุ่มลูกศรซ้าย
            self.keys_pressed.discard('left')
        elif key == 275:  # ปุ่มลูกศรขวา
            self.keys_pressed.discard('right')

    def replay_game(self, instance):
        self.reset_game()
        self.serve_ball(velocity=(6, 6))
        Clock.schedule_interval(self.update, 1.0 / 60.0)  # เริ่มเกมใหม่

    def back_to_main_menu(self, instance):
        self.reset_game()
        App.get_running_app().show_start_screen()

    def reset_game(self):
        self.player1_score = 0
        self.player2_score = 0
        self.win_label.text = ""
        self.replay_button.opacity = 0  # ซ่อนปุ่ม replay
        self.back_to_menu_button.opacity = 0  # ซ่อนปุ่ม back to menu
        self.ball.center = self.center
        self.ball.velocity = Vector(6, 6)

class VolleyballApp(App):
    def build(self):
        self.root = FloatLayout()
        self.bg_image = Image(source='assets/bg.png', allow_stretch=True, keep_ratio=False)
        self.root.add_widget(self.bg_image)
        self.game = VolleyballGame(size=self.root.size)
        self.sound = SoundLoader.load('assets/Aioli - Andrew Langdon.mp3')
        self.ball_hit_sound = SoundLoader.load('assets/ball_hitted.mp3')
        self.ball_hit_sound.volume = 0.5  # ระดับเสียงเริ่มต้น
        self.show_start_screen()
        return self.root

    def show_start_screen(self, *args):
        if self.sound:
            self.sound.loop = True
            self.sound.play()

        start_layout = FloatLayout()
        self.menu_bg_image = Image(source='assets/sky.png', allow_stretch=True, keep_ratio=False)
        start_layout.add_widget(self.menu_bg_image)
        
        box_layout = BoxLayout(orientation='vertical', spacing=10, padding=50)
        
        self.start_button = Button(
            text="Start Game",
            size_hint=(None, None),
            size=(200, 100),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            on_press=self.show_mode_selection
        )
        box_layout.add_widget(self.start_button)

        self.settings_button = Button(
            text="Settings",
            size_hint=(None, None),
            size=(200, 100),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            on_press=self.show_settings
        )
        box_layout.add_widget(self.settings_button)

        self.quit_button = Button(
            text="Quit",
            size_hint=(None, None),
            size=(200, 100),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            on_press=self.quit_game
        )
        box_layout.add_widget(self.quit_button)

        start_layout.add_widget(box_layout)

        self.root.clear_widgets()
        self.root.add_widget(start_layout)

    def _update_bg(self, *args):
        self.bg.size = self.root.size
        self.bg.pos = self.root.pos
        self.bg_image.size = self.root.size
        self.bg_image.pos = self.root.pos
        self.menu_bg_image.size = self.root.size
        self.menu_bg_image.pos = self.root.pos

    def show_mode_selection(self, instance):
        mode_layout = FloatLayout()
        self.menu_bg_image = Image(source='assets/sky.png', allow_stretch=True, keep_ratio=False)
        mode_layout.add_widget(self.menu_bg_image)
        
        box_layout = BoxLayout(orientation='vertical', spacing=10, padding=50)
        
        self.player_vs_cpu_button = Button(
            text="Player 1 vs CPU",
            size_hint=(None, None),
            size=(200, 100),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            on_press=self.show_ai_message
        )
        box_layout.add_widget(self.player_vs_cpu_button)

        self.player_vs_player_button = Button(
            text="Player 1 vs Player 2",
            size_hint=(None, None),
            size=(200, 100),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            on_press=self.start_game
        )
        box_layout.add_widget(self.player_vs_player_button)

        mode_layout.add_widget(box_layout)

        self.root.clear_widgets()
        self.root.add_widget(mode_layout)

    def show_ai_message(self, instance):
        self.root.clear_widgets()
        message_layout = BoxLayout(orientation='vertical', spacing=10, padding=50)
        
        self.message_label = Label(
            text="Sorry, I haven't done AI yet",
            size_hint=(None, None),
            size=(200, 100),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        message_layout.add_widget(self.message_label)

        self.back_button = Button(
            text="Back",
            size_hint=(None, None),
            size=(200, 100),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            on_press=lambda x: self.show_start_screen()
        )
        message_layout.add_widget(self.back_button)

        self.root.add_widget(message_layout)

    def show_settings(self, instance):
        self.root.clear_widgets()
        settings_layout = FloatLayout()
        self.settings_bg_image = Image(source='assets/sky.png', allow_stretch=True, keep_ratio=False)
        settings_layout.add_widget(self.settings_bg_image)
        
        box_layout = BoxLayout(orientation='vertical', spacing=10, padding=50)
        
        self.volume_label = Label(
            text="Background Music Volume",
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        box_layout.add_widget(self.volume_label)

        self.volume_slider = Slider(
            min=0,
            max=1,
            value=self.sound.volume if self.sound else 0.5,
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.volume_slider.bind(value=self.on_volume_change)
        box_layout.add_widget(self.volume_slider)

        self.ball_hit_volume_label = Label(
            text="Ball Hit Sound Volume",
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        box_layout.add_widget(self.ball_hit_volume_label)

        self.ball_hit_volume_slider = Slider(
            min=0,
            max=1,
            value=self.ball_hit_sound.volume if self.ball_hit_sound else 0.5,
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.ball_hit_volume_slider.bind(value=self.on_ball_hit_volume_change)
        box_layout.add_widget(self.ball_hit_volume_slider)

        self.back_button = Button(
            text="Back",
            size_hint=(None, None),
            size=(200, 100),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            on_press=lambda x: self.show_start_screen()
        )
        box_layout.add_widget(self.back_button)

        settings_layout.add_widget(box_layout)
        self.root.add_widget(settings_layout)

    def on_volume_change(self, instance, value):
        if self.sound:
            self.sound.volume = value

    def on_ball_hit_volume_change(self, instance, value):
        if self.ball_hit_sound:
            self.ball_hit_sound.volume = value

    def start_game(self, instance):
        if self.sound:
            self.sound.stop()
        self.game.serve_ball()
        Clock.unschedule(self.game.update)
        Clock.schedule_interval(self.game.update, 1.0 / 60.0)
        self.root.clear_widgets()
        self.root.add_widget(self.game)

    def quit_game(self, instance):
        App.get_running_app().stop()

if __name__ == "__main__":
    VolleyballApp().run()