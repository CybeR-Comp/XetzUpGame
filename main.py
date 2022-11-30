import os
import pygame
import random 
import keyboard



pygame.font.init()
pygame.mixer.init()

#creating our game window
WIDTH,HEIGHT = 750,750
WIN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("XetzUp!")
icon = pygame.image.load(os.path.join("assets","logo.png"))
pygame.display.set_icon(icon)

#enemy players
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets","pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets","pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets","pixel_ship_blue_small.png"))

#player ship

YELLOW_SPACE_SHIP = pygame.transform.scale(pygame.image.load(os.path.join("assets","pixel_ship_yellow.png")),(100,70))

#laser
RED_LASER=pygame.image.load(os.path.join("assets","pixel_laser_red.png"))
BLUE_LASER=pygame.image.load(os.path.join("assets","pixel_laser_blue.png"))
GREEN_LASER=pygame.image.load(os.path.join("assets","pixel_laser_green.png"))
YELLOW_LASER=pygame.image.load(os.path.join("assets","pixel_laser_yellow.png"))

#BackGround


live_heart= pygame.transform.scale(pygame.image.load(os.path.join("assets","pixel_red_heart.png")),(45,45))
heal_icon = pygame.transform.scale(pygame.image.load(os.path.join("assets","pixel_heal.png")),(70,70))
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets","background-black.png")),(WIDTH,HEIGHT))
BGW = pygame.transform.scale(pygame.image.load(os.path.join("assets","background-black-wologo.png")),(WIDTH,HEIGHT))

#sound effects
laser_sound_effect = pygame.mixer.Sound(os.path.join("assets","laser_sound.wav"))
lose_sound_effect = pygame.mixer.Sound(os.path.join("assets","lose_sound.wav"))
theme_Sound = pygame.mixer.music.load(os.path.join("assets","theme_music.wav"))

class Laser:
    def __init__(self, x,y,img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)
    
    def draw(self,window):
        window.blit(self.img, (self.x,self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
       return not (self.y <= height and self.y >= 0 )

    def collision(self,obj):
        return collide(self, obj)

class Ship:
    
    COOLDOWN = 45
    

    def __init__(self,x,y,health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.ship_score = None
        self.lasers = []
        self.cool_down_counter = 0
    
    def draw(self,window):
        window.blit(self.ship_img, (self.x,self.y))
        for laser in self.lasers:
            laser.draw(window)
    
    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)
    

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()
    
    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1
    
    def shoot(self):
        if self.cool_down_counter == 0:
            pygame.mixer.Sound.play(laser_sound_effect)
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

 
    
###########################################################################################    



class Player(Ship):
    TEMP_SKOR = 0
    skor = [0]
    
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health 

    def move_lasers(self, vel, objs):
       
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                   
                    if laser.collision(obj):
                        objs.remove(obj)
                        Enemy.TOTAL_SKOR += obj.ship_score
                        self.lasers.remove(laser)
                        
                        

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)
    
    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))

####################################################################################

    
class Enemy(Ship):
    TOTAL_SKOR= 0
    shoot_freq = 180

    COLOR_MAP = {
        "red" : (RED_SPACE_SHIP, RED_LASER, 1),
        "green" :(GREEN_SPACE_SHIP,GREEN_LASER, 2),
        "blue" : (BLUE_SPACE_SHIP,BLUE_LASER, 3)
                }
    
    def __init__(self, x, y,color, health=100):
        super().__init__(x, y, health)
        self.ship_img,self.laser_img,self.ship_score = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self,vel):
        self.y += vel
    
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x - 18 , self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

class Reload(Ship):
    TOTAL_SKOR= 0
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = heal_icon
        
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health 

    def move(self,vel):
        self.y += vel

    def draw(self, window):
        super().draw(window)
        
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x,offset_y)) != None
    
