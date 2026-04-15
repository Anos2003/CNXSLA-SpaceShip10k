import pygame
import random
import math
from settings import *
# ==============================================================================
# --- ĐỊNH NGHĨA MÀU SẮC ĐẠN CHUẨN THEO HƯỚNG DẪN ---
# ==============================================================================
PLASMA_COLOR = (0, 150, 255)    
LASER_COLOR  = (255, 50, 50)    
HOMING_COLOR = (200, 0, 255)    

_IMAGE_CACHE = {'player': None, 'enemy': None, 'boss': None, 'boss2': None, 'boss3': None, 'drone': None, 'meteor': None}

def get_cached_image(key, path, size):
    if _IMAGE_CACHE[key] is None:
        try:
            img = pygame.image.load(path).convert_alpha()
            _IMAGE_CACHE[key] = pygame.transform.scale(img, size)
        except:
            _IMAGE_CACHE[key] = "ERROR" 
    return _IMAGE_CACHE[key] if _IMAGE_CACHE[key] != "ERROR" else None

class ShootingStar:
    def __init__(self):
        self.x = random.randint(WIDTH // 2, WIDTH + 400); self.y = random.randint(-200, 0)
        self.speed_x = random.uniform(-25, -15); self.speed_y = random.uniform(15, 25)
        self.length = random.randint(50, 120)
        
    def update(self): 
        self.x += self.speed_x; self.y += self.speed_y
        
    def draw(self, surface):
        end_x = self.x - self.speed_x * (self.length / 20)
        end_y = self.y - self.speed_y * (self.length / 20)
        pygame.draw.line(surface, WHITE, (self.x, self.y), (end_x, end_y), 2)

class StarLayer:
    def __init__(self, num_stars, speed_range, size_range, color_range, depth):
        self.stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT), random.uniform(*speed_range), random.uniform(*size_range), random.choice(color_range)] for _ in range(num_stars)]
    def update(self):
        for s in self.stars:
            s[1] += s[2]
            if s[1] > HEIGHT: s[1] = 0; s[0] = random.randint(0, WIDTH)
    def draw(self, surface):
        for s in self.stars: pygame.draw.circle(surface, s[4], (int(s[0]), int(s[1])), int(s[3]))

class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH); self.y = random.randint(0, HEIGHT); self.layer = random.choice([1, 2, 3]) 
        if self.layer == 1: self.speed = random.uniform(0.5, 1.2); self.radius = random.uniform(0.5, 1.0); self.color = (80, 80, 80) 
        elif self.layer == 2: self.speed = random.uniform(1.5, 3.0); self.radius = random.uniform(1.2, 1.8); self.color = (150, 150, 150)
        else: self.speed = random.uniform(3.5, 6.0); self.radius = random.uniform(2.0, 3.0); self.color = WHITE 
    def update(self):
        self.y += self.speed
        if self.y > HEIGHT: self.y = 0; self.x = random.randint(0, WIDTH)
    def draw(self, surface): pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.radius))

