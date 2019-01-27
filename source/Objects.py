import Constants as C
from tensorflow import keras
import pygame
import random

class Tunnel():
    def __init__(self, up, large):
        self.large= large
        self.pos_x = C.TUNNEL_START
        self.width = C.TUNNEL_WIDTH
        self.sprite_tunnel = pygame.image.load(C.TUNNEL_IMG)
        self.sprite_entry = pygame.image.load(C.ENTRY_TUNNEL_IMG)

        if up:
            self.pos_y = 0
            self.sprite_tunnel = pygame.transform.rotate(self.sprite_tunnel, 180)
            self.sprite_entry = pygame.transform.rotate(self.sprite_entry, 180)
        else:
            self.pos_y = C.SCREEN_HEIGHT - self.large

        self.sprite_entry = pygame.transform.scale(self.sprite_entry, (self.width, C.ENTRY_TUNNEL_HEIGHT))
        self.sprite_tunnel = pygame.transform.scale(self.sprite_tunnel, (self.width, self.large))


class Tunnels():
    def __init__(self):
        self.pos_x = C.SCREEN_WIDTH
        self.speed = C.SPEED
        self.width = C.TUNNEL_WIDTH

        self.bot_large = random.randint(C.MIN_TUNNEL_HEIGHT, C.SCREEN_HEIGHT - C.CROSS_SPACE - C.MIN_TUNNEL_HEIGHT )
        self.top_large = C.SCREEN_HEIGHT - self.bot_large - C.CROSS_SPACE
        self.bot_tunnel = Tunnel(False, self.bot_large)
        self.top_tunnel = Tunnel(True, self.top_large)

        self.top_cross_space = C.SCREEN_HEIGHT - self.bot_large - C.CROSS_SPACE - 25
        self.bot_cross_space = C.SCREEN_HEIGHT - self.bot_large - 20

    def set_x(self, new_x):
        self.pos_x = new_x
        self.top_tunnel.pos_x = new_x
        self.bot_tunnel.pos_x = new_x

    def move(self):
        self.bot_tunnel.pos_x -= self.speed
        self.top_tunnel.pos_x -= self.speed
        self.pos_x -= self.speed

    def print(self, screen):
        screen.blit(self.bot_tunnel.sprite_tunnel, (self.bot_tunnel.pos_x, self.bot_tunnel.pos_y))
        screen.blit(self.bot_tunnel.sprite_entry, (self.bot_tunnel.pos_x, self.bot_tunnel.pos_y))

        screen.blit(self.top_tunnel.sprite_tunnel, (self.top_tunnel.pos_x, self.top_tunnel.pos_y))
        screen.blit(self.top_tunnel.sprite_entry, (self.top_tunnel.pos_x, self.top_tunnel.pos_y + self.top_tunnel.large - 20))

    def test(self, screen, general_font):
        top_label = general_font.render('·', 1, (255, 0, 0))
        bot_label = general_font.render('·', 1, (255, 0, 0))
        screen.blit(top_label, (self.pos_x, self.top_cross_space))
        screen.blit(bot_label, (self.pos_x, self.bot_cross_space))


class Bird():
    def __init__(self):
        self.pos_x = C.BIRD_POS_X
        self.pos_y = C.BIRD_INI_POS_Y
        self.width = C.BIRD_WIDTH
        self.height = C.BIRD_HEIGHT
        self.jump_distance = C.BIRD_JUMP_DISTANCE
        self.alive = True

        color = C.COLORS[random.randint(0, C.NUM_COLORS - 1)]
        self.sprite_bird = pygame.image.load('img/' + color + '.png')
        self.sprite_bird = pygame.transform.scale(self.sprite_bird, (self.width, self.height))

        self.fitness = 0
        self.model = keras.Sequential()
        self.model.add(keras.layers.Dense(7, input_dim=4, activation="relu", kernel_initializer='uniform'))
        self.model.add(keras.layers.Dense(1, activation="sigmoid"))
        self.model.compile(loss="binary_crossentropy", optimizer="adam", metrics=["accuracy"])
        # self.createModel()

    def restart(self):
        self.pos_y = C.BIRD_INI_POS_Y
        self.alive = True
        self.fitness = 0

    def createModel(self):
        self.model.add(keras.layers.Dense(7, input_dim=4, activation="relu", kernel_initializer='uniform'))
        self.model.add(keras.layers.Dense(1, activation="sigmoid"))
        self.model.compile(loss="binary_crossentropy", optimizer="adam", metrics=["accuracy"])

    def jump(self):
        if self.alive:
            self.pos_y -= self.jump_distance

    def fall(self):
        if self.alive:
            self.pos_y += C.GRAVITY

    def die(self, tunnels):
        if (self.alive):
            if (self.pos_y < 0) or (self.pos_y - self.height > C.SCREEN_HEIGHT ):
                self.alive = False
            else:
                if (self.pos_x + self.width >= tunnels.pos_x) and (self.pos_x <= tunnels.pos_x + C.TUNNEL_WIDTH):
                    if (self.pos_y - self.height < tunnels.top_cross_space):
                        self.alive = False
                    else:
                        if (self.pos_y > tunnels.bot_cross_space):
                            self.alive = False
            if self.alive:
                return 0
            else:
                return 1
        else:
            return 0

    def getDistances(self, tunnels):
        if self.alive:
            self.h_distance = (tunnels.pos_x + (tunnels.width / 2)) - (self.pos_x + self.width)
            self.v_distance = (tunnels.top_cross_space + (C.CROSS_SPACE / 2)) - (self.pos_y + (self.height / 2))

    def print(self, screen):
        if self.alive:
            screen.blit(self.sprite_bird, (self.pos_x, self.pos_y))

    def test(self, screen, general_font):
        top_label = general_font.render('·', 1, (255, 0, 0))
        bot_label = general_font.render('·', 1, (255, 0, 0))
        screen.blit(top_label, (self.pos_x + self.width, self.pos_y - self.height))
        screen.blit(bot_label, (self.pos_x, self.pos_y))