#!/usr/bin/env python

# Space Invaders
# Created by Lee Robinson

from pygame import *
import sys
from os.path import abspath, dirname
from random import choice
import numpy as np
import gymnasium as gym
from gymnasium import spaces

SPEED_LEVELS = (1, 10, 50)

BASE_PATH = abspath(dirname(__file__))
FONT_PATH = BASE_PATH + '/fonts/'
IMAGE_PATH = BASE_PATH + '/images/'
SOUND_PATH = BASE_PATH + '/sounds/'

# Colors (R, G, B)
WHITE = (255, 255, 255)
GREEN = (78, 255, 87)
YELLOW = (241, 255, 0)
BLUE = (80, 255, 239)
PURPLE = (203, 0, 255)
RED = (237, 28, 36)

ACTIONS = [
    (0, False),     # 0: stay
    (-1, False),    # 1: left
    (1, False),     # 2: right
    (0, True),      # 3: shoot
    (-1, True),     # 4: left + shoot
    (1, True)       # 5: right + shoot
]

SCREEN = display.set_mode((800, 600))
FONT = FONT_PATH + 'space_invaders.ttf'
IMG_NAMES = ['ship', 'mystery',
             'enemy1_1', 'enemy1_2',
             'enemy2_1', 'enemy2_2',
             'enemy3_1', 'enemy3_2',
             'explosionblue', 'explosiongreen', 'explosionpurple',
             'laser', 'enemylaser']
IMAGES = {name: image.load(IMAGE_PATH + '{}.png'.format(name)).convert_alpha()
          for name in IMG_NAMES}

BLOCKERS_POSITION = 450
ENEMY_DEFAULT_POSITION = 65  # Initial value for a new game
ENEMY_MOVE_DOWN = 35

LOGIC_FPS = 60
STEP_MS = 1000 / LOGIC_FPS

class Ship(sprite.Sprite):
    def __init__(self):
        sprite.Sprite.__init__(self)
        self.image = IMAGES['ship']
        self.rect = self.image.get_rect(topleft=(375, 540))
        self.speed = 5

    def update_logic(self, direction):
        if direction == -1 and self.rect.x > 10:
            self.rect.x -= self.speed
        elif direction == 1 and self.rect.x < 740:
            self.rect.x += self.speed

    def update(self, *args):
        game.screen.blit(self.image, self.rect)


class Bullet(sprite.Sprite):
    def __init__(self, xpos, ypos, direction, speed, filename, side):
        sprite.Sprite.__init__(self)
        self.image = IMAGES[filename]
        self.rect = self.image.get_rect(topleft=(xpos, ypos))
        self.speed = speed
        self.direction = direction
        self.side = side
        self.filename = filename

    def update_logic(self):
        self.rect.y += int(self.speed * self.direction)

        if self.rect.y < 15 or self.rect.y > 600:
            self.kill()

    def update(self, *args):
        game.screen.blit(self.image, self.rect)


class Enemy(sprite.Sprite):
    def __init__(self, row, column):
        sprite.Sprite.__init__(self)
        self.row = row
        self.column = column
        self.images = []
        self.load_images()
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()

    def toggle_image(self):
        self.index += 1
        if self.index >= len(self.images):
            self.index = 0
        self.image = self.images[self.index]

    def update(self, *args):
        game.screen.blit(self.image, self.rect)

    def load_images(self):
        images = {0: ['1_2', '1_1'],
                  1: ['2_2', '2_1'],
                  2: ['2_2', '2_1'],
                  3: ['3_1', '3_2'],
                  4: ['3_1', '3_2'],
                  }
        img1, img2 = (IMAGES['enemy{}'.format(img_num)] for img_num in
                      images[self.row])
        self.images.append(transform.scale(img1, (40, 35)))
        self.images.append(transform.scale(img2, (40, 35)))


