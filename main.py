import pygame as pg
import sys
from setting import *
from game_objects import *
import random
from math import sqrt


class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode(RESOLUTION)
        self.clock = pg.time.Clock()

        self.points: int = 0
        self.is_running: bool = False

        pg.font.init()
        self.font = pg.font.SysFont(FONT, 40)
        self.points_text = self.font.render(f'Points: {self.points}', False, TEXTCOLOR)
        self.menu_text = self.font.render("Tap SPACE to play!", False, TEXTCOLOR)

        self.player: Player = Player(position=pg.Vector2(START_WIDTH, START_HEIGHT))
        self.player.velocity.y = MENU_IDLE

        self.coins: list[Coin] = []
        self.obstacles: list[Obstacle] = []
        self.spawn_timer: float = 0

        self.clouds: list[Cloud] = []
        self.cloud_timer: float = 0

        self.cloud_border_image = pg.image.load("./art/CloudBoarder.png")
        self.logo_image = pg.image.load("./art/BalloonBoy.png")
        pg.mixer_music.load("art/POL-azure-waters-short.wav")

        self.credits_text = pg.font.SysFont(FONT, 18).render('Game: Tony Nutzmann, Music: playonloop.com (Azure '
                                                             'Waters)',
                                                             False, TEXTCOLOR)

    def start(self):
        self.player = Player()
        self.player.position = (WIDTH * 0.1, LOWER_BORDER - self.player.body.get_height())

        self.coins = []
        self.obstacles = []
        self.points = 0
        self.is_running = True

    def spawn_object(self, delta):
        self.spawn_timer += delta
        if self.spawn_timer >= OBJECT_SPAWN / (sqrt(self.points + 1)):
            self.spawn_timer = 0
            random.choice((self.add_obstacle, self.add_coin))()

    def spawn_cloud(self, delta):
        self.cloud_timer += delta
        if self.cloud_timer >= 1 / CLOUD_SPAWN_RATE:
            self.cloud_timer = 0
            self.clouds.append(Cloud(position=pg.Vector2(WIDTH, random.randint(UPPER_BORDER, LOWER_BORDER)),
                                     velocity=pg.Vector2(-random.randint(10, 200), 0)))

    def add_obstacle(self):
        self.obstacles.append(
            Obstacle(position=pg.Vector2(WIDTH, random.randint(UPPER_BORDER, LOWER_BORDER - OBSTACLE_HEIGHT)),
                     velocity=pg.Vector2(-(MIN_OBJECT_SPEED + OBJECT_SPEED_INTERVAL * self.points),
                                         0)))

    def add_coin(self):
        self.coins.append(Coin(position=pg.Vector2(WIDTH, random.randint(UPPER_BORDER, LOWER_BORDER - OBSTACLE_HEIGHT)),
                               velocity=pg.Vector2(-(MIN_OBJECT_SPEED + OBJECT_SPEED_INTERVAL * self.points), 0)))

    def update(self):
        delta = self.clock.get_time() * 0.001
        pg.display.flip()
        self.clock.tick(FPS)
        pg.display.set_caption(f'BalloonBoy\t\tFPS: {self.clock.get_fps() : .1f}')
        # pg.display.set_caption(f'{self.clock.get_time()}')

        self.spawn_object(delta)
        self.spawn_cloud(delta)

        for c in self.coins:
            if c.collide(self.player):
                self.coins.remove(c)
                self.points += 1
            elif c.position.x == -100:
                self.coins.remove(c)
            else:
                c.update(delta=delta)

        for o in self.obstacles:
            if o.collide(self.player):
                self.is_running = False
            elif o.position.x == -100:
                self.obstacles.remove(o)
            o.update(delta=delta)

        for c in self.clouds:
            if c.position.x == -100:
                self.clouds.remove(c)
            else:
                c.update(delta=delta)

        self.player.update(delta=delta)

    def draw(self):
        self.screen.fill(BACKGROUND)

        for c in self.clouds:
            c.draw(screen=self.screen)

        for c in self.coins:
            c.draw(screen=self.screen)

        for o in self.obstacles:
            o.draw(screen=self.screen)

        for i in range(0, WIDTH, self.cloud_border_image.get_width()):
            self.screen.blit(source=self.cloud_border_image, dest=(i, LOWER_BORDER))
            self.screen.blit(source=pg.transform.flip(self.cloud_border_image, False, True), dest=(i, 0))

        self.points_text = self.font.render(f'{self.points}', False, TEXTCOLOR)
        self.screen.blit(source=self.points_text, dest=(10, 10))

        self.player.draw(screen=self.screen)

    def check_events(self):
        for event in pg.event.get():
            if self.is_running:
                if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                    self.player.jetpack_on()
                elif event.type == pg.KEYUP and event.key == pg.K_SPACE:
                    self.player.jetpack_off()
            else:
                if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                    self.start()
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()

    def menu(self):
        pg.display.flip()
        self.clock.tick(FPS)
        pg.display.set_caption(f'BalloonBoy\t\tFPS: {self.clock.get_fps() : .1f}')

        delta = self.clock.get_time() * 0.001
        self.screen.fill(BACKGROUND)

        self.spawn_cloud(delta)
        for c in self.clouds:
            if c.position.x == -100:
                self.clouds.remove(c)
            else:
                c.update(delta=delta)
                c.draw(screen=self.screen)

        self.player.gravity = False
        if self.player.position.y < START_HEIGHT - 50:
            self.player.velocity.y = MENU_IDLE
        if self.player.position.y > START_HEIGHT + 50:
            self.player.velocity.y = -MENU_IDLE
        self.player.update(delta)
        self.player.gravity = True
        self.player.draw(self.screen)

        for i in range(0, WIDTH, self.cloud_border_image.get_width()):
            self.screen.blit(source=self.cloud_border_image, dest=(i, LOWER_BORDER))
            self.screen.blit(source=pg.transform.flip(self.cloud_border_image, False, True), dest=(i, 0))

        self.screen.blit(source=self.menu_text, dest=((WIDTH - self.menu_text.get_width()) // 2, HEIGHT // 2))

        if self.points != 0:
            self.points_text = self.font.render(f'Points: {self.points}', False, TEXTCOLOR)
            self.screen.blit(source=self.points_text, dest=((WIDTH - self.points_text.get_width()) // 2, HEIGHT // 4))
        else:
            self.screen.blit(source=self.logo_image, dest=((WIDTH - self.logo_image.get_width()) // 2, HEIGHT // 4))
            self.screen.blit(source=self.credits_text, dest=(20, HEIGHT - 20))

    def run(self):
        pg.mixer_music.load("art/POL-azure-waters-short.wav")
        pg.mixer_music.set_volume(MUSIC_VOLUME)
        pg.mixer_music.play(-1)
        while True:
            while self.is_running:
                self.update()
                self.draw()
                self.check_events()
            while not self.is_running:
                self.menu()
                self.check_events()


if __name__ == '__main__':
    game = Game()
    game.run()
