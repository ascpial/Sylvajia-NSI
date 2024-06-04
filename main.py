# Supprimes le message accueil de pygame
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

from src.game import Pygame

import os

def main():
    """Lance le jeu"""
    game = Pygame()

    game.loop()

if __name__ == "__main__":
    main()
