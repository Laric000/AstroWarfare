import pygame
import random
import math
pygame.init()


LARGURA = 1280
ALTURA = 720
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("AstroWarfare")

FPS = 60
clock = pygame.time.Clock()


FUNDO = pygame.image.load("cenario/corredor.png").convert()
MAO_ARMA = pygame.image.load("objetos/arms.png").convert_alpha()

ROBO_IMG = pygame.transform.scale(
    pygame.image.load("robos/Robo.png").convert_alpha(), (150, 150))

ROBO_CHEFAO_IMG = pygame.transform.scale(
    pygame.image.load("robos/chefão.png").convert_alpha(), (250, 250))

EXPLOSAO_IMG = pygame.transform.scale(
    pygame.image.load("robos/kabum.png").convert_alpha(), (150, 150))

TIRO_SOM = pygame.mixer.Sound("som_tiro.mp3")
EXPLOSAO_SOM = pygame.mixer.Sound("som_explosao.mp3")


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = MAO_ARMA
        self.rect = self.image.get_rect(bottomright=(LARGURA - 70, ALTURA))
        self.health = 5
        self.score = 0

    def update(self):
        pass


class Bullet(pygame.sprite.Sprite):
    def __init__(self, start, target):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(center=start)

        dx = target[0] - start[0]
        dy = target[1] - start[1]
        dist = math.hypot(dx, dy) or 1
        speed = 25
        self.vel = (dx / dist * speed, dy / dist * speed)

    def update(self):
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]

        if not TELA.get_rect().colliderect(self.rect):
            # Só perde vida se o boss estiver ativo
            if boss_spawned:
                player.health -= 1
                if player.health <= 0:
                    pygame.quit()
                    quit()
            self.kill()


class Robo(pygame.sprite.Sprite):
    def __init__(self, x, y, speed=3):
        super().__init__()
        self.image = ROBO_IMG
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed

    def update(self):
        self.rect.y += self.speed


class RoboLento(Robo):
    def __init__(self, x, y):
        super().__init__(x, y, 1)


class RoboRapido(Robo):
    def __init__(self, x, y):
        super().__init__(x, y, 6)


class RoboZigueZague(Robo):
    def __init__(self, x, y):
        super().__init__(x, y, 3)
        self.dir = 1
        self.count = 0

    def update(self):
        self.rect.y += self.speed
        self.rect.x += self.dir * 3
        self.count += 1
        if self.count % 40 == 0:
            self.dir *= -1


class RoboCiclico(Robo):
    def __init__(self, x, y):
        super().__init__(x, y, 2)
        self.angle = 0
        self.center = [x, y]

    def update(self):
        self.angle += 0.05
        self.rect.x = self.center[0] + math.cos(self.angle) * 70
        self.rect.y += self.speed


class RoboSaltador(Robo):
    def __init__(self, x, y):
        super().__init__(x, y, 2)
        self.timer = random.randint(30, 60)

    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            self.rect.y += random.randint(-40, 40)
            self.timer = random.randint(30, 60)
        self.rect.y += self.speed


class RoboCacador(Robo):
    def __init__(self, x, y, player):
        super().__init__(x, y, 2)
        self.player = player

    def update(self):
        dx = self.player.rect.x - self.rect.x
        dy = self.player.rect.y - self.rect.y
        dist = math.hypot(dx, dy) or 1
        self.rect.x += dx / dist * self.speed
        self.rect.y += dy / dist * self.speed