def main():
    pygame.mixer.stop()
    pygame.mixer.music.play(-1)
    run = True
    FPS = 90
    lives = 5
    level = 0
    heal_count = 0
    enemies = []
    reHeal = []
    wave_length = 0
    enemy_vel = 1  
    main_font=pygame.font.Font("Gameplay.ttf", 30)
    skor_font=pygame.font.Font("Gameplay.ttf", 40)
    clock = pygame.time.Clock()
    player_vel = 5
    lost_count = 1
    laser_vel_player = -7
    laser_vel_enemy = 6
    heal_run = True
   


    player = Player(320,620)    # buradaki parametre geminin konumunu  belirler

    
    
    def redraw_window():
        
        WIN.blit(BG,(0,0))# this function draw the picture(BG) to background       
        level_label = main_font.render(f"Level : {level}", 1 ,(240,248,255))  #yazıları oluşturduk
        lives_label = main_font.render(f"Lives : {lives}", 1 , (253,218,0))  #yazıları oluşturduk
        skor_label = skor_font.render(f"{Enemy.TOTAL_SKOR}", 1,(240,248,255))
        WIN.blit(level_label, (10,10))
        WIN.blit(skor_label, (WIDTH/2 -10,30))
        
        
        
        # this line of codes display the hearts on the window
        if lives==1:
            WIN.blit(live_heart,(WIDTH - lives_label.get_width() - 10,5))

        if lives ==2:
            WIN.blit(live_heart,(WIDTH - lives_label.get_width() - 10,5)) 
            WIN.blit(live_heart,(WIDTH - lives_label.get_width() - 10 + 25, 5))

        if lives ==3 :
            WIN.blit(live_heart,(WIDTH - lives_label.get_width() - 10,5)) 
            WIN.blit(live_heart,(WIDTH - lives_label.get_width() - 10 + 25, 5))
            WIN.blit(live_heart,(WIDTH - lives_label.get_width() - 10 + 50, 5))

        if lives==4:
            WIN.blit(live_heart,(WIDTH - lives_label.get_width() - 10,5)) 
            WIN.blit(live_heart,(WIDTH - lives_label.get_width() - 10 + 25, 5))
            WIN.blit(live_heart,(WIDTH - lives_label.get_width() - 10 + 50, 5))
            WIN.blit(live_heart,(WIDTH - lives_label.get_width() - 10 + 75, 5))

        if lives == 5:
            WIN.blit(live_heart,(WIDTH - lives_label.get_width() - 10,5)) 
            WIN.blit(live_heart,(WIDTH - lives_label.get_width() - 10 + 25, 5))
            WIN.blit(live_heart,(WIDTH - lives_label.get_width() - 10 + 50, 5))
            WIN.blit(live_heart,(WIDTH - lives_label.get_width() - 10 + 75, 5))
            WIN.blit(live_heart,(WIDTH - lives_label.get_width() - 10 + 100, 5))

        


        for enemy in enemies:
            enemy.draw(WIN)

        for i in reHeal:
            i.draw(WIN)

        
            
        
      
        player.draw(WIN)
        pygame.display.update()   #that function refresh the screen 

    # unutma aşaıdaki while döngüsü saniyede 60 kez çalışıyor !!! 

    while run:
        #Dışarıda girdiğimiz fps değişkenine göre olayları kontrol eder # when we called this function in here. her sn de ekrana tekrar bu resim çizilir.  
        clock.tick(FPS) 
        redraw_window()  

        if len(enemies)==0:
            level += 1
            wave_length += 4
            Enemy.shoot_freq += 20
            
            if level<=7:
                Ship.COOLDOWN -= 3
            
            
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100),random.randrange(-1500,-100),random.choice(["red","green","blue"]))
                enemies.append(enemy)

        if lives<= 0 or player.health <= 0:
            lost_count += 1         
            if lost_count > FPS * 1 :
                Ship.COOLDOWN = 30
                Player.TEMP_SKOR = Enemy.TOTAL_SKOR
                Player.skor.append(Player.TEMP_SKOR)
                Enemy.TOTAL_SKOR = 0
                lost_menu()
            else:
                continue

        if level > 0 and level%3==0:
            
            
            while heal_run:
                healZ = Reload(random.randrange(50, WIDTH-100),random.randrange(-1500,-100),heal_icon)
                reHeal.append(healZ)
                heal_run=False
                
        if level%3 != 0 :
            heal_run=True        
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

            elif keys[pygame.K_2]:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0:
            player.x -= player_vel

        
            
        
        if keys[pygame.K_LEFT] and player.x - player_vel > 0:
            player.x -= player_vel


        #if keyboard.is_pressed("2"):
           # lost_menu()
        
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH:
            player.x += player_vel

        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH:
            player.x += player_vel
        
        if keys[pygame.K_w] and player.y - player_vel > 0:
            player.y -= player_vel

        if keys[pygame.K_UP] and player.y - player_vel > 0:
            player.y -= player_vel


        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 20  < HEIGHT:
            player.y += player_vel 
        
        if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() + 20  < HEIGHT:
            player.y += player_vel 
        
        
        if keys[pygame.K_SPACE]:
            player.shoot()

       
        for i in reHeal[:]:
            
            i.move(3)
            

            if collide(i,player):
                player.health = 100
                reHeal.remove(i)



        for enemy in enemies[:]:
            enemy.move(enemy_vel) 
            enemy.move_lasers(laser_vel_enemy, player)
           
            if collide(enemy, player):
            
                player.health -= 15
                enemies.remove(enemy) 
                if level > 7:
                    player.health -= 20
           
            if random.randrange(0,enemy.shoot_freq)== 1 :
                enemy.shoot()

            if enemy.y + enemy.get_height() > HEIGHT :
                lives -= 1
                enemies.remove(enemy)
        
        player.move_lasers(laser_vel_player, enemies)


