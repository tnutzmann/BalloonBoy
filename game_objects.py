import random

import pygame as pg
from setting import *


class GameObject:
    def __init__(self,
                 body: pg.Surface,
                 position: pg.Vector2 = pg.Vector2(0, 0),
                 velocity: pg.Vector2 = pg.Vector2(0, 0),
                 gravity: bool = False):
        self.position: pg.Vector2 = position.copy()
        self.velocity: pg.Vector2 = velocity.copy()
        self.body: pg.Surface = body
        self.gravity: bool = gravity

    def update(self, delta: float):
        if self.gravity:
            self.velocity.y += GRAVITY_CONST * delta
        if self.velocity.length() > MAX_PAYER_SPEED:
            self.velocity = self.velocity.normalize() * MAX_PAYER_SPEED
        self.position += self.velocity * delta

    def draw(self, screen: pg.Surface):
        screen.blit(self.body, self.position)


class Player(GameObject):
    def __init__(self,
                 position: pg.Vector2 = pg.Vector2(0, HEIGHT//2),
                 velocity: pg.Vector2 = pg.Vector2(0, 0),
                 gravity: bool = True):
        self.body = pg.transform.scale(pg.image.load("art/Boy2.png"), PLAYER_DIMENSION)

        GameObject.__init__(self, self.body, position, velocity, gravity)
        self.jetpack_is_running: bool = False
        self.on_ground: bool = False

    def jetpack_on(self):
        self.jetpack_is_running = True

    def jetpack_off(self):
        self.jetpack_is_running = False

    def update(self, delta: float):
        if self.jetpack_is_running:
            self.velocity.y -= JETPACK_POWER * delta
        super().update(delta)
        if self.position.y != pg.math.clamp(self.position.y, UPPER_BORDER, LOWER_BORDER - self.body.get_height()):
            self.position.y = pg.math.clamp(self.position.y, UPPER_BORDER, LOWER_BORDER - self.body.get_height())
            self.velocity.y = 0
        self.on_ground = (LOWER_BORDER - self.body.get_height()) == self.position.y

    def draw(self, screen: pg.Surface):
        super().draw(screen)


class Coin(GameObject):
    def __init__(self,
                 position: pg.Vector2 = pg.Vector2(WIDTH, HEIGHT // 2),
                 velocity: pg.Vector2 = pg.Vector2(-100, 0),
                 gravity: bool = False
                 ):
        self.body = pg.transform.scale(pg.image.load("art/Coin_1.png"), COIN_DIMENSION)
        GameObject.__init__(self, self.body, position, velocity, gravity)

        self.coin_animation = [
            pg.transform.scale(pg.image.load("art/Coin_1.png"), COIN_DIMENSION),
            pg.transform.scale(pg.image.load("art/Coin_2.png"), COIN_DIMENSION),
            pg.transform.scale(pg.image.load("art/Coin_3.png"), COIN_DIMENSION),
            pg.transform.scale(pg.image.load("art/Coin_4.png"), COIN_DIMENSION),
            pg.transform.scale(pg.image.load("art/Coin_5.png"), COIN_DIMENSION),
            pg.transform.scale(pg.image.load("art/Coin_6.png"), COIN_DIMENSION),
            pg.transform.scale(pg.image.load("art/Coin_7.png"), COIN_DIMENSION),
            pg.transform.scale(pg.image.load("art/Coin_8.png"), COIN_DIMENSION),
        ]
        self.animation_counter = 0

    def collide(self, player: Player):
        return pg.Rect(player.position,
                       player.body.get_size()).colliderect(pg.Rect(self.position, self.body.get_size()))

    def update(self, delta: float):
        super().update(delta)
        self.animation_counter += 1
        if self.animation_counter == len(self.coin_animation)*10:
            self.animation_counter = 0
        self.body = self.coin_animation[self.animation_counter//10]


class Obstacle(GameObject):
    def __init__(self,
                 position: pg.Vector2 = pg.Vector2(WIDTH, HEIGHT // 2),
                 velocity: pg.Vector2 = pg.Vector2(-100, 0),
                 gravity: bool = False
                 ):
        self.body = pg.transform.scale(pg.image.load("art/Arrow.png"), OBSTACLE_DIMENSION)
        GameObject.__init__(self, self.body, position, velocity, gravity)

    def collide(self, player: Player):
        return pg.Rect(player.position,
                       player.body.get_size()).colliderect(pg.Rect(self.position,
                                                                   (self.body.get_width()//2, self.body.get_height())))


class Cloud(GameObject):
    def __init__(self,
                 position: pg.Vector2 = pg.Vector2(WIDTH, HEIGHT // 2),
                 velocity: pg.Vector2 = pg.Vector2(-random.randint(10, 200), 0),
                 gravity: bool = False):
        self.body = pg.transform.scale(pg.image.load("art/Cloud.png"), OBSTACLE_DIMENSION)
        GameObject.__init__(self, self.body, position, velocity, gravity)
