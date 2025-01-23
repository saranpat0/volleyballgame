from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.graphics import Rectangle, Color, Ellipse
from kivy.core.window import Window

class Paddle(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (100, 100)
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

class Net(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(0, 0, 0)
            self.rect = Rectangle(size=(10, self.height), pos=self.pos)
        self.bind(pos=self.update_graphics_pos, size=self.update_graphics_pos)

    def update_graphics_pos(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

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
            size_hint=(1, None),
            height=50,
            pos=(0, self.height - 50),
        )
        self.add_widget(self.score_label)

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
        self.score_label.pos = (0, self.height - 50)
        self.net.pos = (self.width / 2 - 5, 0)
        self.net.size = (10, self.height)

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

        # Ball collision with paddles
        if self.ball.collide_widget(self.player1) or self.ball.collide_widget(self.player2):
            self.ball.velocity.y = abs(self.ball.velocity.y)  # Ensure the ball bounces upwards

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

class VolleyballApp(App):
    def build(self):
        root = FloatLayout()
        self.game = VolleyballGame(size=root.size)
        root.add_widget(self.game)

        self.start_button = Button(
            text="Start Game",
            size_hint=(1, None),
            height=50,
            pos=(0, 0),
            on_press=self.start_game
        )
        root.add_widget(self.start_button)

        return root

    def start_game(self, instance):
        self.game.serve_ball()
        Clock.unschedule(self.game.update)
        Clock.schedule_interval(self.game.update, 1.0 / 60.0)
        print("Game started and update scheduled!")
        if self.start_button.parent:
            self.start_button.parent.remove_widget(self.start_button)

if __name__ == "__main__":
    VolleyballApp().run()