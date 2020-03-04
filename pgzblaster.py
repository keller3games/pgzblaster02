from random import choice, uniform
from enum import Enum
import pygame, pgzrun
from pgzblasterutils import sin_osc, tri_osc, decide

WIDTH, HEIGHT = 500, 700
W, H = WIDTH, HEIGHT
WH, HH = W/2, H/2

ROCKET_IMAGES = ['rocket01', 'rocket02', 'rocket03', 'rocket04','rocket05']
UFO_IMAGES = ['ufo01', 'ufo02', 'ufo03', 'ufo04', 'ufo05']
BOMB_IMAGES = ['bomb01', 'bomb02', 'bomb03', 'bomb04', 'bomb05']


class State(Enum):
    READY = 0
    PLAY = 1
    HIT = 2
    GAME_OVER = 3


class Ship(Actor):
    def __init__(self):
        Actor.__init__(self, 'ship')
        self.vel = 6
        self.score = 0
        self.lifes = 3
        self.init_position()

    def init_position(self):
        self.bottom = H-50
        self.centerx = WH

    def update(self):
        if keyboard.left:
            self.x -= self.vel
        if keyboard.right:
            self.x += self.vel
        if keyboard.up:
            self.y -= self.vel
        if keyboard.down:
            self.y += self.vel
        self.clamp_ip(0, 0, W, H-50)

    def launch_rocket(self):
        rocket = Rocket(self.x, self.y-50)
        game.rockets.append(rocket)

    def hit(self):
        sounds.ship_hit.play()
        self.lifes -= 1
        if self.lifes > 0:
            game.state = State.HIT
            clock.schedule(game.continue_to_play, 4)
            self.init_position()
        else:
            game.state = State.GAME_OVER
            clock.schedule(game.get_ready, 4)

class Rocket(Actor):
    def __init__(self, x, y):
        Actor.__init__(self, choice(ROCKET_IMAGES))
        sounds.rocket_launch.play()
        self.alive = True
        self.x = x
        self.y = y
        self.vel = 10

    def update(self):
        self.y -= self.vel
        if(self.top < 0):
            self.alive = False
        for actor in game.ufos + game.bombs:
            if self.colliderect(actor):
                actor.hit()
                self.alive = False
                return


class UFO(Actor):
    def __init__(self, y_linear, x1_freq, x2_freq, y_freq, osc_delay, bomb_rate):
        Actor.__init__(self, choice(UFO_IMAGES))
        self.alive = True
        self.y_linear = y_linear
        self.y = y_linear
        self.y_vel = 1
        self.x1_freq = x1_freq
        self.x2_freq = x2_freq
        self.y_freq = y_freq
        self.osc_delay = osc_delay
        self.bomb_rate = bomb_rate

    def update(self):
        x1_osc = tri_osc(self.x1_freq, 0, WH, self.osc_delay)
        x2_osc = tri_osc(self.x2_freq, 0, WH, self.osc_delay)
        y_osc = tri_osc(self.y_freq, -50, 50, self.osc_delay)

        self.x = x1_osc + x2_osc
        self.y_linear += self.y_vel
        self.y = self.y_linear + y_osc

        if self.top > H:
            self.alive = False

        if decide(self.bomb_rate) and self.top > 0:
            self.drop_bomb()

        if self.colliderect(game.ship):
            game.ship.hit()

    def drop_bomb(self):
        game.bombs.append(Bomb(self.center))

    def hit(self):
        sounds.ufo_hit.play()
        self.alive = False
        game.ship.score += 100


class UFOMother():
    def __init__(self):
        self.n_ufos = 7
        self.x1_freq = 0.1
        self.x2_freq = 0.1
        self.y_freq = 0.1
        self.osc_delay = 0.3
        self.bomb_rate = 0.002

    def new_squadron(self):
        result = [UFO((i*-40)-H/4,
                        self.x1_freq,
                        self.x2_freq,
                        self.y_freq,
                        i * self.osc_delay,
                        self.bomb_rate)
                  for i in range(0, self.n_ufos)]
        self.raise_difficulty()
        return result

    def raise_difficulty(self):
        self.n_ufos += 1
        self.x1_freq += uniform(0, 0.05)
        self.x2_freq += uniform(0, 0.05)
        self.y_freq += uniform(0, 0.05)
        self.osc_delay += uniform(0, 0.2)
        self.bomb_rate += 0.0005


class Bomb(Actor):
    def __init__(self, center):
        Actor.__init__(self, choice(BOMB_IMAGES))
        sounds.bomb_drop.play()
        self.alive = True
        self.center = center
        self.vel = 5

    def update(self):
        self.y += self.vel
        if self.top > HEIGHT:
            self.alive = False
        if self.colliderect(game.ship):
            game.ship.hit()
            self.alive = False

    def hit(self):
        sounds.bomb_hit.play()
        self.alive = False


class Game:
    def __init__(self):
        self.state = State.READY
        self.rockets = []
        self.ufos = []
        self.bombs = []
        self.ship = Ship()
        self.ufo_mother = UFOMother()

    def get_ready(self):
        self.state = State.READY
        self.init_actor_lists()
        self.ship = Ship()
        self.ufo_mother = UFOMother()

    def init_actor_lists(self):
        self.rockets = []
        self.ufos = []
        self.bombs = []

    def continue_to_play(self):
        self.state = State.PLAY
        self.init_actor_lists()
        self.ufos = self.ufo_mother.new_squadron()

    def update(self):
        for actor in self.rockets + self.bombs + self.ufos:
            actor.update()
        self.ship.update()

        self.rockets = [r for r in self.rockets if r.alive]
        self.ufos = [u for u in self.ufos if u.alive]
        self.bombs = [b for b in self.bombs if b.alive]

        if len(game.ufos) == 0:
            self.ufos = self.ufo_mother.new_squadron()


def center_message(text):
    screen.draw.text(text,
                    center=(WH, HH),
                    color="black",
                    fontsize=40)


def on_key_down():
    if game.state == State.READY:
        game.state = State.PLAY
        return

    if keyboard.space and game.state == State.PLAY:
        game.ship.launch_rocket()


def update():
    if game.state == State.PLAY:
        game.update()


def draw():
    screen.fill((255, 255, 255))

    if game.state == State.READY:
        center_message("PRESS ANY KEY TO START")

    if game.state == State.PLAY:
        for actor in game.rockets + game.bombs + game.ufos:
            actor.draw()
        game.ship.draw()

    if game.state == State.HIT:
        center_message("YOU'VE BEEN HIT")

    if game.state == State.GAME_OVER:
        center_message("GAME OVER")

    if game.state != State.READY:
        screen.draw.text("Ships: "+str(game.ship.lifes),
                         (20, H-30),
                         color="black")

        screen.draw.text("Score: "+str(game.ship.score),
                         (W-120, H-30),
                         color="black")

game = Game()
pygame.mixer.quit()
pygame.mixer.init(44100, -16, 2, 1024)
pgzrun.go()