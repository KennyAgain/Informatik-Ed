import meinspiel
class Enemy:

    def __init__(self,x,y,type):
        sprites = ["Bilder\goomba.png","Bilder\koopa_blue.png","Bilder\koopa_shell.png"]
        self.x = x
        self.y = y
        self.type = type
        self.velocity = [0,0]
        self.image = sprites[type]
        self.steps = 100

    def tick_enemy(self,main_spiel):
        colls = meinspiel.MeinSpiel.check_collisons(main_spiel,self.x,self.y)
        if not  2 in colls and not 3 in colls:  #checks for collison with ground and applys gravity
            self.velocity[1] += .2
            self.velocity[0] = self.velocity[0] / 1.1

        elif self.velocity[1] > 0: 
            self.velocity[1] = 0
            if self.velocity[0] < 2: self.velocity[0] = 2#the goomba starts walking when its on the ground and stands still

        for step in range(100): #mangae the y movement
            self.y += self.velocity[1] /100
            colls = meinspiel.MeinSpiel.check_collisons(main_spiel,self.x,self.y)
            if self.velocity[1] > 0:
                if 2 in colls or 3 in colls: break
        
        self.x += self.velocity[0]  #apply x velocity and turn around when hitting walls

        if not self.type == 2:
            if 4 in colls or 6 in colls: self.velocity[0] = self.velocity[0] = 2 
            elif 5 in colls or 7 in colls: self.velocity[0] = self.velocity[0] = -2
        elif self.type == 2:
            if 4 in colls or 6 in colls: 
                self.velocity[0] = self.velocity[0] = 5
                if main_spiel.spielfeld[int((self.x -10) // 60)][int(self.y // 60)] == 1: main_spiel.spielfeld[int((self.x -10) // 60)][int(self.y // 60)] = 0
            elif 5 in colls or 7 in colls: 
                self.velocity[0] = self.velocity[0] = -5
                if main_spiel.spielfeld[int((self.x +10 + 60) // 60)][int(self.y // 60)] == 1: main_spiel.spielfeld[int((self.x +10 + 60) // 60)][int(self.y // 60)] = 0


class PowerUp:

    def __init__(self,x,y,type):
        sprites = ["Bilder\mushroom.png"]
        self.x = x
        self.y = y
        self.type = type
        self.velocity = [0,0]
        self.image = sprites[type - 1]
        self.steps = 100

    def tick_powerup(self,main_spiel):
        if self.type == 1:
            colls = meinspiel.MeinSpiel.check_collisons(main_spiel,self.x,self.y)

            if not  2 in colls and not 3 in colls:  #checks for collison with ground and applys gravity
                self.velocity[1] += .2
                self.velocity[0] = self.velocity[0] / 1.1
            elif self.velocity[1] > 0: 
                self.velocity[1] = 0
                if self.velocity[0] < 2: self.velocity[0] = 2#the power up starts walking when its on the ground and stands still

            for step in range(self.steps): #mangae the y movement

                self.y += self.velocity[1] /self.steps

                colls = meinspiel.MeinSpiel.check_collisons(main_spiel,self.x,self.y)

                if self.velocity[1] > 0:
                    if 2 in colls or 3 in colls: break
            
            self.x += self.velocity[0]  #apply x velocity and turn around when hitting walls
            if 4 in colls or 6 in colls: self.velocity[0] = self.velocity[0] = 2
            elif 5 in colls or 7 in colls: self.velocity[0] = self.velocity[0] = -2

class Coin:
    def __init__(self,x,y):
        self.sprite = ["Bilder/1.png","Bilder/2.png","Bilder/3.png","Bilder/4.png"]
        self.image = self.sprite[0]
        self.x = x
        self.y = y
        self.frame = 0
        self.timer = 0
        self.collected = False
    
    def tick_animation(self):
        self.timer += 1
        if self.timer > 10:
            self.timer = 0
            self.frame += 1
            self.frame = self.frame % 4
            self.image = self.sprite[self.frame]

class Flag_Pole:
    def __init__(self,x,y):
        self.sprites = ["Bilder\Pole.png","Bilder\Flag.png"]
        self.raised_pos = 6.5*60 #the height that the flag is raised relativ to the pole base
        self.hit = False #if the player hits the pole
        self.x,self.y = x,y #index
        self.complete = False
    
    def check_hit(self,main_spiel):
        if main_spiel.player_pos[0] >= self.x * 60: #If the playe passes the flag pole
            self.hit = True
    
    def tick(self,main_spiel):
        print(main_spiel.player_pos[1])
        print(self.y)
        if self.hit:
            if main_spiel.player_pos[1] >= self.y*60-self.raised_pos: 
                self.raised_pos -= 3
            else: self.complete = True
