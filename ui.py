import pygame
from settings import *

PLASMA_COLOR = (0, 150, 255)    # Xanh lam điện
LASER_COLOR  = (255, 50, 50)    # Đỏ nóng
HOMING_COLOR = (200, 0, 255)    # Tím hồng

def get_font(size):
    return pygame.font.SysFont("tahoma", size, bold=True)

def draw_button(surface, text, x, y, width, height, color, is_hover, arrow=None, font_size=24):
    target_width = width + 20 if is_hover else width
    target_height = height + 10 if is_hover else height
    target_x = x - (target_width - width) // 2
    target_y = y - (target_height - height) // 2

    cut = 15 if height > 40 else 10 
    points = [
        (target_x + cut, target_y),
        (target_x + target_width - cut, target_y),
        (target_x + target_width, target_y + cut),
        (target_x + target_width, target_y + target_height - cut),
        (target_x + target_width - cut, target_y + target_height),
        (target_x + cut, target_y + target_height),
        (target_x, target_y + target_height - cut),
        (target_x, target_y + cut)
    ]

    if is_hover:
        for i in range(3, 0, -1):
            glow = (max(0, color[0] - i*50), max(0, color[1] - i*50), max(0, color[2] - i*50))
            glow_points = [(px, py + i*2) for px, py in points]
            pygame.draw.polygon(surface, glow, glow_points)

    bg_color = (25, 30, 40) if is_hover else (10, 15, 20)
    pygame.draw.polygon(surface, bg_color, points)
    pygame.draw.polygon(surface, color, points, 2)

    if is_hover:
        pygame.draw.rect(surface, color, (target_x - 8, target_y + target_height//2 - 6, 4, 12))
        pygame.draw.rect(surface, color, (target_x + target_width + 4, target_y + target_height//2 - 6, 4, 12))
    
    font = pygame.font.SysFont("tahoma", font_size, bold=True)
    text_color = WHITE if is_hover else color
    txt_surface = font.render(text, True, text_color)
    
    txt_x = target_x + target_width//2 - txt_surface.get_width()//2
    if arrow: txt_x -= 15 
    surface.blit(txt_surface, (txt_x, target_y + target_height//2 - txt_surface.get_height()//2))
                               
    if arrow:
        arrow_color = WHITE if is_hover else color
        ax = target_x + target_width - 25 
        ay = target_y + target_height // 2
        
        if arrow == "down":
            pygame.draw.polygon(surface, arrow_color, [(ax - 6, ay - 3), (ax + 6, ay - 3), (ax, ay + 4)])
        elif arrow == "up":
            pygame.draw.polygon(surface, arrow_color, [(ax - 6, ay + 3), (ax + 6, ay + 3), (ax, ay - 4)])

    return pygame.Rect(x, y, width, height)

def show_how_to_play(screen, mouse_click):
    panel = pygame.Rect(WIDTH//2 - 420, HEIGHT//2 - 280, 840, 560)
    pygame.draw.rect(screen, (15, 20, 25), panel) 
    pygame.draw.rect(screen, NEON_CYAN, panel, 2)
    
    title = get_font(40).render("HƯỚNG DẪN CHI TIẾT", True, YELLOW)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 250))

    font = get_font(18)
    font_small = get_font(14) 
    
    left_x = WIDTH//2 - 380
    start_y = HEIGHT//2 - 160
    
    screen.blit(font.render("[ ĐIỀU KHIỂN & CƠ CHẾ ]", True, NEON_CYAN), (left_x, start_y))
    controls = [
        "- Di chuyển tay: Lái tàu vũ trụ",
        "- Giơ 1 ngón trỏ: Bắn Đạn cơ bản",
        "- Giơ 3 ngón tay: Bắn Nuke (Cần đầy Nộ)",
        "- Tích Nộ: Bắn trúng mục tiêu",
        "- Nhấn ESC: Tạm dừng / Phóng To (Nhấn F11)"
    ]
    for i, txt in enumerate(controls):
        screen.blit(font.render(txt, True, WHITE), (left_x, start_y + 35 + i * 30))

    mode_y = start_y + 200
    screen.blit(font.render("[ CÁC CHẾ ĐỘ CHƠI ]", True, NEON_ORANGE), (left_x, mode_y))
    modes_desc = [
        ("VƯỢT ẢI:", "Tiêu diệt quái, đánh Boss để qua Stage.", NEON_CYAN),
        ("VÔ TẬN:", "Sống sót tính giờ. Boss ra liên tục mỗi 60s.", NEON_GREEN),
        ("HỎA NGỤC:", "Mưa đạn Bullet Hell, KHÔNG rớt máu/khiên.", NEON_RED)
    ]
    for i, (m_title, m_desc, m_color) in enumerate(modes_desc):
        t_surf = font.render(m_title, True, m_color)
        screen.blit(t_surf, (left_x, mode_y + 35 + i * 30))
        screen.blit(font_small.render(m_desc, True, WHITE), (left_x + t_surf.get_width() + 5, mode_y + 37 + i * 30))

    right_x = WIDTH//2 + 40
    screen.blit(font.render("[ VẬT PHẨM & NÂNG CẤP ]", True, NEON_ORANGE), (right_x, start_y))
    
    # --- ĐÃ SỬA LẠI CHỈ SỐ DMG VÀ MÀU SẮC ĐỒNG BỘ ---
    items_info = [
        (NEON_GREEN, "+", "Hồi 30 Máu"),
        (NEON_CYAN, "S", "Khiên bảo vệ (3s)"),
        (PLASMA_COLOR, "P", "Súng Plasma (DMG 6)"),
        (LASER_COLOR, "L", "Súng Laser (DMG 10)"),
        (HOMING_COLOR, "H", "Súng Đuổi (DMG 4)"),
        (NEON_MAGENTA, "D", "Phi Thuyền Phụ (Đánh Boss 1)"),
        (NEON_ORANGE, "B", "Thiêu Đốt 1.5 HP/s (Đánh Boss 2)")
    ]
    
    for i, (color, char, desc) in enumerate(items_info):
        iy = start_y + 35 + i * 35 
        box_rect = pygame.Rect(right_x, iy, 24, 24)
        pygame.draw.rect(screen, (20, 25, 30), box_rect) 
        pygame.draw.rect(screen, color, box_rect, 2, border_radius=4)
        
        if char in ["L", "P", "H"]:
            cx, cy = right_x + 12, iy + 12
            pygame.draw.polygon(screen, color, [(cx, cy - 6), (cx - 6, cy + 2), (cx + 6, cy + 2)])
            pygame.draw.rect(screen, color, (cx - 2, cy + 2, 4, 6))
        else:
            txt_icon = get_font(16).render(char, True, color)
            screen.blit(txt_icon, (right_x + 12 - txt_icon.get_width()//2, iy + 12 - txt_icon.get_height()//2))

        screen.blit(font.render(desc, True, WHITE), (right_x + 35, iy + 2))

    txt_esc = font.render("[ NHẤN CLICK CHUỘT HOẶC ESC ĐỂ VỀ MENU ]", True, GRAY)
    screen.blit(txt_esc, (WIDTH//2 - txt_esc.get_width()//2, HEIGHT//2 + 245))
    
    if mouse_click: return "MENU"
    return "HOW_TO_PLAY"

def show_achievements(screen, game_stats, mouse_click):
    panel_w, panel_h = 860, 560
    panel_x = WIDTH//2 - panel_w//2
    panel_y = HEIGHT//2 - panel_h//2
    
    pygame.draw.rect(screen, (10, 15, 25), (panel_x, panel_y, panel_w, panel_h), border_radius=8)
    pygame.draw.rect(screen, NEON_CYAN, (panel_x, panel_y, panel_w, panel_h), 2, border_radius=8)
    
    title = get_font(40).render("BẢNG THÀNH TỰU", True, YELLOW)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, panel_y + 15))
    
    pygame.draw.line(screen, (100, 100, 120), (panel_x + 20, panel_y + 65), (panel_x + panel_w - 20, panel_y + 65), 1)

    headers = ["QUÁI DIỆT", "BOSS DIỆT", "TỔNG ĐIỂM"]
    colors = [NEON_CYAN, NEON_RED, YELLOW]
    x_offsets = [-70, 90, 280] 
    
    for idx, h in enumerate(headers):
        t = get_font(20).render(h, True, colors[idx])
        screen.blit(t, (WIDTH//2 + x_offsets[idx] - t.get_width()//2, panel_y + 80))
        
    modes_display = [
        ("VƯỢT ẢI", "CAMPAIGN", NEON_CYAN, panel_y + 120), 
        ("VÔ TẬN", "ENDLESS", HOMING_COLOR, panel_y + 240), 
        ("HỎA NGỤC", "INFERNO", NEON_RED, panel_y + 360)
    ]
    
    for display_name, key, theme_color, y_pos in modes_display:
        row_rect = pygame.Rect(panel_x + 20, y_pos, panel_w - 40, 100)
        
        pygame.draw.rect(screen, (20, 25, 35), row_rect, border_radius=6)
        pygame.draw.rect(screen, theme_color, row_rect, 1, border_radius=6)
        
        font_big = get_font(26)
        t_name = font_big.render(display_name, True, WHITE)
        screen.blit(t_name, (panel_x + 40, y_pos + 20))
        
        if key == "ENDLESS":
            sub = get_font(16).render("THỜI GIAN", True, WHITE)
            screen.blit(sub, (panel_x + 40, y_pos + 60))
            
        data = game_stats.get(key, {"kills": 0, "boss_kills": 0, "score": 0})
        
        icon_font = get_font(24)
        kill_icon = icon_font.render("💀", True, NEON_CYAN)
        boss_icon = icon_font.render("💀", True, NEON_RED)
        score_icon = icon_font.render("★", True, YELLOW)

        texts = [
            (kill_icon, str(data["kills"]), WHITE),
            (boss_icon, str(data["boss_kills"]), WHITE),
            (score_icon, str(data["score"]), YELLOW)
        ]
        
        for col_idx, (icon, text, val_color) in enumerate(texts):
            col_x = WIDTH//2 + x_offsets[col_idx]
            val_surf = get_font(26).render(text, True, val_color)
            
            total_w = icon.get_width() + 10 + val_surf.get_width()
            start_x = col_x - total_w//2
            
            screen.blit(icon, (start_x, y_pos + 35))
            screen.blit(val_surf, (start_x + icon.get_width() + 10, y_pos + 35))

    txt_esc = get_font(18).render("[ NHẤN CLICK CHUỘT HOẶC ESC ĐỂ VỀ MENU ]", True, GRAY)
    screen.blit(txt_esc, (WIDTH//2 - txt_esc.get_width()//2, panel_y + panel_h - 40))
    
    if mouse_click: return "MENU"
    return "ACHIEVEMENTS"

def show_pause_menu(screen, mouse_pos, mouse_click):
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(150)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    font_pause = get_font(60)
    txt_pause = font_pause.render("TẠM DỪNG", True, WHITE)
    screen.blit(txt_pause, (WIDTH//2 - txt_pause.get_width()//2, HEIGHT//2 - 150))

    btn_w, btn_h = 250, 50
    btn_resume_y = HEIGHT//2 - 20
    btn_menu_y = HEIGHT//2 + 50

    is_hover_resume = pygame.Rect(WIDTH//2 - btn_w//2, btn_resume_y, btn_w, btn_h).collidepoint(mouse_pos)
    is_hover_menu = pygame.Rect(WIDTH//2 - btn_w//2, btn_menu_y, btn_w, btn_h).collidepoint(mouse_pos)

    draw_button(screen, "TIẾP TỤC", WIDTH//2 - btn_w//2, btn_resume_y, btn_w, btn_h, NEON_CYAN, is_hover_resume)
    draw_button(screen, "QUAY LẠI MENU", WIDTH//2 - btn_w//2, btn_menu_y, btn_w, btn_h, NEON_RED, is_hover_menu)

    if mouse_click:
        if is_hover_resume: return "PLAYING"
        elif is_hover_menu: return "MENU"
    return "PAUSED"

def show_game_over(screen, state, mouse_click):
    msg = "THẤT BẠI" if state == "GAME_OVER" else "VƯỢT ẢI THÀNH CÔNG"
    col = NEON_RED if state == "GAME_OVER" else NEON_GREEN
    f_big = get_font(50)
    txt = f_big.render(msg, True, col)
    sub = get_font(20).render("Nhấn chuột bất kỳ đâu để về MENU", True, WHITE)
    screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - 50))
    screen.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 20))
    
    if mouse_click: return "MENU"
    return state