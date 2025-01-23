from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.togglebutton import ToggleButton

class Paddle(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.velocity = Vector(0, 0)  # ใช้สำหรับการกระโดด
        self.gravity = -0.5  # แรงโน้มถ่วง
        self.jump_strength = 10

    def move(self):
        self.velocity.y += self.gravity
        self.y += self.velocity.y
        if self.y < 0:  # ไม่ให้หลุดล่าง
            self.y = 0
            self.velocity.y = 0

    def jump(self):
        if self.y == 0:  # กระโดดได้เฉพาะบนพื้น
            self.velocity.y = self.jump_strength

class Ball(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.velocity = Vector(6, 6)

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos

class VolleyballGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ball = Ball(size=(30, 30), center=self.center)
        self.player1 = Paddle(size=(50, 50), pos=(50, 0))
        self.player2 = Paddle(size=(50, 50), pos=(self.width - 100, 0))
        self.net = Widget(size=(10, self.height), pos=(self.center_x - 5, 0))  # ตาข่าย

        self.add_widget(self.ball)
        self.add_widget(self.player1)
        self.add_widget(self.player2)
        self.add_widget(self.net)

        self.score_label = Label(text="Player 1: 0 | Player 2: 0", size_hint=(1, None), height=50)
        self.add_widget(self.score_label)

        self.player1_score = 0
        self.player2_score = 0

    def serve_ball(self, velocity=(6, 6)):
        self.ball.center = self.center
        self.ball.velocity = Vector(*velocity)

    def update(self, dt):
        self.ball.move()
        self.player1.move()
        self.player2.move()

        # Bounce off walls
        if self.ball.top > self.height or self.ball.y < 0:
            self.ball.velocity.y *= -1

        # Bounce off paddles
        if self.ball.collide_widget(self.player1) or self.ball.collide_widget(self.player2):
            self.ball.velocity.x *= -1.1
            self.ball.velocity.y *= 1.1

        # Score points
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
        game = VolleyballGame()
        root.add_widget(game)

        start_button = Button(text="Start Game", size_hint=(1, None), height=50, on_press=lambda x: game.serve_ball())
        root.add_widget(start_button)

        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return root

if __name__ == "__main__":
    VolleyballApp().run()