class RoboChefe(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = ROBO_CHEFAO_IMG
        self.rect = self.image.get_rect(center=(x, y))
        self.max_health = 500  
        self.health = self.max_health
        self.vel_x = 6
        self.vel_y = 3
        self.dir_x = 1
        self.dir_y = 1


        self.invul = False

        self.teleport_cooldown = 5000  
        self.last_teleport = 0
        self.teleport_warning = False  


        self.shield_cooldown = 10000  
        self.last_shield = 0
        self.shield_active = False
        self.shield_duration = 2000  

        self.timer = 0

    def update(self):
        self.timer += clock.get_time()
        self.rect.x += self.vel_x * self.dir_x
        if self.rect.left <= 50 or self.rect.right >= LARGURA - 50:
            self.dir_x *= -1

        self.rect.y += self.vel_y * self.dir_y
        if self.rect.top <= 50 or self.rect.bottom >= ALTURA // 2:
            self.dir_y *= -1


        if self.timer - self.last_teleport >= self.teleport_cooldown:
            self.invul = True
            self.teleport_warning = True

            if self.timer - self.last_teleport >= self.teleport_cooldown + 600:
                self.teleport()
                self.last_teleport = self.timer
                self.teleport_warning = False
                self.invul = False

        if self.timer - self.last_shield >= self.shield_cooldown:
            self.shield_active = True
            self.invul = True  
            if self.timer - self.last_shield >= self.shield_cooldown + self.shield_duration:
                self.shield_active = False
                self.invul = False
                self.last_shield = self.timer

    def teleport(self):
        new_x = random.randint(100, LARGURA - 100)
        new_y = random.randint(50, ALTURA // 2)
        self.rect.center = (new_x, new_y)


class PersonagemEaster(pygame.sprite.Sprite):
    def __init__(self, img, y):
        super().__init__()
        self.image = pygame.transform.scale(
            pygame.image.load(img).convert_alpha(), (150, 150))
        self.rect = self.image.get_rect(midtop=(random.randint(100, LARGURA - 100), -self.image.get_height()))


        self.vel_y = 2
        self.vel_x = 3
        self.dir = 1
        self.count = 0

        self.health = 60

    def update(self):
        self.rect.y += self.vel_y

        self.rect.x += self.dir * self.vel_x
        self.count += 1
        if self.count % 40 == 0:
            self.dir *= -1

        if self.rect.left > LARGURA + 50:
            self.kill()

class Explosao(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = EXPLOSAO_IMG
        self.rect = self.image.get_rect(center=pos)
        self.timer = 10

    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            self.kill()


all_sprites = pygame.sprite.Group()
robos = pygame.sprite.Group()
bullets = pygame.sprite.Group()
explosions = pygame.sprite.Group()
easter_group = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

boss = None
boss_spawned = False
easter_spawned = False


spawn_timer = 0
running = True
r2d2_spawned = False
c3po_spawned = False
easter_timer = 0


while running:
    clock.tick(FPS)
    TELA.blit(FUNDO, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            b = Bullet(player.rect.center, pygame.mouse.get_pos())
            bullets.add(b)
            all_sprites.add(b)
            TIRO_SOM.play()

    spawn_timer += 1
    if spawn_timer > 20 and not boss_spawned:
        tipo = random.choice([
            RoboLento, RoboRapido, RoboZigueZague, RoboCiclico, RoboSaltador, RoboCacador])
        robo = tipo(random.randint(100, LARGURA - 100), -50, player) \
            if tipo == RoboCacador else tipo(random.randint(100, LARGURA - 100), -50)

        robos.add(robo)
        all_sprites.add(robo)
        spawn_timer = 0

    if player.score >= 9000 and not easter_spawned:
        c3po = PersonagemEaster("robos/c3po.png", ALTURA - 350)
        h2d2 = PersonagemEaster("robos/r2d2.png", ALTURA - 200)
        easter_group.add(c3po, h2d2)
        all_sprites.add(c3po, h2d2)
        easter_spawned = True

    if player.score >= 15000 and not boss_spawned:
        boss = RoboChefe(LARGURA // 2, ALTURA // 4)
        boss_spawned = True
        all_sprites.add(boss)

        for r in robos:
            r.kill()
        for e in easter_group:
            e.kill()

    all_sprites.update()

    if boss_spawned:
        hits = pygame.sprite.spritecollide(boss, bullets, True)
        if hits and not boss.invul:
            boss.health -= 5 * len(hits)
            EXPLOSAO_SOM.play()
            e = Explosao(boss.rect.center)
            explosions.add(e)
            all_sprites.add(e)

        if boss.health <= 0:
            boss.kill()
            boss_spawned = False
            print("Você venceu o jogo!")
            running = False

    hits = pygame.sprite.groupcollide(robos, bullets, True, True)
    for r in hits:
        player.score += 100
        EXPLOSAO_SOM.play()
        e = Explosao(r.rect.center)
        explosions.add(e)
        all_sprites.add(e)

    hits = pygame.sprite.groupcollide(easter_group, bullets, False, True)
    for r in hits:
        e.health -= 10
        player.score += 500
        EXPLOSAO_SOM.play()
        if e.health <= 0:
            e.kill()

    for r in list(robos):
        if r.rect.top > ALTURA:
            r.kill()
            player.health -= 1
            if player.health <= 0:
                running = False

    all_sprites.draw(TELA)

    font = pygame.font.SysFont(None, 32)
    TELA.blit(font.render(f"Pontos: {player.score}", True, (255,255,255)), (10,10))
    TELA.blit(font.render(f"Vidas: {player.health}", True, (255,0,0)), (10,40))
    if boss_spawned:
        TELA.blit(font.render(f"Boss HP: {boss.health}", True, (255,0,0)), (10,70))

    pygame.display.flip()

pygame.quit()