class Player:
    def __init__(self):
        self.x = WIDTH // 2; self.y = HEIGHT - 100
        self.hp = 100; self.max_hp = 100; self.lives = 3
        self.invincible_timer = 0; self.rage = 0; self.max_rage = 100; self.score = 0
        self.level = 1; self.bonus_damage = 0; 
        
        self.weapon_type = 'laser' 
        self.color = LASER_COLOR; 
        
        self.spread_shot = False 
        self.shield_timer = 0; self.laser_cooldown = 0; self.missile_cooldown = 0
        self.burn_unlocked = False 
        self.has_drone = False 
        self.drone_cooldown = 0 

    def draw(self, surface):
        if self.invincible_timer > 0:
            if self.invincible_timer % 10 < 5: return
            pygame.draw.circle(surface, YELLOW, (int(self.x), int(self.y)), 55, 2)
            
        if self.shield_timer > 0: 
            shield_surf = pygame.Surface((110, 110), pygame.SRCALPHA)
            local_center = (55, 55)
            time_factor = pygame.time.get_ticks() / 150.0
            pulse_alpha = 100 + int(70 * math.sin(time_factor))
            outline_alpha = 180 + int(70 * math.sin(time_factor))

            pygame.draw.circle(shield_surf, (0, 255, 255, int(pulse_alpha//2)), local_center, 45)

            rot_angle = pygame.time.get_ticks() / 3.0
            for a in range(3):
                rect = pygame.Rect(local_center[0] - 50, local_center[1] - 50, 100, 100)
                start_rad = math.radians(rot_angle + a * 120)
                end_rad = math.radians(rot_angle + a * 120 + 80)
                pygame.draw.arc(shield_surf, (200, 255, 255, int(outline_alpha)), rect, start_rad, end_rad, 4)

            surface.blit(shield_surf, (int(self.x) - local_center[0], int(self.y) - local_center[1]))

        ship_poly = [(self.x, self.y - 30), (self.x - 25, self.y + 20), (self.x, self.y + 10), (self.x + 25, self.y + 20)]
        glow_color = self.color 
        for thickness in range(5, 0, -1):
            alpha = int(100 / thickness) 
            temp_color = glow_color + (alpha,)
            temp_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
            local_poly = [(p[0] - self.x + 30, p[1] - self.y + 30) for p in ship_poly]
            pygame.draw.polygon(temp_surf, temp_color, local_poly, thickness)
            surface.blit(temp_surf, (self.x - 30, self.y - 30))

        player_img = get_cached_image('player', 'graphics/player.png', (90, 90))
        if player_img:
            surface.blit(player_img, player_img.get_rect(center=(int(self.x), int(self.y))))
            flame_len = random.randint(10, 25)
            pygame.draw.polygon(surface, NEON_ORANGE, [(self.x - 6, self.y + 25), (self.x + 6, self.y + 25), (self.x, self.y + 25 + flame_len)])
            pygame.draw.polygon(surface, YELLOW, [(self.x - 3, self.y + 25), (self.x + 3, self.y + 25), (self.x, self.y + 25 + flame_len/2)])
        else:
            flame_len = random.randint(10, 25)
            pygame.draw.polygon(surface, NEON_ORANGE, [(self.x - 8, self.y + 15), (self.x + 8, self.y + 15), (self.x, self.y + 15 + flame_len)])
            pygame.draw.polygon(surface, YELLOW, [(self.x - 4, self.y + 15), (self.x + 4, self.y + 15), (self.x, self.y + 15 + flame_len/2)])
            body_points = [(self.x, self.y - 25), (self.x - 20, self.y + 15), (self.x, self.y + 5), (self.x + 20, self.y + 15)]
            cockpit_points = [(self.x, self.y - 12), (self.x - 6, self.y + 5), (self.x + 6, self.y + 5)]
            pygame.draw.polygon(surface, (20, 30, 40), body_points); pygame.draw.polygon(surface, NEON_CYAN, cockpit_points) 
            pygame.draw.polygon(surface, self.color, body_points, 3)

        if self.has_drone:
            drone_img = get_cached_image('drone', 'graphics/drone.png', (40, 40))
            drone_x, drone_y = self.x + 55, self.y + 15
            if drone_img:
                surface.blit(drone_img, drone_img.get_rect(center=(int(drone_x), int(drone_y))))
                d_flame = random.randint(5, 12)
                pygame.draw.polygon(surface, NEON_ORANGE, [(drone_x - 3, drone_y + 15), (drone_x + 3, drone_y + 15), (drone_x, drone_y + 15 + d_flame)])
                if self.drone_cooldown <= 0: pygame.draw.circle(surface, NEON_RED, (int(drone_x), int(drone_y - 10)), 4)
            else:
                pygame.draw.polygon(surface, (255, 0, 255), [(drone_x, drone_y-10), (drone_x-10, drone_y+10), (drone_x+10, drone_y+10)])

    def upgrade_weapon(self, upgrade_type):
        if upgrade_type == 'upgrade_plasma': self.weapon_type = 'plasma'; self.color = PLASMA_COLOR
        elif upgrade_type == 'upgrade_laser': self.weapon_type = 'laser'; self.color = LASER_COLOR 
        elif upgrade_type == 'upgrade_homing': self.weapon_type = 'homing'; self.color = HOMING_COLOR 

    def shoot(self, bullets_list):
        if self.laser_cooldown > 0: return False
        lvl = min(self.level, 6) 
        
        if self.weapon_type == 'plasma':
            self.laser_cooldown = max(5, 14 - lvl*2) 
            if lvl == 1: angles = [90]
            elif lvl == 2: angles = [85, 95]
            elif lvl == 3: angles = [75, 90, 105]
            elif lvl == 4: angles = [60, 80, 100, 120]
            elif lvl == 5: angles = [50, 70, 90, 110, 130]
            else: angles = [30, 54, 78, 102, 126, 150] 
            for ang in angles: bullets_list.append(Bullet(self.x, self.y - 20, self.weapon_type, angle=ang, level=lvl))

        elif self.weapon_type == 'laser':
            self.laser_cooldown = max(10, (14 - lvl*2) * 2) 
            if lvl == 6:
                bullets_list.append(Bullet(self.x, self.y - 20, self.weapon_type, dx=0, level=lvl))
            else:
                if lvl == 1: offsets = [0]
                elif lvl == 2: offsets = [-15, 15]
                elif lvl == 3: offsets = [-20, 0, 20]
                elif lvl == 4: offsets = [-30, -10, 10, 30]
                elif lvl == 5: offsets = [-40, -20, 0, 20, 40] 
                for off in offsets:
                    ang = 90
                    if lvl == 5: ang = 90 - (off/3) 
                    bullets_list.append(Bullet(self.x + off, self.y - 20, self.weapon_type, angle=ang, level=lvl))

        elif self.weapon_type == 'homing':
            self.laser_cooldown = max(12, 25 - lvl*2)
            if lvl == 1: angles = [90]
            elif lvl == 2: angles = [80, 100]
            elif lvl == 3: angles = [70, 90, 110]
            elif lvl == 4: angles = [60, 80, 100, 120]
            elif lvl == 5: angles = [50, 70, 90, 110, 130]
            else: angles = [0, 72, 144, 216, 288, 360] 
            for ang in angles: bullets_list.append(Bullet(self.x, self.y - 20, self.weapon_type, angle=ang, level=lvl))
                
        return True

class Enemy:
    def __init__(self, difficulty, is_asteroid=False, is_boss=False, is_meteor=False, stage=1):
        self.x = random.randint(30, WIDTH - 30); self.y = random.randint(-100, -40)
        self.speed = random.uniform(2, 5) * difficulty
        self.is_asteroid = is_asteroid; self.is_boss = is_boss; self.is_meteor = is_meteor 
        self.attack_cooldown = 60; self.stage = stage; self.dx = 0; self.shoot_timer = random.randint(60, 120) 
        
        self.target_y = random.randint(100, 250) 
        self.reached_target = False
        
        self.is_kamikaze = False
        if not is_boss and not is_asteroid and not is_meteor and stage >= 2:
            self.dx = random.choice([-2, -1.5, 1.5, 2]) * difficulty
            if random.random() < 0.3: self.is_kamikaze = True
        
        self.shield_hp = 0; self.max_shield = 0
        self.current_phase = 1
        self.is_burning = False 

        if is_boss:
            self.x = WIDTH // 2; self.y = -100; self.speed = 1.5; self.dx = 2.5 
            self.radius = 60; self.spiral_angle = 0 
            self.shield_rotation = 0 
            
            base_hp = 600 * difficulty
            if stage == 1: self.hp = base_hp
            elif stage == 2: self.hp = base_hp * 1.5 
            elif stage >= 3:
                self.hp = base_hp * 1.5 * 2 
                self.max_shield = self.hp / 3
                self.shield_hp = self.max_shield
            self.max_hp = self.hp
            
        elif is_asteroid:
            self.hp = 9999; self.radius = 20; self.angle = 0; self.spin_speed = random.uniform(-3, 3)
            self.offsets = [(math.cos(math.pi*2*i/8)*(self.radius+random.uniform(-6,6)), math.sin(math.pi*2*i/8)*(self.radius+random.uniform(-6,6))) for i in range(8)]
        elif is_meteor:
            self.radius = random.randint(30, 70) 
            self.hp = 150 * difficulty; 
            self.speed = random.uniform(3, 6); self.dx = random.uniform(-2, 2); self.angle = 0; self.spin_speed = random.uniform(-4, 4)
            self.offsets = [(math.cos(math.pi*2*i/6)*(self.radius+random.uniform(-5,5)), math.sin(math.pi*2*i/6)*(self.radius+random.uniform(-5,5))) for i in range(6)]
        else:
            self.hp = 30 * difficulty * (2 ** (stage - 1)); self.radius = 15
        self.max_hp = self.hp

    def update(self, player=None):
        if self.is_boss:
            if self.y < 150: self.y += self.speed
            else: 
                current_dx = self.dx * 2.0 if (self.stage >= 3 and self.hp / self.max_hp < 0.5) else self.dx
                self.x += current_dx
                if self.x < 100 or self.x > WIDTH - 100: self.dx *= -1
            self.shield_rotation += 5 
        elif self.is_asteroid or self.is_meteor:
            self.y += self.speed; self.x += self.dx; self.angle += self.spin_speed
        else:
            if getattr(self, 'is_kamikaze', False) and self.hp < self.max_hp * 0.4 and player:
                angle = math.atan2(player.y - self.y, player.x - self.x)
                self.x += math.cos(angle) * 15; self.y += math.sin(angle) * 15
            else:
                if not self.reached_target and self.y < self.target_y:
                    self.y += 15 
                else:
                    self.reached_target = True; self.y += 0.5; self.x += self.dx
                    if self.x < self.radius or self.x > WIDTH - self.radius: self.dx *= -1

    def draw(self, surface):
        if self.is_boss:
            if self.shield_hp > 0: 
                pulse = (math.sin(pygame.time.get_ticks() / 100.0) + 1) / 2 
                alpha = int(100 + 100 * pulse) 
                
                shield_color = (200, int(50 + 50 * pulse), 0, alpha) 
                bright_color = (255, int(150 + 100 * pulse), 100, 255)
                
                rad = self.radius + 20
                
                num_points = 12
                points = []
                for i in range(num_points * 2):
                    angle = math.radians(i * (360 / (num_points * 2)) + self.shield_rotation)
                    r = rad if i % 2 == 0 else rad - 10
                    px = self.x + math.cos(angle) * r
                    py = self.y + math.sin(angle) * r
                    points.append((px, py))
                
                temp_surf = pygame.Surface((rad*2+20, rad*2+20), pygame.SRCALPHA)
                local_points = [(p[0] - self.x + rad + 10, p[1] - self.y + rad + 10) for p in points]
                pygame.draw.polygon(temp_surf, shield_color, local_points)
                pygame.draw.polygon(temp_surf, bright_color, local_points, 3)
                surface.blit(temp_surf, (self.x - rad - 10, self.y - rad - 10))

                if random.random() < 0.3: 
                    arc_color = bright_color
                    num_arcs = 4
                    for _ in range(num_arcs):
                        start_angle = math.radians(random.randint(0, 360))
                        end_angle = start_angle + math.radians(random.randint(20, 90))
                        
                        arc_points = []
                        steps = 5
                        for step in range(steps + 1):
                            ang = start_angle + (end_angle - start_angle) * (step / steps)
                            r = random.randint(self.radius, rad - 5)
                            px = self.x + math.cos(ang) * r
                            py = self.y + math.sin(ang) * r
                            arc_points.append((px, py))
                        
                        pygame.draw.lines(surface, arc_color, False, arc_points, 2)
                
            if self.stage == 2:
                boss_img = get_cached_image('boss2', 'graphics/boss2.png', (170, 170))
            elif self.stage >= 3:
                boss_img = get_cached_image('boss3', 'graphics/boss3.png', (200, 200))
            else:
                boss_img = get_cached_image('boss', 'graphics/boss.png', (150, 150))
                
            if boss_img: 
                if self.stage >= 3 and self.hp / self.max_hp < 0.5 and pygame.time.get_ticks() % 200 < 100:
                    surface.blit(boss_img, boss_img.get_rect(center=(int(self.x), int(self.y))), special_flags=pygame.BLEND_RGB_ADD)
                else: surface.blit(boss_img, boss_img.get_rect(center=(int(self.x), int(self.y))))
            else: pygame.draw.circle(surface, NEON_MAGENTA, (int(self.x), int(self.y)), self.radius, 3)
            
            pygame.draw.rect(surface, NEON_RED, (self.x - 40, self.y - 60, 80, 6)); pygame.draw.rect(surface, NEON_GREEN, (self.x - 40, self.y - 60, 80 * (max(0, self.hp)/self.max_hp), 6))
            if self.shield_hp > 0:
                pygame.draw.rect(surface, (0, 50, 100), (self.x - 40, self.y - 52, 80, 4)); pygame.draw.rect(surface, (100, 200, 255), (self.x - 40, self.y - 52, 80 * (self.shield_hp/max(1, self.max_shield)), 4))
                
        elif self.is_asteroid:
            rotated_points = [(self.x + ox*math.cos(math.radians(self.angle)) - oy*math.sin(math.radians(self.angle)), self.y + ox*math.sin(math.radians(self.angle)) + oy*math.cos(math.radians(self.angle))) for ox, oy in self.offsets]
            pygame.draw.polygon(surface, (30, 20, 10), rotated_points); pygame.draw.polygon(surface, NEON_ORANGE, rotated_points, 2)
            
        elif self.is_meteor:
            meteor_img = get_cached_image('meteor', 'graphics/meteor.png', (int(self.radius*2.5), int(self.radius*2.5)))
            if meteor_img:
                rotated = pygame.transform.rotate(meteor_img, self.angle)
                surface.blit(rotated, rotated.get_rect(center=(int(self.x), int(self.y))))
            else:
                rotated_points = [(self.x + ox*math.cos(math.radians(self.angle)) - oy*math.sin(math.radians(self.angle)), self.y + ox*math.sin(math.radians(self.angle)) + oy*math.cos(math.radians(self.angle))) for ox, oy in self.offsets]
                pygame.draw.polygon(surface, (50, 40, 40), rotated_points); pygame.draw.polygon(surface, (150, 100, 50), rotated_points, 2)
            pygame.draw.rect(surface, NEON_RED, (self.x - 15, self.y - self.radius - 10, 30, 4)); pygame.draw.rect(surface, NEON_GREEN, (self.x - 15, self.y - self.radius - 10, 30 * (max(0, self.hp)/self.max_hp), 4))
            
        else:
            enemy_img = get_cached_image('enemy', 'graphics/enemy.png', (60, 60))
            if enemy_img: 
                if getattr(self, 'is_kamikaze', False) and self.hp < self.max_hp * 0.4:
                    surface.blit(enemy_img, enemy_img.get_rect(center=(int(self.x), int(self.y))), special_flags=pygame.BLEND_RGB_ADD)
                else: surface.blit(enemy_img, enemy_img.get_rect(center=(int(self.x), int(self.y))))
            else:
                points = [(self.x, self.y - self.radius), (self.x + self.radius + 5, self.y), (self.x, self.y + self.radius), (self.x - self.radius - 5, self.y)]
                pygame.draw.polygon(surface, (40, 10, 20), points); pygame.draw.polygon(surface, NEON_RED, points, 2)
            pygame.draw.rect(surface, NEON_RED, (self.x - 15, self.y - 25, 30, 4)); pygame.draw.rect(surface, NEON_GREEN, (self.x - 15, self.y - 25, 30 * (max(0, self.hp)/self.max_hp), 4))

class Bullet:
    def __init__(self, x, y, b_type, dx=0, angle=None, level=1):
        self.x = x; self.y = y; self.type = b_type; self.level = level
        self.timer = 0
        self.trail = [] 
        self.hit_enemies = [] 
        
        speed = 15 
        if b_type == 'plasma': speed = 25 
        elif b_type == 'laser': speed = 40 if level == 6 else 18 
        elif b_type == 'homing': speed = 12 
        elif b_type == 'drone_laser': speed = 35 
        
        if angle is not None:
            rad = math.radians(angle)
            self.dx = math.cos(rad) * speed; self.speed = math.sin(rad) * speed 
        else: self.dx = dx; self.speed = speed
        
        self.start_x = x; self.start_y = y
        self.target_angle = angle if angle else 90

    def update(self, enemies=None, particles=None): 
        self.timer += 1
        
        if self.type == 'homing':
            self.trail.append((self.x, self.y))
            max_trail = 8 if self.level == 6 else 5
            if len(self.trail) > max_trail: self.trail.pop(0)

            if self.level == 6 and self.timer < 12:
                radius = self.timer * 4
                current_angle = self.timer * 30 + self.target_angle
                self.x = self.start_x + math.cos(math.radians(current_angle)) * radius
                self.y = self.start_y - math.sin(math.radians(current_angle)) * radius
            else:
                if enemies and self.timer > 10: 
                    target = min(enemies, key=lambda e: math.hypot(e.x - self.x, e.y - self.y), default=None)
                    if target:
                        angle = math.atan2(target.y - self.y, target.x - self.x)
                        self.dx = math.cos(angle) * 16; self.speed = -math.sin(angle) * 16 
                        if particles is not None and random.random() < 0.2:
                            particles.append(Particle(self.x, self.y, HOMING_COLOR))
                self.x += self.dx; self.y -= self.speed
        else:
            self.y -= self.speed; self.x += self.dx

    def draw(self, surface):
        if self.type == 'plasma':
            if self.level == 6: 
                pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), 12)
                pygame.draw.circle(surface, PLASMA_COLOR, (int(self.x), int(self.y)), 18, 5)
                pygame.draw.circle(surface, (0, 50, 255), (int(self.x), int(self.y)), 24, 2)
                for _ in range(3):
                    ex = self.x + random.randint(-20, 20); ey = self.y + random.randint(-20, 20)
                    pygame.draw.line(surface, WHITE, (self.x, self.y), (ex, ey), 2)
            else:
                glow_radius = 12
                pygame.draw.circle(surface, (0, 100, 200), (int(self.x), int(self.y)), glow_radius)
                pygame.draw.circle(surface, PLASMA_COLOR, (int(self.x), int(self.y)), 8)
                pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)-2), 4)
                
                start_p = (self.x, self.y)
                trail_vec_x = -self.dx * 1.5
                trail_vec_y = self.speed * 1.5 
                end_p = (self.x + trail_vec_x, self.y + trail_vec_y)
                pygame.draw.line(surface, PLASMA_COLOR, start_p, end_p, 4)
                pygame.draw.line(surface, WHITE, start_p, end_p, 1) 
                
        elif self.type == 'laser':
            if self.level == 6: 
                beam_length = 1200
                w = 12 + math.sin(pygame.time.get_ticks() / 30) * 2 
                
                pygame.draw.rect(surface, (120, 0, 0), (self.x - w*2, self.y - beam_length, w*4, beam_length), border_radius=10)
                pygame.draw.rect(surface, LASER_COLOR, (self.x - w, self.y - beam_length, w*2, beam_length), border_radius=6)
                pygame.draw.rect(surface, WHITE, (self.x - w/3, self.y - beam_length, w*2/3, beam_length))
                
                for i in range(0, beam_length, 100):
                    offset = (pygame.time.get_ticks() / 2 + i) % beam_length
                    pygame.draw.ellipse(surface, WHITE, (self.x - w*2.5, self.y - offset - 10, w*5, 20), 2)
            else:
                w = 6 if self.level >= 3 else 4
                pygame.draw.rect(surface, (150, 0, 0), (self.x - w-2, self.y - 25, w*2+4, 45), border_radius=4)
                pygame.draw.rect(surface, LASER_COLOR, (self.x - w, self.y - 20, w*2, 40), border_radius=3)
                pygame.draw.rect(surface, WHITE, (self.x - w/3, self.y - 20, w*2/3, 40), border_radius=2)
                
        elif self.type == 'homing':
            if len(self.trail) > 2: 
                for i, (tx, ty) in enumerate(self.trail):
                    ratio = i / len(self.trail)
                    radius = int(ratio * (8 if self.level == 6 else 4))
                    color = (int(200 * ratio), 0, int(255 * ratio)) 
                    pygame.draw.circle(surface, color, (int(tx), int(ty)), radius)
            
            angle = math.atan2(-self.speed, self.dx)
            l = 16 if self.level == 6 else 12
            w = 6 if self.level == 6 else 4
            
            p1 = (self.x + math.cos(angle)*l, self.y + math.sin(angle)*l) 
            p2 = (self.x + math.cos(angle + 2.2)*w, self.y + math.sin(angle + 2.2)*w) 
            p3 = (self.x + math.cos(angle - 2.2)*w, self.y + math.sin(angle - 2.2)*w) 
            
            f1 = (self.x + math.cos(angle + 2.5)*(w+4), self.y + math.sin(angle + 2.5)*(w+4)) 
            f2 = (self.x + math.cos(angle - 2.5)*(w+4), self.y + math.sin(angle - 2.5)*(w+4)) 
            
            pygame.draw.polygon(surface, (100, 0, 150), [p1, f1, p2, p3, f2]) 
            pygame.draw.polygon(surface, HOMING_COLOR, [p1, p2, p3]) 
            pygame.draw.circle(surface, WHITE, (int(p1[0]), int(p1[1])), 2) 
            
        elif self.type == 'drone_laser':
            pygame.draw.rect(surface, (200, 80, 0), (self.x - 8, self.y - 120, 16, 120), border_radius=4)
            pygame.draw.rect(surface, NEON_ORANGE, (self.x - 4, self.y - 120, 8, 120), border_radius=2)
            pygame.draw.rect(surface, WHITE, (self.x - 2, self.y - 120, 4, 120))

