"""
Harvest Farm Constructor - Main Menu
Tela inicial animada com opções de Novo Jogo, Continuar e Sair.
"""
import pygame
import math
import random
from src.savesystem import save_exists


def lerp_color(c1, c2, t):
    return tuple(max(0, min(255, int(c1[i] + (c2[i] - c1[i]) * t))) for i in range(3))


def draw_star(surf, x, y, size, color, alpha):
    s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
    pts = []
    for i in range(10):
        angle = math.pi / 2 + i * math.pi / 5
        r = size if i % 2 == 0 else size // 2
        pts.append((size + r * math.cos(angle), size - r * math.sin(angle)))
    pygame.draw.polygon(s, (*color, alpha), pts)
    surf.blit(s, (x - size, y - size))


class Particle2D:
    def __init__(self, sw, sh):
        self.reset(sw, sh)

    def reset(self, sw, sh):
        self.x = random.uniform(0, sw)
        self.y = random.uniform(sh, sh + 40)
        self.vx = random.uniform(-0.4, 0.4)
        self.vy = random.uniform(-1.2, -0.4)
        self.size = random.randint(3, 8)
        self.color = random.choice([
            (120, 200, 80), (200, 220, 80), (80, 200, 120),
            (255, 200, 50), (200, 150, 80),
        ])
        self.life = random.randint(80, 180)
        self.max_life = self.life
    def update(self, sw, sh):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        if self.life <= 0 or self.y < -20:
            self.reset(sw, sh)

    def draw(self, surf):
        alpha = int(200 * self.life / self.max_life)
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (self.size, self.size), self.size)
        surf.blit(s, (int(self.x) - self.size, int(self.y) - self.size))


class Cloud:
    def __init__(self, sw):
        self.x = random.uniform(-200, sw)
        self.y = random.uniform(40, 200)
        self.w = random.uniform(120, 280)
        self.speed = random.uniform(0.15, 0.4)
        self.sw = sw

    def update(self):
        self.x += self.speed
        if self.x > self.sw + 200:
            self.x = -self.w - 20

    def draw(self, surf):
        s = pygame.Surface((int(self.w), 60), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (240, 245, 255, 180), (0, 20, int(self.w), 40))
        pygame.draw.ellipse(s, (240, 245, 255, 180), (int(self.w * 0.2), 5, int(self.w * 0.45), 46))
        pygame.draw.ellipse(s, (250, 252, 255, 160), (int(self.w * 0.5), 10, int(self.w * 0.4), 38))
        surf.blit(s, (int(self.x), int(self.y)))


