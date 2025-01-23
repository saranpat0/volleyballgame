from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.graphics import Rectangle, Color

class Paddle(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (50, 50)
        self.velocity = Vector(0, 0)
        self.gravity = -0.5
        self.jump_strength = 10

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

    def _update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos

    def serve_ball(self, velocity=(6, 6)):
        self.ball.center = self.center
        self.ball.velocity = Vector(*velocity)

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

    def start_game(self):
        self.serve_ball()
        Clock.unschedule(self.update)
        Clock.schedule_interval(self.update, 1.0 / 60.0)
        print("Game started and update scheduled!")

class VolleyballApp(App):
    def build(self):
        root = FloatLayout()
        self.game = VolleyballGame(size=root.size)
        root.add_widget(self.game)

        start_button = Button(
            text="Start Game",
            size_hint=(1, None),
            height=50,
            pos=(0, 0),
            on_press=lambda x: self.game.start_game()
        )
        root.add_widget(start_button)

        # Start the game automatically when the app is built
        self.game.start_game()

        return root

if __name__ == "__main__":
    VolleyballApp().run()
