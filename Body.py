# -*- coding: utf-8 -*-
import pygame
import random
from os import path
import math

img_dir = path.join(path.dirname(__file__), 'img')
pow_img_dir = path.join(path.dirname(__file__), 'img/powimg')
snd_dir = path.join(path.dirname(__file__), 'snd')

# игровые параметры
FPS = 60
FPS2 = 30

PlAYER_DEATH_TIME = 1000
SHOOT_DELAY = 250
BULLET_SPEED = 15
LASER_GUN_RADIUS = 400
POWS_TIMINGS = {"throw": 2000, "duo": 5000, "laser": 5000, "2x_speed": 5000}

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SPEC = (71, 112, 76)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)


class MiniScore:
    def __init__(self):
        self.last_update = 0
        self.score = 0

    def update_drow(self):
        if self.score and pygame.time.get_ticks() - self.last_update < 1000:
            draw_text(screen, "+" + str(self.score), 16, WIDTH / 2, 30, GREEN)
        else:
            self.score = 0

    def plus_score(self, score):
        if score:
            self.last_update = pygame.time.get_ticks()
            self.score += score


class MiniPows:
    def __init__(self):
        self.pow = {}
        for l_key, l_time in POWS_TIMINGS.items():
            self.pow[l_key] = {'pict': MINI_POWS_LIST[l_key], 'start_time': 0}

    def add_pow_time(self, type):
        now = pygame.time.get_ticks()
        if type in self.pow.keys():
            old_time = POWS_TIMINGS[type] - (now - self.pow[type]['start_time'])
            if old_time < 0:
                old_time = 0
            self.pow[type]['start_time'] = now + old_time

    def update_drow(self):
        now = pygame.time.get_ticks()
        if now < 5000:
            return
        print_list = []
        for l_key, val in self.pow.items():
            if now - val['start_time'] < POWS_TIMINGS[l_key]:
                print_list.append((val['pict'], (POWS_TIMINGS[l_key] - now + val['start_time']) // 100 / 10))

        for i in range(len(print_list)):
            img_rect = print_list[i][0].get_rect()
            img_rect.x = 5 + 38 * i
            img_rect.y = 25
            screen.blit(print_list[i][0], img_rect)
            draw_text(screen, str(print_list[i][1]), 16, img_rect.x + 19, 65, YELLOW)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = self.orig_image = player_images[3]
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH / 2
        self.rect.centery = HEIGHT - 55
        self.radius = 39

        self.is_live = True
        self.shield = 100
        self.lives = 3
        self.speedx = 0

        self.last_shot = pygame.time.get_ticks()

        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()

        self.power = 0
        self.power_time = pygame.time.get_ticks()

        self.throw = 0
        self.throw_time = pygame.time.get_ticks()

        self.laser = 0
        self.laser_time = pygame.time.get_ticks()

        self.gun_speed = 0
        self.gun_speed_time = pygame.time.get_ticks()

        self.last_update = pygame.time.get_ticks()
        self.last_press = 8
        self.throw = False

    def update(self):
        if self.power >= 1 and pygame.time.get_ticks() - self.power_time > POWS_TIMINGS["duo"]:
            self.power -= 1
            self.power_time = pygame.time.get_ticks()

        if self.throw >= 1 and pygame.time.get_ticks() - self.throw_time > POWS_TIMINGS["throw"]:
            self.throw -= 1
            self.power_time = pygame.time.get_ticks()

        if self.laser >= 1 and pygame.time.get_ticks() - self.laser_time > POWS_TIMINGS["laser"]:
            self.laser -= 1
            self.laser_time = pygame.time.get_ticks()

        if self.power >= 1 and pygame.time.get_ticks() - self.power_time > POWS_TIMINGS["duo"]:
            self.power -= 1
            self.power_time = pygame.time.get_ticks()

        if self.gun_speed >= 1 and pygame.time.get_ticks() - self.gun_speed_time > POWS_TIMINGS["2x_speed"]:
            self.gun_speed -= 1
            self.gun_speed_time = pygame.time.get_ticks()

        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.centery = HEIGHT - 55

        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_a] and keystate[pygame.K_d]:
            self.speedx = 0
        elif keystate[pygame.K_d]:
            self.speedx = 8
            self.last_press = 8
        elif keystate[pygame.K_a]:
            self.speedx = -8
            self.last_press = -8
        else:
            self.speedx = 0

        self.rect.centerx += self.speedx
        distance_x, distance_y = self.catit()
        self.rotate(distance_x, distance_y)

        mous_state = pygame.mouse.get_pressed()
        if mous_state[0]:
            self.shoot(distance_x, distance_y)
        elif self.laser:
            laser.off()
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shield_update(self, shield):
        self.shield += shield
        if self.shield > 200:
            self.shield = 200
        im = self.shield // 26
        if im < 0:
            im = 0
        if im > 3:
            im = 3
        self.orig_image = player_images[im]

    def powerup(self):
        self.power += 1
        self.power_time = pygame.time.get_ticks()

    def laserup(self):
        self.laser += 1
        self.laser_time = pygame.time.get_ticks()

    def throwup(self):
        self.throw += 1
        self.throw_time = pygame.time.get_ticks()

    def gun_speedup(self):
        self.gun_speed += 1
        self.gun_speed_time = pygame.time.get_ticks()

    def rotate(self, x, y):
        self.image = pygame.transform.rotate(self.orig_image, (180 / math.pi) * -math.atan2(y, x) - 90)
        self.rect = self.image.get_rect(center=self.rect.center)

    def math_pos(self, x, y):
        sin = y / (x ** 2 + y ** 2) ** 0.5
        cos = x / (x ** 2 + y ** 2) ** 0.5
        return sin, cos

    def catit(self):
        mx, my = pygame.mouse.get_pos()
        return mx - self.rect.centerx, my - self.rect.centery

    def shoot(self, x, y):
        if self.hidden:
            return
        now = pygame.time.get_ticks()
        if self.laser:
            laser.on()
            return
        else:
            laser.off()

        if self.gun_speed:
            delay = SHOOT_DELAY / 1.5
        else:
            delay = SHOOT_DELAY

        if now - self.last_shot > delay:
            self.last_shot = now
            angle = math.atan2(y, x)
            sx = int(BULLET_SPEED * math.cos(angle))
            sy = int(BULLET_SPEED * math.sin(angle))

            sin, cos = self.math_pos(x, y)
            r = self.rect.width / 2

            if self.power:
                bullet1 = Bullet(self.rect.centerx - r * sin, self.rect.centery + r * cos, sx, sy, self.throw)
                bullet2 = Bullet(self.rect.centerx + r * sin, self.rect.centery - r * cos, sx, sy, self.throw)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shoot_sound.play()
            else:
                bullet = Bullet(self.rect.centerx + r * cos, self.rect.centery + r * sin, sx, sy, self.throw)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()

    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 400)


