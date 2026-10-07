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
pyGameBilder = []
damage_animation_timer = 0
hide_player = False
animation_dy = 0
animation_acc_y = -.7
animation_vel_y = 0
DrawCollisionDebug = False
stop_physics = False
stop_draw = False
dead = False
font = pygame.font.Font(None, 50)
death_animation = False
won = False

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

    
    if not stop_physics:meinSpiel.CullPhysics() #Cull physiscs
    # Spielfeld löschen
    for x in range(FelderX):
        for y in range(FelderY):  #draw scene
            if meinSpiel.spielfeld[x][y] == 3:
                fenster.blit(pygame.transform.scale(pygame.image.load(meinSpiel.Flag_Pole.sprites[0]),(60,60*8)),(x*Pixel,y*Pixel-60*7))#draw the pole and base
                fenster.blit(pygame.transform.scale(pygame.image.load(meinSpiel.Flag_Pole.sprites[1]),(60,60)),(x*Pixel-Pixel/2,y*Pixel-meinSpiel.Flag_Pole.raised_pos))
                meinSpiel.Flag_Pole.check_hit(meinSpiel)
                meinSpiel.Flag_Pole.tick(meinSpiel)
                if meinSpiel.Flag_Pole.hit: stop_physics = True
                if meinSpiel.Flag_Pole.complete == True: won = True
            elif not stop_draw:
                fenster.blit(pyGameBilder[meinSpiel.spielfeld[x][y]],(x*Pixel,y*Pixel))
    if not stop_physics:            
        for object in meinSpiel.enemys + meinSpiel.power_ups:
            fenster.blit(pygame.transform.scale(pygame.image.load(object.image),(60,60)),(object.x,object.y))
        
        for coin in meinSpiel.coins:
            if not coin.collected: 
                fenster.blit(pygame.transform.scale(pygame.image.load(coin.image),(60,60)),(coin.x,coin.y))
    
    if not death_animation:
        if meinSpiel.lives == 2:
            player_image = pygame.transform.scale(pyGameBilder[4],(60,120))
            if meinSpiel.stretch == 0: meinSpiel.player_pos[1] -= 60 #if its the first transition move player 60 up
            meinSpiel.stretch = 60
        elif meinSpiel.lives == 1: 
            player_image = pygame.transform.scale(pyGameBilder[3],(60,60))
            #if its the first transition frame move player down
            if meinSpiel.stretch == 60: meinSpiel.player_pos[1] += meinSpiel.stretch; damage_animation_timer = meinSpiel.invincible_timer
            meinSpiel.stretch = 0
        elif meinSpiel.lives <= 0:
            death_animation = True

    #player blinking anamation when hit

    if damage_animation_timer > 0 and not death_animation:
        damage_animation_timer -= 1
        mod_timer = damage_animation_timer % 20
        if mod_timer > 8:
            hide_player = True
        else:
            hide_player = False
    else: hide_player = False

    if death_animation and not dead:
        stop_physics = True
        animation_dy += animation_vel_y
        animation_vel_y += animation_acc_y
        if animation_dy < -70:
            animation_acc_y = 1
        fenster.blit(player_image,(meinSpiel.player_pos[0],meinSpiel.player_pos[1] + animation_dy))
        if meinSpiel.player_pos[1] + animation_dy - 60 > Hoehe:
            stop_draw = True
            dead = True
    
    if not hide_player and not death_animation:fenster.blit(player_image,(meinSpiel.player_pos[0],meinSpiel.player_pos[1]))

    if not dead and not won:
        coins = font.render(f'Coins: {meinSpiel.collected_coins}', True, (255, 215, 0))
        fenster.blit(coins,(10,10))


    if DrawCollisionDebug:
        for i,point in enumerate(meinSpiel.player_debug_coll_points):
            if i < 4: pygame.draw.circle(fenster,(255,0,0),(point[0],point[1]),4) #draw debug collison points
            else:pygame.draw.circle(fenster,(0,255,0),(point[0],point[1]),4) #draw debug collison points
        
    if dead: #draw game over screen if dead
        pygame.draw.rect(fenster,(0,0,0),((0,0),(Breite,Hoehe)))
        game_over = font.render("Game Over", True, (255, 0, 0))
        fenster.blit(game_over,(Breite/2 - 100,Hoehe/2))
    
    if won:
        stop_draw = True
        pygame.draw.rect(fenster,(0,0,0),((0,0),(Breite,Hoehe)))
        game_over = font.render("YOU WON!", True, (0, 255, 0))
        fenster.blit(game_over,(Breite/2 - 100,Hoehe/2))

    # Fenster aktualisieren
    pygame.display.flip()
    clock.tick(FPS)