class EnemyBullet:
    def __init__(self, x, y, angle, b_type='normal'):
        self.x = x; self.y = y; self.type = b_type
        self.speed = 6 if b_type in ['normal', 'blue_bullet'] else (5 if b_type == 'boss_homing' else 18) 
        self.dx = math.cos(math.radians(angle)) * self.speed; self.dy = math.sin(math.radians(angle)) * self.speed
        self.track_time = 45 
    def update(self): self.x += self.dx; self.y += self.dy
    def draw(self, surface):
        if self.type == 'normal': 
            pygame.draw.circle(surface, (150, 0, 0), (int(self.x), int(self.y)), 8); pygame.draw.circle(surface, NEON_RED, (int(self.x), int(self.y)), 5); pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), 2)
        elif self.type == 'blue_bullet':
            pygame.draw.circle(surface, (0, 100, 150), (int(self.x), int(self.y)), 10); pygame.draw.circle(surface, NEON_CYAN, (int(self.x), int(self.y)), 6); pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), 2)
        elif self.type == 'boss_homing':
            pygame.draw.circle(surface, (100, 0, 150), (int(self.x), int(self.y)), 12); pygame.draw.circle(surface, HOMING_COLOR, (int(self.x), int(self.y)), 8); pygame.draw.circle(surface, YELLOW, (int(self.x), int(self.y)), 3)
        elif self.type in ['laser', 'purple_laser']:
            color = (200, 50, 255) if self.type == 'purple_laser' else NEON_ORANGE
            pygame.draw.line(surface, color, (self.x, self.y), (self.x - self.dx*4, self.y - self.dy*4), 10); pygame.draw.line(surface, WHITE, (self.x, self.y), (self.x - self.dx*4, self.y - self.dy*4), 4)

