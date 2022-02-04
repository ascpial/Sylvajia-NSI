# Supprimes le message d'acceuil de pygame
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

from src.game import Pygame

import sys
import os

# Vérifie si un ID est passé en argument (si il y a plusieurs clients discord sur la même machine)
if len(sys.argv) > 1:
    if sys.argv[1].isdigit:
        os.environ["DISCORD_INSTANCE_ID"] = sys.argv[1]

def main():
    """Lance le jeu"""
    game = Pygame()

    game.loop()

if __name__ == "__main__":
    main()