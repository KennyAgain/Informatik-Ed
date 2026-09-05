# Importieren u. initialisieren der Pygame-Bibliothek
from meinspiel import MeinSpiel
import pygame
from pygame.locals import *
pygame.init()


# Variablen/KONSTANTEN setzen
Breite, Hoehe = 1800, 840
Pixel = 60
FelderX, FelderY = int(Breite / Pixel), int(Hoehe / Pixel)
FPS  = 60
SCHWARZ = ( 0, 0, 0)
WEISS   = ( 255, 255, 255)
pyGameBilder = []

# Bilder aus meinSpiel werden für pygame vorbereitet
meinSpiel = MeinSpiel(FelderX, FelderY,Pixel)
for fname in meinSpiel.bilder:
    pyGameBilder.append(pygame.transform.scale(pygame.image.load(fname),(60,60)))


# Definieren und Öffnen eines neuen Fensters
fenster = pygame.display.set_mode((Breite, Hoehe))
pygame.display.set_caption("Mein erstes Spiel")
clock = pygame.time.Clock()

# Schleife Hauptprogramm
while True:
    # Überprüfen, ob Nutzer eine Aktion durchgeführt hat
    for event in pygame.event.get():
        # Beenden bei [ESC] oder [X]
        if event.type==pygame.QUIT or (event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE):
            pygame.quit()

    # Spiellogik
        if event.type==pygame.KEYDOWN:
            meinSpiel.key_pressed(event.key)
        if event.type==pygame.KEYUP:
            meinSpiel.key_released(event.key)
    
    meinSpiel.CullPhysics() #Cull physiscs

    # Spielfeld löschen
    for x in range(FelderX):
        for y in range(FelderY):  #draw scene
            fenster.blit(pyGameBilder[meinSpiel.spielfeld[x][y]],(x*Pixel,y*Pixel))
    
    fenster.blit(pyGameBilder[3],(meinSpiel.player_pos[0],meinSpiel.player_pos[1]))

    for point in meinSpiel.collsion_points :
        pygame.draw.circle(fenster,(255,0,0),(point[0],point[1]),4) #draw debug collison points


    # Fenster aktualisieren
    pygame.display.flip()
    clock.tick(FPS)