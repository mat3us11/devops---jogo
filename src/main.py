"""
Harvest Farm Constructor - Main V5
Entry point: tela cheia, menu inicial, loop de jogo, save/load automático.
"""
import pygame
import sys
import random
import math

pygame.init()

# ─── configuração de tela cheia ────────────────────────────────────────────────
info = pygame.display.Info()
SW = info.current_w
SH = info.current_h
screen = pygame.display.set_mode((SW, SH), pygame.FULLSCREEN)
pygame.display.set_caption("🌾 Harvest Farm Constructor")

# injeta a resolução do monitor no módulo engine antes de importar as classes
import src.engine as engine_mod
engine_mod.SW = SW
engine_mod.SH = SH
engine_mod.WIDTH = SW
engine_mod.HEIGHT = SH

from src.engine import (
    World, Player, Camera, UIManager, WeatherSystem,
    Particle, FloatingText, PLANT_DB, PLANT_LIST, TILE, SEASONS,
    C_WHITE, C_YELLOW, C_GOLD, C_GREEN_BRIGHT, C_RED, C_BLUE, C_ORANGE,
    T_SOIL, T_HOUSE, T_BARN, T_MARKET, T_WATER,
    draw_player_sprite,
)
from src.menu import run_menu
from src.savesystem import save_game, load_game, apply_save, save_exists, delete_save

clock = pygame.time.Clock()
font    = pygame.font.SysFont("segoeui", 18, bold=True)
font_sm = pygame.font.SysFont("segoeui", 14)
font_lg = pygame.font.SysFont("segoeui", 30, bold=True)

# ─── tecla de salvar ─────────────────────────────────────────────────────────
AUTOSAVE_INTERVAL = 60 * 3   # salva automaticamente a cada 3 minutos reais
autosave_counter  = 0

# ─── funções auxiliares ─────────────────────────────────────────────────────────
def make_new_game():
    w  = World(60, 40)
    pl = Player(5 * TILE, 6 * TILE)
    cam= Camera()
    ui = UIManager(SW, SH)
    we = WeatherSystem(SW, SH)
    we.roll_weather("Primavera")
    return w, pl, cam, ui, we

def load_game_state():
    data = load_game()
    if data is None:
        return None
    w, pl, cam, ui, we = make_new_game()
    day, hour, minute, sidx = apply_save(data, pl, w, we)
    return w, pl, cam, ui, we, day, hour, minute, sidx

def spawn_particles(wx, wy, color, count=12, gravity=0.05):
    for _ in range(count):
        particles.append(Particle(
            wx, wy, color,
            life=random.randint(25, 50),
            vx=random.uniform(-1.5, 1.5),
            vy=random.uniform(-2.5, -0.5),
            size=random.randint(3, 6),
            gravity=gravity
        ))

def spawn_float(wx, wy, text, color):
    floating_texts.append(FloatingText(wx, wy, text, color, font))

def advance_time(dt_real):
    global time_accumulator, game_minute, game_hour, game_day
    global season_idx, current_season, next_weather_day
    time_accumulator += dt_real * MINS_PER_REAL_SECOND
    while time_accumulator >= 1.0:
        time_accumulator -= 1.0
        game_minute += 1
        if game_minute >= 60:
            game_minute = 0
            game_hour  += 1
            if game_hour >= 24:
                game_hour  = 0
                game_day  += 1
                if weather.get_auto_water():
                    for (r,c) in list(world.crop_state.keys()):
                        world.soil_wetness[(r,c)] = 800
                if (game_day - 1) % days_in_season == 0 and game_day > 1:
                    season_idx     = (season_idx + 1) % 4
                    current_season = SEASONS[season_idx]
                    weather.roll_weather(current_season)
                if game_day >= next_weather_day:
                    weather.roll_weather(current_season)
                    next_weather_day = game_day + random.randint(2, 4)

