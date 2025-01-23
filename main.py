from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.graphics import Rectangle, Color, Ellipse

class Paddle(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (50, 50)
        self.velocity = Vector(0, 0)
        self.gravity = -0.5
        self.jump_strength = 10
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

    def _update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos

    def _update_positions(self, *args):
        self.player1.pos = (50, self.height / 2)
        self.player2.pos = (self.width - 100, self.height / 2)
        self.ball.center = self.center
        self.score_label.pos = (0, self.height - 50)

    def serve_ball(self, velocity=(6, 6)):
        self.ball.center = self.center
        self.ball.velocity = Vector(*velocity)
        print(f"Ball served at {self.ball.center} with velocity {self.ball.velocity}")

    def update(self, dt):
        self.ball.move()
        self.player1.move()
        self.player2.move()

        if self.ball.top > self.height or self.ball.y < 0:
            self.ball.velocity.y *= -1

        if self.ball.collide_widget(self.player1) or self.ball.collide_widget(self.player2):
            self.ball.velocity.x *= -1.1
            self.ball.velocity.y *= 1.1

        if self.ball.x < 0:
            self.player2_score += 1
            self.serve_ball(velocity=(6, 6))
        if self.ball.x > self.width:
            self.player1_score += 1
            self.serve_ball(velocity=(-6, 6))

        self.score_label.text = f"Player 1: {self.player1_score} | Player 2: {self.player2_score}"

    def on_touch_down(self, touch):
        if touch.x < self.width / 2:
            self.player1.jump()
        else:
            self.player2.jump()

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
            on_press=lambda x: self.start_game()
        )
        root.add_widget(self.start_button)

        return root

    def start_game(self):
        self.game.serve_ball()
        Clock.unschedule(self.game.update)
        Clock.schedule_interval(self.game.update, 1.0 / 60.0)
        print("Game started and update scheduled!")
        if self.start_button.parent:
            self.start_button.parent.remove_widget(self.start_button)

if __name__ == "__main__":
    VolleyballApp().run()