class Meteor(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.images = random.choice(meteor_images)
        self.image_orig = self.images[0]
        self.image = self.image_orig.copy()

        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-150, -100)
        self.radius = int(self.rect.width * .85 / 2)

        self.lives = len(self.images)
        self.speedy = random.randrange(1, int(43 / self.rect.width * 9))
        self.speedx = random.randrange(-3, 3)
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()

    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            self.image = pygame.transform.rotate(self.image_orig, self.rot)
            self.rect = self.image.get_rect(center=self.rect.center)

    def update(self):
        self.rotate()
        if self.rect.top > HEIGHT:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)
            self.lives = len(self.images)
            self.image_orig = self.images[0]
        else:
            self.rect.right = self.rect.right % (WIDTH + self.rect.width)
        self.rect.x += self.speedx
        self.rect.y += self.speedy

    def damage(self):
        self.lives -= 1
        if self.lives > 0:
            self.image_orig = self.images[len(self.images) - self.lives]
            return False
        return True

    def resurrect(self):  # потому что суицд это плохо
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 8)
        self.lives = len(self.images)
        self.image_orig = self.images[0]


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, sx=0, sy=-BULLET_SPEED, throw=False):
        pygame.sprite.Sprite.__init__(self)
        rot = (180 / math.pi) * -math.atan2(sy, sx) - 90
        self.image = pygame.transform.rotate(bullet_img[int(bool(throw))], rot)
        self.rect = self.image.get_rect()
        self.rect.centery = y
        self.rect.centerx = x
        self.speedy = sy
        self.speedx = sx
        self.is_throw = throw

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.bottom < 0 or self.rect.top > HEIGHT or self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()  # суицид это плохо