def lost_menu():
    pygame.mixer.music.stop()
    lost_font = pygame.font.Font("Gameplay.ttf", 50)
    run = True
    
    pygame.mixer.Sound.play(lose_sound_effect)
   
    lost_label = lost_font.render("YOU LOST!" , 1 , (253,218,0))
    WIN.blit(lost_label,(WIDTH/2 - lost_label.get_width()/2, 350))

    

    while run:
        WIN.blit(BGW,(0,0))
        replay_label = lost_font.render("(R) Try Again",1,(253,218,0))
        WIN.blit(replay_label,(WIDTH/4 - replay_label.get_width()/2 + 45, 350))

        temp_skor_label = lost_font.render(f"Skor : {Player.TEMP_SKOR}",1, (253,218,0))
        WIN.blit(temp_skor_label, (40,100 ))

        max_skor_label = lost_font.render(f"Max : {max(Player.skor)}",1, (253,218,0))
        WIN.blit(max_skor_label, (WIDTH - (max_skor_label.get_width()+ 50) ,100 ))


        return_label = lost_font.render("(M) Main Menu",1,(253,218,0))
        WIN.blit(return_label,(WIDTH/4 - return_label.get_width()/2 + 55, 450))

        close_label = lost_font.render("(C) Close",1,(253,218,0))
        WIN.blit(close_label,(WIDTH/4 - return_label.get_width()/2 + 55, 550))
        
        for event in pygame.event.get():
            if event.type ==pygame.QUIT:
                quit()

        if keyboard.is_pressed("c"):
            quit()
        if keyboard.is_pressed("r"):
            main()

        if keyboard.is_pressed("m"):
            main_menu()

        pygame.display.update()


def main_menu():
    title_font = pygame.font.Font("Gameplay.ttf", 90)
    run = True
    while run:
        
        WIN.blit(BG, (0,0))
        start_label = title_font.render("1-Play", 1, (252,218,0) )
        WIN.blit(start_label, (WIDTH - 2*start_label.get_width()+ 55, 400))

        quit_label = title_font.render("2- Quit", 1, (252,218,0))
        WIN.blit(quit_label, (WIDTH - 2*quit_label.get_width() + 80, 550))

        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            elif keyboard.is_pressed("1"):
                main()
            elif keyboard.is_pressed("2"):
                run = False
           
        pygame.display.update()
                  

main_menu()  


