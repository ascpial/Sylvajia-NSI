"""Ce script est utilisé pour extraire les images du pack de textures
Il n'est pas utilisé par le jeu mais peut être utilisé pour recréer les textures facilement.
"""

from PIL import Image
import os

SOURCE = "./data/Toen's Medieval Strategy Sprite Pack v.1.0 (16x16)/Tile-set - Toen's Medieval Strategy (16x16) - v.1.0.png"

OUTPUT = "./data/images/output"

# Créé le dossier de sortie si il n'existe pas
if not os.path.exists(OUTPUT):
    os.makedirs(OUTPUT)

image = Image.open(SOURCE)

image_data = image.load()

height,width = image.size
for loop1 in range(height):
    for loop2 in range(width):
        r,g,b, a = image_data[loop1,loop2]
        if r == 255 and g == 255 and b == 255:
            image_data[loop1,loop2] = 0,0, 0, 0

for y in range(44):
    for x in range(7):
        actual = image.crop((x*16,y*16,(x+1)*16,(y+1)*16))
        actual = actual.resize((32, 32), resample=Image.NEAREST)
        actual.save(f"{OUTPUT}/{y}_{x}.png")