class Pow(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(list(POWS_LIST.keys()))
        self.image = POWS_LIST[self.type]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = random.randrange(1, 3)

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()


class LaserGun():
    def __init__(self):
        self.is_on = False
        self.pos = (WIDTH, HEIGHT)

    def on(self):
        if self.is_on:
            laser_sound.play(-1)
        else:
            self.is_on = True

    def off(self):
        self.is_on = False
        laser_sound.stop()

    def killer(self, mob):
        p1x, p1y = player.rect.center
        p2x, p2y = self.pos
        r1x, r1y = mob.rect.topleft
        r2x, r2y = mob.rect.topright
        r3x, r3y = mob.rect.bottomleft
        r4x, r4y = mob.rect.bottomright

        if p1x > r1x and p1x > r2x and p1x > r3x and p1x > r4x and p2x > r1x and p2x > r2x and p2x > r3x and p2x > r4x:
            return False
        if p1x < r1x and p1x < r2x and p1x < r3x and p1x < r4x and p2x < r1x and p2x < r2x and p2x < r3x and p2x < r4x:
            return False
        if p1y > r1y and p1y > r2y and p1y > r3y and p1y > r4y and p2y > r1y and p2y > r2y and p2y > r3y and p2y > r4y:
            return False
        if p1y < r1y and p1y < r2y and p1y < r3y and p1y < r4y and p2y < r1y and p2y < r2y and p2y < r3y and p2y < r4y:
            return False

        f1 = (p2y - p1y) * r1x + (p1x - p2x) * r1y + (p2x * p1y - p1x * p2y)
        f2 = (p2y - p1y) * r2x + (p1x - p2x) * r2y + (p2x * p1y - p1x * p2y)
        f3 = (p2y - p1y) * r3x + (p1x - p2x) * r3y + (p2x * p1y - p1x * p2y)
        f4 = (p2y - p1y) * r4x + (p1x - p2x) * r4y + (p2x * p1y - p1x * p2y)

        if f1 < 0 and f2 < 0 and f3 < 0 and f4 < 0:
            return False
        if f1 > 0 and f2 > 0 and f3 > 0 and f4 > 0:
            return False

        return True

    def update(self):
        if self.is_on:
            sin, cos = player.math_pos(*player.catit())
            self.pos = (player.rect.centerx + LASER_GUN_RADIUS * cos, player.rect.centery + LASER_GUN_RADIUS * sin)
            pygame.draw.line(screen, RED, player.rect.center, self.pos, 5)


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect(center=self.rect.center)


def save_record(save_score=0):
    if not path.exists('records.txt'):
        with open('records.txt', 'w') as file:
            file.write('0')

    with open('records.txt', 'r') as file:
        old_sscore = int(file.read())

    with open('records.txt', 'w') as file:
        file.write(str(max(save_score, old_sscore)))
    return max(save_score, old_sscore)


def draw_text(surf, text, size, x, y, color=WHITE):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def new_mob():
    m = Meteor()
    all_sprites.add(m)
    mobs.add(m)


def draw_shield_bar(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (pct / 100) * BAR_LENGTH / 2
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)


def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)


def player_death():
    death_sound.play()
    death_explosion = Explosion(player.rect.center, 'player')
    all_sprites.add(death_explosion)
    player.hide()
    player.lives -= 1
    player.shield = 100
    player.shield_update(0)


def show_go_screen(score=False):
    screen.blit(background, background_rect)
    draw_text(screen, "ShipX!", 64, WIDTH / 2, HEIGHT / 5)
    if score:
        draw_text(screen, "Yours score: " + ' '.join('{:,}'.format(score).split(',')), 22,
                  WIDTH / 2, HEIGHT / 2)
    else:
        draw_text(screen, "A/D keys move, Space/Mous buttons to fire", 22,
                  WIDTH / 2, HEIGHT / 2)
    draw_text(screen, "Yours record: " + ' '.join('{:,}'.format(save_record(score)).split(',')), 22,
              WIDTH / 2, HEIGHT / 2 + 30)
    draw_text(screen, "Press Esc key to leave the game", 18, WIDTH / 2, HEIGHT * 3 / 4)
    pygame.display.flip()

    local_running = True
    waiting = True
    delay = bool(score)
    delay_time = pygame.time.get_ticks()
    while waiting:
        clock.tick(FPS2)
        for go_event in pygame.event.get():
            if go_event.type == pygame.QUIT:
                pygame.quit()
            if go_event.type == pygame.KEYUP:
                if go_event.key == pygame.K_ESCAPE:
                    local_running = False
                    waiting = False
                elif delay:
                    if pygame.time.get_ticks() - delay_time > 2500:
                        waiting = False
                else:
                    waiting = False
    return local_running


