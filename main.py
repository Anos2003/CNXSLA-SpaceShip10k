import pygame
import cv2
import math
import random
import os
import json
import numpy as np
from settings import *
from vision import cap, hands, mp_draw, mp_hands, analyze_hand_gestures
from ui import draw_button, show_how_to_play, show_pause_menu, show_game_over, show_achievements
from entities import StarLayer, Star, Player, Enemy, Bullet, Item, EnemyBullet, ShootingStar, Particle, DamageNumber, NukeMissile, HOMING_COLOR, PLASMA_COLOR, LASER_COLOR, get_drop_type, spawn_wave

pygame.init()
pygame.mixer.init() 
pygame.mixer.set_num_channels(32)

current_w, current_h = WIDTH, HEIGHT
window = pygame.display.set_mode((current_w, current_h), pygame.RESIZABLE)
screen = pygame.Surface((WIDTH, HEIGHT)) 
is_fullscreen = False

pygame.display.set_caption("Spaceship 10k")
clock = pygame.time.Clock()

def get_font(size): return pygame.font.SysFont("tahoma", size, bold=True)

MENU_MUSIC_PATH = "audio/menu_music.mp3.mp3"
GAME_MUSIC_PATH = "audio/nhacnen.mp3" 

try:
    pygame.mixer.music.load(MENU_MUSIC_PATH)
    pygame.mixer.music.set_volume(0.4) 
    laser_sfx = pygame.mixer.Sound("audio/laser.wav.mp3")
    laser_sfx.set_volume(0.4) 
    explosion_sfx = pygame.mixer.Sound("audio/explosion.wav.mp3")
    explosion_sfx.set_volume(0.6) 
    audio_loaded = True
except: audio_loaded = False

def create_beep_sound(frequency=800, duration=0.05, volume=0.1):
    sample_rate = 44100
    n_samples = int(round(duration * sample_rate))
    buf = np.zeros((n_samples, 2), dtype=np.int16)
    max_sample = 2**(16 - 1) - 1
    for s in range(n_samples):
        t = float(s) / sample_rate
        val = int(round(math.sin(2 * math.pi * frequency * t) * max_sample * volume))
        buf[s][0] = val; buf[s][1] = val
    return pygame.sndarray.make_sound(buf)

beep_sound = create_beep_sound(800, 0.05, 0.1)
glitch_sound = create_beep_sound(300, 0.1, 0.2) 
radar_sound = create_beep_sound(1200, 0.2, 0.15) 

STATS_FILE = "stats.json"
def load_stats():
    d = {"CAMPAIGN": {"kills": 0, "boss_kills": 0, "score": 0}, "ENDLESS": {"kills": 0, "boss_kills": 0, "score": 0}, "INFERNO": {"kills": 0, "boss_kills": 0, "score": 0}}
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r") as f:
                s = json.load(f)
                for m in d:
                    if m not in s: s[m] = d[m]
                return s
        except: return d
    return d

def save_stats(stats):
    with open(STATS_FILE, "w") as f: json.dump(stats, f)

def load_highscore():
    if os.path.exists(SCORE_FILE):
        try: return int(open(SCORE_FILE, "r").read().strip())
        except: return 0
    return 0

def save_highscore(score): open(SCORE_FILE, "w").write(str(score))

try:
    background_space = pygame.image.load("graphics/background_space.png").convert()
    far_galaxy_img = pygame.image.load("graphics/far_galaxy.png").convert_alpha()
    nebula_layer_far_img = pygame.image.load("graphics/nebula_layer_far.png").convert_alpha()
    nebula_layer_near_img = pygame.image.load("graphics/nebula_layer_near.png").convert_alpha()
    try: nebula_bg_img = pygame.image.load("graphics/nebula_stage3.jpg").convert()
    except: nebula_bg_img = None
except: background_space, far_galaxy_img, nebula_layer_far_img, nebula_layer_near_img, nebula_bg_img = None, None, None, None, None

STAR_CONFIGS = [(200, (0.2, 0.6), (0.5, 1.2), [(100, 100, 100), (80, 80, 80)], 10), (100, (1.0, 2.5), (1.5, 2.0), [(150, 150, 150), (130, 130, 130)], 5), (50, (3.5, 5.0), (2.0, 2.5), [(255, 255, 255), (230, 230, 230)], 2)]

def handle_camera_logic(is_fullscreen, x_offset, current_w):
    ret, frame = cap.read()
    cam_surface = None; results = None
    if ret:
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)
        if results.multi_hand_landmarks: 
            mp_draw.draw_landmarks(rgb_frame, results.multi_hand_landmarks[0], mp_hands.HAND_CONNECTIONS)
        
        cam_w, cam_h = 320, 240
        if is_fullscreen or x_offset > 5: 
            if cv2.getWindowProperty("Camera Control", cv2.WND_PROP_VISIBLE) >= 1:
                cv2.destroyWindow("Camera Control")
            rgb_frame_resized = cv2.resize(rgb_frame, (cam_w, cam_h))
            cam_surface = pygame.image.frombuffer(rgb_frame_resized.tobytes(), (cam_w, cam_h), "RGB")
        else: cv2.imshow("Camera Control", cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR))
    return cam_surface, results

# ==============================================================================
# --- [NÂNG CẤP LỚN] HỆ THỐNG INTRO CUTSCENE (CHUẨN 10 BƯỚC) ---
# ==============================================================================
class Typewriter:
    def __init__(self, text, speed=40):
        self.text = text
        self.current_text = ""
        self.index = 0
        self.last_update = pygame.time.get_ticks()
        self.speed = speed  
        self.done = False
    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.speed and not self.done:
            self.current_text += self.text[self.index]
            self.index += 1
            self.last_update = now
            if self.text[self.index - 1] != " " and beep_sound:
                beep_sound.play()
            if self.index >= len(self.text): self.done = True

def glitch_text(text):
    chars = list(text)
    for i in range(len(chars)):
        if chars[i] != " " and random.random() < 0.2: # Tăng tỉ lệ nhiễu
            chars[i] = random.choice("!@#$%^&*()_+-=[]{}|;':,./<>?░▒▓█")
    return "".join(chars)