class Item:
    def __init__(self, x, y, mode, forced_type=None):
        self.x = x; self.y = y; self.speed = 3
        if forced_type: self.type = forced_type
        else: self.type = random.choice(['heal', 'shield', 'upgrade_plasma'])
    def update(self): self.y += self.speed
    def draw(self, surface):
        box_rect = pygame.Rect(self.x - 12, self.y - 12, 24, 24); pygame.draw.rect(surface, (20, 25, 30), box_rect) 
        if self.type == 'upgrade_universal':
            pygame.draw.rect(surface, WHITE, box_rect, 2, border_radius=4); pygame.draw.circle(surface, PLASMA_COLOR, (int(self.x - 5), int(self.y + 4)), 4); pygame.draw.circle(surface, LASER_COLOR, (int(self.x), int(self.y - 4)), 4); pygame.draw.circle(surface, HOMING_COLOR, (int(self.x + 5), int(self.y + 4)), 4)
            return
        char = ""
        if self.type == 'heal': color, char = (0, 255, 0), "+"
        elif self.type == 'shield': color, char = (0, 255, 255), "S"
        elif self.type == 'upgrade_plasma': color, char = PLASMA_COLOR, "P" 
        elif self.type == 'upgrade_laser': color, char = LASER_COLOR, "L"
        elif self.type == 'upgrade_homing': color, char = HOMING_COLOR, "H"
        elif self.type == 'upgrade_drone': color, char = (255, 0, 255), "D"
        elif self.type == 'upgrade_burn': color, char = (255, 100, 0), "B" 
        
        pygame.draw.rect(surface, color, box_rect, 2, border_radius=4) 
        if self.type in ['upgrade_laser', 'upgrade_plasma', 'upgrade_homing']:
            points = [(self.x, self.y - 6), (self.x - 6, self.y + 2), (self.x + 6, self.y + 2)]; pygame.draw.polygon(surface, color, points); pygame.draw.rect(surface, color, (self.x - 2, self.y + 2, 4, 6))
        else:
            txt = pygame.font.SysFont("tahoma", 16, bold=True).render(char, True, color); surface.blit(txt, (self.x - txt.get_width()//2, self.y - txt.get_height()//2))

class NukeMissile:
    def __init__(self, x, y):
        self.x = x; self.y = y; self.target_x = WIDTH // 2; self.target_y = HEIGHT // 2; self.speed = 12; self.exploded = False
    def update(self):
        if math.hypot(self.target_x - self.x, self.target_y - self.y) < self.speed: self.exploded = True
        else:
            angle = math.atan2(self.target_y - self.y, self.target_x - self.x); self.x += math.cos(angle) * self.speed; self.y += math.sin(angle) * self.speed
    def draw(self, surface):
        # ==============================================================================
        # --- [ĐẠI PHẪU] MŨI TÊN LỬA SIÊU NHỌN (KHÍ ĐỘNG HỌC) ---
        # ==============================================================================
        missile_angle = math.atan2(self.target_y - self.y, self.target_x - self.x)
        m_len = 50 # Tăng chiều dài để trông thon hơn
        m_w = 14

        # Mũi nhọn đâm thẳng ra trước m_len pixels
        nose_tip = (self.x + math.cos(missile_angle) * m_len, 
                    self.y + math.sin(missile_angle) * m_len)
        
        # Thân trên (thu hẹp lại để tạo góc nhọn)
        p_r = (self.x + math.cos(missile_angle - math.pi*0.2) * (m_len*0.3), 
               self.y + math.sin(missile_angle - math.pi*0.2) * (m_len*0.3))
        p_l = (self.x + math.cos(missile_angle + math.pi*0.2) * (m_len*0.3), 
               self.y + math.sin(missile_angle + math.pi*0.2) * (m_len*0.3))
        
        # Đuôi
        back_r = (self.x + math.cos(missile_angle - math.pi*0.8) * (m_len*0.4), 
                  self.y + math.sin(missile_angle - math.pi*0.8) * (m_len*0.4))
        back_l = (self.x + math.cos(missile_angle + math.pi*0.8) * (m_len*0.4), 
                  self.y + math.sin(missile_angle + math.pi*0.8) * (m_len*0.4))
        
        missile_body = [nose_tip, p_r, back_r, back_l, p_l]

        temp_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
        local_poly_glow = [(p[0] - self.x + 60, p[1] - self.y + 60) for p in missile_body]
        alpha_glow = 100 + int(50 * math.sin(pygame.time.get_ticks() / 80.0))
        pygame.draw.polygon(temp_glow, (255, 100, 100, alpha_glow), local_poly_glow, 6) 
        surface.blit(temp_glow, (self.x - 60, self.y - 60))

        pygame.draw.polygon(surface, (50, 60, 70), missile_body)
        pygame.draw.polygon(surface, WHITE, missile_body, 1) 

        fin_poly = [
            (self.x + math.cos(missile_angle - math.pi*0.7) * (m_len*0.6), self.y + math.sin(missile_angle - math.pi*0.7) * (m_len*0.6)),
            (self.x + math.cos(missile_angle - math.pi) * (m_len*0.6), self.y + math.sin(missile_angle - math.pi) * (m_len*0.6)),
            back_r
        ]
        pygame.draw.polygon(surface, (255, 50, 50), fin_poly)
        fin_poly_l = [
            (self.x + math.cos(missile_angle + math.pi*0.7) * (m_len*0.6), self.y + math.sin(missile_angle + math.pi*0.7) * (m_len*0.6)),
            (self.x + math.cos(missile_angle + math.pi) * (m_len*0.6), self.y + math.sin(missile_angle + math.pi) * (m_len*0.6)),
            back_l
        ]
        pygame.draw.polygon(surface, (255, 50, 50), fin_poly_l)

        f_len = 20 + random.randint(0, 10)
        engine_base_center = (self.x + math.cos(missile_angle + math.pi) * (m_len*0.4), self.y + math.sin(missile_angle + math.pi) * (m_len*0.4))
        flame_tip = (engine_base_center[0] + math.cos(missile_angle + math.pi) * (f_len), engine_base_center[1] + math.sin(missile_angle + math.pi) * (f_len))
        
        flame_poly = [
            back_r,
            (self.x + math.cos(missile_angle + math.pi*1.05) * (m_len*0.3), self.y + math.sin(missile_angle + math.pi*1.05) * (m_len*0.3)), 
            flame_tip,
            (self.x + math.cos(missile_angle + math.pi*0.95) * (m_len*0.3), self.y + math.sin(missile_angle + math.pi*0.95) * (m_len*0.3)), 
            back_l
        ]
        pygame.draw.polygon(surface, (255, 100, 0), flame_poly)
        pygame.draw.polygon(surface, (255, 255, 0), flame_poly, 1)

        nuke_font = pygame.font.SysFont("Impact", 12)
        n_txt = nuke_font.render("[NUKE]", True, WHITE)
        n_txt_rot = pygame.transform.rotate(n_txt, -math.degrees(missile_angle))
        surface.blit(n_txt_rot, n_txt_rot.get_rect(center=(int(self.x), int(self.y))))

class Particle:
    def __init__(self, x, y, color):
        self.x = x; self.y = y; self.color = color; self.radius = random.uniform(2, 5)
        angle = random.uniform(0, math.pi * 2); speed = random.uniform(3, 8)
        self.dx = math.cos(angle) * speed; self.dy = math.sin(angle) * speed; self.life = 20
    def update(self): self.x += self.dx; self.y += self.dy; self.radius -= 0.2; self.life -= 1
    def draw(self, surface):
        if self.radius > 0: pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.radius))

