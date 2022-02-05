from __future__ import annotations

import logging

import pygame
import pygame.display
import pygame.time
import pygame.event
import pygame.key
import pygame.font
import pygame.image

from .discord import Discord
from .players import Players
from . import players
from .map import Map

FPS = 30

class Pygame:
    """Ceci est la classe principale de l'affichage.
    C'est elle qui gère l'affichage à l'écran et les inputs au clavier.
    Elle contient l'instance du connecteur discord (`self.discord`), l'instance des joueurs (`self.players`),
    et l'instance du monde (`self.map`).
    """
    exit = 0
    animation_state = 0
    debug: int
    debug_key_pressed: bool = False
    noclip: bool = False

    def __init__(self):
        """Initialise le jeu.
        Cette fonction charge les fonts, prépare l'écran et l'horloge du jeu, créé le connecteur discord, la classe qui gère les joueurs
        et la classe contenant le terrain.
        """
        pygame.init()

        self.debug = 0

        self.font = pygame.font.Font(
            "./data/fonts/04B_30__.TTF",
            20
        )

        self.small_font = pygame.font.Font(
            "./data/fonts/04B_30__.TTF",
            10
        )

        self.screen = pygame.display.set_mode((650, 500))
        pygame.display.set_caption("Sylvajia")
        pygame_icon = pygame.image.load('./data/images/player.png')
        pygame.display.set_icon(pygame_icon)
        self.clock = pygame.time.Clock()

        self.discord = Discord(self)

        self.players = Players(self)

        if True:
            self.map = Map(self)
        
    
    def loop(self):
        """Cette fonction fait tourner le jeu tant qu'il n'est pas quitté (avec la croix ou alt+f4).
        """
        message = self.font.render(
            "Connexion a discord...",
            False,
            (255, 255, 255)
        )
        self.screen.blit(
            message, 
            (
                self.screen.get_width() // 2 - message.get_width() // 2,
                self.screen.get_height() // 2 - message.get_height() // 2
            )
        )
        
        timeout = 0
        while not self.discord.ready:
            self.discord.loop()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
            
            key_input = pygame.key.get_pressed()
            if key_input[pygame.K_ESCAPE]:
                return
            
            self.discord.loop_end()
            pygame.display.update()

            # Gérer le timeout
            timeout += 1
            if timeout >= 600:
                self.discord.disable()
            self.clock.tick(FPS)
        
        self.players.init()

        while not self.exit:
            self.discord.loop()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit=True
                #elif event.type == pygame.KEYDOWN and self.discord.lobby is not None:
                #    self.discord.send_message(ChannelType.pos, b"Bonjour :)")

            self.process_keys()
            
            self.discord.loop_end()

            self.screen.fill((255,255,255))
            self.map.render()
            self.players.render()
            if self.debug == 1:
                self.screen.blit(
                    self.font.render(
                        f"{int(self.clock.get_fps())} fps, x={round(self.players.player.x, 2)}, y={round(self.players.player.y, 2)}",
                        True, (255, 255, 255)
                    ),
                    (0,0)
                )
            elif self.debug == 2:
                tile = self.map[self.players.player.x, self.players.player.y]
                self.screen.blit(
                    self.font.render(
                        f"Tile type={tile.type}, data={tile.data}, x={tile.x}, y={tile.y}",
                        True, (255, 255, 255)
                    ),
                    (0,0)
                )

            pygame.display.update()

            self.clock.tick(FPS)
    
    def process_keys(self):
        global MOVE_INTERVAL
        """Cette fonction regarde les touches pressées et agit en conséquence
        (c'est elle qui gère le mouvement, et le menu de débogage)
        """
        key_input = pygame.key.get_pressed()
        if key_input[pygame.K_UP]:
            self.players.player.move_by(0, -1, not self.noclip)
        if key_input[pygame.K_DOWN]:
            self.players.player.move_by(0, 1, not self.noclip)
        if key_input[pygame.K_RIGHT]:
            self.players.player.move_by(1, 0, not self.noclip)
        if key_input[pygame.K_LEFT]:
            self.players.player.move_by(-1, 0, not self.noclip)
        if not key_input[pygame.K_F3] and self.debug_key_pressed:
            if self.debug_mode_input==1:
                self.noclip = not self.noclip
                logging.info("Noclip %s", "enabled" if self.noclip else "disabled")
            elif self.debug_mode_input==2:
                if players.MOVE_INTERVAL == 0:
                    players.MOVE_INTERVAL = 0.15
                elif players.MOVE_INTERVAL == 0.15:
                    players.MOVE_INTERVAL = 0
                logging.info("Speed %s", "enabled" if players.MOVE_INTERVAL==0 else "disabled")
            else:
                self.debug += 1
                if self.debug >= 3:
                    self.debug = 0
                logging.info("Debug %s", "enabled" if self.debug else "disabled")
            self.debug_key_pressed=False
        if key_input[pygame.K_F3] and not self.debug_key_pressed:
            self.debug_key_pressed = True
            self.debug_mode_input = 0
        if self.debug_key_pressed:
            if key_input[pygame.K_n]:
                self.debug_mode_input = 1
            elif key_input[pygame.K_s]:
                self.debug_mode_input = 2
    
    @property
    def camera_x(self):
        """camera_x et camera_y sont utilisées pour le point central de l'écran.
        Ces propriétés pourront être utilisées plus tard pour décaler l'écran quand on arrive au bord du monde si besoin.
        """
        if self.players.player is not None:
            return self.players.player.x
        else:
            return 0
    
    @property
    def camera_y(self):
        """camera_x et camera_y sont utilisées pour le point central de l'écran.
        Ces propriétés pourront être utilisées plus tard pour décaler l'écran quand on arrive au bord du monde si besoin.
        """
        if self.players.player is not None:
            return self.players.player.y
        else:
            return 0