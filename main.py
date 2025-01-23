from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.clock import Clock
from kivy.vector import Vector
from functools import partial
from kivy.properties import NumericProperty, ObjectProperty, StringProperty

class Paddle(Widget):
    score = NumericProperty(0)
    def bounce_ball(self, ball):
        if self.collide_widget(ball):
            ball.velocity_x *= -1.1
class Ball(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ObjectProperty(Vector(0, 0))
    def move(self):
        self.pos = Vector(*self.velocity) + self.pos
class VolleyballGame(Widget):
    ball = ObjectProperty(None)
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)
    status_label = ObjectProperty(None)
    def __init__(self, **kwargs):
        super().__init__(self,**kwargs)
        self.ball = Ball()
        self.player1 = Paddle(pos=(10, self.center_y))
        self.player2 = Paddle(pos=(self.width - 30, self.center_y))
        self.status_label = Label(text="Press Start to Play", font_size=24)            
        self.add_widget(self.ball)
        self.add_widget(self.player1)
        self.add_widget(self.player2)
        self.add_widget(self.status_label)

    def serve_ball(self, velocity=(4, 0)):
        self.ball.velocity_x, self.ball.velocity_y = velocity
        self.status_label.text = "Game On!"

    def update(self, dt):
        self.ball.move()

        # Bounce off paddles
        self.player1.bounce_ball(self.ball)
        self.player2.bounce_ball(self.ball)

        # Bounce off top and bottom
        if (self.ball.y < 0) or (self.ball.top > self.height):
            self.ball.velocity_y *= -1

        # Score points
        if self.ball.x < self.x:
            self.player2.score += 1
            self.serve_ball(velocity=(4, 0))
            self.status_label.text = f"Player 2 scores! Total: {self.player2.score}"
        if self.ball.x > self.width:
            self.player1.score += 1
            self.serve_ball(velocity=(-4, 0))
            self.status_label.text = f"Player 1 scores! Total: {self.player1.score}"

    def on_touch_move(self, touch):
        if touch.x < self.width / 3:
            self.player1.center_y = touch.y
        if touch.x > self.width * 2 / 3:
            self.player2.center_y = touch.y

class MenuScreen(BoxLayout):
    def __init__(self, start_game_callback, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.start_game_callback = start_game_callback
        self.add_widget(Label(text="Volleyball Game!", font_size=32))
        self.add_widget(Button(text="Start Game", on_press=partial(self.start_game_callback)))
        self.add_widget(Button(text="Quit", on_press=lambda x: App.get_running_app().stop()))
class VolleyballApp(App):
    def build(self):
        self.root_widget = BoxLayout(orientation='vertical')
        self.menu = MenuScreen(start_game_callback=self.start_game)
        self.game = VolleyballGame()
        self.root_widget.add_widget(self.menu)
        return self.root_widget
    def start_game(self, instance):
        self.root_widget.clear_widgets()
        self.root_widget.add_widget(self.game)
        self.game.serve_ball()
        Clock.schedule_interval(self.game.update, 1.0 / 60.0)

if __name__ == "__main__":
    VolleyballApp().run()
