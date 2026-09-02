import copy
import pygame

class MeinSpiel:
    #bilder = ["Spiel\Bilder\dirt.jpg","Spiel\Bilder/apo.png","Spiel\Bilder\Grass.jpg","Spiel\Bilder\Sky.jpg"]
    bilder = ["Bilder/Bilder/dirt.jpg","Bilder/Bilder/apo.png","Bilder/Bilder/Grass.jpg","Bilder/Bilder/Sky.jpg"]
    spielfeld = [] 
    player_pos = []
    player_vel=[]
    player_acc = []
    scene_screen = 0 #start at the default screen

    def __init__(self, felderX, felderY,fieldSize):
        self.level_data = []
        self.data_path = "level_data.txt"
        self.can_jump = False
        self.fieldSize = fieldSize
        self.player_pos = [600,420] #given in exact coordinats
        self.player_vel = [0,0]
        self.player_acc = [0,0]
        self.fields_x, self.fields_y = felderX,felderY
        self.grass_y = 4
        self.spielfeld = []
        self.createField(0,self.grass_y)
        self.read_level_data()

    def read_level_data(self):
        with open(self.data_path) as f:
            for x in f:
                self.level_data.append(x.strip("\n"))
        print(self.level_data)

    def sign(self,num): #gives back the sign of number num
        return -1 if num < 0 else (1 if num > 0 else 0)
    
    def transition_scene(self,trans_edge):
        if trans_edge == "L":
            self.scene_screen -= 1
            self.player_pos[0] = self.fields_x*self.fieldSize
        elif trans_edge == "R":
            self.scene_screen += 1
            self.player_pos[0] = 0

        

    def check_scene_transition(self):
        L_Edge,R_Edge = 0, self.fields_x*self.fieldSize #define the transtiton edges
        if self.player_pos[0] <= L_Edge:
            self.transition_scene("L")
        elif self.player_pos[0] >= R_Edge:
            self.transition_scene("R")

    def check_ground(self):#checks the two x extrems of the player for ground contact
        check_points = self.player_pos[1],self.player_pos[1]+60
        ground_points = 0
        for point in check_points:
            if int((point - 1) // self.fieldSize) >= 0 or int((point - 1) // self.fieldSize) <= self.fields_x:
                if not self.spielfeld[int(self.player_pos[1] // self.fieldSize)][int((point - 1) // self.fieldSize)] == 3:
                    ground_points += 1

        if ground_points == 0: #Only return False when no points are on the ground
            return False 
        return True

    def CullPhysics(self):

        #apply y vel to player
        self.player_pos[1] += self.player_vel[1] 
        
        self.player_pos[0] += self.player_vel[0]
        self.check_scene_transition()#check for scene transition after moving

        self.player_vel[0] += self.player_acc[0]

        if(self.can_jump):self.player_vel[0] -= self.player_vel[0]/10 #add drag only when on ground

        if(abs(self.player_vel[0]) > 4): 
            self.player_vel[0] = 4 * self.sign(self.player_vel[0]) #cap x velocity at 2

        #Aplly gravity
        if not self.check_ground():
            self.player_vel[1] += .1 #accelerate player if hes not standing on ground
        else:
            self.player_vel[1] = 0
            self.can_jump = True

    
    def createField(self,Grass_x,Grass_y):
        for dx in range(self.fields_x):
            self.spielfeld.append([])
            for dy in range(self.fields_y):
                if dy > self.fields_y-Grass_y:
                    self.spielfeld[dx].append(0)
                elif dy == self.fields_y-Grass_y:
                    self.spielfeld[dx].append(2)
                else:
                    self.spielfeld[dx].append(3)    

    def key_released(self,key):
        if key == pygame.K_a or key == pygame.K_d:
            self.player_acc[0] = 0

    def key_pressed(self, taste):
        if taste == pygame.K_SPACE and self.can_jump:
            self.can_jump = False
            self.player_vel[1] = -6 #set jump velocity

        if taste == pygame.K_a:
            self.player_acc[0] = -.3
        elif taste == pygame.K_d:
            self.player_acc[0] = .3
           