class EnemiesGroup(sprite.Group):
    def __init__(self, columns, rows, current_time):
        sprite.Group.__init__(self)
        self.enemies = [[None] * columns for _ in range(rows)]
        self.columns = columns
        self.rows = rows
        self.leftAddMove = 0
        self.rightAddMove = 0
        self.moveTime = 600
        self.direction = 1
        self.rightMoves = 30
        self.leftMoves = 30
        self.moveNumber = 15
        self.timer = current_time
        self.bottom = game.enemyPosition + ((rows - 1) * 45) + 35
        self._aliveColumns = list(range(columns))
        self._leftAliveColumn = 0
        self._rightAliveColumn = columns - 1

    def update(self, current_time):
        if current_time - self.timer > self.moveTime:
            if self.direction == 1:
                max_move = self.rightMoves + self.rightAddMove
            else:
                max_move = self.leftMoves + self.leftAddMove

            if self.moveNumber >= max_move:
                self.leftMoves = 30 + self.rightAddMove
                self.rightMoves = 30 + self.leftAddMove
                self.direction *= -1
                self.moveNumber = 0
                self.bottom = 0
                for enemy in self:
                    enemy.rect.y += ENEMY_MOVE_DOWN
                    enemy.toggle_image()
                    if self.bottom < enemy.rect.y + 35:
                        self.bottom = enemy.rect.y + 35
            else:
                velocity = 10 if self.direction == 1 else -10
                for enemy in self:
                    enemy.rect.x += velocity
                    enemy.toggle_image()
                self.moveNumber += 1

            self.timer += self.moveTime

    def add_internal(self, *sprites):
        super(EnemiesGroup, self).add_internal(*sprites)
        for s in sprites:
            self.enemies[s.row][s.column] = s

    def remove_internal(self, *sprites):
        super(EnemiesGroup, self).remove_internal(*sprites)
        for s in sprites:
            self.kill(s)
        self.update_speed()

    def is_column_dead(self, column):
        return not any(self.enemies[row][column]
                       for row in range(self.rows))

    def random_bottom(self):
        col = choice(self._aliveColumns)
        col_enemies = (self.enemies[row - 1][col]
                       for row in range(self.rows, 0, -1))
        return next((en for en in col_enemies if en is not None), None)

    def update_speed(self):
        if len(self) == 1:
            self.moveTime = 200
        elif len(self) <= 10:
            self.moveTime = 400

    def kill(self, enemy):
        self.enemies[enemy.row][enemy.column] = None
        is_column_dead = self.is_column_dead(enemy.column)
        if is_column_dead:
            self._aliveColumns.remove(enemy.column)

        if enemy.column == self._rightAliveColumn:
            while self._rightAliveColumn > 0 and is_column_dead:
                self._rightAliveColumn -= 1
                self.rightAddMove += 5
                is_column_dead = self.is_column_dead(self._rightAliveColumn)

        elif enemy.column == self._leftAliveColumn:
            while self._leftAliveColumn < self.columns and is_column_dead:
                self._leftAliveColumn += 1
                self.leftAddMove += 5
                is_column_dead = self.is_column_dead(self._leftAliveColumn)


class Blocker(sprite.Sprite):
    def __init__(self, size, color, row, column):
        sprite.Sprite.__init__(self)
        self.height = size
        self.width = size
        self.color = color
        self.image = Surface((self.width, self.height))
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.row = row
        self.column = column

    def update(self, keys, *args):
        game.screen.blit(self.image, self.rect)


class Mystery(sprite.Sprite):
    def __init__(self, current_time):
        sprite.Sprite.__init__(self)
        self.image = IMAGES['mystery']
        self.image = transform.scale(self.image, (75, 35))
        self.rect = self.image.get_rect(topleft=(-80, 45))
        self.row = 5
        self.moveTime = 25000
        self.direction = 1
        self.timer = current_time
        self.mysteryEntered = mixer.Sound(SOUND_PATH + 'mysteryentered.wav')
        self.mysteryEntered.set_volume(0.3)
        self.playSound = True

    def update_logic(self, current_time):
        resetTimer = False
        passed = current_time - self.timer
        if passed > self.moveTime:
            if (self.rect.x < 0 or self.rect.x > 800) and self.playSound:
                self.mysteryEntered.play()
                self.playSound = False
            if self.rect.x < 840 and self.direction == 1:
                self.mysteryEntered.fadeout(4000)
                self.rect.x += 2
            if self.rect.x > -100 and self.direction == -1:
                self.mysteryEntered.fadeout(4000)
                self.rect.x -= 2

        if self.rect.x > 830:
            self.playSound = True
            self.direction = -1
            resetTimer = True
        if self.rect.x < -90:
            self.playSound = True
            self.direction = 1
            resetTimer = True
        if passed > self.moveTime and resetTimer:
            self.timer = current_time

    def update(self, *args):
        if 0 <= self.rect.x <= 800:
            game.screen.blit(self.image, self.rect)


