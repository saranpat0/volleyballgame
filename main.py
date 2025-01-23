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

class Paddle(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.score = 0  # ใช้ตัวแปรปกติแทน NumericProperty
        self.size = (20, 100)  # กำหนดขนาดให้ Paddle

    def bounce_ball(self, ball):
        if self.collide_widget(ball):
            ball.velocity[0] *= -1.1  # เปลี่ยนจาก velocity_x เป็น velocity[0]

class Ball(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.velocity = Vector(4, 4)  # ให้มีความเร็วเริ่มต้น
        self.size = (30, 30)  # กำหนดขนาดให้ Ball
        self.center = (300, 300)  # ให้เริ่มต้นอยู่ตรงกลาง

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos

class VolleyballGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ball = Ball()
        self.player1 = Paddle(pos=(10, self.center_y))
        self.player2 = Paddle(pos=(self.width - 30, self.center_y))
        self.status_label = Label(text="Press Start to Play", font_size=24)

        # เพิ่ม Widget เข้าไปใน Layout
        self.add_widget(self.ball)
        self.add_widget(self.player1)
        self.add_widget(self.player2)
        self.add_widget(self.status_label)

    def serve_ball(self, velocity=(4, 4)):
        self.ball.velocity = Vector(*velocity)  # ใช้ Vector ตรงๆ แทนการกำหนดแยก x, y
        self.ball.center = self.center  # ให้เริ่มต้นจากตรงกลาง
        self.status_label.text = "Game On!"

    def update(self, dt):
        self.ball.move()
        print(f"Ball Position: {self.ball.pos}")  # Debug เช็คตำแหน่งบอล

        self.player1.bounce_ball(self.ball)
        self.player2.bounce_ball(self.ball)

        # Bounce off top and bottom
        if (self.ball.y < 0) or (self.ball.top > self.height):
            self.ball.velocity[1] *= -1  # แก้ให้ใช้ Vector[1] แทน velocity_y

        # Score points
        if self.ball.x < self.x:
            self.player2.score += 1
            self.serve_ball(velocity=(4, 4))
            self.status_label.text = f"Player 2 scores! Total: {self.player2.score}"
        if self.ball.x > self.width:
            self.player1.score += 1
            self.serve_ball(velocity=(-4, 4))
            self.status_label.text = f"Player 1 scores! Total: {self.player1.score}"

    def on_touch_move(self, touch):
        if touch.x < self.width / 3:
            self.player1.center_y = touch.y
        if touch.x > self.width * 2 / 3:
            self.player2.center_y = touch.y

class MenuScreen(BoxLayout):
    def __init__(self, start_game_callback, open_settings_callback, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.add_widget(Label(text="Volleyball Game!", font_size=32))
        self.add_widget(Button(text="Start Game", on_press=start_game_callback))
        self.add_widget(Button(text="Settings", on_press=open_settings_callback))
        self.add_widget(Button(text="Quit", on_press=lambda x: App.get_running_app().stop()))

class SettingsScreen(BoxLayout):
    def __init__(self, back_callback, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.add_widget(Label(text="Settings", font_size=24))
        self.add_widget(Label(text="Volume"))
        self.add_widget(ToggleButton(text="Mute"))
        self.add_widget(Button(text="Back", on_press=back_callback))

class VolleyballApp(App):
    def build(self):
        self.root_widget = BoxLayout(orientation='vertical')
        self.menu = MenuScreen(start_game_callback=self.start_game, open_settings_callback=self.open_settings)
        self.settings = SettingsScreen(back_callback=self.show_menu)
        self.game = VolleyballGame()
        self.show_menu()
        return self.root_widget
    
    def show_menu(self, instance=None):
        self.root_widget.clear_widgets()
        self.root_widget.add_widget(self.menu)
    
    def open_settings(self, instance):
        self.root_widget.clear_widgets()
        self.root_widget.add_widget(self.settings)

    def start_game(self, instance):
        self.root_widget.clear_widgets()
        self.root_widget.add_widget(self.game)
        self.game.serve_ball()
        Clock.schedule_interval(self.game.update, 1.0 / 60.0)

if __name__ == "__main__":
    VolleyballApp().run()
