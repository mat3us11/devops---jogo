import pygame
import sys
import random
from pathlib import Path

pygame.init()

# ==============================
# CONFIGURAÇÃO DA JANELA / GRID
# ==============================
WIDTH, HEIGHT = 960, 544  # 30x17 tiles se TILE=32 (cabe UI legal)
TILE = 32
COLS = WIDTH // TILE
ROWS = HEIGHT // TILE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fazenda Constructor - Plantio, Recompensa e Loja")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)
big_font = pygame.font.SysFont(None, 36)

# ==============================
# CORES (fallback)
# ==============================
GREEN = (90, 170, 90)
BROWN = (130, 90, 60)
DARK = (30, 30, 30)
WHITE = (240, 240, 240)
YELLOW = (255, 210, 60)
BLUE = (80, 120, 230)

# ==============================
# PATH PARA PYINSTALLER
# ==============================
def resource_path(relative_path: str) -> str:
    if hasattr(sys, "_MEIPASS"):
        return str(Path(sys._MEIPASS) / relative_path)
    return str(Path(__file__).resolve().parent.parent / relative_path)

def load_sprite(path: str, size: int):
    try:
        img = pygame.image.load(resource_path(path)).convert_alpha()
        return pygame.transform.scale(img, (size, size))
    except Exception:
        return None

# ==============================
# SPRITES (com fallback)
# ==============================
spr_grass = load_sprite("assets/grama.png", TILE)
spr_fence = load_sprite("assets/cerca.png", TILE)
spr_soil  = load_sprite("assets/terra.jpeg", TILE)
spr_player = load_sprite("assets/personagem.png", TILE)
spr_seed = load_sprite("assets/.png", TILE)

spr_crop1 = load_sprite("assets/planta.png", TILE)
spr_crop2 = load_sprite("assets/planta.png", TILE)
spr_crop3 = load_sprite("assets/planta.png", TILE)

# ==============================
# TIPOS DE PLANTA
# ==============================

PLANT_TYPES = {
    "trigo": {
        "growth": 200,
        "reward": 5
    },
    "milho": {
        "growth": 260,
        "reward": 8
    },
    "tomate": {
        "growth": 320,
        "reward": 12
    }
}

PLANT_LIST = ["trigo", "milho", "tomate"]

# planta selecionada
current_seed = "trigo"

# ==============================
# TILES / MAPA
# ==============================
# 0 = grama (anda)
# 1 = cerca/obstáculo (bloqueia)
# 2 = terra plantável (anda + pode plantar)
T_GRASS, T_FENCE, T_SOIL = 0, 1, 2

