# -*- coding: utf-8 -*-
"""
Version modifiée (verticale) :
- Le régiment est en bas de l'écran.
- Les ennemis et les cases tombent du haut vers le bas.
- Les ennemis ont des points de vie (1–50).
- Si un ennemi touche le régiment, on perd autant de soldats que ses PV.
- Les cases rouges négatives retirent des soldats, les bleues positives en ajoutent.
- Les cases peuvent monter jusqu'à +50.
- Tir limité à 20 balles par seconde.
- Les dégâts des balles se répartissent sur les soldats :
  ex : 40 soldats = 20 balles de 2 dégâts chacune ;
  45 soldats = 5 balles de 3 dégâts + 15 balles de 2 dégâts.
"""
import math
import random
import sys
from dataclasses import dataclass

import pygame

WIDTH, HEIGHT = 900, 600
FPS = 60
BG_COLOR = (18, 18, 22)

REGIMENT_SPEED = 8
REGIMENT_RADIUS = 20
REGIMENT_Y = HEIGHT - 60
REGIMENT_START_SOLDIERS = 20
REGIMENT_MIN_SOLDIERS = 0
REGIMENT_MAX_SOLDIERS = 999

BULLET_SPEED = 10
BULLET_RADIUS = 4
MAX_BULLETS_PER_SECOND = 20

ENEMY_SPEED_BASE = 2.0
ENEMY_SIZE = 32
ENEMY_SPAWN_EVERY_FRAMES = 60

BLOCK_SPEED_BASE = 1.8
BLOCK_SIZE = 48
BLOCK_SPAWN_EVERY_FRAMES = 90
BLOCK_NEGATIVE_MIN = -6
BLOCK_NEGATIVE_MAX = -2
BLOCK_POSITIVE_CAP = 50

DIFFICULTY_RAMP = 0.0005

pygame.font.init()
FONT = pygame.font.SysFont("arial", 22, bold=True)
SMALL = pygame.font.SysFont("arial", 16)
BIG = pygame.font.SysFont("arial", 36, bold=True)

@dataclass
class Bullet:
    x: float
    y: float
    vy: float
    damage: int

    def update(self):
        self.y -= self.vy

    def draw(self, surf):
        pygame.draw.circle(surf, (230, 230, 240), (int(self.x), int(self.y)), BULLET_RADIUS)

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x - BULLET_RADIUS), int(self.y - BULLET_RADIUS), BULLET_RADIUS * 2, BULLET_RADIUS * 2)

@dataclass
class Enemy:
    x: float
    y: float
    speed: float
    hp: int

    def update(self):
        self.y += self.speed

    def draw(self, surf):
        rect = pygame.Rect(int(self.x - ENEMY_SIZE / 2), int(self.y - ENEMY_SIZE / 2), ENEMY_SIZE, ENEMY_SIZE)
        pygame.draw.rect(surf, (200, 80, 80), rect, border_radius=6)
        pygame.draw.rect(surf, (255, 230, 230), rect, width=2, border_radius=6)
        hp_text = FONT.render(str(self.hp), True, (255, 255, 255))
        surf.blit(hp_text, hp_text.get_rect(center=rect.center))

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x - ENEMY_SIZE / 2), int(self.y - ENEMY_SIZE / 2), ENEMY_SIZE, ENEMY_SIZE)

@dataclass
class Block:
    x: float
    y: float
    value: int
    speed: float

    def update(self):
        self.y += self.speed

    def on_hit(self, damage):
        self.value = min(self.value + damage, BLOCK_POSITIVE_CAP)

    def color(self):
        if self.value < 0:
            return (220, 60, 60)
        elif self.value == 0:
            return (200, 200, 210)
        else:
            return (70, 150, 255)

    def draw(self, surf):
        rect = pygame.Rect(int(self.x - BLOCK_SIZE / 2), int(self.y - BLOCK_SIZE / 2), BLOCK_SIZE, BLOCK_SIZE)
        pygame.draw.rect(surf, self.color(), rect, border_radius=8)
        pygame.draw.rect(surf, (30, 30, 36), rect, width=2, border_radius=8)
        text = FONT.render(f"{self.value:+d}", True, (15, 15, 20))
        surf.blit(text, text.get_rect(center=rect.center))

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x - BLOCK_SIZE / 2), int(self.y - BLOCK_SIZE / 2), BLOCK_SIZE, BLOCK_SIZE)

