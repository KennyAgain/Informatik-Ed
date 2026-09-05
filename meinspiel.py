import copy
import pygame

class MeinSpiel:
    #bilder = ["Spiel\Bilder\dirt.jpg","Spiel\Bilder/apo.png","Spiel\Bilder\Grass.jpg","Spiel\Bilder\Sky.jpg"]
    bilder = ["Bilder/Bilder/Sky.jpg","Bilder/Bilder/dirt.jpg","Bilder/Bilder/Grass.jpg","Bilder/Bilder/apo.png"]
    spielfeld = [] 
    player_pos = []
    player_vel=[]
    player_acc = []
    scene_screen = 1 #start at the default screen
    collsion_points = []

    def __init__(self, felderX, felderY,fieldSize):
        self.key_held = []
        self.jump_vel = -9.5
        self.collsion_points = [[0,0],[0,0],[0,0],[0,0]]
        self.level_data = []
        self.data_path = "level_data.txt"
        self.can_jump = False
        self.jumping = False
        self.fieldSize = fieldSize
        self.player_pos = [600,420] #given in exact coordinats
        self.player_vel = [0,0]
        self.player_acc = [0,0]
        self.fields_x, self.fields_y = felderX,felderY
        self.grass_y = 4
        self.spielfeld = []
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

        print(self.level_data)

    def load_scene(self,scene):
        start = self.level_data.index("L"+str(scene)+".")
        self.spielfeld = [[0 for y in range(self.fields_y)] for x in range(self.fields_x)]
        for y in range(start,start+self.fields_y):
            for dx,tile in enumerate(self.level_data[y + 1]):
                self.spielfeld[dx][y-start] = int(tile)
        print(self.spielfeld)

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


    def check_collisons(self):#checks the two x extrems of the player for ground contact
        player_size_x,player_size_y = 60,60
        point_offset = 5 #the offset of the check points from the edge of the player

        collisons = []

        self.collsion_points = [[self.player_pos[0]+point_offset ,self.player_pos[1]], #TL_Hit 0
                        [self.player_pos[0]+player_size_x-point_offset,self.player_pos[1]], #TR_Hit 1   #defines six points around the player for collision checks in the following order "TL_Hit,TR_Hit,BL_Fall,BR_Fall,BL,BR"
                        [self.player_pos[0]+point_offset  ,self.player_pos[1]+player_size_y], #BL_Fall 2
                        [self.player_pos[0]+player_size_x-point_offset ,self.player_pos[1]+player_size_y], #BR_Fall 3
                        [self.player_pos[0]+point_offset,self.player_pos[1]+player_size_y/1.2], #BL 4
                        [self.player_pos[0]+player_size_x-point_offset,self.player_pos[1]+player_size_y/1.2], #BR 5
                        [self.player_pos[0]+point_offset,self.player_pos[1]+point_offset], #TL 6 
                        [self.player_pos[0]+player_size_x-point_offset,self.player_pos[1]+point_offset]] #TR 7
        
        for i,point in enumerate(self.collsion_points):
            field_index_x,field_index_y = int(point[0] // self.fieldSize), int(point[1]//self.fieldSize)
            if field_index_x < 0 or field_index_x > self.fields_x-1: continue
            if field_index_y < 0 or field_index_y > self.fields_y-1: continue

            if self.spielfeld[field_index_x][field_index_y] != 0:
                collisons.append(i)

            # print("index_x: " + str(field_index_x))
            # print("index_y: " + str(field_index_y))

        return collisons

    def CullPhysics(self):

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

        Cols = self.check_collisons()
        
        #apply y vel to player
        for step in range(steps):

            self.player_pos[1] += self.player_vel[1] /steps

            colls = self.check_collisons()

            if self.player_vel[1] > 0:
                if 2 in Cols or 3 in colls: break
            elif self.player_vel[1] < 0:
                if 0 in Cols or 1 in colls: print("head hitter"); self.player_vel[1] = 1; break

        #apply x vel to player
        for step in range(steps):

            self.player_pos[0] += self.player_vel[0] /steps

            colls = self.check_collisons()

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
        print(Cols)
    
        if not 2 in Cols and not 3 in Cols: #checks if collsions points 2 and 3 are in the collsion list
            self.player_vel[1] += .25 #accelerate player if hes not standing on ground
            if self.player_vel[1] < 0: self.jumping = False
        elif not self.jumping and self.player_vel[1] > 0:
            self.player_vel[1] = 0
            self.can_jump = True

    
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

           

