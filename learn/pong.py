from random import randint, choice
from time import sleep

from kivy.app import App
from kivy.uix.widget import Widget, WidgetException
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock
# from kivy.core.window import Window


class PongPaddle(Widget):
    score = NumericProperty(0)

    def bounce_ball(self, ball):
        if self.collide_widget(ball):
            vx, vy = ball.velocity
            offset = (ball.center_y - self.center_y) / (self.height / 2)
            bounced = Vector(-1 * vx, vy)
            vel = bounced * 1.1
            ball.velocity = vel.x, vel.y + offset


class PongBall(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    _move = True

    def move(self):
        if self._move:
            self.pos = Vector(*self.velocity) + self.pos


class PongGame(Widget):
    ball = ObjectProperty(None)
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)
    btn_start = ObjectProperty(None)
    winner_label = ObjectProperty(None)

    _run = False

    def __init__(self, **kwargs):
        super(PongGame, self).__init__(**kwargs)
        # self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        # self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self.rectangle = self.canvas.children[1]

    def on_btn_start_press(self):
        if self._run:
            self.stop()
        else:
            self.start()

    def update(self, dt):
        if not self._run:
            return

        self.ball.move()

        # bounce of paddles
        self.player1.bounce_ball(self.ball)
        self.player2.bounce_ball(self.ball)

        # bounce off top and bottom
        if self.ball.y < 0 or self.ball.top > self.height:
            self.ball.velocity_y *= -1

        # Went of to a side to score point ?
        if self.ball.x < self.x:
            self.player2.score += 1
            self.serve_ball()
        if self.ball.x > self.width:
            self.player1.score += 1
            self.serve_ball()

        self.check_stats()

    def stop(self):
        self.ball._move = False
        self._run = False
        self.remove_widget(self.ball)
        self.btn_start.text = 'Start'

    def start(self):
        self.player1.score = 0
        self.player2.score = 0
        try:
            self.add_widget(self.ball)
        except WidgetException:
            # Error on first run
            pass
        self._run = True
        self.ball._move = True
        self.serve_ball()
        self.rectangle.size = 10, self.height
        self.btn_start.text = 'Stop'
        self.winner_label.text = ''

    def check_stats(self):
        win = ''
        if self.player1.score == 1:
            win = 'Player 1 WINS!'
        elif self.player2.score == 1:
            win = 'Player 2 WINS!'

        if win:
            self.winner_label.pos = self.center_x - self.winner_label.size[0] / 2, self.center_y
            self.winner_label.text = win
            self.rectangle.size = 0, 0
            self.stop()

    def on_touch_move(self, touch):
        if touch.x < self.width / 2:
            self.player1.center_y = touch.y
        if touch.x > self.width - self.width / 2:
            self.player2.center_y = touch.y

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        key = keycode[1]

        if key == 'w':
            self.player1.center_y += 30
        elif key == 's':
            self.player1.center_y -= 30
        elif key == 'up':
            self.player2.center_y += 30
        elif key == 'down':
            self.player2.center_y -= 30

    def serve_ball(self):
        self.ball.size = 50, 50
        self.ball.center = self.center
        numbers = range(-12, -8) + range(8, 12)
        self.ball.velocity = (choice(numbers), randint(2, 4))


class PongApp(App):
    def build(self):
        game = PongGame()
        game.serve_ball()
        Clock.schedule_interval(game.update, 1.0 / 60)
        return game