def do_interact(mx_world, my_world, right_click=False):
    tc = int(mx_world // TILE)
    tr = int(my_world // TILE)
    dist_px = math.hypot(player.x + TILE//2 - mx_world, player.y + TILE//2 - my_world)
    if dist_px > TILE * 3.5:
        return None
    if not (0 <= tr < world.rows and 0 <= tc < world.cols):
        return None

    tile_val = world.grid[tr][tc]
    sel      = ui.hotbar_items[ui.active_slot]

    if tile_val == T_HOUSE:
        spawn_float(player.x, player.y - 20, "💤 Até amanhã!", C_WHITE)
        spawn_particles(player.x + TILE//2, player.y, (200,180,255), 20)
        return ("sleep", None)

    if tile_val == T_SOIL:
        if right_click or sel == "regador":
            world.soil_wetness[(tr,tc)] = 600
            spawn_particles(tc*TILE+TILE//2, tr*TILE+TILE//2, (100,180,255), 14, gravity=-0.02)
        else:
            plant_here = world.crop_state.get((tr,tc))
            if plant_here and plant_here["stage"] == 3:
                return ("harvest", (tr,tc))
            elif not plant_here:
                qty = player.seed_inventory.get(sel, 0)
                if qty > 0:
                    if world.soil_wetness.get((tr,tc),0) == 0:
                        world.soil_wetness[(tr,tc)] = 1
                    player.seed_inventory[sel] -= 1
                    data = PLANT_DB[sel]
                    boost = player.growth_boost
                    gtimer = max(30, int(data["growth_s"] * 60 * (1 - boost/100)))
                    world.crop_state[(tr,tc)] = {"type": sel, "stage": 1}
                    world.crop_timer[(tr,tc)]  = gtimer
                    spawn_particles(tc*TILE+TILE//2, tr*TILE+TILE//2, (80,200,80), 8)
                    spawn_float(tc*TILE+TILE//2, tr*TILE-10, "Plantado! 🌱", C_GREEN_BRIGHT)
                else:
                    spawn_float(player.x, player.y-20, "Sem sementes!", C_RED)
    return None

def check_achievements():
    for cond, key, msg in [
        (player.coins >= 500,   "rico",   "🏆 Primeiros $500 ganhos!"),
        (player.level >= 3,     "nivel3", "⭐ Nível 3 alcançado!"),
        (player.level >= 5,     "nivel5", "🌟 Nível 5 — Fazendeiro Expert!"),
    ]:
        if cond and key not in shown_achievements:
            shown_achievements.add(key)
            spawn_float(view_w()//2, SH//3, msg, C_GOLD)

def view_w():
    return SW - ui.sidebar_w

# ─── loop do menu principal ──────────────────────────────────────────────────
while True:
    choice = run_menu(screen, clock)

    if choice == "quit":
        pygame.quit(); sys.exit()

    if choice == "new":
        delete_save()
        world, player, camera, ui, weather = make_new_game()
        game_day=1; game_hour=8; game_minute=0; season_idx=0
        current_season = SEASONS[0]
    else:  # continue
        result = load_game_state()
        if result is None:
            world, player, camera, ui, weather = make_new_game()
            game_day=1; game_hour=8; game_minute=0; season_idx=0
            current_season = SEASONS[0]
        else:
            world, player, camera, ui, weather, game_day, game_hour, game_minute, season_idx = result
            current_season = SEASONS[season_idx % 4]

    days_in_season   = 7
    next_weather_day = 2
    time_accumulator = 0.0
    MINS_PER_REAL_SECOND = 10

    particles      = []
    floating_texts = []
    shown_achievements = set()
    tick            = 0
    smoke_tick      = 0
    pending_sleep   = False
    sleep_fade      = 0
    autosave_counter= 0

    # ─── loop do jogo ───────────────────────────────────────────────────────────
    back_to_menu = False
    running      = True
    while running:
        dt = clock.tick(60) / 1000.0
        tick += 1
        autosave_counter += 1

        advance_time(dt)
        weather.update(tick, current_season)
        for npc in world.npcs:
            npc.update(world)

        # Auto-save
        if autosave_counter >= AUTOSAVE_INTERVAL:
            autosave_counter = 0
            save_game(player, world, game_day, game_hour, game_minute,
                      season_idx, weather.weather)
            spawn_float(view_w()//2 - TILE, ui.topbar_h + 20, "💾 Salvo!", (120,220,160))

        mouse_pos = pygame.mouse.get_pos()

        # ── EVENTS ──
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_game(player, world, game_day, game_hour, game_minute,
                          season_idx, weather.weather)
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                k = event.key
                if k == pygame.K_ESCAPE:
                    save_game(player, world, game_day, game_hour, game_minute,
                              season_idx, weather.weather)
                    spawn_float(view_w()//2, SH//2, "💾 Jogo salvo!", C_YELLOW)
                    back_to_menu = True
                    running = False
                if pygame.K_1 <= k <= pygame.K_9:
                    idx = k - pygame.K_1
                    if idx < len(ui.hotbar_items):
                        ui.active_slot = idx
                if k == pygame.K_TAB:
                    ui.active_tab = (ui.active_tab + 1) % 3
                if k == pygame.K_F1:
                    ui.show_help = not ui.show_help
                if k == pygame.K_F5:
                    save_game(player, world, game_day, game_hour, game_minute,
                              season_idx, weather.weather)
                    spawn_float(view_w()//2, ui.topbar_h + 20, "💾 Salvo manualmente!", C_GREEN_BRIGHT)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if ui.handle_hotbar_click(mouse_pos):
                    pass
                elif ui.handle_click(mouse_pos):
                    # ações da loja e upgrades via hover no painel lateral
                    if mouse_pos[0] > SW - ui.sidebar_w and mouse_pos[1] > 42:
                        actions = ui.draw_sidebar(pygame.Surface((1,1)), player, mouse_pos, world)
                        for act in actions:
                            if act[0] == "buy_seed":
                                _, pname, cost = act
                                if player.coins >= cost:
                                    player.coins -= cost
                                    player.seed_inventory[pname] += 5
                                    ui.shop_message    = f"+5 {pname.capitalize()}! ✅"
                                    ui.shop_msg_timer  = 120
                                    spawn_float(player.x, player.y-20, f"+5 {pname} 🌱", C_GREEN_BRIGHT)
                                else:
                                    ui.shop_message   = "Ouro insuficiente! ❌"
                                    ui.shop_msg_timer = 120
                                break
                            elif act[0] == "upgrade":
                                _, key, cost = act
                                if player.coins >= cost:
                                    player.coins -= cost
                                    if key == "expand" and world.cols < 100:
                                        world.cols += 6; world.rows += 4 # expande o mundo
                                        world.generate()
                                        spawn_float(player.x, player.y-20, "🏗️ Fazenda expandida!", C_YELLOW)
                                    elif key == "growth":
                                        player.growth_boost = min(75, player.growth_boost + 25)
                                        spawn_float(player.x, player.y-20, f"🌿 Crescimento +25%!", C_GREEN_BRIGHT)
                                    elif key == "wetness":
                                        spawn_float(player.x, player.y-20, "💧 Solo retém mais água!", C_BLUE)
                                    elif key == "silo":
                                        spawn_float(player.x, player.y-20, "🏚️ Silo construído!", C_ORANGE)
                                    ui.shop_message   = "Comprado! ✅"
                                    ui.shop_msg_timer = 150
                                else:
                                    ui.shop_message   = "Ouro insuficiente! ❌"
                                    ui.shop_msg_timer = 120
                                break
                else:
                    mx_w = mouse_pos[0] + camera.x
                    my_w = mouse_pos[1] + camera.y
                    result = do_interact(mx_w, my_w, right_click=(event.button == 3))
                    if result:
                        action, data = result
                        if action == "sleep":
                            pending_sleep = True
                        elif action == "harvest":
                            tr, tc = data
                            plant = world.crop_state.pop((tr,tc), None)
                            world.crop_timer.pop((tr,tc), None)
                            if plant:
                                pdata  = PLANT_DB[plant["type"]]
                                reward = pdata["reward"]
                                player.coins += reward
                                leveled = player.gain_xp(reward * 2)
                                spawn_particles(tc*TILE+TILE//2, tr*TILE+TILE//2,
                                                pdata["color"], 20, gravity=0.08)
                                spawn_float(tc*TILE+TILE//2, tr*TILE-16,
                                            f"+${reward} {pdata['emoji']}", C_GOLD)
                                if leveled:
                                    spawn_float(player.x, player.y-40,
                                                f"⭐ LEVEL UP! Nv {player.level}", (120,220,255))

        # ── movimentação do personagem ──
        keys = pygame.key.get_pressed()
        dx = dy = 0
        speed = player.speed * dt
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: dx=-speed; player.direction="left"
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx= speed; player.direction="right"
        if keys[pygame.K_UP]    or keys[pygame.K_w]: dy=-speed; player.direction="up"
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: dy= speed; player.direction="down"
        player.moving = dx != 0 or dy != 0
        if player.moving: player.frame += 1 # colisão no eixo x
        nx = player.x + dx
        fr = int((player.y + TILE - 4) // TILE)
        if not (world.is_blocked(fr, int((nx+4)//TILE)) or world.is_blocked(fr, int((nx+TILE-4)//TILE))):
            player.x = nx
        # colisão no eixo y
        ny = player.y + dy
        if not world.is_blocked(int((ny+TILE-4)//TILE), int((player.x+TILE//2)//TILE)):
            player.y = ny

        vw = view_w()
        camera.update(player.x, player.y, world.cols*TILE, world.rows*TILE, vw, SH)

        # diminui a umidade do solo a cada frame
        for pos in list(world.soil_wetness):
            world.soil_wetness[pos] -= 1
            if world.soil_wetness[pos] <= 0:
                del world.soil_wetness[pos]

        to_grow = []
        for pos, timer in list(world.crop_timer.items()):
            if world.soil_wetness.get(pos,0) > 0:
                world.crop_timer[pos] = timer - 1
                if world.crop_timer[pos] <= 0:
                    to_grow.append(pos)

        for pos in to_grow:
            plant = world.crop_state.get(pos)
            if plant and plant["stage"] < 3:
                plant["stage"] += 1
                data  = PLANT_DB[plant["type"]]
                boost = player.growth_boost
                if plant["stage"] < 3:
                    world.crop_timer[pos] = max(30, int(data["growth_s2"]*60*(1-boost/100)))
                else:
                    world.crop_timer.pop(pos, None)
                world.soil_wetness.pop(pos, None)
                if plant["stage"] == 3:
                    tc2,tr2 = pos[1], pos[0]
                    spawn_float(tc2*TILE+TILE//2, tr2*TILE-10,
                                f"{data['emoji']} Pronto!", data["color"])

        # fumaça da chaminé da casa
        smoke_tick += 1
        if smoke_tick % 22 == 0:
            particles.append(Particle(
                2*TILE + TILE - 10, 2*TILE - 5,
                (190,190,190), life=random.randint(40,70),
                vx=random.uniform(-0.3,0.3), vy=random.uniform(-0.8,-0.4),
                size=random.randint(4,9), gravity=-0.02
            ))

        for p in particles[:]:
            p.update()
            if p.life<=0: particles.remove(p)
        for f in floating_texts[:]:
            f.update()
            if f.life<=0: floating_texts.remove(f)

        check_achievements()
        if ui.shop_msg_timer > 0:
            ui.shop_msg_timer -= 1

        # Dormir
        if pending_sleep:
            sleep_fade = min(255, sleep_fade+8)
            if sleep_fade >= 240:
                pending_sleep = False
                game_hour=7; game_minute=30; game_day+=1
                for pos in list(world.crop_timer):
                    world.crop_timer[pos] = max(0, world.crop_timer[pos]-300)
                save_game(player, world, game_day, game_hour, game_minute,
                          season_idx, weather.weather)
        else:
            sleep_fade = max(0, sleep_fade-6)

        # ═══════════════════════════════
        # renderização
        # ═══════════════════════════════
        weather.draw_sky(screen, game_hour, game_minute)
        screen.fill((30,40,25), (0, SH//4, vw, SH-SH//4))

        sc = max(0, int(camera.x//TILE)-1)
        sr = max(0, int(camera.y//TILE)-1)
        ec = min(world.cols, sc + vw//TILE + 3)
        er = min(world.rows, sr + SH//TILE + 3)

        for r in range(sr, er):
            for c in range(sc, ec):
                world.draw_tile(screen, r, c, camera.x, camera.y, tick, current_season)

        world.draw_buildings(screen, camera.x, camera.y)
        world.draw_crops(screen, camera.x, camera.y, tick)

        for npc in world.npcs:
            npc.draw(screen, camera.x, camera.y)

        # cursor de destaque no tile sob o mouse
        if mouse_pos[0] < vw and mouse_pos[1] > ui.topbar_h and mouse_pos[1] < SH-70:
            mxw = mouse_pos[0]+camera.x; myw = mouse_pos[1]+camera.y
            htc = int(mxw//TILE); htr = int(myw//TILE)
            dist = math.hypot(player.x+TILE//2-mxw, player.y+TILE//2-myw)
            in_range = dist < TILE*3.5
            if 0<=htr<world.rows and 0<=htc<world.cols:
                cs = pygame.Surface((TILE,TILE), pygame.SRCALPHA)
                if in_range:
                    cs.fill((255,255,255,45))
                    pygame.draw.rect(cs,(255,255,255,160),(0,0,TILE,TILE),2)
                else:
                    cs.fill((255,60,60,20))
                    pygame.draw.rect(cs,(255,60,60,100),(0,0,TILE,TILE),2)
                screen.blit(cs,(htc*TILE-int(camera.x), htr*TILE-int(camera.y)))

                # Dica de ferramenta
                plant_here = world.crop_state.get((htr,htc))
                tile_here  = world.grid[htr][htc]
                if plant_here:
                    s = ["🌱 Semente","🌿 Crescendo","✅ Pronto!"][plant_here["stage"]-1]
                    tip = f"{plant_here['type'].capitalize()} — {s}"
                elif tile_here == T_HOUSE:   tip = "🏠 Casa — Clique para dormir (salva!)"
                elif tile_here == T_BARN:    tip = "🏚️ Celeiro"
                elif tile_here == T_MARKET:  tip = "🛒 Mercado — use a aba Loja →"
                elif tile_here == T_WATER:   tip = "💧 Água"
                elif tile_here == T_SOIL:
                    sel = ui.hotbar_items[ui.active_slot]
                    if sel=="regador": tip="Clique: Regar | Clique Dir: Regar"
                    elif player.seed_inventory.get(sel,0)>0: tip=f"Clique: Plantar {sel} | Dir: Regar"
                    else: tip=f"Sem {sel} — compre na Loja →"
                else: tip=""
                if tip and in_range:
                    ts=font_sm.render(tip,True,C_WHITE)
                    tb=pygame.Rect(mouse_pos[0]+14,mouse_pos[1]-28,ts.get_width()+12,22)
                    if tb.right>vw: tb.x=mouse_pos[0]-tb.w-4
                    pygame.draw.rect(screen,(20,25,35),tb,border_radius=5)
                    pygame.draw.rect(screen,(70,80,100),tb,1,border_radius=5)
                    screen.blit(ts,(tb.x+6,tb.y+3))

        # personagem do jogador
        px = int(player.x-camera.x); py = int(player.y-camera.y)
        if player.sprite:
            screen.blit(player.sprite,(px,py))
        else:
            sel_item = ui.hotbar_items[ui.active_slot]
            draw_player_sprite(screen, px, py, player.direction, player.frame, sel_item)

        for p in particles:    p.draw(screen, camera.x, camera.y)
        for f in floating_texts: f.draw(screen, camera.x, camera.y)

        weather.draw_clouds(screen)
        weather.draw_weather_fx(screen)
        ui.draw_night_overlay(screen, game_hour, game_minute)

        # overlay de dormir (fade preto + texto)
        if sleep_fade > 0:
            bl = pygame.Surface((SW,SH), pygame.SRCALPHA)
            bl.fill((0,0,0,sleep_fade))
            screen.blit(bl,(0,0))
            if sleep_fade > 150:
                zt=font_lg.render("💤 Dormindo... novo dia!", True, C_WHITE)
                screen.blit(zt,(SW//2-zt.get_width()//2, SH//2-20))

        # ── camadas da interface (sempre por cima) ──
        ui.draw_topbar(screen, player, game_day, game_hour, game_minute, current_season, weather.weather)
        ui.draw_sidebar(screen, player, mouse_pos, world)
        ui.draw_hotbar(screen, player, mouse_pos)

        # bolha do clima no centro superior
        wb = pygame.Rect((vw-130)//2, ui.topbar_h+8, 130, 28)
        wc = {"Ensolarado":(200,180,30),"Nublado":(100,110,130),"Chuvoso":(60,100,160),
              "Tempestade":(60,50,120),"Nevando":(160,180,220)}.get(weather.weather,(80,80,80))
        wsurf=pygame.Surface((wb.w,wb.h),pygame.SRCALPHA)
        wsurf.fill((*wc,200))
        pygame.draw.rect(wsurf,(*wc,200),wsurf.get_rect(),border_radius=8)
        screen.blit(wsurf,wb.topleft)
        wt=font_sm.render(weather.weather,True,C_WHITE)
        screen.blit(wt,(wb.x+(wb.w-wt.get_width())//2,wb.y+5))

        # dica de controles no rodapé
        sv=font_sm.render("ESC – Menu  |  F5 – Salvar  |  F1 – Ajuda  |  WASD – Mover  |  Clique – Interagir",
                           True,(90,100,115))
        screen.blit(sv,((vw-sv.get_width())//2, SH-20))

        # tela de ajuda (f1)
        if ui.show_help:
            ho=pygame.Surface((vw,SH),pygame.SRCALPHA)
            ho.fill((0,0,0,175))
            screen.blit(ho,(0,0))
            lines=[("🎮 CONTROLES",C_GOLD),("WASD / Setas — Mover",C_WHITE),
                   ("Clique Esquerdo — Plantar / Colher",C_WHITE),
                   ("Clique Direito  — Regar terra",C_WHITE),
                   ("1-9 — Selecionar item no hotbar",C_WHITE),
                   ("TAB — Mudar aba lateral",C_WHITE),
                   ("F5  — Salvar manualmente",C_WHITE),
                   ("ESC — Salvar e ir ao menu",C_WHITE),
                   ("",""), ("🌾 DICAS",C_GOLD),
                   ("• Regue a terra antes de plantar",C_WHITE),
                   ("• Chuva rega automaticamente!",C_WHITE),
                   ("• Durma na casa — salva o jogo!",C_WHITE),
                   ("• Compre upgrades na aba 'Obras'",C_WHITE)]
            yh=SH//4
            for text,col in lines:
                if text:
                    ts=font.render(text,True,col)
                    screen.blit(ts,(vw//2-ts.get_width()//2,yh))
                yh+=30
            esc_t=font_sm.render("F1 para fechar",True,(150,150,160))
            screen.blit(esc_t,(vw//2-esc_t.get_width()//2,yh+10))

        pygame.display.flip()

    # Back to menu or quit
    if not back_to_menu:
        break

pygame.quit()
sys.exit()