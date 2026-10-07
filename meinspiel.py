import copy
import pygame
import objects
import math

class MeinSpiel:
    #bilder = ["Spiel\Bilder\dirt.jpg","Spiel\Bilder/apo.png","Spiel\Bilder\Grass.jpg","Spiel\Bilder\Sky.jpg"]
    bilder = ["legacy\Bilder\Sky.jpg","legacy\Bilder/brick.jpg",
              "legacy\Bilder\hard_brick.jpg","legacy\Bilder\Mari_big.png","legacy\Bilder\Mario_small.png"]
    spielfeld = [] 
    player_pos = []
    player_vel=[]
    player_acc = []
    scene_screen = 1 #start at the default screen
    collsion_points = []

    def __init__(self, felderX, felderY,fieldSize):
        self.collected_coins = 0
        self.player_debug_coll_points = [[0,0],[0,0],[0,0],[0,0]]
        self.lives = 2
        self.stretch = 0 #the amount of pixel the player is streched beond the normal height
        self.invincible_timer = 0
        self.key_held = []
        self.jump_vel = -9.5
        self.collsion_points = [[0,0],[0,0],[0,0],[0,0]]
        self.level_data = []
        self.object_data = []
        self.power_ups=[]
        self.coins = []
        self.enemys = []
        self.data_path = "legacy\level_data.txt"
        self.can_jump = False
        self.jumping = False
        self.fieldSize = fieldSize
        self.player_pos = [100,420] #given in exact coordinats
        self.player_vel = [0,0]
        self.player_acc = [0,0]
        self.fields_x, self.fields_y = felderX,felderY
        self.grass_y = 4
        self.spielfeld = []
        self.Flag_Pole = None
        self.read_level_data()
        self.load_scene(self.scene_screen)
       

    def read_level_data(self):
        with open(self.data_path) as f:
            for x in f:
                self.level_data.append(x.strip("\n"))

        #sanity check data size
        if not int(self.level_data[0].strip("#").strip("x")) == self.fields_x or not int(self.level_data[1].strip("#").strip("y")) == self.fields_y:
            print("level data has wrong size")
            quit()

        #print(self.level_data)

    def load_scene(self,scene):
        start = self.level_data.index("L"+str(scene)+".")
        self.object_data = []
        self.enemys = []
        self.power_ups = []
        self.coins = []
        end = start+self.fields_y
        self.spielfeld = [[0 for y in range(self.fields_y)] for x in range(self.fields_x)]
        for y in range(start,end):
            for dx,tile in enumerate(self.level_data[y + 1]):
                if int(tile) == 3: self.Flag_Pole = objects.Flag_Pole(dx,y-start)
                self.spielfeld[dx][y-start] = int(tile)
        #check for enemy data
        start = end +1
        if self.level_data[start] == "#Objects":
            end = self.level_data[start:len(self.level_data)].index("#End") +start

            for enemy_index in range(start+1,end):
                data = self.level_data[enemy_index]
                l_brak_i = data.index("(")
                r_brak_i = data.index(")")
                comma_i = data.index(",")
                x,y,t = int(data[l_brak_i+1:comma_i]),int(data[comma_i+1:r_brak_i]),int(data[r_brak_i+2:len(data)])
                self.object_data.append((x,y,t))
            print(self.object_data)
        for object in self.object_data:
            if object[2] <= 9:#object indecies till 9 are enemys
                self.enemys.append(objects.Enemy(object[0],object[1],object[2]))
            elif object[2] >= 10 and object[2] < 20:#between 10 and 19 are powerups
                self.power_ups.append(objects.PowerUp(object[0],object[1],object[2] - 9))
            elif object[2] >= 20:
                self.coins.append(objects.Coin(object[0] * 60,object[1] * 60))#the coins coordinats are defined to be the tile index

        #print(self.spielfeld)

    def sign(self,num): #gives back the sign of number num
        return -1 if num < 0 else (1 if num > 0 else 0)
    
    def transition_scene(self,trans_edge):
        if trans_edge == "L":
            self.scene_screen -= 1
            self.player_pos[0] = self.fields_x*self.fieldSize
        elif trans_edge == "R":
            self.scene_screen += 1
            self.player_pos[0] = 0
        self.load_scene(self.scene_screen)

        

    def check_scene_transition(self):
        L_Edge,R_Edge = 0, self.fields_x*self.fieldSize #define the transtiton edges
        if self.player_pos[0] <= L_Edge:
            self.transition_scene("L")
        elif self.player_pos[0] >= R_Edge:
            self.transition_scene("R")


    def check_collisons(self,x,y,player=False):#checks the two x extrems of the player for ground contact
        player_size_x,player_size_y = 60,60
        point_offset = 5 #the offset of the check points from the edge of the player

        collisons = []

        y_stretch = 0
        if player: y_stretch = self.stretch
        
        self.collsion_points = [[x+point_offset ,y], #TL_Hit 0
                        [x+player_size_x-point_offset,y], #TR_Hit 1   #defines six points around the player for collision checks in the following order "TL_Hit,TR_Hit,BL_Fall,BR_Fall,BL,BR"
                        [x+point_offset  ,y+player_size_y+y_stretch], #BL_Fall 2
                        [x+player_size_x-point_offset ,y+player_size_y+y_stretch], #BR_Fall 3
                        [x+point_offset,y+player_size_y/1.2+y_stretch], #BL 4
                        [x+player_size_x-point_offset,y+player_size_y/1.2+y_stretch], #BR 5
                        [x+point_offset,y+point_offset], #TL 6 
                        [x+player_size_x-point_offset,y+point_offset], #TR 7
                        [x+player_size_x/2,y + player_size_y+y_stretch-1]] #Stuck 8
        if player: self.player_debug_coll_points = self.collsion_points
        
        for i,point in enumerate(self.collsion_points):
            field_index_x,field_index_y = int(point[0] // self.fieldSize), int(point[1]//self.fieldSize)
            if field_index_x < 0 or field_index_x > self.fields_x-1: continue
            if field_index_y < 0 or field_index_y > self.fields_y-1: continue

            if self.spielfeld[field_index_x][field_index_y] != 0:
                collisons.append(i)

            # print("index_x: " + str(field_index_x))
            # print("index_y: " + str(field_index_y))

        return collisons
    
    def handle_hit(self,object,hitter): #hitter |0 = player | 1 = enemy | 2 = powerup
        if hitter == 1 and self.invincible_timer <= 0:
            if object.type == 2: 
                if abs(object.velocity[0]) < .1: 
                    #check wich side the koopa shell is hit from
                    if object.x < self.player_pos[0]: #Approach from left
                        object.velocity[0] = -5 
                        self.invincible_timer = 10 #give the player 10 invicible frames to not get damaged by the shell
                        return
                    elif object.x > self.player_pos[0]:
                        object.velocity[0] = +5
                        self.invincible_timer = 10
                        return 
            self.lives -= 1
            self.invincible_timer = 200
        elif hitter == 0:
            if object.type == 1: self.enemys.append(objects.Enemy(object.x,object.y,object.type+1))#if the obejct type is koopa spawn koopa shell if 
            if object.type == 2: object.velocity[0] = 0; return
            self.enemys.remove(object)
        elif hitter == 2:
            self.lives += 1
            self.power_ups.remove(object)

    def CullPhysics(self):
        self.invincible_timer -= 1

        if "a" in self.key_held and "d" not in self.key_held:
            self.player_acc[0] = -0.3
        elif "d" in self.key_held and "a" not in self.key_held:
            self.player_acc[0] = .3
        else:
            self.player_acc[0] = 0

        if "space" in self.key_held and self.can_jump:
            self.can_jump = False
            self.jumping = True
            self.player_vel[1] = self.jump_vel #set jump velocity


        steps = 100 #define the indivudial steps that get checked for collision

        Cols = self.check_collisons(self.player_pos[0],self.player_pos[1],True)
        
        #apply y vel to player
        for step in range(steps):

            colls = self.check_collisons(self.player_pos[0],self.player_pos[1],True)
            self.player_pos[1] += self.player_vel[1] /steps   

            #check if the player is stuck in the ground
            if 2 in Cols and 3 in colls and 8 in colls:
                self.jumping = False
                self.can_jump = True
                self.player_pos[1] -= 20;print("Player stuck in ground") ;break

            if self.player_vel[1] > 0:
                if 2 in Cols or 3 in colls:break
            elif self.player_vel[1] < 0:
                if 0 in Cols or 1 in colls: 
                    print("head hitter")
                    self.player_vel[1] = 2
                    for dx in range(3): #check 3 points across the player head for colls
                        if self.spielfeld[int((self.player_pos[0] + dx * 20) // 60)][int((self.player_pos[1] - 10) // 60)] == 1  and self.stretch > 0: #destory block above when it is breakble and the player is big
                            self.spielfeld[int((self.player_pos[0] + dx * 20) // 60)][int((self.player_pos[1] - 10) // 60)] = 0
                            break



        #apply x vel to player
        for step in range(steps):

            self.player_pos[0] += self.player_vel[0] /steps

            colls = self.check_collisons(self.player_pos[0],self.player_pos[1],True)

            if self.player_vel[0] > 0:
                if 5 in colls or 7 in colls: self.player_pos[0] -= self.player_vel[0] /steps ;self.player_vel[0]=0;break #break out and reverses last step
            elif self.player_vel[0] < 0:
                if 4 in colls or 6 in colls: self.player_pos[0] -= self.player_vel[0] /steps ;self.player_vel[0]=0;break

        self.check_scene_transition()#check for scene transition after moving

        self.player_vel[0] += self.player_acc[0]

        if(self.can_jump and abs(self.player_acc[0]) < 0.1):self.player_vel[0] -= self.player_vel[0]/8 #add drag only when on ground

        if(abs(self.player_vel[0]) > 4): 
            self.player_vel[0] = 4 * self.sign(self.player_vel[0]) #cap x velocity at 2

        #Aplly gravity
    
        if not 2 in Cols and not 3 in Cols: #checks if collsions points 2 and 3 are in the collsion list
            self.player_vel[1] += .25 #accelerate player if hes not standing on ground
            if self.player_vel[1] < 0: self.jumping = False
        elif not self.jumping and self.player_vel[1] > 0:
            self.player_vel[1] = 0
            self.can_jump = True

        #tick all enemys
        for enemy in self.enemys:
            enemy.tick_enemy(self)

            #check for collison with enemy
            player_center_x,player_center_y = self.player_pos[0] + 30, self.player_pos[1] + 30+self.stretch#find player center by adding half the size
            enemy_center_x, enemy_center_y = enemy.x + 30 , enemy.y +30
            if math.sqrt(pow(player_center_x-enemy_center_x,2)+pow(player_center_y-enemy_center_y,2)) <= 60:
                if player_center_y  -   enemy.y -60 < -40 and self.player_vel[1] > 0: #checks if the player is hitting the enemy from above and falling
                    self.handle_hit(enemy,0)
                    self.player_vel[1] = self.jump_vel/1.3
                else:
                    self.handle_hit(enemy,1)

            for enemy_partner in self.enemys: #loop through all enemys again so that we can match every enemy against each other
                if enemy_partner == enemy: continue
                partner_center_x, partner_center_y = enemy_partner.x + 30, enemy_center_y + 30
                if math.sqrt(pow(enemy_center_x-partner_center_x,2)+pow(enemy_center_y-partner_center_y,2)) <= 60:#check collsions againt eachother   
                    if enemy_partner.type == 2 and abs(enemy_partner.velocity[0]) > .1:
                        self.enemys.remove(enemy) 
                    elif enemy.type != 2:
                        enemy.velocity[0] = -enemy.velocity[0]
        
        
        #tick all powerups
        for power_up in self.power_ups:
            power_up.tick_powerup(self)

            player_center_x,player_center_y = self.player_pos[0] + 30, self.player_pos[1] + 30+self.stretch#find player center by adding half the size
            power_up_center_x, power_up_center_y = power_up.x + 30 , power_up.y +30
            if math.sqrt(pow(player_center_x-power_up_center_x,2)+pow(player_center_y-power_up_center_y,2)) <= 60:
                self.handle_hit(power_up,2)

        #tick all coins
        for coin in self.coins:
            coin.tick_animation()
            player_center_x,player_center_y = self.player_pos[0] + 30, self.player_pos[1] + 30+self.stretch#find player center by adding half the size
            coin_center_x, coin_center_y = coin.x + 30 , coin.y +30
            if math.sqrt(pow(player_center_x-coin_center_x,2)+pow(player_center_y-coin_center_y,2)) <= 60 and not coin.collected:
                coin.collected = True
                self.collected_coins += 1

    
    def createField(self,Grass_x,Grass_y):
        for dx in range(self.fields_x):
            self.spielfeld.append([])
            for dy in range(self.fields_y):
                if dy > self.fields_y-Grass_y:
                    self.spielfeld[dx].append(1)
                elif dy == self.fields_y-Grass_y:
                    self.spielfeld[dx].append(2)
                else:
                    self.spielfeld[dx].append(0)    

    def key_released(self,key):
        if key == pygame.K_a:
            self.key_held.remove("a")
        if key == pygame.K_d:
            self.key_held.remove("d")
        if key == pygame.K_SPACE:
            self.key_held.remove("space")

    def key_pressed(self, key):
        if key == pygame.K_SPACE:
            self.key_held.append("space")
        if key == pygame.K_a:
            self.key_held.append("a")
        elif key == pygame.K_d:
            self.key_held.append("d")

           