# инициализация pygame и тд.
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
infoObject = pygame.display.Info()
WIDTH = infoObject.current_w  # эти константы стали известны только после инициализации pygame
HEIGHT = infoObject.current_h

clock = pygame.time.Clock()

pygame.display.set_caption("ShipX")
pygame.mouse.set_visible(False)
font_name = pygame.font.match_font('arial')

'''Выгрузка всех картинок:----------------------------------------------------------------------'''
# Изображения Бустов
POWS_LIST = {}
MINI_POWS_LIST = {}
pows_fils_names = {"health": "plus_health", "exp": "plus_xp", "throw": "throw_laser", "duo": "duo_gun",
                   "laser": "laser", "2x_speed": "2x_speed"}
for key, name in pows_fils_names.items():
    p_im = pygame.image.load(path.join(pow_img_dir, name + ".png")).convert()
    POWS_LIST[key] = pygame.transform.scale(p_im, (40, 40))
    POWS_LIST[key].set_colorkey(BLACK)
    MINI_POWS_LIST[key] = pygame.transform.scale(p_im, (35, 35))
    MINI_POWS_LIST[key].set_colorkey(BLACK)

CURSOR = (pygame.image.load(path.join(img_dir, 'cursor1.png')).convert_alpha(),
          pygame.image.load(path.join(img_dir, 'cursor2.png')).convert_alpha())  # изображения курсоров

background = pygame.image.load(path.join(img_dir, "starfield.png")).convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))
background_rect = background.get_rect()

player_images = []
player_names_images = ['playerShip4.png', 'playerShip3.png', 'playerShip2.png', 'playerShip1.png']
for im in player_names_images:
    im = pygame.transform.scale(pygame.image.load(path.join(img_dir, im)).convert(), (110, 70))
    im.set_colorkey(BLACK)
    player_images.append(im)

player_mini_img = pygame.transform.scale(player_images[3], (25, 19))
player_mini_img.set_colorkey(BLACK)

bullet_img = [i for i in [pygame.image.load(path.join(img_dir, "laserRed16.png")).convert(),
                          pygame.image.load(path.join(img_dir, "laserRed17.png")).convert()] if
              not i.set_colorkey(BLACK)]

meteor_images = []
meteor_list = [['meteor1.png'], ['meteor2.png'], ['meteor3.png'],
               ['meteor4.png', 'meteor4_1.png', 'meteor4_2.png'],
               ['meteor6.png', 'meteor6_2.png']]

for grp in meteor_list:
    group = []
    for im in grp:
        im = pygame.image.load(path.join(img_dir, im)).convert()
        im.set_colorkey(BLACK)
        group.append(im)
    meteor_images.append(group)

explosion_anim = {'lg': [], 'sm': [], 'player': []}
for i in range(9):
    filename = 'regularExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)

    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_anim['lg'].append(img_lg)

    img_sm = pygame.transform.scale(img, (32, 32))
    explosion_anim['sm'].append(img_sm)

    filename = 'sonicExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    explosion_anim['player'].append(img)

'''Выгрузка музыки и звуков:--------------------------------------------------------------------'''
shoot_sound = pygame.mixer.Sound(path.join(snd_dir, 'pew.wav'))
shoot_sound.set_volume(0.7)

hil_sound = pygame.mixer.Sound(path.join(snd_dir, 'hil.wav'))
hil_sound.set_volume(0.7)

death_sound = pygame.mixer.Sound(path.join(snd_dir, 'death.wav'))
death_sound.set_volume(1)

damage_sound = pygame.mixer.Sound(path.join(snd_dir, 'damage.wav'))
damage_sound.set_volume(1)

laser_sound = pygame.mixer.Sound(path.join(snd_dir, 'laser.wav'))
laser_sound.set_volume(1)