class CutsceneManager:
    def __init__(self, script):
        self.script = script
        self.current_index = 0
        self.typewriter = Typewriter(self.script[0]["text"], speed=40)
        self.wait_timer = 0
        self.is_finished = False
        self.radar_angle = 0
        self.fade_alpha = 255 # Bắt đầu bằng màn hình đen (Fade-in)
        self.fade_state = "FADE_IN" 
        self.radar_dots = []
        self.glitch_timer = 0

    def update(self, mouse_click=False):
        # 1. StartScene Init: Màn đen -> Fade in mượt mà
        if self.fade_state == "FADE_IN":
            self.fade_alpha -= 5
            if self.fade_alpha <= 0:
                self.fade_alpha = 0
                self.fade_state = "PLAYING"
            return
            
        # 10. Transition: Màn hình mờ dần (Fade out)
        if self.fade_state == "FADE_OUT":
            self.fade_alpha += 5
            if self.fade_alpha >= 255: 
                self.is_finished = True
            return
            
        # 9. Interaction: Tua nhanh bằng chuột
        if mouse_click:
            if not self.typewriter.done:
                self.typewriter.current_text = self.typewriter.text
                self.typewriter.index = len(self.typewriter.text)
                self.typewriter.done = True
            else:
                self.next_line()
                
        # 3. Text System: Typewriter update
        self.typewriter.update()
        
        # 5. Radar Background: Quét tia liên tục
        self.radar_angle += 0.05
        for dot in self.radar_dots:
            dot[1] += dot[2] 
            
        # 4. Glitch Effect: Quản lý thời gian nhiễu
        current_line = self.script[self.current_index] if self.current_index < len(self.script) else {}
        if current_line.get("effect") == "glitch":
            if random.random() < 0.2: self.glitch_timer = 5 # frames
        if self.glitch_timer > 0: self.glitch_timer -= 1
            
        # 7. Animation Flow: Tự động nhảy thoại sau Delay
        if self.typewriter.done:
            self.wait_timer += 1
            if self.current_index < len(self.script):
                delay_frames = self.script[self.current_index].get("delay", 1) * 60
                if self.wait_timer > delay_frames:
                    self.next_line()
            else:
                self.fade_state = "FADE_OUT"
                
    def next_line(self):
        self.current_index += 1
        self.wait_timer = 0
        if self.current_index < len(self.script):
            line = self.script[self.current_index]
            self.typewriter = Typewriter(line["text"], speed=40)
            
            # 6. Sound System
            if line.get("sound") == "radar" and radar_sound: radar_sound.play()
            if line.get("effect") == "glitch" and glitch_sound: glitch_sound.play()
                
            # Địch xuất hiện đúng timeline kịch bản
            if self.current_index == 3: 
                self.radar_dots.clear()
                for _ in range(15): 
                    x = WIDTH // 2 - 150 + random.randint(0, 300)
                    y = HEIGHT // 2 - 200 - random.randint(0, 200) 
                    speed = random.uniform(1.0, 2.5)
                    self.radar_dots.append([x, y, speed])
        else: 
            self.fade_state = "FADE_OUT"
        
    def draw(self, surface):
        surface.fill((5, 10, 15)) 
        
        # --- 5. Tích hợp Radar System ---
        radar_cx, radar_cy = WIDTH // 2, HEIGHT // 2 - 100
        radar_radius = 150
        
        # Vẽ tia quét (Sweep Cone) với Alpha
        sweep_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        points = [(radar_cx, radar_cy)]
        for i in range(30):
            ang = self.radar_angle - math.radians(i * 2)
            alpha = 255 - (i * 8)
            px = radar_cx + radar_radius * math.cos(ang)
            py = radar_cy + radar_radius * math.sin(ang)
            points.append((px, py))
        pygame.draw.polygon(sweep_surf, (0, 255, 0, 30), points)
        surface.blit(sweep_surf, (0,0))
        
        # Khung Radar
        pygame.draw.circle(surface, (0, 50, 0), (radar_cx, radar_cy), radar_radius, 0)
        pygame.draw.circle(surface, (0, 200, 0), (radar_cx, radar_cy), radar_radius, 2)
        pygame.draw.circle(surface, (0, 100, 0), (radar_cx, radar_cy), radar_radius * 2 // 3, 1)
        pygame.draw.circle(surface, (0, 100, 0), (radar_cx, radar_cy), radar_radius // 3, 1)
        pygame.draw.line(surface, (0, 100, 0), (radar_cx - radar_radius, radar_cy), (radar_cx + radar_radius, radar_cy), 1)
        pygame.draw.line(surface, (0, 100, 0), (radar_cx, radar_cy - radar_radius), (radar_cx, radar_cy + radar_radius), 1)
        
        end_x = radar_cx + radar_radius * math.cos(self.radar_angle)
        end_y = radar_cy + radar_radius * math.sin(self.radar_angle)
        pygame.draw.line(surface, (0, 255, 0), (radar_cx, radar_cy), (end_x, end_y), 3)
        
        # Chấm Enemy nhấp nháy khi bị tia quét qua
        for dot in self.radar_dots:
            dist = math.hypot(dot[0] - radar_cx, dot[1] - radar_cy)
            if dist < radar_radius - 2:
                dot_angle = math.atan2(dot[1] - radar_cy, dot[0] - radar_cx)
                if dot_angle < 0: dot_angle += 2*math.pi
                sweep_angle = self.radar_angle % (2*math.pi)
                
                # Nổi bật chấm đỏ khi tia quét chạm tới
                if abs(sweep_angle - dot_angle) < 0.2:
                    pygame.draw.circle(surface, (255, 255, 255), (int(dot[0]), int(dot[1])), 6)
                pygame.draw.circle(surface, (255, 0, 0), (int(dot[0]), int(dot[1])), 4)
                
        # --- 2. HUD/UI Sci-fi Panel ---
        box_w, box_h = 600, 150
        box_x = WIDTH // 2 - box_w // 2
        box_y = HEIGHT - 200
        
        pygame.draw.rect(surface, (10, 20, 20), (box_x, box_y, box_w, box_h))
        pygame.draw.rect(surface, (0, 255, 255), (box_x, box_y, box_w, box_h), 2)
        # Góc bo mạch sci-fi
        pygame.draw.line(surface, WHITE, (box_x, box_y), (box_x+20, box_y), 4)
        pygame.draw.line(surface, WHITE, (box_x, box_y), (box_x, box_y+20), 4)
        
        # Scanlines ngang tạo chiều sâu
        for i in range(0, box_h, 4): pygame.draw.line(surface, (0, 50, 50), (box_x, box_y + i), (box_x + box_w, box_y + i), 1)
        
        # --- KẾT HỢP GLITCH & TEXT SYSTEM ---
        if self.current_index < len(self.script):
            line = self.script[self.current_index]
            speaker = line.get("speaker", "")
            speaker_color = (0, 255, 255) if speaker == "KX-17" else (255, 50, 50)
            surface.blit(get_font(24).render(speaker, True, speaker_color), (box_x + 20, box_y + 15))
            
            display_text = self.typewriter.current_text
            text_color = (0, 255, 0) if speaker == "KX-17" else (255, 100, 100)
            
            if self.glitch_timer > 0:
                display_text = glitch_text(display_text)
                # Chromatic Aberration: Tách RGB tạo độ nhiễu cực mạnh
                surf_r = get_font(20).render(display_text, True, (255,0,0))
                surf_b = get_font(20).render(display_text, True, (0,255,255))
                rx = random.randint(-3, 3); ry = random.randint(-3, 3)
                surface.blit(surf_r, (box_x + 20 + rx, box_y + 60 + ry))
                surface.blit(surf_b, (box_x + 20 - rx, box_y + 60 - ry))
            else:
                surface.blit(get_font(20).render(display_text, True, text_color), (box_x + 20, box_y + 60))
            
        # Draw Fade (màn hình đen đè lên với độ mờ tương ứng)
        if self.fade_alpha > 0:
            fade_surf = pygame.Surface((WIDTH, HEIGHT)); fade_surf.fill((0, 0, 0)); fade_surf.set_alpha(self.fade_alpha)
            surface.blit(fade_surf, (0, 0))

def main():
    global window, current_w, current_h, is_fullscreen 
    
    state = "MENU"
    game_mode = None
    
    player = Player()
    star_layers = [StarLayer(*config) for config in STAR_CONFIGS]
    enemies, bullets, items, enemy_bullets, nukes = [], [], [], [], []
    particles, damage_numbers, shooting_stars = [], [], []
    
    difficulty = 1.0; spawn_timer = 0; highscore = load_highscore(); game_stats = load_stats()
    session_kills = 0; session_boss_kills = 0
    boss_spawned = False; flash_timer = 0; screen_shake = 0 
    current_stage = 1; stage_intro_timer = 0; stage_clear_timer = 0 
    stage_timer = 0; survival_time = 0; last_boss_spawn_time = 0
    
    current_wave = 0; current_music = "NONE"; show_modes = False 
    cutscene_manager = None
    
    try: title_font = pygame.font.SysFont("Impact", 100)
    except: title_font = pygame.font.SysFont("Arial", 100, bold=True)
    title_text = "SPACESHIP 10K"

    running = True
    while running:
        mouse_click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: mouse_click = True
            
            if event.type == pygame.VIDEORESIZE and not is_fullscreen:
                current_w, current_h = event.w, event.h
                window = pygame.display.set_mode((current_w, current_h), pygame.RESIZABLE)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and state == "CUTSCENE":
                    cutscene_manager.fade_state = "OUT"; cutscene_manager.fade_alpha = 255
                    
                if event.key == pygame.K_ESCAPE:
                    if state == "PLAYING": state = "PAUSED"
                    elif state == "PAUSED": state = "PLAYING"
                    elif state in ["HOW_TO_PLAY", "ACHIEVEMENTS"]: state = "MENU"
                
                if event.key == pygame.K_F11:
                    is_fullscreen = not is_fullscreen
                    if is_fullscreen:
                        info = pygame.display.Info()
                        current_w, current_h = info.current_w, info.current_h
                        window = pygame.display.set_mode((current_w, current_h), pygame.FULLSCREEN)
                    else:
                        current_w, current_h = WIDTH, HEIGHT
                        window = pygame.display.set_mode((current_w, current_h), pygame.RESIZABLE)
                        if cv2.getWindowProperty("Camera Control", cv2.WND_PROP_VISIBLE) >= 1: cv2.destroyWindow("Camera Control")

        raw_mouse_x, raw_mouse_y = pygame.mouse.get_pos()
        scale = min(current_w / float(WIDTH), current_h / float(HEIGHT))
        new_w = int(WIDTH * scale); new_h = int(HEIGHT * scale)
        x_offset = (current_w - new_w) // 2; y_offset = (current_h - new_h) // 2
        mouse_pos = (int((raw_mouse_x - x_offset) / scale), int((raw_mouse_y - y_offset) / scale))

        if audio_loaded:
            target_music = "MENU" if state in ["MENU", "CUTSCENE"] else ("GAME" if state == "PLAYING" and game_mode in ["CAMPAIGN", "ENDLESS"] else "NONE")
            if target_music != current_music:
                pygame.mixer.music.stop()
                if target_music == "MENU":
                    try: pygame.mixer.music.load(MENU_MUSIC_PATH); pygame.mixer.music.play(-1)
                    except: pass
                elif target_music == "GAME":
                    try: pygame.mixer.music.load(GAME_MUSIC_PATH); pygame.mixer.music.play(-1)
                    except: pass
                current_music = target_music

        cam_surface, results = handle_camera_logic(is_fullscreen, x_offset, current_w)
        screen.fill((0, 0, 0)) 
        
        if background_space and state not in ["MENU", "CUTSCENE"]:
             current_bg = nebula_bg_img if (game_mode == "CAMPAIGN" and current_stage == 3 and nebula_bg_img) else background_space
             screen.blit(current_bg, (0, 0))
             if far_galaxy_img: screen.blit(far_galaxy_img, (0, 0))
        
        if state != "CUTSCENE":
            for layer in star_layers: 
                layer.update()
                if game_mode == "INFERNO" and state != "MENU":
                    for s in layer.stars: pygame.draw.circle(screen, random.choice([(255, 0, 0), (255, 100, 0), (255, 255, 0)]), (int(s[0]), int(s[1])), int(s[3]))
                else: layer.draw(screen)
                    
            if background_space and state != "MENU":
                 if nebula_layer_far_img: screen.blit(nebula_layer_far_img, (0, 0))
                 if nebula_layer_near_img: screen.blit(nebula_layer_near_img, (0, 0))

        if state == "MENU":
            time_now = pygame.time.get_ticks()
            for i in range(0, WIDTH, 50): pygame.draw.line(screen, (15, 20, 30), (i, 0), (i, HEIGHT))
            for i in range(0, HEIGHT, 50): pygame.draw.line(screen, (15, 20, 30), (0, i), (WIDTH, i))

            if random.random() < 0.02: shooting_stars.append(ShootingStar())
            for ss in shooting_stars[:]:
                ss.update(); ss.draw(screen)
                if ss.y > HEIGHT or ss.x < -100 or ss.x > WIDTH + 100: shooting_stars.remove(ss)

            pygame.draw.line(screen, (0, 40, 40), (0, (time_now // 2) % HEIGHT), (WIDTH, (time_now // 2) % HEIGHT), 3)
            
            title_w, title_h = title_font.size(title_text)
            title_x = WIDTH//2 - title_w//2
            title_y = 90
            
            shadow_surf = title_font.render(title_text, True, (0, 40, 40))
            screen.blit(shadow_surf, (title_x + 6, title_y + 6))
            
            pulse = (math.sin(time_now / 150.0) + 1) / 2 
            glow_intensity = int(100 + 155 * pulse) 
            glow_color = (0, int(glow_intensity*0.8), glow_intensity) 
            
            glow_surf = title_font.render(title_text, True, glow_color)
            for ox, oy in [(-3,0), (3,0), (0,-3), (0,3), (-2,-2), (2,2), (-2,2), (2,-2)]:
                screen.blit(glow_surf, (title_x + ox, title_y + oy))
                
            core_color = (200, 255, 255) if pulse > 0.5 else (150, 255, 255)
            core_surf = title_font.render(title_text, True, core_color)
            screen.blit(core_surf, (title_x, title_y))

            screen.blit(get_font(20).render(f"KỶ LỤC CAO NHẤT: {highscore}", True, (255, 255, 0)), (WIDTH//2 - get_font(20).size(f"KỶ LỤC CAO NHẤT: {highscore}")[0]//2, 210))

            menu_items = []
            arrow_state = "up" if show_modes else "down"
            
            menu_items.append(("CÁC CHẾ ĐỘ CHƠI", (100, 150, 255), "TOGGLE_MODES", "main", arrow_state))
            if show_modes:
                menu_items.append(("CHẾ ĐỘ VƯỢT ẢI", (0, 255, 255), "CAMPAIGN", "sub", None))
                menu_items.append(("CHẾ ĐỘ VÔ TẬN", (255, 255, 0), "ENDLESS", "sub", None))
                menu_items.append(("CHẾ ĐỘ HỎA NGỤC", (255, 100, 0), "INFERNO", "sub", None))
                
            menu_items.extend([
                ("THÀNH TỰU", (255, 0, 255), "ACHIEVEMENTS", "main", None),
                ("HƯỚNG DẪN CHƠI", (0, 255, 0), "HOW_TO_PLAY", "main", None),
                ("THOÁT GAME", (128, 128, 128), "EXIT", "main", None)
            ])

            current_y = 250
            base_x = WIDTH // 2 - 340 // 2 

            for text, color, mode, m_type, arrow in menu_items:
                if m_type == "main": w, h, f_size, spacing, draw_x = 340, 50, 24, 15, base_x
                else: w, h, f_size, spacing, draw_x = 280, 40, 18, 10, base_x + 30

                rect = pygame.Rect(draw_x, current_y, w, h)
                is_hover = rect.collidepoint(mouse_pos)
                
                draw_button(screen, text, draw_x, current_y, w, h, color, is_hover, arrow=arrow, font_size=f_size)

                if is_hover and mouse_click:
                    if mode == "EXIT": running = False
                    elif mode == "HOW_TO_PLAY": state = "HOW_TO_PLAY"
                    elif mode == "ACHIEVEMENTS": state = "ACHIEVEMENTS"
                    elif mode == "TOGGLE_MODES": show_modes = not show_modes
                    else:
                        game_mode = mode; 
                        player = Player()
                        enemies.clear(); bullets.clear(); items.clear(); enemy_bullets.clear(); particles.clear(); nukes.clear()
                        difficulty = 1.0 if mode != 'INFERNO' else 1.5
                        session_kills = 0; session_boss_kills = 0
                        boss_spawned = False; current_stage = 1; survival_time = 0; last_boss_spawn_time = 0; stage_timer = 0
                        current_wave = 0 
                        
                        if game_mode == "CAMPAIGN":
                            state = "CUTSCENE"
                            script = [
                                {"speaker": "KX-17", "text": "KX-17 gọi tàu mẹ... lặp lại...", "delay": 1.5},
                                {"speaker": "SYSTEM", "text": "---tín hiệu--- mất --- kết nối---", "effect": "glitch", "delay": 1.5},
                                {"speaker": "KX-17", "text": "Chết tiệt... mất liên lạc hoàn toàn.", "delay": 1.5},
                                {"speaker": "SYSTEM", "text": "Cảnh báo: Phát hiện nhiều mục tiêu.", "sound": "radar", "delay": 1.5},
                                {"speaker": "KX-17", "text": "...Bị lộ rồi.", "delay": 1},
                                {"speaker": "SYSTEM", "text": "Kẻ địch đang tiếp cận.", "delay": 1},
                                {"speaker": "KX-17", "text": "Không còn đường lui... chiến thôi.", "delay": 2}
                            ]
                            cutscene_manager = CutsceneManager(script)
                        else:
                            state = "PLAYING"
                
                current_y += h + spacing

        elif state == "HOW_TO_PLAY": state = show_how_to_play(screen, mouse_click)
        elif state == "ACHIEVEMENTS": state = show_achievements(screen, game_stats, mouse_click)

        elif state == "CUTSCENE":
            if cutscene_manager:
                cutscene_manager.update(mouse_click)
                cutscene_manager.draw(screen)
                
                font_small = get_font(14)
                screen.blit(font_small.render("CLICK HOẶC [SPACE] ĐỂ TUA", True, (128,128,128)), (10, 10))
                
                if cutscene_manager.is_finished:
                    state = "PLAYING"
                    stage_intro_timer = 60

        elif state in ["PLAYING", "GAME_OVER", "VICTORY", "PAUSED"]:
            shoot_laser, shoot_missile = False, False

            if results and results.multi_hand_landmarks and state == "PLAYING":
                wrist_x, wrist_y, is_laser, is_missile = analyze_hand_gestures(results.multi_hand_landmarks[0])
                player.x += (wrist_x * WIDTH - player.x) * 0.15; player.y += (wrist_y * HEIGHT - player.y) * 0.15
                player.x = max(20, min(WIDTH - 20, player.x)); player.y = max(50, min(HEIGHT - 50, player.y))
                shoot_laser = is_laser
                if is_missile and player.rage >= player.max_rage: shoot_missile = True; player.rage = 0 

            if state == "PLAYING":
                dt = 1/60.0
                survival_time += dt; stage_timer += dt

                if stage_clear_timer > 0:
                    stage_clear_timer -= 1
                    if stage_clear_timer <= 0:
                        current_stage += 1; stage_timer = 0
                        boss_spawned = False; stage_intro_timer = 60; current_wave = 0
                        bullets.clear(); enemy_bullets.clear()

                if game_mode == "CAMPAIGN" and stage_intro_timer > 0:
                    stage_intro_timer -= 1
                    st_txt = get_font(60).render(f"STAGE {current_stage}", True, (0, 255, 255))
                    screen.blit(st_txt, (WIDTH//2 - st_txt.get_width()//2, HEIGHT//2 - 50))
                    player.laser_cooldown -= 1
                    for i in items: i.draw(screen)
                    player.draw(screen)
                    
                    scaled_screen = pygame.transform.scale(screen, (new_w, new_h))
                    window.fill((0, 0, 0))
                    window.blit(scaled_screen, (x_offset, y_offset))
                    if cam_surface: window.blit(cam_surface, (current_w - 320, 0))
                    pygame.display.flip(); clock.tick(60)
                    continue

                if player.invincible_timer > 0: player.invincible_timer -= 1
                if player.shield_timer > 0: player.shield_timer -= 1; player.shield_active = True
                else: player.shield_active = False

                if shoot_laser:
                    if player.shoot(bullets):
                        if audio_loaded: laser_sfx.play()

                if player.has_drone and player.drone_cooldown <= 0:
                    bullets.append(Bullet(player.x + 55, player.y + 5, 'drone_laser'))
                    player.drone_cooldown = 60
                if player.drone_cooldown > 0: player.drone_cooldown -= 1
                
                if shoot_missile: nukes.append(NukeMissile(player.x, player.y))

                for nuke in nukes[:]:
                    nuke.update(); nuke.draw(screen)
                    
                    # Tạo Particle kéo đuôi cho Nuke (Trong main.py)
                    if random.random() < 0.4:
                        missile_angle = math.atan2(nuke.target_y - nuke.y, nuke.target_x - nuke.x)
                        spawn_x = nuke.x + math.cos(missile_angle + math.pi) * 20
                        spawn_y = nuke.y + math.sin(missile_angle + math.pi) * 20
                        p_color = random.choice([(255, 0, 0), (255, 100, 0), (100, 200, 255)])
                        p = Particle(spawn_x, spawn_y, p_color)
                        p.dx *= 0.2; p.dy *= 0.2
                        particles.append(p)
                        
                    if nuke.exploded:
                        flash_timer = 6; screen_shake = 25
                        if audio_loaded: explosion_sfx.play()
                        for _ in range(50): particles.append(Particle(WIDTH//2, HEIGHT//2, (255, 0, 0)))
                        for e in enemies[:]:
                            if getattr(e, 'is_meteor', False):
                                e.hp -= 20
                                if e.hp <= 0:
                                    if random.random() < 0.05: items.append(Item(e.x, e.y, game_mode))
                                    enemies.remove(e)
                            elif not e.is_asteroid:
                                if e.is_boss: e.shield_hp = 0; e.hp -= 20; damage_numbers.append(DamageNumber(e.x, e.y, 20, is_crit=True))
                                else:
                                    e.hp -= 20
                                    if e.hp <= 0:
                                        player.score += 10; session_kills += 1
                                        if game_mode == "CAMPAIGN":
                                            drop_type = get_drop_type(current_stage, current_wave)
                                            if drop_type: items.append(Item(e.x, e.y, game_mode, forced_type=drop_type))
                                        else:
                                            if random.random() < 0.45: items.append(Item(e.x, e.y, game_mode))
                                        enemies.remove(e)
                        nukes.remove(nuke)

                player.laser_cooldown -= 1
                
                if game_mode == "CAMPAIGN":
                    max_waves = {1: 5, 2: 7, 3: 10}
                    current_max = max_waves.get(current_stage, 10)
                    
                    if not boss_spawned and stage_clear_timer <= 0:
                        active_enemies = [e for e in enemies if not getattr(e, 'is_meteor', False) and not e.is_boss]
                        
                        if len(active_enemies) == 0:
                            spawn_timer += 1
                            if spawn_timer > 60: 
                                current_wave += 1
                                spawn_timer = 0
                                
                                if current_wave > current_max:
                                    enemies.append(Enemy(difficulty, is_boss=True, stage=current_stage))
                                    boss_spawned = True
                                    if current_stage == 3: spawn_wave(current_stage, 10, difficulty, enemies)
                                else:
                                    spawn_wave(current_stage, current_wave, difficulty, enemies)
                                    
                        if current_stage == 3 and random.random() < 0.015:
                            enemies.append(Enemy(difficulty, is_meteor=True, stage=3))
                            
                elif game_mode == "ENDLESS":
                    difficulty = 1.0 + (survival_time / 60.0); spawn_timer += 1
                    if spawn_timer > max(20, 60 / difficulty): enemies.append(Enemy(difficulty, stage=current_stage)); spawn_timer = 0
                    if survival_time - last_boss_spawn_time >= 60:
                        current_stage += 1; enemies.append(Enemy(difficulty, is_boss=True, stage=min(3, current_stage)))
                        last_boss_spawn_time = survival_time
                elif game_mode == "INFERNO":
                    difficulty = 2.0 + (survival_time / 30.0); spawn_timer += 1
                    if spawn_timer > 45 / difficulty: enemies.append(Enemy(difficulty, stage=current_stage)); spawn_timer = 0
                    if survival_time - last_boss_spawn_time >= 45:
                        current_stage = 3; enemies.append(Enemy(difficulty * 1.5, is_boss=True, stage=3))
                        last_boss_spawn_time = survival_time

                for b in bullets[:]:
                    is_hit = False
                    
                    if b.type == 'drone_laser':
                        for e in enemies:
                            if abs(b.x - e.x) < e.radius + 6 and (b.y - 120) < e.y + e.radius and b.y > e.y - e.radius:
                                is_hit = True
                                if not e.is_asteroid: 
                                    if player.burn_unlocked: e.is_burning = True
                                    if e.is_boss: damage_numbers.append(DamageNumber(e.x, e.y, 2, is_crit=False))
                                    if hasattr(e, 'shield_hp') and e.shield_hp > 0:
                                        e.shield_hp -= 2
                                        if e.shield_hp < 0: e.hp += e.shield_hp; e.shield_hp = 0
                                    else: e.hp -= 2
                                    for _ in range(3): particles.append(Particle(e.x, e.y, (255, 0, 0)))
                                    
                    elif b.type == 'laser' and getattr(b, 'level', 1) == 6:
                        for e in enemies:
                            if e not in getattr(b, 'hit_enemies', []): 
                                if abs(b.x - e.x) < e.radius + 30 and e.y < b.y + e.radius:
                                    if not hasattr(b, 'hit_enemies'): b.hit_enemies = []
                                    b.hit_enemies.append(e) 
                                    is_hit = True
                                    
                                    if not e.is_asteroid:
                                        if player.burn_unlocked: e.is_burning = True
                                        
                                        damage = min(200, 15 + player.bonus_damage)
                                        if e.is_boss: damage_numbers.append(DamageNumber(e.x, e.y, damage, is_crit=True))
                                        
                                        if hasattr(e, 'shield_hp') and e.shield_hp > 0:
                                            e.shield_hp -= damage
                                            if e.shield_hp < 0: e.hp += e.shield_hp; e.shield_hp = 0
                                        else:
                                            prev_hp = e.hp; e.hp -= damage
                                            if e.is_boss and e.hp > 0:
                                                if int((prev_hp / e.max_hp) * 10) > int((e.hp / e.max_hp) * 10): 
                                                    if random.random() < 0.25: items.append(Item(e.x, e.y, game_mode))
                                        
                                        player.rage = min(player.rage + 5, player.max_rage)
                                        for _ in range(8): particles.append(Particle(e.x, e.y, (255, 0, 0)))
                    else:
                        for e in enemies:
                            if math.hypot(b.x - e.x, b.y - e.y) < e.radius + 5:
                                is_hit = True
                                if b in bullets: bullets.remove(b) 
                                if not e.is_asteroid: 
                                    if player.burn_unlocked: e.is_burning = True
                                    
                                    base_dmg = 4 if b.type == 'homing' else (10 if b.type == 'laser' else 6)
                                    damage = min(50, base_dmg + player.bonus_damage)
                                    
                                    if e.is_boss: damage_numbers.append(DamageNumber(e.x, e.y, damage, is_crit=(b.type=='plasma')))

                                    if hasattr(e, 'shield_hp') and e.shield_hp > 0:
                                        e.shield_hp -= damage
                                        if e.shield_hp < 0: e.hp += e.shield_hp; e.shield_hp = 0
                                    else:
                                        prev_hp = e.hp; e.hp -= damage
                                        if e.is_boss and e.hp > 0:
                                            if int((prev_hp / e.max_hp) * 10) > int((e.hp / e.max_hp) * 10): 
                                                if random.random() < 0.25: items.append(Item(e.x, e.y, game_mode))
                                                
                                    player.rage = min(player.rage + 5, player.max_rage)
                                    for _ in range(5): particles.append(Particle(e.x, e.y, (0, 255, 255)))
                                break 
                                
                    b.update(enemies, particles) 
                    if b.y < -150 or b.x < 0 or b.x > WIDTH or b.y > HEIGHT + 150: 
                        if b in bullets: bullets.remove(b)

                for eb in enemy_bullets[:]:
                    if eb.type == 'boss_homing':
                        if hasattr(eb, 'track_time') and eb.track_time > 0:
                            angle = math.atan2(player.y - eb.y, player.x - eb.x)
                            eb.dx = math.cos(angle) * eb.speed; eb.dy = math.sin(angle) * eb.speed
                            eb.track_time -= 1
                    eb.update()
                    if eb.y > HEIGHT or eb.x < 0 or eb.x > WIDTH: 
                        if eb in enemy_bullets: enemy_bullets.remove(eb)
                        continue
                        
                    if math.hypot(player.x - eb.x, player.y - eb.y) < 15:
                        if player.shield_active:
                            if eb in enemy_bullets: enemy_bullets.remove(eb)
                            for _ in range(3): particles.append(Particle(eb.x, eb.y, (0, 255, 255)))
                        elif player.invincible_timer <= 0:
                            if eb in enemy_bullets: enemy_bullets.remove(eb)
                            player.hp -= 15 if eb.type == 'normal' else 25
                            screen_shake = 10 
                            if player.hp <= 0: 
                                if player.lives > 1:
                                    player.lives -= 1; player.hp = player.max_hp; player.invincible_timer = 180
                                    if audio_loaded: explosion_sfx.play()
                                else: player.lives = 0; state = "GAME_OVER"

                for e in enemies[:]:
                    e.update(player)
                    
                    if getattr(e, 'is_burning', False):
                        e.hp -= 1.5 / 60.0 
                        if random.random() < 0.1: 
                            particles.append(Particle(e.x + random.randint(-15,15), e.y + random.randint(-15,15), (255, 100, 0)))
                            
                    if e.y > HEIGHT: enemies.remove(e); continue

                    if not e.is_boss and not e.is_asteroid and not getattr(e, 'is_meteor', False):
                        e.shoot_timer -= 1
                        if e.shoot_timer <= 0:
                            aim_angle = math.degrees(math.atan2(player.y - e.y, player.x - e.x))
                            if game_mode == "INFERNO":
                                enemy_bullets.append(EnemyBullet(e.x, e.y, aim_angle - 15, 'blue_bullet'))
                                enemy_bullets.append(EnemyBullet(e.x, e.y, aim_angle, 'normal'))
                                enemy_bullets.append(EnemyBullet(e.x, e.y, aim_angle + 15, 'blue_bullet'))
                                e.shoot_timer = random.randint(40, 80)
                            else:
                                if current_stage == 2 and current_wave == 6:
                                    enemy_bullets.append(EnemyBullet(e.x, e.y, aim_angle, 'blue_bullet'))
                                elif current_stage == 3 and current_wave in [4,5,6]:
                                    for off in [-15, 0, 15]: enemy_bullets.append(EnemyBullet(e.x, e.y, aim_angle+off, 'normal'))
                                elif current_stage == 3 and current_wave in [7,8]:
                                    enemy_bullets.append(EnemyBullet(e.x, e.y, aim_angle, 'blue_bullet'))
                                else:
                                    enemy_bullets.append(EnemyBullet(e.x, e.y, aim_angle, 'normal'))
                                e.shoot_timer = random.randint(80, 150)

                    if e.is_boss:
                        hp_ratio = e.hp / e.max_hp
                        new_phase = 3 if hp_ratio <= 0.33 else (2 if hp_ratio <= 0.66 else 1)
                        if getattr(e, 'current_phase', 1) != new_phase and current_stage >= 2:
                            e.shield_hp += e.max_hp * 0.11
                            e.max_shield = max(getattr(e, 'max_shield', 1), e.shield_hp)
                            e.current_phase = new_phase
                            
                        atk_cd_mult = 0.5 if (current_stage >= 3 and hp_ratio < 0.5) else 1.0
                        
                        e.attack_cooldown -= 1
                        if e.attack_cooldown <= 0:
                            if game_mode == "INFERNO":
                                e.spiral_angle += 20
                                for i in range(8): enemy_bullets.append(EnemyBullet(e.x, e.y, e.spiral_angle + i*45, 'normal'))
                                if hp_ratio < 0.5: 
                                    aim_angle = math.degrees(math.atan2(player.y - e.y, player.x - e.x))
                                    enemy_bullets.append(EnemyBullet(e.x, e.y, aim_angle, 'purple_laser'))
                                e.attack_cooldown = int(10 * atk_cd_mult)
                            else:
                                if current_stage == 1:
                                    for angle in [80, 90, 100]: 
                                        enemy_bullets.append(EnemyBullet(e.x, e.y, angle, 'normal'))
                                    if hp_ratio < 0.5 and random.random() < 0.3:
                                        enemy_bullets.append(EnemyBullet(e.x - 30, e.y, 90, 'laser'))
                                        enemy_bullets.append(EnemyBullet(e.x + 30, e.y, 90, 'laser'))
                                    e.attack_cooldown = int(50 * atk_cd_mult)

                                elif current_stage == 2:
                                    if hp_ratio > 0.66: 
                                        e.spiral_angle += 15
                                        for i in range(3):
                                            enemy_bullets.append(EnemyBullet(e.x, e.y, e.spiral_angle + i*120, 'normal'))
                                        e.attack_cooldown = int(15 * atk_cd_mult)
                                    elif hp_ratio > 0.33: 
                                        if random.random() < 0.05: 
                                            minion = Enemy(difficulty, stage=1)
                                            minion.x = e.x; minion.y = e.y; enemies.append(minion)
                                        aim_angle = math.degrees(math.atan2(player.y - e.y, player.x - e.x))
                                        enemy_bullets.append(EnemyBullet(e.x, e.y, aim_angle, 'blue_bullet'))
                                        e.attack_cooldown = int(30 * atk_cd_mult)
                                    else: 
                                        for angle in [70, 90, 110]:
                                            enemy_bullets.append(EnemyBullet(e.x, e.y, angle, 'laser'))
                                        e.attack_cooldown = int(45 * atk_cd_mult)

                                elif current_stage >= 3:
                                    if hp_ratio > 0.66: 
                                        e.spiral_angle += 20
                                        for i in range(4):
                                            enemy_bullets.append(EnemyBullet(e.x, e.y, e.spiral_angle + i*90, 'blue_bullet'))
                                        aim_angle = math.degrees(math.atan2(player.y - e.y, player.x - e.x))
                                        for offset in [-15, 0, 15]:
                                            enemy_bullets.append(EnemyBullet(e.x, e.y, aim_angle + offset, 'normal'))
                                        e.attack_cooldown = int(20 * atk_cd_mult)

                                    elif hp_ratio > 0.33: 
                                        for angle in [80, 100]:
                                            enemy_bullets.append(EnemyBullet(e.x - 50, e.y, angle, 'purple_laser'))
                                            enemy_bullets.append(EnemyBullet(e.x + 50, e.y, angle, 'purple_laser'))
                                        if random.random() < 0.4:
                                            enemy_bullets.append(EnemyBullet(e.x, e.y, random.randint(45, 135), 'boss_homing'))
                                        e.attack_cooldown = int(35 * atk_cd_mult)

                                    else: 
                                        if random.random() < 0.1:
                                            minion = Enemy(difficulty, stage=2)
                                            minion.x = e.x + random.randint(-50, 50); minion.y = e.y; enemies.append(minion)
                                            
                                        e.spiral_angle += 13
                                        for i in range(6):
                                            enemy_bullets.append(EnemyBullet(e.x, e.y, e.spiral_angle + i*60, 'normal'))
                                            enemy_bullets.append(EnemyBullet(e.x, e.y, -e.spiral_angle + i*60, 'blue_bullet'))
                                            
                                        if hp_ratio < 0.3 and random.random() < 0.3:
                                            enemy_bullets.append(EnemyBullet(e.x, e.y, 90, 'purple_laser'))
                                            
                                        e.attack_cooldown = int(12 * atk_cd_mult)
                            
                    if not e.is_asteroid and e.hp <= 0:
                        player.score += 10
                        if audio_loaded: explosion_sfx.play()
                        for _ in range(15): particles.append(Particle(e.x, e.y, (255, 0, 0)))

                        if e.is_boss:
                            session_boss_kills += 1 
                            screen_shake = 20 
                            if game_mode == "CAMPAIGN":
                                if current_stage == 1:
                                    items.append(Item(e.x, e.y, game_mode, forced_type='upgrade_drone'))
                                    stage_clear_timer = 180 
                                elif current_stage == 2:
                                    items.append(Item(e.x, e.y, game_mode, forced_type='upgrade_burn'))
                                    stage_clear_timer = 180
                                else:
                                    state = "VICTORY"
                            else:
                                for _ in range(3): items.append(Item(e.x + random.randint(-30, 30), e.y, game_mode))
                                boss_spawned = False
                                
                        elif getattr(e, 'is_meteor', False):
                            if random.random() < 0.05: items.append(Item(e.x, e.y, game_mode))
                        else:
                            session_kills += 1 
                            if game_mode == "CAMPAIGN":
                                drop_type = get_drop_type(current_stage, current_wave)
                                if drop_type: items.append(Item(e.x, e.y, game_mode, forced_type=drop_type))
                            else:
                                if random.random() < 0.45: items.append(Item(e.x, e.y, game_mode))
                        enemies.remove(e)
                        continue
                    
                    if math.hypot(player.x - e.x, player.y - e.y) < e.radius + 20:
                        if player.shield_active:
                            if not e.is_boss: 
                                enemies.remove(e)
                                if audio_loaded: explosion_sfx.play()
                                for _ in range(15): particles.append(Particle(e.x, e.y, (100, 255, 255)))
                                player.score += 10; session_kills += 1
                                if game_mode == "CAMPAIGN":
                                    drop_type = get_drop_type(current_stage, current_wave)
                                    if drop_type: items.append(Item(e.x, e.y, game_mode, forced_type=drop_type))
                                else:
                                    if random.random() < 0.45: items.append(Item(e.x, e.y, game_mode))
                        elif player.invincible_timer <= 0:
                            player.hp -= 30 if e.is_asteroid or e.is_boss or getattr(e, 'is_meteor', False) else 20
                            screen_shake = 10 
                            if not e.is_boss: 
                                enemies.remove(e)
                                if audio_loaded: explosion_sfx.play()
                                for _ in range(15): particles.append(Particle(e.x, e.y, (255, 0, 0)))
                            
                            if player.hp <= 0: 
                                if player.lives > 1:
                                    player.lives -= 1; player.hp = player.max_hp; player.invincible_timer = 180 
                                    if audio_loaded: explosion_sfx.play()
                                else: player.lives = 0; state = "GAME_OVER"

                for i in items[:]:
                    i.update() 
                    if i.y > HEIGHT: items.remove(i)
                    elif math.hypot(player.x - i.x, player.y - i.y) < 30:
                        if i.type == 'upgrade_drone':
                            player.has_drone = True
                        elif i.type == 'upgrade_burn':
                            player.burn_unlocked = True
                        elif i.type == 'heal': 
                            player.hp = min(player.hp + (5 if game_mode == "INFERNO" else 30), player.max_hp)
                        elif i.type == 'shield': 
                            player.shield_timer = 60 if game_mode == "INFERNO" else 180 
                        elif i.type in ['upgrade_laser', 'upgrade_plasma', 'upgrade_homing', 'upgrade_universal', 'upgrade_spread']:
                            if i.type == 'upgrade_universal':
                                if player.level < 6: player.level += 1
                                else: player.bonus_damage = min(30, player.bonus_damage + 2)
                            elif i.type == 'upgrade_spread':
                                player.spread_shot = True
                            else:
                                weapon_code = i.type.replace('upgrade_', '')
                                if player.weapon_type == weapon_code:
                                    if player.level < 6: player.level += 1
                                    else: player.bonus_damage = min(30, player.bonus_damage + 2)
                                else:
                                    player.upgrade_weapon(i.type); player.level = 1; player.bonus_damage = 0
                        items.remove(i)

                for p in particles[:]:
                    p.update()
                    if p.life <= 0: particles.remove(p)
                    
                for dn in damage_numbers[:]:
                    dn.update()
                    if dn.life <= 0: damage_numbers.remove(dn)

            for i in items: i.draw(screen)
            for p in particles: p.draw(screen) 
            for b in bullets: b.draw(screen)
            for eb in enemy_bullets: eb.draw(screen)
            for e in enemies: e.draw(screen)
            for dn in damage_numbers: dn.draw(screen) 
            
            if state not in ["GAME_OVER", "VICTORY"]: player.draw(screen)

            font = get_font(20); font_small = get_font(14)
            
            current_base_dmg = 4 if player.weapon_type == 'homing' else (10 if player.weapon_type == 'laser' else 6)
            display_dmg = current_base_dmg + player.bonus_damage
            max_dmg = current_base_dmg + 30 
            
            if game_mode in ["ENDLESS", "INFERNO"]:
                score_txt = font.render(f"ĐIỂM: {player.score} | THỜI GIAN: {int(survival_time//60):02d}:{int(survival_time%60):02d} | DMG: {display_dmg}/{max_dmg}", True, (255, 255, 255))
            else:
                score_txt = font.render(f"ĐIỂM: {player.score} | STAGE: {current_stage} - WAVE: {current_wave} | DMG: {display_dmg}/{max_dmg}", True, (255, 255, 255))
                
            screen.blit(score_txt, (10, 10))
            pygame.draw.rect(screen, (255, 0, 0), (10, 40, 200, 15), 2)
            pygame.draw.rect(screen, (0, 255, 0), (12, 42, 196 * (max(0, player.hp)/player.max_hp), 11))
            pygame.draw.rect(screen, (128, 128, 128), (10, 65, 200, 15), 2)
            pygame.draw.rect(screen, (255, 100, 0), (12, 67, 196 * (player.rage/player.max_rage), 11))
            screen.blit(font_small.render("[NUKE]", True, (255, 100, 0) if player.rage == player.max_rage else (128, 128, 128)), (215, 63))

            for i in range(player.lives):
                hx = WIDTH - 30 - (i * 30)
                pygame.draw.polygon(screen, (0, 255, 0), [(hx, 12), (hx - 8, 28), (hx, 24), (hx + 8, 28)], 2)

            if flash_timer > 0: screen.fill((255, 255, 255)); flash_timer -= 1
            if state == "PAUSED": state = show_pause_menu(screen, mouse_pos, mouse_click)

            if state in ["GAME_OVER", "VICTORY"]:
                if player.score > 0: 
                    if player.score > game_stats[game_mode].get("score", 0):
                        game_stats[game_mode]["kills"] = session_kills
                        game_stats[game_mode]["boss_kills"] = session_boss_kills
                        game_stats[game_mode]["score"] = player.score
                        save_stats(game_stats)
                        
                    if player.score > highscore: 
                        save_highscore(player.score)
                        highscore = player.score
                        
                    player.score = 0 
                state = show_game_over(screen, state, mouse_click)

        scaled_screen = pygame.transform.scale(screen, (new_w, new_h))
        shake_x, shake_y = 0, 0
        if screen_shake > 0:
            shake_x = random.randint(-8, 8); shake_y = random.randint(-8, 8); screen_shake -= 1
            
        window.fill((0, 0, 0)) 
        window.blit(scaled_screen, (x_offset + shake_x, y_offset + shake_y))
        
        if cam_surface and state not in ["MENU", "GAME_OVER", "VICTORY", "HOW_TO_PLAY", "ACHIEVEMENTS"]:
            window.blit(cam_surface, (current_w - 320, 0)) 
        
        pygame.display.flip(); clock.tick(60)

    cap.release(); cv2.destroyAllWindows(); pygame.quit()

if __name__ == "__main__": main()