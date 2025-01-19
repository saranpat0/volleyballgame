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
from kivy.properties import NumericProperty
from kivy.properties import ObjectProperty

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
class VollyeballGame(Widget):
    ball = ObjectProperty(None)
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)
    status_label = ObjectProperty(None)
class menu(Boxlayout):
        def __init__(self, call_gamestart, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.call_gamestart = call_gamestart
        self.add_widget(Label(text="Volleyball Game!", font_size=32))
        self.add_widget(Button(text="Start Game", on_press=self.call_gamestart))
        self.add_widget(Button(text="Quit", on_press=lambda x: App.get_running_app().stop()))
class VolleyballApp(App):
    pass