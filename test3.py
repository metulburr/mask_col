import pygame as pg
import math
    
pg.init()
  
def enemy_image_load():
    image = pg.image.load('enemy.png').convert()
    image.set_colorkey((255,0,255))
    transformed_image = pg.transform.rotate(image, 180)
    orig_image = pg.transform.scale(transformed_image, (40,80))
    mask = pg.mask.from_surface(orig_image)
    return (orig_image, mask)
  
class Enemy:
    def __init__(self, images, screen_rect):
        self.screen_rect = screen_rect
        self.image = images[0]
        self.mask = images[1]
        start_buffer = 0
        self.rect = self.image.get_rect(
            center=(screen_rect.centerx, screen_rect.centery + start_buffer)
        )
        self.distance_above_player = 100 
        self.speed = 2
        self.bullet_color = (255,0,0)
        self.is_hit = False
        self.range_to_fire = False
        self.timer = 0.0
        self.bullets = [ ]
          
    def pos_towards_player(self, player_rect):
        c = math.sqrt((player_rect.x - self.rect.x) ** 2 + (player_rect.y - self.distance_above_player  - self.rect.y) ** 2)
        try:
            x = (player_rect.x - self.rect.x) / c
            y = ((player_rect.y - self.distance_above_player)  - self.rect.y) / c
        except ZeroDivisionError: 
            return False
        return (x,y)
          
    def update(self, dt, player):
        new_pos = self.pos_towards_player(player.rect)
        if new_pos: #if not ZeroDivisonError
            self.rect.x, self.rect.y = (self.rect.x + new_pos[0] * self.speed, self.rect.y + new_pos[1] * self.speed)
          
        self.check_attack_ability(player)
        if self.range_to_fire:  
            if pg.time.get_ticks() - self.timer > 1500.0:
                self.timer = pg.time.get_ticks()
                self.bullets.append(Laser(self.rect.center, self.bullet_color))
                  
        self.update_bullets(player)
                  
    def draw(self, surf):
        if self.bullets:
            for bullet in self.bullets:
                surf.blit(bullet.image, bullet.rect)
        surf.blit(self.image, self.rect)
          
    def check_attack_ability(self, player):
        #if player is lower than enemy
        if player.rect.y >= self.rect.y: 
            try:
                offset_x =  self.rect.x - player.rect.x
                offset_y =  self.rect.y - player.rect.y
                d = int(math.degrees(math.atan(offset_x / offset_y)))
            except ZeroDivisionError: #player is above enemy
                return
            #if player is within 15 degrees lower of enemy
            if math.fabs(d) <= 15: 
                self.range_to_fire = True
            else:
                self.range_to_fire = False
                  
    def update_bullets(self, player):
        if self.bullets:
            for obj in self.bullets[:]:
                obj.update('down')
                #check collision
                if obj.rect.colliderect(player.rect):
                    offset_x =  obj.rect.x - player.rect.x 
                    offset_y =  obj.rect.y - player.rect.y
                    print((offset_x, offset_y))
                    if player.mask.overlap(obj.mask, (offset_x, offset_y)):
                        player.take_damage(1)
                        print(player.damage)
                        self.bullets.remove(obj)
          
class Laser:
    def __init__(self, loc, screen_rect):
        self.screen_rect = screen_rect
        self.image = pg.Surface((5,40)).convert()
        self.mask = pg.mask.from_surface(self.image)
        self.image.fill((255,255,0))
        self.rect = self.image.get_rect(center=loc)
        self.speed = 5
    
    def update(self,direction='up'):
        if direction == 'down':
            self.rect.y += self.speed
        else:
            self.rect.y -= self.speed
    
    def render(self, surf):
        surf.blit(self.image, self.rect)
    
class Player:
    def __init__(self, screen_rect):
        self.screen_rect = screen_rect
        self.image = pg.image.load('spaceship.png').convert()
        self.mask = pg.mask.from_surface(self.image)
        self.image.set_colorkey((255,0,255))
        self.transformed_image = pg.transform.rotate(self.image, 180)
        start_buffer = 300
        self.rect = self.image.get_rect(
            center=(screen_rect.centerx, screen_rect.centery + start_buffer)
        )
        self.dx = 300
        self.dy = 300
        self.lasers = []
        self.timer = 0.0
        self.laser_delay = 500
        self.add_laser = False
        self.damage = 10
        
    def take_damage(self, value):
        self.damage -= value
    
    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                if self.add_laser:
                    self.lasers.append(Laser(self.rect.center, self.screen_rect))
                    self.add_laser = False
    
    def update(self, keys, dt):
        self.rect.clamp_ip(self.screen_rect)
        if keys[pg.K_LEFT]:
            self.rect.x -= self.dx * dt
        if keys[pg.K_RIGHT]:
            self.rect.x += self.dx * dt
        if keys[pg.K_UP]:
            self.rect.y -= self.dy * dt
        if keys[pg.K_DOWN]:
            self.rect.y += self.dy * dt
        for laser in self.lasers:
            laser.update()
        if pg.time.get_ticks()-self.timer > self.laser_delay:
            self.timer = pg.time.get_ticks()
            self.add_laser = True
    
    def draw(self, surf):
        for laser in self.lasers:
            laser.render(surf)
        surf.blit(self.transformed_image, self.rect)
    
screen = pg.display.set_mode((800,600))
screen_rect = screen.get_rect()
player = Player(screen_rect)
ENEMY_IMAGE = enemy_image_load()
enemy = Enemy(ENEMY_IMAGE, screen_rect)
clock = pg.time.Clock()
done = False
while not done:
    keys = pg.key.get_pressed()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            done = True
        player.get_event(event)
    screen.fill((0,0,0))
    delta_time = clock.tick(60)/1000.0
    player.update(keys, delta_time)
    enemy.update(delta_time, player)
    player.draw(screen)
    enemy.draw(screen)
    pg.display.update()