class EnemyExplosion(sprite.Sprite):
    def __init__(self, enemy, current_time, *groups):
        super().__init__(*groups)
        self.image = transform.scale(self.get_image(enemy.row), (40, 35))
        self.image2 = transform.scale(self.get_image(enemy.row), (50, 45))
        self.rect = self.image.get_rect(topleft=(enemy.rect.x, enemy.rect.y))
        self.timer = current_time

    @staticmethod
    def get_image(row):
        img_colors = ['purple', 'blue', 'blue', 'green', 'green']
        return IMAGES['explosion{}'.format(img_colors[row])]

    def update(self, current_time, *args):
        passed = current_time - self.timer
        if passed <= 100:
            game.screen.blit(self.image, self.rect)
        elif passed <= 200:
            game.screen.blit(self.image2, (self.rect.x - 6, self.rect.y - 6))
        elif 400 < passed:
            self.kill()

    def update_logic(self, current_time):
        if current_time - self.timer > 400:
            self.kill()


class MysteryExplosion(sprite.Sprite):
    def __init__(self, mystery, score, current_time, *groups):
        super().__init__(*groups)
        self.text = Text(FONT, 20, str(score), WHITE,
                         mystery.rect.x + 20, mystery.rect.y + 6)
        self.timer = current_time

    def update(self, current_time, *args):
        passed = current_time - self.timer
        if passed <= 200 or 400 < passed <= 600:
            self.text.draw(game.screen)
        elif 600 < passed:
            self.kill()

    def update_logic(self, current_time):
        if current_time - self.timer > 600:
            self.kill()


class ShipExplosion(sprite.Sprite):
    def __init__(self, ship, current_time, *groups):
        super().__init__(*groups)
        self.image = IMAGES['ship']
        self.rect = self.image.get_rect(topleft=(ship.rect.x, ship.rect.y))
        self.timer = current_time

    def update(self, current_time, *args):
        passed = current_time - self.timer
        if 300 < passed <= 600:
            game.screen.blit(self.image, self.rect)
        elif 900 < passed:
            self.kill()

    def update_logic(self, current_time):
        if current_time - self.timer > 900:
            self.kill()


class Life(sprite.Sprite):
    def __init__(self, xpos, ypos):
        sprite.Sprite.__init__(self)
        self.image = IMAGES['ship']
        self.image = transform.scale(self.image, (23, 23))
        self.rect = self.image.get_rect(topleft=(xpos, ypos))

    def update(self, *args):
        game.screen.blit(self.image, self.rect)


class Text(object):
    def __init__(self, textFont, size, message, color, xpos, ypos):
        self.font = font.Font(textFont, size)
        self.surface = self.font.render(message, True, color)
        self.rect = self.surface.get_rect(topleft=(xpos, ypos))

    def draw(self, surface):
        surface.blit(self.surface, self.rect)