class DamageNumber:
    def __init__(self, x, y, damage, is_crit=False):
        self.x = x + random.randint(-20, 20); self.y = y + random.randint(-10, 10); self.damage = int(damage); self.life = 30; self.max_life = 30; self.color = (255, 255, 0) if is_crit else (255, 255, 255)
    def update(self): self.y -= 2; self.life -= 1
    def draw(self, surface):
        if self.life > 0:
            txt = pygame.font.SysFont("Impact", 20, italic=True).render(f"-{self.damage}", True, self.color); txt.set_alpha(int((self.life / self.max_life) * 255)); surface.blit(txt, (self.x, self.y))


def get_drop_type(stage, wave):
    r = random.randint(1, 100)
    hp_c, sh_c, pw_c = 0, 0, 0
    if stage == 1:
        if wave == 1: hp_c, sh_c, pw_c = 10, 5, 20
        elif wave == 2: hp_c, sh_c, pw_c = 8, 4, 18
        elif wave == 3: hp_c, sh_c, pw_c = 7, 3, 15
        elif wave == 4: hp_c, sh_c, pw_c = 6, 3, 15
        else: hp_c, sh_c, pw_c = 5, 2, 12
    elif stage == 2:
        hp_c, sh_c, pw_c = 6, 3, 16
    else: 
        hp_c, sh_c, pw_c = 4, 2, 13
        
    if r <= hp_c: return 'heal'
    elif r <= hp_c + sh_c: return 'shield'
    elif r <= hp_c + sh_c + pw_c:
        return random.choice(['upgrade_plasma', 'upgrade_laser', 'upgrade_homing', 'upgrade_universal'])
    return None

