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

class Paddle(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (100, 150)
        self.velocity = Vector(0, 0)
        self.gravity = -0.5
        self.jump_strength = 10
        self.speed = 7  # Speed of the player
        with self.canvas:
            Color(1, 0, 0)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.update_graphics_pos, size=self.update_graphics_pos)

    def update_graphics_pos(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

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
        if self.x - self.speed >= 0:  # Prevent moving out of the left boundary
            self.x -= self.speed

    def move_right(self):
        if self.right + self.speed <= self.parent.width:  # Prevent moving out of the right boundary
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

    def increase_speed(self, factor=1.01):
        self.velocity = self.velocity * factor

class Net(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = 200  # Default height of the net
        self.thickness = 10  # Default thickness of the net
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
        with self.canvas.before:
            Color(0.5, 0.7, 1)
            self.bg = Rectangle(size=self.size, pos=self.pos)

        self.player1 = Paddle(pos=(50, self.height / 2))
        self.add_widget(self.player1)

        self.player2 = Paddle(pos=(self.width - 100, self.height / 2))
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
            pos=(self.width / 2 - 100, self.height - 50),  # Centered at the top
        )
        self.add_widget(self.score_label)

        self.win_label = Label(
            text="",
            size_hint=(None, None),
            size=(200, 50),
            pos=(self.width / 2 - 100, self.height / 2),  # Centered in the middle
        )
        self.add_widget(self.win_label)

        self.replay_button = Button(
            text="Replay",
            size_hint=(None, None),
            size=(100, 50),
            pos=(self.width / 2 - 50, self.height / 2 - 100),
            on_press=self.replay_game,
        )
        self.replay_button.opacity = 0  # Hide the button initially
        self.add_widget(self.replay_button)

        self.bind(size=self._update_bg, pos=self._update_bg)
        self.bind(size=self._update_positions)

        Window.bind(on_key_down=self.on_key_down)
        Window.bind(on_key_up=self.on_key_up)

        self.keys_pressed = set()
        self.serving_player = 1  # Start with player 1 serving

    def _update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos

    def _update_positions(self, *args):
        self.player1.pos = (50, self.height / 2)
        self.player2.pos = (self.width - 100, self.height / 2)
        self.ball.center = self.center
        self.score_label.pos = (self.width / 2 - 100, self.height - 50)  # Centered at the top
        self.win_label.pos = (self.width / 2 - 100, self.height / 2)  # Centered in the middle
        self.replay_button.pos = (self.width / 2 - 50, self.height / 2 - 100)
        self.net.pos = (self.width / 2 - self.net.thickness / 2, 0)
        self.net.set_height(self.height * 2 / 5)  # Set net height to 2/5 of the screen height

    def serve_ball(self, velocity=(6, 6)):
        if self.serving_player == 1:
            self.ball.center = (self.player1.center_x, self.player1.top + self.ball.height)
            self.ball.velocity = Vector(*velocity)
            self.serving_player = 2  # Next serve will be by player 2
        else:
            self.ball.center = (self.player2.center_x, self.player2.top + self.ball.height)
            self.ball.velocity = Vector(-velocity[0], velocity[1])
            self.serving_player = 1  # Next serve will be by player 1
        print(f"Ball served at {self.ball.center} with velocity {self.ball.velocity}")

    def update(self, dt):
        self.ball.move()
        self.player1.move()
        self.player2.move()

        # Gradually increase the ball's speed
        self.ball.increase_speed()

        # Ball collision with top
        if self.ball.top > self.height:
            self.ball.velocity.y *= -1

        # Ball collision with left and right
        if self.ball.x < 0 or self.ball.right > self.width:
            self.ball.velocity.x *= -1

        # Ball collision with bottom
        if self.ball.y < 0:
            if self.ball.center_x < self.width / 2:
                self.player2_score += 1
            else:
                self.player1_score += 1
            self.serve_ball(velocity=(6, 6))

        # Check for win condition
        if self.player1_score >= 7:
            self.win_label.text = "Player 1 Wins!"
            self.replay_button.opacity = 1  # Show the replay button
            Clock.unschedule(self.update)  # Stop the game
        elif self.player2_score >= 7:
            self.win_label.text = "Player 2 Wins!"
            self.replay_button.opacity = 1  # Show the replay button
            Clock.unschedule(self.update)  # Stop the game

        # Ball collision with paddles
        if self.ball.collide_widget(self.player1):
            if self.ball.center_x < self.player1.center_x:
                self.ball.velocity.x = -abs(self.ball.velocity.x)  # Ensure the ball bounces to the left
                self.ball.right = self.player1.x  # Adjust ball position to the left of the player
            else:
                self.ball.velocity.x = abs(self.ball.velocity.x)  # Ensure the ball bounces to the right
                self.ball.x = self.player1.right  # Adjust ball position to the right of the player
            self.ball.velocity.y = abs(self.ball.velocity.y)  # Ensure the ball bounces upwards
        elif self.ball.collide_widget(self.player2):
            if self.ball.center_x < self.player2.center_x:
                self.ball.velocity.x = -abs(self.ball.velocity.x)  # Ensure the ball bounces to the left
                self.ball.right = self.player2.x  # Adjust ball position to the left of the player
            else:
                self.ball.velocity.x = abs(self.ball.velocity.x)  # Ensure the ball bounces to the right
                self.ball.x = self.player2.right  # Adjust ball position to the right of the player
            self.ball.velocity.y = abs(self.ball.velocity.y)  # Ensure the ball bounces upwards

        # Ball collision with net
        if self.ball.collide_widget(self.net):
            self.ball.velocity.x *= -1  # Invert the x-component of the ball's velocity

        self.score_label.text = f"Player 1: {self.player1_score} | Player 2: {self.player2_score}"

        # Prevent players from passing through the net
        if self.player1.collide_widget(self.net):
            self.player1.x = self.net.x - self.player1.width
        if self.player2.collide_widget(self.net):
            self.player2.x = self.net.right

        # Update player movements based on keys pressed
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
        if key == 119:  # W key
            self.keys_pressed.add('w')
        elif key == 97:  # A key
            self.keys_pressed.add('a')
        elif key == 100:  # D key
            self.keys_pressed.add('d')
        elif key == 273:  # Up arrow key
            self.keys_pressed.add('up')
        elif key == 276:  # Left arrow key
            self.keys_pressed.add('left')
        elif key == 275:  # Right arrow key
            self.keys_pressed.add('right')

    def on_key_up(self, window, key, *args):
        if key == 119:  # W key
            self.keys_pressed.discard('w')
        elif key == 97:  # A key
            self.keys_pressed.discard('a')
        elif key == 100:  # D key
            self.keys_pressed.discard('d')
        elif key == 273:  # Up arrow key
            self.keys_pressed.discard('up')
        elif key == 276:  # Left arrow key
            self.keys_pressed.discard('left')
        elif key == 275:  # Right arrow key
            self.keys_pressed.discard('right')

    def replay_game(self, instance):
        self.player1_score = 0
        self.player2_score = 0
        self.win_label.text = ""
        self.replay_button.opacity = 0  # Hide the replay button
        self.serve_ball(velocity=(6, 6))
        Clock.schedule_interval(self.update, 1.0 / 60.0)  # Restart the game

class VolleyballApp(App):
    def build(self):
        self.root = FloatLayout()
        self.game = VolleyballGame(size=self.root.size)
        self.sound = SoundLoader.load('assets/Aioli - Andrew Langdon.mp3')
        self.show_start_screen()
        return self.root

    def show_start_screen(self, *args):
        if self.sound:
            self.sound.loop = True
            self.sound.play()

        start_layout = FloatLayout()
        
        with start_layout.canvas.before:
            Color(0.5, 0.7, 1)  # สีพื้นหลัง (สีเทา)
            self.bg = Rectangle(size=self.root.size, pos=self.root.pos)
            start_layout.bind(size=self._update_bg, pos=self._update_bg)

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

    def show_mode_selection(self, instance):
        mode_layout = FloatLayout()
        
        with mode_layout.canvas.before:
            Color(0.5, 0.7, 1)  # สีพื้นหลัง (สีฟ้า)
            self.bg = Rectangle(size=self.root.size, pos=self.root.pos)
            mode_layout.bind(size=self._update_bg, pos=self._update_bg)

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
        
        with settings_layout.canvas.before:
            Color(0.5, 0.7, 1)  # สีพื้นหลัง (สีฟ้า)
            self.bg = Rectangle(size=self.root.size, pos=self.root.pos)
            settings_layout.bind(size=self._update_bg, pos=self._update_bg)

        box_layout = BoxLayout(orientation='vertical', spacing=10, padding=50)
        
        self.volume_label = Label(
            text="Volume",
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