music = pygame.mixer.Sound(path.join(snd_dir, 'Make_Down.wav'))
music.play(-1)

expl_sounds = []
for snd in ['expl6.wav']:
    expl_sounds.append(pygame.mixer.Sound(path.join(snd_dir, snd)))

'''Переменные игрового цикла:----------------------------------------------------------------   '''
all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()
player_group = pygame.sprite.Group()

mini_score = MiniScore()
laser = LaserGun()
player = Player()
player_group.add(player)

mini_pows = MiniPows()

score = 0
now_score = 0

game_over = True
running = True
paused = False

mob_time = 0

for i in range(8):
    new_mob()

'''игровой цикл---------------------------------------------------------------------------------'''
while running:
    if game_over:
        running = show_go_screen(score)
        all_sprites = pygame.sprite.Group()
        mobs = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        player_group = pygame.sprite.Group()

        player = Player()
        player_group.add(player)

        mini_pows = MiniPows()

        score = 0
        now_score = 0
        game_over = False
        mob_time = 0

        for i in range(8):
            new_mob()

    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_SPACE:
                paused = not paused
                pygame.mouse.set_visible(paused)
            if event.key == pygame.K_f and not paused:
                player_death()

    screen.blit(background, background_rect)
    if paused:  # пауза
        draw_text(screen, "PAUSE", 48, WIDTH // 2, HEIGHT // 2)
        pygame.display.flip()
        continue

    '''обновление спрайтов и обработка столкновений_____________________________________________'''
    all_sprites.update()  # обновление спрайтов
    player_group.update()
    laser.update()

    hits = pygame.sprite.groupcollide(mobs, bullets, False, False)
    for mob, bull in hits.items():
        if not bull[0].is_throw:
            bull[0].kill()
        if mob.damage():
            now_score += mob.radius
            random.choice(expl_sounds).play()
            expl = Explosion(mob.rect.center, 'lg')
            all_sprites.add(expl)
            if random.random() > 0.92:
                pow = Pow(mob.rect.center)
                all_sprites.add(pow)
                powerups.add(pow)
            mob.resurrect()

    if laser.is_on:
        for mob in mobs:
            if laser.killer(mob):
                if mob.damage():
                    now_score += mob.radius
                    random.choice(expl_sounds).play()
                    random.choice(expl_sounds).play()
                    expl = Explosion(mob.rect.center, 'lg')
                    all_sprites.add(expl)
                    mob.resurrect()

    hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
    for hit in hits:
        player.shield_update(-hit.radius)
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        if player.shield <= 0:
            player_death()
        else:
            damage_sound.play()

    hits = pygame.sprite.spritecollide(player, powerups, True)
    for hit in hits:
        mini_pows.add_pow_time(hit.type)
        if hit.type == 'health':
            player.shield_update(10)
            hil_sound.play()
        elif hit.type == 'exp':
            now_score += 1000
        elif hit.type == 'throw':
            player.throwup()
        elif hit.type == 'duo':
            player.powerup()
        elif hit.type == 'laser':
            player.laserup()
        elif hit.type == '2x_speed':
            player.gun_speedup()

    if player.lives == 0 and not player.hidden:
        game_over = True

    '''отрисовка________________________________________________________________________________'''
    all_sprites.draw(screen)
    player_group.draw(screen)

    mous_cords = pygame.mouse.get_pos()
    screen.blit(CURSOR[bool(any(pygame.mouse.get_pressed()))], (mous_cords[0] - 15, mous_cords[1] - 15))

    mini_pows.update_drow()
    mini_score.update_drow()

    draw_shield_bar(screen, 5, 5, player.shield)
    draw_lives(screen, WIDTH - 100, 5, player.lives, player_mini_img)

    draw_text(screen, "fps:" + str(int(clock.get_fps())), 18, WIDTH - 38, 28)
    draw_text(screen, str(score), 18, WIDTH / 2, 10)

    '''обновление переменных____________________________________________________________________'''
    if int(mob_time) > 4:  # повышение урвня
        new_mob()
        mob_time = 0
    mob_time += 60 / 1000

    mini_score.plus_score(now_score)
    score += now_score
    now_score = 0

    pygame.display.flip()

pygame.quit()