class MenuButton:
    def __init__(self, x, y, w, h, text, font, color_bg, color_hover, color_text=(245, 248, 252)):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font
        self.color_bg = color_bg
        self.color_hover = color_hover
        self.color_text = color_text
        self.hovered = False
        self.scale = 1.0
        self.target_scale = 1.0

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
        self.target_scale = 1.04 if self.hovered else 1.0
        self.scale += (self.target_scale - self.scale) * 0.15

    def draw(self, surf):
        sw = int(self.rect.w * self.scale)
        sh = int(self.rect.h * self.scale)
        sx = self.rect.centerx - sw // 2
        sy = self.rect.centery - sh // 2
        r = pygame.Rect(sx, sy, sw, sh)

        # Shadow
        sr = r.move(4, 4)
        ss = pygame.Surface((sr.w, sr.h), pygame.SRCALPHA)
        ss.fill((0, 0, 0, 60))
        pygame.draw.rect(ss, (0, 0, 0, 60), ss.get_rect(), border_radius=14)
        surf.blit(ss, (sr.x, sr.y))

        # Button body
        color = self.color_hover if self.hovered else self.color_bg
        pygame.draw.rect(surf, color, r, border_radius=14)
        # Shine top
        shine = pygame.Surface((sw, sh // 2), pygame.SRCALPHA)
        shine.fill((255, 255, 255, 25))
        pygame.draw.rect(shine, (255, 255, 255, 25), shine.get_rect(), border_radius=14)
        surf.blit(shine, (sx, sy))
        # Border
        bc = (255, 255, 255, 80) if self.hovered else (255, 255, 255, 40)
        border_surf = pygame.Surface((sw, sh), pygame.SRCALPHA)
        pygame.draw.rect(border_surf, bc, border_surf.get_rect(), 2, border_radius=14)
        surf.blit(border_surf, (sx, sy))

        # Text
        ts = self.font.render(self.text, True, self.color_text)
        surf.blit(ts, (sx + (sw - ts.get_width()) // 2, sy + (sh - ts.get_height()) // 2))

    def clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN and
                event.button == 1 and self.rect.collidepoint(event.pos))


def run_menu(screen, clock):
    """
    Exibe o menu principal animado.
    Retorna: "new", "continue", ou "quit"
    """
    sw, sh = screen.get_size()

    font_title = pygame.font.SysFont("segoeui", 72, bold=True)
    font_sub   = pygame.font.SysFont("segoeui", 26)
    font_btn   = pygame.font.SysFont("segoeui", 22, bold=True)
    font_sm    = pygame.font.SysFont("segoeui", 14)

    has_save = save_exists()

    # lista de botões = []
    bw, bh = 320, 58
    cx = sw // 2
    btn_y0 = sh // 2 + 30

    btns = []

    if has_save:
        btns.append(MenuButton(cx - bw//2, btn_y0,      bw, bh, "▶  Continuar Jogo", font_btn,
                               (40, 110, 60), (55, 145, 80)))
        btns.append(MenuButton(cx - bw//2, btn_y0 + 76, bw, bh, "✦  Novo Jogo",       font_btn,
                               (60, 80, 130), (80, 105, 170)))
        btns.append(MenuButton(cx - bw//2, btn_y0+152,  bw, bh, "✕  Sair",            font_btn,
                               (100, 40, 40), (140, 55, 55)))
    else:
        btns.append(MenuButton(cx - bw//2, btn_y0,      bw, bh, "✦  Novo Jogo",       font_btn,
                               (40, 110, 60), (55, 145, 80)))
        btns.append(MenuButton(cx - bw//2, btn_y0 + 76, bw, bh, "✕  Sair",            font_btn,
                               (100, 40, 40), (140, 55, 55)))

    # elementos do fundo animados
    clouds = [Cloud(sw) for _ in range(7)]
    particles = [Particle2D(sw, sh) for _ in range(60)]
    tick = 0

    # pirilampos flutuantes
    flies = [{"x": random.uniform(0, sw), "y": random.uniform(sh * 0.4, sh),
              "phase": random.uniform(0, math.tau), "speed": random.uniform(0.3, 0.8)}
             for _ in range(30)]

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        tick += 1
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "quit"
            for i, btn in enumerate(btns):
                if btn.clicked(event):
                    if has_save:
                        if i == 0: return "continue"
                        if i == 1: return "new"
                        if i == 2: return "quit"
                    else:
                        if i == 0: return "new"
                        if i == 1: return "quit"

        # Update
        for cl in clouds: cl.update()
        for p in particles: p.update(sw, sh)
        for btn in btns: btn.update(mouse_pos)
        for fly in flies:
            fly["x"] += math.sin(tick * 0.02 + fly["phase"]) * 0.6
            fly["y"] += math.cos(tick * 0.015 + fly["phase"]) * 0.4

        # ---- DRAW ----
        # gradiente do céu animado
        t_day = 0.5 + 0.5 * math.sin(tick * 0.005)
        sky_top = lerp_color((20, 40, 80), (60, 120, 200), t_day)
        sky_bot = lerp_color((60, 100, 40), (120, 180, 80), t_day)
        for row in range(sh):
            frac = row / sh
            c = lerp_color(sky_top, sky_bot, frac)
            pygame.draw.line(screen, c, (0, row), (sw, row))

        # Clouds
        for cl in clouds: cl.draw(screen)

        # sol com brilho pulsante
        sun_x = int(sw * 0.75)
        sun_y = int(sh * 0.18)
        # brilho ao redor do sol
        for r in range(60, 0, -10):
            a = int(20 * r / 60)
            glow = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 220, 80, a), (r, r), r)
            screen.blit(glow, (sun_x-r, sun_y-r))
        pygame.draw.circle(screen, (255, 230, 80), (sun_x, sun_y), 40)
        pygame.draw.circle(screen, (255, 245, 140), (sun_x, sun_y), 32)

        # faixa de terra no rodapé
        ground_y = int(sh * 0.72)
        pygame.draw.rect(screen, (60, 120, 40), (0, ground_y, sw, sh - ground_y))
        pygame.draw.rect(screen, (50, 100, 30), (0, ground_y, sw, 8))

        # silhueta das colinas ondulando
        hill_surf = pygame.Surface((sw, sh - ground_y + 30), pygame.SRCALPHA)
        pts = [(0, 30)]
        for i in range(sw + 1):
            hy = 30 + int(22 * math.sin(i * 0.015 + tick * 0.003) +
                          12 * math.sin(i * 0.03 + tick * 0.005))
            pts.append((i, hy))
        pts += [(sw, 200), (0, 200)]
        pygame.draw.polygon(hill_surf, (45, 95, 25, 220), pts)
        screen.blit(hill_surf, (0, ground_y - 30))

        # silhueta da fazenda
        hx, hy2 = int(sw * 0.15), ground_y - 90
        pygame.draw.rect(screen, (30, 45, 25), (hx, hy2 + 30, 70, 60))
        pygame.draw.polygon(screen, (25, 35, 20), [(hx - 8, hy2 + 30), (hx + 35, hy2), (hx + 78, hy2 + 30)])
        pygame.draw.rect(screen, (60, 40, 15), (hx + 25, hy2 + 55, 20, 35))
        # silhueta do moinho de vento
        wx, wy2 = int(sw * 0.82), ground_y - 110
        pygame.draw.rect(screen, (30, 45, 25), (wx - 8, wy2 + 30, 16, 80))
        # pás girando do moinho
        for bi in range(4):
            angle = tick * 0.03 + bi * math.pi / 2
            bx2 = wx + int(32 * math.cos(angle))
            by2 = wy2 + 34 + int(32 * math.sin(angle))
            pygame.draw.line(screen, (30, 45, 25), (wx, wy2 + 34), (bx2, by2), 4)
        pygame.draw.circle(screen, (30, 45, 25), (wx, wy2 + 34), 6)

        # árvores na paisagem
        for tx, ty3 in [(int(sw*0.05), ground_y-50),(int(sw*0.1), ground_y-65),
                         (int(sw*0.35), ground_y-55),(int(sw*0.65), ground_y-60),(int(sw*0.9), ground_y-45)]:
            pygame.draw.rect(screen, (60, 35, 10), (tx - 4, ty3 + 20, 8, 30))
            pygame.draw.circle(screen, (35, 80, 25), (tx, ty3), 28)
            pygame.draw.circle(screen, (45, 100, 30), (tx - 8, ty3 + 4), 18)

        # partículas de folhas e pirilampos
        for p in particles: p.draw(screen)
        for fly in flies:
            pulse = 0.5 + 0.5 * math.sin(tick * 0.08 + fly["phase"])
            a = int(60 + 160 * pulse)
            fs = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(fs, (200, 240, 100, a), (4, 4), 3)
            screen.blit(fs, (int(fly["x"]) - 4, int(fly["y"]) - 4))

        # ──── título ────
        # sombra do título
        glow_offset = int(3 * math.sin(tick * 0.04))
        title_shadow = font_title.render("Harvest Farm", True, (10, 30, 10))
        screen.blit(title_shadow, (cx - title_shadow.get_width()//2 + 4, sh//4 + 4 + glow_offset))

        # título principal com duas cores
        t1 = font_title.render("Harvest", True, (200, 240, 80))
        t2 = font_title.render("Farm", True, (80, 220, 120))
        total_w = t1.get_width() + 14 + t2.get_width()
        screen.blit(t1, (cx - total_w//2, sh//4 + glow_offset))
        screen.blit(t2, (cx - total_w//2 + t1.get_width() + 14, sh//4 + glow_offset))

        # subtítulo
        sub = font_sub.render("Constructor · Manager · Simulator", True, (200, 230, 180))
        screen.blit(sub, (cx - sub.get_width()//2, sh//4 + 80 + glow_offset))

        # estrelas decorativas ao redor do título
        for si, (sox, soy) in enumerate([(-total_w//2-20, 20), (total_w//2+10, 20),
                                          (-total_w//2-10, 55), (total_w//2, 55)]):
            star_pulse = int(180 + 75 * math.sin(tick * 0.05 + si))
            draw_star(screen, cx + sox, sh//4 + soy + glow_offset, 10,
                      (255, 220, 60), star_pulse)

        # painel semitransparente atrás dos botões
        panel_rect = pygame.Rect(cx - bw//2 - 30, btn_y0 - 20, bw + 60, len(btns) * 76 + 30)
        panel_surf = pygame.Surface((panel_rect.w, panel_rect.h), pygame.SRCALPHA)
        panel_surf.fill((0, 0, 0, 80))
        pygame.draw.rect(panel_surf, (0,0,0,80), panel_surf.get_rect(), border_radius=20)
        border_s = pygame.Surface((panel_rect.w, panel_rect.h), pygame.SRCALPHA)
        pygame.draw.rect(border_s, (255,255,255,30), border_s.get_rect(), 2, border_radius=20)
        screen.blit(panel_surf, panel_rect.topleft)
        screen.blit(border_s, panel_rect.topleft)

        # botões principais do menu
        for btn in btns: btn.draw(screen)

        # indicador de save existente
        if has_save:
            save_txt = font_sm.render("💾 Arquivo de save encontrado", True, (160, 220, 140))
            screen.blit(save_txt, (cx - save_txt.get_width()//2, btn_y0 - 42))

        # credítos na parte inferior
        cr = font_sm.render("v5.0  |  Use WASD para mover  |  F1 para ajuda no jogo", True, (120, 140, 110))
        screen.blit(cr, (cx - cr.get_width()//2, sh - 26))

        pygame.display.flip()

    return "quit"