def spawn_wave(stage, wave, difficulty, enemies_list):
    positions = []
    base_x = WIDTH // 2
    formation_y = 150 
    dx_val = 0
    
    if stage == 1:
        if wave == 1: positions = [(0,0), (-100,-80), (100,-80), (-200,-160), (200,-160)] 
        elif wave == 2: positions = [(x, 0) for x in range(-200, 201, 80)] 
        elif wave == 3: positions = [(0,0), (-80,-80), (80,-80), (0,-160), (-160,-160), (160,-160), (0,-240)] 
        elif wave == 4: positions = [(x, y) for x in [-120, -40, 40, 120] for y in [0, -80]]; dx_val = 2 
        else: positions = [(x, y) for x in range(-200, 201, 80) for y in [0, -80, -160]] 
    elif stage == 2:
        if wave in [1, 2]: positions = [(x, y) for x in range(-160, 161, 80) for y in [0, -80]]
        elif wave == 3: positions = [(0,0), (100,-100), (0,-200), (-100,-100), (160,-160), (-160,-160), (0, -260)] 
        elif wave in [4, 5]: positions = [(x, y) for x in [-160, -80, 0, 80, 160] for y in [0, -80, -160]]; dx_val = 3.5 
        elif wave == 6: positions = [(x, y) for x in [-80, 80] for y in [0, -80, -160, -240]] 
        else: positions = [(x, y) for x in range(-200, 201, 80) for y in [0, -80, -160, -240]] 
    else: 
        if wave in [1,2,3]: positions = [(x, y) for x in range(-160, 161, 80) for y in [0, -100, -200]]; dx_val = 2
        elif wave in [4,5,6]: positions = [(x, y) for x in range(-200, 201, 80) for y in [0, -80]]
        elif wave in [7,8]: positions = [(0,0), (120,-120), (0,-240), (-120,-120), (200,-200), (-200,-200), (0,-120)]
        elif wave == 9: positions = [(x, y) for x in range(-240, 241, 80) for y in [0, -80, -160, -240, -320]] 
        else: positions = [(x, y) for x in [-160, -80, 80, 160] for y in [0, -80]]
        
    for px, py in positions:
        e = Enemy(difficulty, stage=stage)
        e.x = max(30, min(WIDTH-30, base_x + px))
        e.y = -150 + (py * 1.5) - abs(px) 
        e.target_y = formation_y + py 
        if dx_val != 0: e.dx = dx_val * random.choice([-1, 1])
        enemies_list.append(e)