class Regiment:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = REGIMENT_Y
        self.soldiers = REGIMENT_START_SOLDIERS
        self.fire_timer = 0

    def update(self, move_x):
        self.x = max(REGIMENT_RADIUS + 6, min(WIDTH - REGIMENT_RADIUS - 6, self.x + move_x))
        self.fire_timer = max(0, self.fire_timer - 1)

    def get_bullet_damages(self):
        if self.soldiers <= 0:
            return []
        soldiers = self.soldiers
        base = soldiers // MAX_BULLETS_PER_SECOND
        remainder = soldiers % MAX_BULLETS_PER_SECOND
        damages = [base] * MAX_BULLETS_PER_SECOND
        for i in range(remainder):
            damages[i] += 1
        return [d for d in damages if d > 0]

    def try_fire(self, bullets):
        if self.fire_timer > 0:
            return []
        self.fire_timer = FPS // MAX_BULLETS_PER_SECOND
        damages = self.get_bullet_damages()
        new_bullets = []
        for dmg in damages:
            new_bullets.append(Bullet(self.x, self.y - REGIMENT_RADIUS - 8, BULLET_SPEED, dmg))
        return new_bullets

    def draw(self, surf):
        pygame.draw.circle(surf, (120, 200, 255), (self.x, self.y), REGIMENT_RADIUS)
        pygame.draw.circle(surf, (10, 40, 60), (self.x, self.y), REGIMENT_RADIUS, 3)
        txt = FONT.render(str(self.soldiers), True, (255, 255, 255))
        surf.blit(txt, txt.get_rect(center=(self.x, self.y)))

    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x - REGIMENT_RADIUS, self.y - REGIMENT_RADIUS, REGIMENT_RADIUS * 2, REGIMENT_RADIUS * 2)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Tireurs verticaux")
        self.clock = pygame.time.Clock()
        self.running = True

        self.regiment = Regiment()
        self.bullets = []
        self.enemies = []
        self.blocks = []

        self.frame = 0
        self.score = 0
        self.best = 0
        self.difficulty = 1.0

    def spawn_enemy(self):
        x = random.randint(60, WIDTH - 60)
        speed = ENEMY_SPEED_BASE * (0.8 + random.random() * 0.6) * self.difficulty
        hp = random.randint(1, 50)
        self.enemies.append(Enemy(x, -30, speed, hp))

    def spawn_block(self):
        x = random.randint(80, WIDTH - 80)
        speed = BLOCK_SPEED_BASE * (0.8 + random.random() * 0.6) * (0.9 + 0.3 * self.difficulty)
        val = random.randint(BLOCK_NEGATIVE_MIN, BLOCK_NEGATIVE_MAX)
        self.blocks.append(Block(x, -40, val, speed))

    def handle_collisions(self):
        for b in list(self.bullets):
            br = b.rect()
            for e in list(self.enemies):
                if br.colliderect(e.rect()):
                    e.hp -= b.damage
                    self.bullets.remove(b)
                    if e.hp <= 0:
                        self.enemies.remove(e)
                        self.score += 10
                    break
            else:
                for bl in list(self.blocks):
                    if br.colliderect(bl.rect()):
                        bl.on_hit(b.damage)
                        self.bullets.remove(b)
                        break

        rr = self.regiment.rect()
        for e in list(self.enemies):
            if rr.colliderect(e.rect()) or e.y > self.regiment.y:
                self.enemies.remove(e)
                self.regiment.soldiers -= e.hp
                if self.regiment.soldiers < 0:
                    self.regiment.soldiers = 0

        for bl in list(self.blocks):
            if rr.colliderect(bl.rect()) or bl.y > self.regiment.y:
                if bl.value < 0:
                    self.regiment.soldiers = max(0, self.regiment.soldiers + bl.value)
                elif bl.value > 0:
                    self.regiment.soldiers = min(REGIMENT_MAX_SOLDIERS, self.regiment.soldiers + bl.value)
                self.blocks.remove(bl)

    def draw_hud(self):
        hud = pygame.Rect(0, 0, WIDTH, 46)
        pygame.draw.rect(self.screen, (28, 28, 34), hud)
        pygame.draw.line(self.screen, (50, 50, 60), (0, 46), (WIDTH, 46))

        txt_sold = BIG.render(f"Soldats: {self.regiment.soldiers}", True, (235, 235, 245))
        txt_score = BIG.render(f"Score: {self.score}", True, (235, 235, 245))
        self.screen.blit(txt_sold, (16, 6))
        self.screen.blit(txt_score, (WIDTH - txt_score.get_width() - 16, 6))

    def update(self):
        self.frame += 1
        self.difficulty += DIFFICULTY_RAMP

        keys = pygame.key.get_pressed()
        dx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= REGIMENT_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += REGIMENT_SPEED

        self.regiment.update(dx)

        new_bullets = self.regiment.try_fire(self.bullets)
        self.bullets.extend(new_bullets)

        if self.frame % max(8, int(ENEMY_SPAWN_EVERY_FRAMES / self.difficulty)) == 0:
            self.spawn_enemy()
        if self.frame % max(12, int(BLOCK_SPAWN_EVERY_FRAMES / (0.7 + 0.3 * self.difficulty))) == 0:
            self.spawn_block()

        for b in list(self.bullets):
            b.update()
            if b.y < -20:
                self.bullets.remove(b)
        for e in list(self.enemies):
            e.update()
            if e.y > HEIGHT + 40:
                self.enemies.remove(e)
        for bl in list(self.blocks):
            bl.update()
            if bl.y > HEIGHT + 60:
                self.blocks.remove(bl)

        self.handle_collisions()
        self.score += 1
        self.best = max(self.best, self.score)

    def draw(self):
        self.screen.fill(BG_COLOR)
        for y in range(0, HEIGHT, 60):
            pygame.draw.line(self.screen, (24, 24, 30), (0, y), (WIDTH, y))
        for x in range(60, WIDTH, 60):
            pygame.draw.line(self.screen, (24, 24, 30), (x, 0), (x, HEIGHT))

        for bl in self.blocks:
            bl.draw(self.screen)
        for e in self.enemies:
            e.draw(self.screen)
        for b in self.bullets:
            b.draw(self.screen)
        self.regiment.draw(self.screen)

        self.draw_hud()

        if self.regiment.soldiers <= 0:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            self.screen.blit(overlay, (0, 0))
            txt = BIG.render("Défaite : plus de soldats", True, (240, 240, 250))
            self.screen.blit(txt, txt.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

        pygame.display.flip()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False

            if self.regiment.soldiers <= 0:
                self.draw()
                continue

            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    Game().run()