def new_world(cols, rows):
    w = [[T_GRASS for _ in range(cols)] for _ in range(rows)]

    # borda cercada
    for x in range(cols):
        w[0][x] = T_FENCE
        w[rows - 1][x] = T_FENCE
    for y in range(rows):
        w[y][0] = T_FENCE
        w[y][cols - 1] = T_FENCE

    # área de terra plantável (um “campo”)
    field_x0, field_y0 = 3, 3
    field_w, field_h = max(6, cols // 2), max(5, rows // 2)
    for y in range(field_y0, min(rows - 2, field_y0 + field_h)):
        for x in range(field_x0, min(cols - 2, field_x0 + field_w)):
            w[y][x] = T_SOIL

    # cercas internas para “cara de constructor”
    if cols > 18:
        for y in range(2, rows - 2):
            if y % 2 == 0:
                w[y][cols // 2] = T_FENCE

    return w

world_cols, world_rows = COLS, ROWS
world = new_world(world_cols, world_rows)

def is_blocked(r, c):
    if r < 0 or r >= world_rows or c < 0 or c >= world_cols:
        return True
    return world[r][c] == T_FENCE

# ==============================
# SISTEMAS DE PLANTIO / CRESCIMENTO
# ==============================
# crop_state[(r,c)] = stage (1..3)
# crop_timer[(r,c)] = ticks até próximo estágio
crop_state = {}
crop_timer = {}

# ticks para crescer (quanto menor, mais rápido)
growth_ticks = 200  # base
# recompensa por colher
harvest_reward = 5

# estoque
seeds = 5
coins = 0

# ==============================
# PLAYER
# ==============================
player_r, player_c = 2, 2

# ==============================
# LOJA
# ==============================
shop_open = False

# Itens: (nome, custo, ação)
# 1) expandir: aumenta cols/rows e recria mundo (mantém fazenda maior)
# 2) sementes +5
# 3) upgrade: reduz growth_ticks (cresce mais rápido)
def shop_items():
    return [
        ("Expandir fazenda (+4 cols, +3 rows)", 30),
        ("Comprar sementes (+5)", 10),
        ("Upgrade crescimento (-20 ticks)", 25),
    ]

def apply_purchase(idx):
    global coins, seeds, growth_ticks, world_cols, world_rows, world, world_rows, world_cols
    items = shop_items()
    name, cost = items[idx]
    if coins < cost:
        return "Dinheiro insuficiente!"

    coins -= cost

    if idx == 0:
        # expandir mundo
        world_cols = min(60, world_cols + 4)
        world_rows = min(40, world_rows + 3)
        # recria mundo maior
        world = new_world(world_cols, world_rows)
        # ao expandir, mantemos plantações em tiles que ainda existem
        # (simples: remove as que ficaram fora)
        keys = list(crop_state.keys())
        for (r, c) in keys:
            if r >= world_rows or c >= world_cols:
                crop_state.pop((r, c), None)
                crop_timer.pop((r, c), None)

        return "Fazenda expandida!"
    elif idx == 1:
        seeds += 5
        return "+5 sementes!"
    elif idx == 2:
        growth_ticks = max(60, growth_ticks - 20)
        return "Crescimento mais rápido!"
    return "OK"

shop_message = ""
shop_message_timer = 0

# ==============================
# FUNÇÕES DE DESENHO
# ==============================
def draw_tile(tile, x, y):
    if tile == T_GRASS:
        if spr_grass:
            screen.blit(spr_grass, (x, y))
        else:
            pygame.draw.rect(screen, GREEN, (x, y, TILE, TILE))
    elif tile == T_FENCE:
        if spr_fence:
            screen.blit(spr_fence, (x, y))
        else:
            pygame.draw.rect(screen, BROWN, (x, y, TILE, TILE))
    elif tile == T_SOIL:
        if spr_soil:
            screen.blit(spr_soil, (x, y))
        else:
            pygame.draw.rect(screen, (150, 110, 80), (x, y, TILE, TILE))

def draw_crop(r, c):

    plant = crop_state.get((r, c))
    if not plant:
        return

    stage = plant["stage"]

    x, y = c * TILE, r * TILE

    img = None
    if stage == 1:
        img = spr_crop1
    elif stage == 2:
        img = spr_crop2
    elif stage == 3:
        img = spr_crop3

    if img:
        screen.blit(img, (x, y))
    else:
        pygame.draw.circle(screen, (40,160,60), (x+TILE//2, y+TILE//2), 6+stage*3)

def draw_player():
    x, y = player_c * TILE, player_r * TILE
    if spr_player:
        screen.blit(spr_player, (x, y))
    else:
        pygame.draw.rect(screen, DARK, (x, y, TILE, TILE))

def draw_ui():
    ui = f"Moedas:{coins}  Sementes:{seeds}  Planta:{current_seed}"
    txt = font.render(ui, True, WHITE)
    pygame.draw.rect(screen, DARK, (0, 0, WIDTH, 28))
    screen.blit(txt, (10, 6))

def draw_seed_hud():

    size = 32
    spacing = 10

    total_width = len(PLANT_LIST) * (size + spacing)

    start_x = WIDTH - total_width - 20
    y = 0

    # fundo da HUD
    bg_rect = pygame.Rect(start_x-10, 0, total_width+20, 32)
    pygame.draw.rect(screen, (40,40,40), bg_rect)

    for i, plant in enumerate(PLANT_LIST):

        x = start_x + i * (size + spacing)

        rect = pygame.Rect(x, y, size, size)

        # destaque da planta selecionada
        if plant == current_seed:
            pygame.draw.rect(screen, (255,210,60), rect)
        else:
            pygame.draw.rect(screen, (80,80,80), rect)

        # ícone
        if spr_crop1:
            img = pygame.transform.scale(spr_crop1, (22,22))
            screen.blit(img, (x+5, y+5))

        # número
        num = font.render(str(i+1), True, WHITE)
        num_rect = num.get_rect(center=(x + size//2, y + size//2))
        screen.blit(num, num_rect)

def draw_shop():
    # overlay simples
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    screen.blit(overlay, (0, 0))

    title = big_font.render("LOJA (B para fechar)", True, WHITE)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 60))

    items = shop_items()
    y = 140
    for i, (name, cost) in enumerate(items, start=1):
        line = font.render(f"{i}) {name}  -  {cost} moedas", True, WHITE)
        screen.blit(line, (120, y))
        y += 40

    hint = font.render("Use 1, 2, 3 para comprar.", True, YELLOW)
    screen.blit(hint, (120, y + 20))

    if shop_message_timer > 0:
        msg = font.render(shop_message, True, BLUE)
        screen.blit(msg, (120, y + 60))

# ==============================
# LÓGICA DO JOGO
# ==============================
tick_counter = 0

running = True
while running:
    dt = clock.tick(60)
    tick_counter += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                running = False

             # selecionar planta
            if event.key == pygame.K_1:
                current_seed = "trigo"

            if event.key == pygame.K_2:
                current_seed = "milho"

            if event.key == pygame.K_3:
                current_seed = "tomate"

            # abrir/fechar loja
            if event.key == pygame.K_b:
                shop_open = not shop_open

            # compras na loja
            if shop_open:
                if event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                    idx = {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2}[event.key]
                    shop_message = apply_purchase(idx)
                    shop_message_timer = 120  # frames ~2s
                continue

            # movimento em grid estilo constructor
            nr, nc = player_r, player_c
            if event.key == pygame.K_LEFT:
                nc -= 1
            elif event.key == pygame.K_RIGHT:
                nc += 1
            elif event.key == pygame.K_UP:
                nr -= 1
            elif event.key == pygame.K_DOWN:
                nr += 1
            elif event.key == pygame.K_a:
                nc -= 1
            elif event.key == pygame.K_d:
                nc += 1
            elif event.key == pygame.K_w:
                nr -= 1
            elif event.key == pygame.K_s:
                nr += 1

            if (nr, nc) != (player_r, player_c):
                if not is_blocked(nr, nc):
                    player_r, player_c = nr, nc

            # interação: plantar/colher
            if event.key == pygame.K_e:
                tile = world[player_r][player_c]

                # plantar só em terra e se não tiver planta e tiver semente
                if tile == T_SOIL and (player_r, player_c) not in crop_state:
                    if seeds > 0:
                        seeds -= 1
                        crop_state[(player_r, player_c)] = {
                        "type": current_seed,
                        "stage": 1
                    }
                        
                    crop_timer[(player_r, player_c)] = PLANT_TYPES[current_seed]["growth"]

                    # se não tiver seed, não faz nada

                # colher se planta madura
                plant = crop_state.get((player_r, player_c))

                if plant and plant["stage"] == 3:

                    coins += PLANT_TYPES[plant["type"]]["reward"]

                    crop_state.pop((player_r, player_c), None)
                    crop_timer.pop((player_r, player_c), None)

    # crescimento das plantas (tick-based)
    # a cada frame, decrementa timers e sobe estágio
    to_upgrade = []
    for pos, t in list(crop_timer.items()):
        t -= 1
        crop_timer[pos] = t
        if t <= 0:
            to_upgrade.append(pos)

    for pos in to_upgrade:
        plant = crop_state.get(pos)

        stage = plant["stage"]
        if stage in (1,2):
            plant["stage"] += 1
            crop_timer[pos] = PLANT_TYPES[plant["type"]]["growth"]
        else:
            # madura fica madura (sem timer)
            crop_timer.pop(pos, None)

    # mensagem da loja
    if shop_message_timer > 0:
        shop_message_timer -= 1
        if shop_message_timer <= 0:
            shop_message = ""

    # ==============================
    # DESENHAR
    # ==============================
    screen.fill((0, 0, 0))

    # desenha o mundo
    for r in range(world_rows):
        for c in range(world_cols):
            # só desenha o que cabe na tela (camera simples: sem scroll por enquanto)
            # no começo, o mundo não pode ser maior que a tela; a expansão vai além,
            # mas aqui ainda desenhamos só o que cabe.
            if r >= ROWS or c >= COLS:
                continue
            x, y = c * TILE, r * TILE
            draw_tile(world[r][c], x, y)

    # desenha plantações
    for (r, c) in list(crop_state.keys()):
        if r < ROWS and c < COLS:
            draw_crop(r, c)

    # desenha player
    draw_player()

    # ui
    draw_ui()
    draw_seed_hud()

    # hint tile
    tile_here = world[player_r][player_c]
    hint = ""
    if tile_here == T_SOIL and (player_r, player_c) not in crop_state and seeds > 0:
        hint = "E: Plantar"
    elif crop_state.get((player_r, player_c)) == 3:
        hint = "E: Colher (+moedas)"
    elif tile_here == T_SOIL and seeds == 0:
        hint = "Sem sementes (compre na loja: B)"
    else:
        hint = "B: Loja | E: Interagir"

    hint_txt = font.render(hint, True, WHITE)
    pygame.draw.rect(screen, DARK, (0, HEIGHT - 28, WIDTH, 28))
    screen.blit(hint_txt, (10, HEIGHT - 22))

    # loja
    if shop_open:
        draw_shop()

    pygame.display.update()

pygame.quit()
sys.exit()