class SpaceInvaders(object):
    def __init__(self, start_speed=1):
        self.speed_index = SPEED_LEVELS.index(start_speed)
        self.speed_multiplier = start_speed

        global game
        game = self

        self.simulation_time = 0

        self.shoot_requested = False
        #self.steps_per_render = steps_per_render
        # It seems, in Linux buffersize=512 is not enough, use 4096 to prevent:
        #   ALSA lib pcm.c:7963:(snd_pcm_recover) underrun occurred
        mixer.pre_init(44100, -16, 1, 4096)
        init()
        self.clock = time.Clock()
        self.caption = display.set_caption('Space Invaders')
        self.screen = SCREEN
        self.background = image.load(IMAGE_PATH + 'background.jpg').convert()
        self.startGame = False
        self.mainScreen = True
        self.gameOver = False
        # Counter for enemy starting position (increased each new round)
        self.enemyPosition = ENEMY_DEFAULT_POSITION
        self.titleText = Text(FONT, 50, 'Space Invaders', WHITE, 164, 155)
        self.titleText2 = Text(FONT, 25, 'Press any key to continue', WHITE,
                               201, 225)
        self.gameOverText = Text(FONT, 50, 'Game Over', WHITE, 250, 270)
        self.nextRoundText = Text(FONT, 50, 'Next Round', WHITE, 240, 270)
        self.enemy1Text = Text(FONT, 25, '   =   10 pts', GREEN, 368, 270)
        self.enemy2Text = Text(FONT, 25, '   =  20 pts', BLUE, 368, 320)
        self.enemy3Text = Text(FONT, 25, '   =  30 pts', PURPLE, 368, 370)
        self.enemy4Text = Text(FONT, 25, '   =  ?????', RED, 368, 420)
        self.scoreText = Text(FONT, 20, 'Score', WHITE, 5, 5)
        self.livesText = Text(FONT, 20, 'Lives ', WHITE, 640, 5)

        self.life1 = Life(715, 3)
        self.life2 = Life(742, 3)
        self.life3 = Life(769, 3)
        self.livesGroup = sprite.Group(self.life1, self.life2, self.life3)

    def cycle_speed(self):
        self.speed_index = (self.speed_index + 1) % len(SPEED_LEVELS)
        self.speed_multiplier = SPEED_LEVELS[self.speed_index]

        print(f"Speed: x{self.speed_multiplier}")

    def advance(self, action):
        self.simulation_time += STEP_MS

        # Between rounds
        if not self.enemies and not self.explosionsGroup:
            if self.simulation_time - self.gameTimer >= 3000:
                self.enemyPosition += ENEMY_MOVE_DOWN
                self.reset(self.score)

            return self.get_state(), 0, self.gameOver
        
        return self.game_step(self.simulation_time, action)

    # def get_state(self):
    #     danger_bullets = [
    #         b for b in self.enemyBullets
    #         if b.rect.centery < self.player.rect.centery
    #     ]

    #     # bullet = min(
    #     #     danger_bullets,
    #     #     key=lambda b:
    #     #         3 * abs(b.rect.centerx - self.player.rect.centerx)
    #     #         + (self.player.rect.centery - b.rect.centery),
    #     #     default=None
    #     # )

    #     # bullet_dx = (
    #     #     (bullet.rect.centerx - self.player.rect.centerx) / 800
    #     #     if bullet else 0
    #     # )

    #     # bullet_dy = (
    #     #     (bullet.rect.centery - self.player.rect.centery) / 600
    #     #     if bullet else 0
    #     # )

    #     danger_bullets = sorted(
    #         danger_bullets,
    #         key=lambda b:
    #             3 * abs(b.rect.centerx - self.player.rect.centerx)
    #             + (self.player.rect.centery - b.rect.centery)
    #     )

    #     bullet1 = danger_bullets[0] if len(danger_bullets) > 0 else None
    #     bullet2 = danger_bullets[1] if len(danger_bullets) > 1 else None

    #     bullet1_dx = (
    #         (bullet1.rect.centerx - self.player.rect.centerx) / 800
    #         if bullet1 else 0
    #     )

    #     bullet1_dy = (
    #         (bullet1.rect.centery - self.player.rect.centery) / 600
    #         if bullet1 else 0
    #     )

    #     bullet2_dx = (
    #         (bullet2.rect.centerx - self.player.rect.centerx) / 800
    #         if bullet2 else 0
    #     )

    #     bullet2_dy = (
    #         (bullet2.rect.centery - self.player.rect.centery) / 600
    #         if bullet2 else 0
    #     ) 

    #     target = min(
    #         self.enemies,
    #         key=lambda e: abs(e.rect.centerx - self.player.rect.centerx),
    #         default=None
    #     )

    #     target_dx = (target.rect.centerx - self.player.rect.centerx) / 800 if target else 0
    #     target_dy = (target.rect.centery - self.player.rect.centery) / 600 if target else 0

    #     enemy_direction = self.enemies.direction

    #     return np.array([
    #         self.player.rect.x / 800,

    #         #bullet.rect.x / 800 if bullet else 0,
    #         #bullet.rect.y / 600 if bullet else 0,
    #         bullet1_dx,
    #         bullet1_dy,
    #         bullet2_dx,
    #         bullet2_dy,

    #         #target.rect.x / 800 if target else 0,
    #         #target.rect.y / 600 if target else 0,
    #         target_dx,
    #         target_dy,

    #         1.0 if self.bullets else 0.0,
    #         1.0 if enemy_direction == 1 else 0.0
    #     ], dtype=np.float32)

    def get_bullets(self):
        danger_bullets = [
            b for b in self.enemyBullets
            if b.rect.centery < self.player.rect.centery
            and abs(b.rect.centerx - self.player.rect.centerx) < (self.player.rect.width / 2 + 3)
            #and (self.player.rect.centery - b.rect.centery) > 50
        ]
        danger_bullets = sorted(
            danger_bullets,
            key=lambda b:
                3 * abs(b.rect.centerx - self.player.rect.centerx)
                + (self.player.rect.centery - b.rect.centery)
        )

        bullet1 = danger_bullets[0] if len(danger_bullets) > 0 else None
        bullet2 = danger_bullets[1] if len(danger_bullets) > 1 else None

        #print(f"bullet1: {bullet1}, bullet2: {bullet2}")

        bullet1_dx = (
            (bullet1.rect.centerx - self.player.rect.centerx) / 800
            if bullet1 else 0
        )

        bullet1_vertical_heat = (
            bullet1.rect.centery / self.player.rect.top
            if bullet1 else 0
        )

        bullet2_dx = (
            (bullet2.rect.centerx - self.player.rect.centerx) / 800
            if bullet2 else 0
        )

        bullet2_vertical_heat = (
            bullet2.rect.centery / self.player.rect.top
            if bullet2 else 0
        )

        return bullet1_dx, bullet1_vertical_heat, bullet2_dx, bullet2_vertical_heat

    def get_target(self):
        target = min(
            self.enemies,
            key=lambda e: abs(e.rect.centerx - self.player.rect.centerx),
            default=None
        )

        target_dx = (target.rect.centerx - self.player.rect.centerx) / 800 if target else 0
        target_dy = (target.rect.centery - self.player.rect.centery) / 600 if target else 0

        return target_dx, target_dy

    def get_state(self):
        bullet1_dx, bullet1_vertical_heat, bullet2_dx, bullet2_vertical_heat = self.get_bullets()

        target_dx, target_dy = self.get_target()

        enemy_direction = self.enemies.direction

        return np.array([
            self.player.rect.x / 800,

            bullet1_dx,
            bullet1_vertical_heat,
            bullet2_dx,
            bullet2_vertical_heat,

            target_dx,
            target_dy,

            1.0 if self.bullets else 0.0,
            1.0 if enemy_direction == 1 else 0.0
        ], dtype=np.float32)

    def reset_game(self):
        self.allBlockers = sprite.Group(
            self.make_blockers(1),
            self.make_blockers(2),
            self.make_blockers(3),
            self.make_blockers(4)
        )

        self.livesGroup.add(self.life1, self.life2, self.life3)
        self.enemyPosition = ENEMY_DEFAULT_POSITION
        self.gameOver = False

        self.reset(0)

        return self.get_state()

    def reset(self, score):
        self.gameOver = False
        self.simulation_time = time.get_ticks()
        self.player = Ship()
        self.playerGroup = sprite.Group(self.player)
        self.explosionsGroup = sprite.Group()
        self.bullets = sprite.Group()
        self.mysteryShip = Mystery(self.simulation_time)
        self.mysteryGroup = sprite.Group(self.mysteryShip)
        self.enemyBullets = sprite.Group()
        self.make_enemies(self.simulation_time)
        self.allSprites = sprite.Group(self.player, self.enemies,
                                       self.livesGroup, self.mysteryShip)
        self.keys = key.get_pressed()

        self.timer = self.simulation_time
        self.noteTimer = time.get_ticks()
        self.shipTimer = time.get_ticks()
        self.score = score
        self.create_audio()
        self.makeNewShip = False
        self.shipAlive = True

    def make_blockers(self, number):
        blockerGroup = sprite.Group()
        for row in range(4):
            for column in range(9):
                blocker = Blocker(10, GREEN, row, column)
                blocker.rect.x = 50 + (200 * number) + (column * blocker.width)
                blocker.rect.y = BLOCKERS_POSITION + (row * blocker.height)
                blockerGroup.add(blocker)
        return blockerGroup

    def create_audio(self):
        self.sounds = {}
        for sound_name in ['shoot', 'shoot2', 'invaderkilled', 'mysterykilled',
                           'shipexplosion']:
            self.sounds[sound_name] = mixer.Sound(
                SOUND_PATH + '{}.wav'.format(sound_name))
            self.sounds[sound_name].set_volume(0.2)

        self.musicNotes = [mixer.Sound(SOUND_PATH + '{}.wav'.format(i)) for i
                           in range(4)]
        for sound in self.musicNotes:
            sound.set_volume(0.5)

        self.noteIndex = 0

    def play_main_music(self, currentTime):
        if currentTime - self.noteTimer > self.enemies.moveTime:
            self.note = self.musicNotes[self.noteIndex]
            if self.noteIndex < 3:
                self.noteIndex += 1
            else:
                self.noteIndex = 0

            self.note.play()
            self.noteTimer += self.enemies.moveTime

    @staticmethod
    def should_exit(evt):
        # type: (pygame.event.EventType) -> bool
        return evt.type == QUIT or (evt.type == KEYUP and evt.key == K_ESCAPE)

    def shoot(self):
        if len(self.bullets) == 0 and self.shipAlive:
            if self.score < 1000:
                bullet = Bullet(self.player.rect.x + 23,
                                self.player.rect.y + 5, -1,
                                15, 'laser', 'center')
                self.bullets.add(bullet)
                self.allSprites.add(bullet)
                self.sounds['shoot'].play()
            else:
                leftbullet = Bullet(self.player.rect.x + 8,
                                    self.player.rect.y + 5, -1,
                                    15, 'laser', 'left')
                rightbullet = Bullet(self.player.rect.x + 38,
                                        self.player.rect.y + 5, -1,
                                        15, 'laser', 'right')
                self.bullets.add(leftbullet, rightbullet)
                self.allSprites.add(leftbullet, rightbullet)
                self.sounds['shoot2'].play()

    def check_input(self):
        self.keys = key.get_pressed()
        for e in event.get():
            if self.should_exit(e):
                sys.exit()
            if e.type == KEYDOWN:
                if e.key == K_SPACE:
                    self.shoot_requested = True
                elif e.key == K_TAB:
                    self.cycle_speed()

    def make_enemies(self, current_time):
        enemies = EnemiesGroup(10, 5, current_time)
        for row in range(5):
            for column in range(10):
                enemy = Enemy(row, column)
                enemy.rect.x = 157 + (column * 50)
                enemy.rect.y = self.enemyPosition + (row * 45)
                enemies.add(enemy)

        self.enemies = enemies

    def make_enemies_shoot(self, current_time):
        if current_time - self.timer > 700 and self.enemies:
            enemy = self.enemies.random_bottom()

            self.enemyBullets.add(
                Bullet(enemy.rect.x + 14, enemy.rect.y + 20,
                    1, 5, "enemylaser", "center")
            )

            self.allSprites.add(self.enemyBullets)
            self.timer = current_time

    def calculate_score(self, row):
        scores = {0: 30,
                  1: 20,
                  2: 20,
                  3: 10,
                  4: 10,
                  5: choice([50, 100, 150, 300])
                  }

        score = scores[row]
        self.score += score
        return score

    def create_main_menu(self):
        self.enemy1 = IMAGES['enemy3_1']
        self.enemy1 = transform.scale(self.enemy1, (40, 40))
        self.enemy2 = IMAGES['enemy2_2']
        self.enemy2 = transform.scale(self.enemy2, (40, 40))
        self.enemy3 = IMAGES['enemy1_2']
        self.enemy3 = transform.scale(self.enemy3, (40, 40))
        self.enemy4 = IMAGES['mystery']
        self.enemy4 = transform.scale(self.enemy4, (80, 40))
        self.screen.blit(self.enemy1, (318, 270))
        self.screen.blit(self.enemy2, (318, 320))
        self.screen.blit(self.enemy3, (318, 370))
        self.screen.blit(self.enemy4, (299, 420))

    def check_collisions(self, current_time):
        sprite.groupcollide(self.bullets, self.enemyBullets, True, True)

        for enemy in sprite.groupcollide(self.enemies, self.bullets,
                                         True, True).keys():
            self.sounds['invaderkilled'].play()
            self.calculate_score(enemy.row)
            EnemyExplosion(enemy, current_time, self.explosionsGroup)
            self.gameTimer = current_time

        for mystery in sprite.groupcollide(self.mysteryGroup, self.bullets,
                                           True, True).keys():
            mystery.mysteryEntered.stop()
            self.sounds['mysterykilled'].play()
            score = self.calculate_score(mystery.row)
            MysteryExplosion(mystery, score, current_time, self.explosionsGroup)
            newShip = Mystery(current_time)
            self.allSprites.add(newShip)
            self.mysteryGroup.add(newShip)

        for player in sprite.groupcollide(self.playerGroup, self.enemyBullets,
                                          True, True).keys():
            if self.life3.alive():
                self.life3.kill()
            elif self.life2.alive():
                self.life2.kill()
            elif self.life1.alive():
                self.life1.kill()
            else:
                self.gameOver = True
                self.startGame = False
                self.game_over_timer = current_time
            self.sounds['shipexplosion'].play()
            ShipExplosion(player, current_time, self.explosionsGroup)
            self.makeNewShip = True
            self.shipTimer = current_time
            self.shipAlive = False

        if self.enemies.bottom >= 540:
            sprite.groupcollide(self.enemies, self.playerGroup, True, True)
            if not self.player.alive() or self.enemies.bottom >= 600:
                self.gameOver = True
                self.startGame = False
                self.game_over_timer = current_time

        sprite.groupcollide(self.bullets, self.allBlockers, True, True)
        sprite.groupcollide(self.enemyBullets, self.allBlockers, True, True)
        if self.enemies.bottom >= BLOCKERS_POSITION:
            sprite.groupcollide(self.enemies, self.allBlockers, False, True)

    def create_new_ship(self, createShip, currentTime):
        if createShip and (currentTime - self.shipTimer > 900):
            self.player = Ship()
            self.allSprites.add(self.player)
            self.playerGroup.add(self.player)
            self.makeNewShip = False
            self.shipAlive = True

    def create_game_over(self, currentTime):
        self.screen.blit(self.background, (0, 0))
        passed = currentTime - self.game_over_timer
        if passed < 750:
            self.gameOverText.draw(self.screen)
        elif 750 < passed < 1500:
            self.screen.blit(self.background, (0, 0))
        elif 1500 < passed < 2250:
            self.gameOverText.draw(self.screen)
        elif 2250 < passed < 2750:
            self.screen.blit(self.background, (0, 0))
        elif passed > 3000:
            self.mainScreen = True

        for e in event.get():
            if self.should_exit(e):
                sys.exit()

    def get_human_action(self):
        direction = 0

        if self.keys[K_LEFT]:
            direction = -1
        elif self.keys[K_RIGHT]:
            direction = 1

        #action = (direction, self.shoot_requested)
        shoot = self.shoot_requested
        self.shoot_requested = False

        return ACTIONS.index((direction, shoot))

    def game_step(self, current_time, action_id):
        score_before = self.score
        ship_was_alive = self.shipAlive

        self.enemies.update(current_time)

        direction, should_shoot = ACTIONS[action_id]

        invalid_shoot = should_shoot and len(self.bullets) > 0

        if self.shipAlive:
            self.player.update_logic(direction)

        for obj in self.allSprites:
            if isinstance(obj, Bullet):
                obj.update_logic()

        reward = 0

        shot_x = self.player.rect.centerx

        will_hit = any(
            enemy.rect.left <= shot_x <= enemy.rect.right
            and enemy.rect.bottom < self.player.rect.top
            for enemy in self.enemies
        )

        if should_shoot:
            self.shoot()
            if will_hit:
                 reward += 1
            #     #print("rewarded for having aim and shooting", reward)
            # else:
            #     reward -= 1
            #     #print("punished for shooting without aim", reward)
        else:
            if will_hit and len(self.bullets) == 0:
                reward -= 0.1
        #         #print("punished for having aim but not shooting", reward)

        for mystery in self.mysteryGroup:
            mystery.update_logic(current_time)

        self.check_collisions(current_time)

        self.create_new_ship(self.makeNewShip, current_time)
        self.make_enemies_shoot(current_time)

        for explosion in self.explosionsGroup:
            explosion.update_logic(current_time)
        
        reward += self.score - score_before
        #if reward != 0:
        #    print("increased score", reward)

        if ship_was_alive and not self.shipAlive:
            reward -= 300

        #if invalid_shoot:
        #    reward -= 0.1

        state = self.get_state()

        _, heat1, _, heat2 = self.get_bullets()

        heat = heat1 + heat2
        
        reward -= ( heat * 10)

        #if heat > 0:
        #    print("heat", reward)

        #if heat > 0: print("HEAT", reward)

        target_dx, _ = self.get_target()

        if abs(target_dx) > 0.03:
            reward -= abs(target_dx) * 100
        #    print("punished for being far away", reward)
        else:
            reward += 0.1
            #print("reward for something", reward)

        done = self.gameOver

        #if reward < 0:
        #    print("reward", reward)

        return state, reward, done

    def render_frame(self):
        # Allow closing the window and changing speed during AI training
        for e in event.get():
            if self.should_exit(e):
                sys.exit()

            if e.type == KEYDOWN and e.key == K_TAB:
                self.cycle_speed()

        current_time = time.get_ticks()

        self.screen.blit(self.background, (0, 0))
        self.allBlockers.update(self.screen)

        self.scoreText2 = Text(
            FONT, 20, str(self.score), GREEN, 85, 5
        )

        self.scoreText.draw(self.screen)
        self.scoreText2.draw(self.screen)
        self.livesText.draw(self.screen)

        keys = key.get_pressed()
        self.allSprites.update(keys, current_time)
        self.explosionsGroup.update(self.simulation_time)

        display.update()

    def main(self):
        while True:
            if self.mainScreen:
                self.screen.blit(self.background, (0, 0))
                self.titleText.draw(self.screen)
                self.titleText2.draw(self.screen)
                self.enemy1Text.draw(self.screen)
                self.enemy2Text.draw(self.screen)
                self.enemy3Text.draw(self.screen)
                self.enemy4Text.draw(self.screen)
                self.create_main_menu()
                for e in event.get():
                    if self.should_exit(e):
                        sys.exit()
                    if e.type == KEYUP:
                        # Only create blockers on a new game, not a new round
                        self.allBlockers = sprite.Group(self.make_blockers(0),
                                                        self.make_blockers(1),
                                                        self.make_blockers(2),
                                                        self.make_blockers(3))
                        self.livesGroup.add(self.life1, self.life2, self.life3)
                        self.reset(0)
                        self.startGame = True
                        self.mainScreen = False

            elif self.startGame:
                if not self.enemies and not self.explosionsGroup:

                    # Advance game time even though normal game_step() is paused
                    for _ in range(self.speed_multiplier):
                        self.simulation_time += STEP_MS

                    elapsed = self.simulation_time - self.gameTimer

                    if elapsed < 3000:
                        self.screen.blit(self.background, (0, 0))
                        self.scoreText2 = Text(
                            FONT, 20, str(self.score), GREEN, 85, 5
                        )
                        self.scoreText.draw(self.screen)
                        self.scoreText2.draw(self.screen)
                        self.nextRoundText.draw(self.screen)
                        self.livesText.draw(self.screen)
                        self.livesGroup.update()
                        self.check_input()

                    else:
                        self.enemyPosition += ENEMY_MOVE_DOWN
                        self.reset(self.score)
                else:
                    currentTime = time.get_ticks()
                    self.play_main_music(currentTime)
                    self.screen.blit(self.background, (0, 0))
                    self.allBlockers.update(self.screen)
                    self.scoreText2 = Text(FONT, 20, str(self.score), GREEN,
                                           85, 5)
                    self.scoreText.draw(self.screen)
                    self.scoreText2.draw(self.screen)
                    self.livesText.draw(self.screen)
                    self.check_input()
                    action = self.get_human_action()

                    for _ in range(self.speed_multiplier):
                        self.simulation_time += STEP_MS
                        state, reward, done = self.game_step(self.simulation_time, action)
                        #if reward != 0:
                        #    print(f"state: {state}, reward: {reward}, done: {done}")
                        if done:
                            break

                    self.allSprites.update(self.keys, currentTime)
                    self.explosionsGroup.update(self.simulation_time)

            elif self.gameOver:
                for _ in range(self.speed_multiplier):
                    self.simulation_time += STEP_MS

                self.enemyPosition = ENEMY_DEFAULT_POSITION
                self.create_game_over(self.simulation_time)

            display.update()
            self.clock.tick(60)


if __name__ == '__main__':
    game = SpaceInvaders(start_speed=1)
    game.main()
