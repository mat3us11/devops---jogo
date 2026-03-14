"""
Harvest Farm Constructor - Engine V5
Motor de jogo completo com arte vetorial, sistemas ricos e UI avançada.
"""
import pygame
import math
import random
import sys
from pathlib import Path

# ==========================================
# constantes do jogo
# ==========================================
TILE = 48
WIDTH, HEIGHT = 1200, 720
SW = WIDTH  # atalho para largura da tela
SH = HEIGHT

# paleta de cores
C_SKY_DAY    = (135, 206, 235)
C_SKY_DAWN   = (255, 140, 60)
C_SKY_DUSK   = (180, 80, 120)
C_SKY_NIGHT  = (10, 15, 40)
C_GRASS      = (106, 168, 79)
C_GRASS_DARK = (69, 129, 49)
C_SOIL_DRY   = (160, 110, 60)
C_SOIL_WET   = (100, 65, 30)
C_FENCE      = (139, 90, 43)
C_FENCE_DARK = (100, 60, 20)
C_WATER      = (64, 164, 223)
C_WATER_DARK = (30, 90, 170)
C_PATH       = (200, 170, 120)
C_PATH_DARK  = (160, 130, 80)
C_UI_BG      = (28, 32, 38)
C_UI_PANEL   = (38, 43, 52)
C_UI_BORDER  = (70, 80, 95)
C_UI_HOVER   = (55, 65, 80)
C_UI_ACTIVE  = (80, 130, 200)
C_WHITE      = (245, 248, 252)
C_YELLOW     = (255, 210, 50)
C_GREEN_BRIGHT=(80, 220, 100)
C_RED        = (220, 80, 80)
C_ORANGE     = (255, 160, 30)
C_PURPLE     = (160, 80, 220)
C_BLUE       = (80, 140, 230)
C_GOLD       = (255, 195, 10)
C_SHADOW     = (0, 0, 0, 80)

# tipos de tile do mapa
T_GRASS=0; T_FENCE=1; T_SOIL=2; T_HOUSE=3; T_BARN=4
T_BLOCK=5; T_PATH=6; T_WATER=7; T_ORCHARD=8; T_MARKET=9

# estações do ano
SEASONS = ["Primavera", "Verão", "Outono", "Inverno"]
SEASON_COLORS = {
    "Primavera": C_GRASS,
    "Verão":     (80, 150, 50),
    "Outono":    (160, 120, 40),
    "Inverno":   (180, 190, 200),
}

# tipos de clima
WEATHER_TYPES = ["Ensolarado", "Nublado", "Chuvoso", "Tempestade", "Nevando"]

# banco de dados das plantas
PLANT_DB = {
    "trigo":   {"emoji":"🌾","growth_s":8,"growth_s2":16,"reward":8, "buy":10,"stages":3,"color":(220,200,60),"color2":(180,160,20)},
    "milho":   {"emoji":"🌽","growth_s":12,"growth_s2":24,"reward":15,"buy":18,"stages":3,"color":(255,215,0),"color2":(200,160,0)},
    "tomate":  {"emoji":"🍅","growth_s":20,"growth_s2":36,"reward":25,"buy":28,"stages":3,"color":(220,60,60),"color2":(180,30,30)},
    "batata":  {"emoji":"🥔","growth_s":6, "growth_s2":12,"reward":6, "buy":8, "stages":3,"color":(210,180,100),"color2":(160,130,60)},
    "cenoura": {"emoji":"🥕","growth_s":10,"growth_s2":20,"reward":12,"buy":14,"stages":3,"color":(230,130,30),"color2":(190,90,10)},
    "morango": {"emoji":"🍓","growth_s":25,"growth_s2":48,"reward":40,"buy":50,"stages":3,"color":(220,50,80),"color2":(180,20,50)},
    "abóbora": {"emoji":"🎃","growth_s":30,"growth_s2":60,"reward":55,"buy":65,"stages":3,"color":(230,130,20),"color2":(190,90,10)},
    "uva":     {"emoji":"🍇","growth_s":40,"growth_s2":80,"reward":80,"buy":90,"stages":3,"color":(130,30,180),"color2":(80,10,140)},
}
PLANT_LIST = list(PLANT_DB.keys())

# ==========================================
# funções utilitárias
# ==========================================
def resource_path(rel):
    if hasattr(sys,"_MEIPASS"):
        return str(Path(sys._MEIPASS)/rel)
    return str(Path(__file__).resolve().parent.parent/rel)

def load_sprite(path, size):
    try:
        img = pygame.image.load(resource_path(path)).convert_alpha()
        return pygame.transform.scale(img, (size,size))
    except:
        return None

def draw_rounded_rect(surf, color, rect, radius=8, border=0, border_color=None):
    pygame.draw.rect(surf, color, rect, border_radius=radius)
    if border and border_color:
        pygame.draw.rect(surf, border_color, rect, border, border_radius=radius)

def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i]-c1[i])*t) for i in range(3))

def draw_shadow(surf, x, y, w, h, alpha=60):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    s.fill((0,0,0,alpha))
    surf.blit(s, (x,y))

# ==========================================
# arte: funções de desenho procedural dos tiles
# ==========================================
def draw_grass_tile(surf, x, y, variant=0, season="Primavera"):
    gc = SEASON_COLORS.get(season, C_GRASS)
    gd = tuple(max(0,c-30) for c in gc)
    pygame.draw.rect(surf, gc, (x,y,TILE,TILE))
    # linhas sutis de grade
    pygame.draw.line(surf, gd, (x,y+TILE-1),(x+TILE,y+TILE-1),1)
    pygame.draw.line(surf, gd, (x+TILE-1,y),(x+TILE-1,y+TILE),1)
    # detalhe de folhas de grama
    if variant == 1:
        for i in range(4):
            bx = x+6+i*10+random.randint(-2,2)
            pygame.draw.line(surf, gd, (bx, y+TILE-4),(bx-2,y+TILE-10),2)

def draw_fence_tile(surf, x, y):
    pygame.draw.rect(surf, C_GRASS, (x,y,TILE,TILE))
    # postes da cerca
    pygame.draw.rect(surf, C_FENCE_DARK, (x+2,y+2,8,TILE-4))
    pygame.draw.rect(surf, C_FENCE_DARK, (x+TILE-10,y+2,8,TILE-4))
    # trilhos horizontais
    pygame.draw.rect(surf, C_FENCE, (x+2,y+8,TILE-4,6))
    pygame.draw.rect(surf, C_FENCE, (x+2,y+TILE-18,TILE-4,6))
    # topo dos postes
    pygame.draw.polygon(surf, (180,120,60), [(x+2,y+2),(x+10,y+2),(x+6,y-4)])
    pygame.draw.polygon(surf, (180,120,60), [(x+TILE-10,y+2),(x+TILE-2,y+2),(x+TILE-6,y-4)])

def draw_soil_tile(surf, x, y, wet=False):
    c = C_SOIL_WET if wet else C_SOIL_DRY
    cd = tuple(max(0,v-20) for v in c)
    pygame.draw.rect(surf, c, (x,y,TILE,TILE))
    # linhas de textura da terra
    for i in range(4):
        ry = y+4+i*10
        pygame.draw.line(surf, cd, (x+4,ry),(x+TILE-4,ry),1)
    if wet:
        # brilho de umidade
        s = pygame.Surface((TILE,TILE),pygame.SRCALPHA)
        s.fill((40,80,200,30))
        surf.blit(s,(x,y))

def draw_path_tile(surf, x, y):
    pygame.draw.rect(surf, C_PATH, (x,y,TILE,TILE))
    pygame.draw.rect(surf, C_PATH_DARK, (x,y,TILE,TILE),1)
    # padrão de pedras do caminho
    for ri in range(3):
        for ci in range(2):
            px = x+4+ci*22 + (ri%2)*11
            py = y+4+ri*14
            pygame.draw.rect(surf,(180,150,100),(px,py,18,10),border_radius=2)
            pygame.draw.rect(surf,(150,120,70),(px,py,18,10),1,border_radius=2)

def draw_water_tile(surf, x, y, tick=0):
    pygame.draw.rect(surf, C_WATER, (x,y,TILE,TILE))
    # ondas animadas com seno
    for i in range(3):
        wx = x+4+i*14
        wy = y+TILE//2 + int(3*math.sin(tick*0.05+i*1.2))
        pygame.draw.arc(surf, C_WATER_DARK, (wx,wy,20,8),0,math.pi,2)
    # brilho da água
    s = pygame.Surface((TILE,TILE),pygame.SRCALPHA)
    shimmer_alpha = int(20+10*math.sin(tick*0.08))
    s.fill((255,255,255,shimmer_alpha))
    surf.blit(s,(x,y))

def draw_house(surf, x, y, size):
    hw = size*2
    hh = size*2
    # sombra da casa
    draw_shadow(surf, x+8, y+hh-8, hw, 16, 60)
    # paredes
    pygame.draw.rect(surf,(220,200,170),(x,y+hh//3,hw,hh*2//3))
    # porta
    pygame.draw.rect(surf,(120,70,30),(x+hw//2-10,y+hh-28,20,28))
    pygame.draw.circle(surf,(200,160,80),(x+hw//2-3,y+hh-14),3)
    # janelas
    for wx in [x+10,x+hw-26]:
        pygame.draw.rect(surf,(150,220,255),(wx,y+hh//2-4,16,16))
        pygame.draw.line(surf,(100,160,200),(wx+8,y+hh//2-4),(wx+8,y+hh//2+12),1)
        pygame.draw.line(surf,(100,160,200),(wx,y+hh//2+4),(wx+16,y+hh//2+4),1)
        pygame.draw.rect(surf,(150,100,50),(wx,y+hh//2-4,16,16),2)
    # telhado
    roof_pts = [(x-6,y+hh//3),(x+hw//2,y-10),(x+hw+6,y+hh//3)]
    pygame.draw.polygon(surf,(180,60,50),roof_pts)
    pygame.draw.polygon(surf,(140,40,30),roof_pts,3)
    # chaminé
    pygame.draw.rect(surf,(160,80,60),(x+hw-22,y-18,12,hh//3+5))
    # fumaça é criada via partículas no loop principal
    return None

def draw_barn(surf, x, y, size):
    hw = size*2
    hh = size*2
    draw_shadow(surf, x+8, y+hh-8, hw, 16, 60)
    # corpo principal do celeiro
    pygame.draw.rect(surf,(180,60,40),(x,y+hh//4,hw,hh*3//4))
    # porta grande do celeiro
    pygame.draw.rect(surf,(130,40,20),(x+hw//2-16,y+hh//2,32,hh//2))
    # padrão X na porta
    pygame.draw.line(surf,(100,30,10),(x+hw//2-16,y+hh//2),(x+hw//2+16,y+hh),(2))
    pygame.draw.line(surf,(100,30,10),(x+hw//2+16,y+hh//2),(x+hw//2-16,y+hh),(2))
    # telhado arredondado do celeiro
    barn_top = pygame.Rect(x-4, y+hh//4-hh//3, hw+8, hh//2)
    pygame.draw.ellipse(surf,(160,50,30),barn_top)
    # friso branco decorativo
    pygame.draw.rect(surf,(240,230,220),(x,y+hh//4,hw,6))

def draw_market(surf, x, y, size):
    hw = size*2
    hh = size*2
    draw_shadow(surf, x+8, y+hh-8, hw, 16, 60)
    # base do mercado
    pygame.draw.rect(surf,(240,220,180),(x,y+hh//3,hw,hh*2//3))
    # toldo
    awning_pts = [(x-4,y+hh//3),(x+hw+4,y+hh//3),(x+hw,y+hh//3-18),(x,y+hh//3-18)]
    pygame.draw.polygon(surf,(80,160,220),awning_pts)
    # listras decorativas no toldo
    for i in range(5):
        ax = x+i*(hw//5)
        pygame.draw.line(surf,(60,120,180),(ax,y+hh//3-18),(ax,y+hh//3),2)
    # balcão
    pygame.draw.rect(surf,(180,140,80),(x+8,y+hh-24,hw-16,20))
    # placa do mercado
    pygame.draw.rect(surf,(255,200,50),(x+hw//2-24,y+hh//3-40,48,20),border_radius=4)
    font_small = pygame.font.SysFont("segoeui",12,bold=True)
    label = font_small.render("MERCADO",True,(60,40,10))
    surf.blit(label,(x+hw//2-24+2,y+hh//3-37))

def draw_crop(surf, x, y, plant_name, stage, tick=0):
    """desenha uma planta no tile. estágio 1=semente, 2=crescendo, 3=madura."""
    data = PLANT_DB.get(plant_name, PLANT_DB["trigo"])
    c1 = data["color"]
    c2 = data["color2"]
    cx = x + TILE//2
    cy = y + TILE

    if stage == 1:
        # semente: brotos verdes pequenos
        for i in range(2):
            sx = cx - 5 + i*10
            sway = int(1.5*math.sin(tick*0.04+i))
            pygame.draw.line(surf,(80,180,60),(sx,cy-2),(sx+sway,cy-12),2)
            pygame.draw.circle(surf,(100,210,80),(sx+sway,cy-13),3)

    elif stage == 2:
        # crescimento médio: caule mais alto com folhas
        sway = int(2*math.sin(tick*0.03))
        for i in range(3):
            sx = cx - 10 + i*10
            pygame.draw.line(surf,(60,140,30),(sx,cy),(sx+sway,cy-22),2)
        # folhas laterais
        pygame.draw.ellipse(surf,(80,170,40),(cx-14+sway,cy-20,14,7))
        pygame.draw.ellipse(surf,(80,170,40),(cx+sway,cy-26,14,7))

    elif stage == 3:
        # matura: planta completa com fruto ou grão
        sway = int(1.5*math.sin(tick*0.03))
        # caule
        for i in range(3):
            sx = cx - 10 + i*10
            pygame.draw.line(surf,(70,140,20),(sx,cy),(sx+sway,cy-28),2)
        # fruto específico de cada planta no topo
        if plant_name in ("trigo","batata"):
            # espigas de grão
            for i in range(5):
                gx = cx - 10 + i*5 + sway
                pygame.draw.ellipse(surf, c1,(gx-3,cy-36,7,14))
                pygame.draw.ellipse(surf, c2,(gx-3,cy-36,7,14),1)
        elif plant_name in ("milho","cenoura"):
            # fruto único e grande
            pygame.draw.ellipse(surf,c1,(cx-8+sway,cy-36,16,22))
            pygame.draw.ellipse(surf,c2,(cx-8+sway,cy-36,16,22),1)
        else:
            # grupo de frutas redondas (berries)
            for i in range(4):
                fx = cx - 8 + (i%2)*10 + sway
                fy = cy - 30 - (i//2)*10
                pygame.draw.circle(surf,c1,(fx,fy),7)
                pygame.draw.circle(surf,c2,(fx,fy),7,1)
                pygame.draw.circle(surf,(255,255,255),(fx-2,fy-2),2)

def draw_player_sprite(surf, x, y, direction="down", frame=0, held_item=None):
    """desenha o personagem do jogador com detalhes."""
    cx = int(x)
    cy = int(y)
    # sombra elíptica do personagem
    pygame.draw.ellipse(surf,(0,0,0,80),(cx-10,cy+36,28,10))

    # macacão azul
    pygame.draw.rect(surf,(60,100,200),(cx-7,cy+12,22,20),border_radius=4)
    # camisa por baixo
    pygame.draw.rect(surf,(250,200,160),(cx-5,cy+10,18,14),border_radius=3)
    # pernas
    pygame.draw.rect(surf,(60,100,200),(cx-7,cy+28,9,16),border_radius=3)
    pygame.draw.rect(surf,(60,100,200),(cx+6,cy+28,9,16),border_radius=3)
    # botas
    pygame.draw.rect(surf,(80,50,20),(cx-8,cy+40,11,8),border_radius=2)
    pygame.draw.rect(surf,(80,50,20),(cx+5,cy+40,11,8),border_radius=2)
    # braços
    arm_off = int(3*math.sin(frame*0.25)) if frame else 0
    pygame.draw.rect(surf,(250,200,160),(cx-14,cy+12,8,14),border_radius=3)
    pygame.draw.rect(surf,(250,200,160),(cx+14,cy+12,8,14),border_radius=3)
    # cabeça
    pygame.draw.circle(surf,(250,200,160),(cx+4,cy+8),10)
    # olhos
    eye_y = cy+7
    if direction in ("down","left","right"):
        pygame.draw.circle(surf,(40,25,10),(cx+1,eye_y),2)
        pygame.draw.circle(surf,(40,25,10),(cx+7,eye_y),2)
        # sorriso
        pygame.draw.arc(surf,(180,100,80),pygame.Rect(cx,eye_y+2,8,6),math.pi,2*math.pi,1)
    # chapéu de fazendeiro
    hat_pts = [(cx-8,cy+1),(cx+16,cy+1),(cx+18,cy-2),(cx+14,cy-10),(cx-2,cy-10),(cx-10,cy-2)]
    pygame.draw.polygon(surf,(120,80,20),hat_pts)
    pygame.draw.rect(surf,(100,60,10),(cx-2,cy-10,16,8),border_radius=2)
    # indicador do item segurado
    if held_item and held_item != "regador":
        data = PLANT_DB.get(held_item)
        if data:
            c = data["color"]
            pygame.draw.circle(surf,c,(cx+20,cy+18),5)
    elif held_item == "regador":
        # regador
        pygame.draw.rect(surf,(80,140,220),(cx+14,cy+14,10,10),border_radius=2)
        pygame.draw.line(surf,(60,110,190),(cx+24,cy+16),(cx+30,cy+20),2)

# ==========================================
# sistema de partículas
# ==========================================
class Particle:
    def __init__(self, x, y, color, life, vx, vy, size=4, gravity=0.0):
        self.x=x; self.y=y; self.color=color
        self.life=life; self.max_life=life
        self.vx=vx; self.vy=vy
        self.size=size; self.gravity=gravity

    def update(self):
        self.x+=self.vx; self.y+=self.vy
        self.vy+=self.gravity
        self.life-=1

    def draw(self, surf, cx, cy):
        if self.life>0:
            alpha=int(255*(self.life/self.max_life))
            sz=max(1,int(self.size*(self.life/self.max_life)))
            s=pygame.Surface((sz*2,sz*2),pygame.SRCALPHA)
            c=(*self.color[:3],alpha)
            pygame.draw.circle(s,c,(sz,sz),sz)
            surf.blit(s,(int(self.x-cx)-sz,int(self.y-cy)-sz))

class FloatingText:
    def __init__(self,x,y,text,color,font,life=80):
        self.x=float(x); self.y=float(y)
        self.text=text; self.color=color
        self.font=font; self.life=life; self.max_life=life

    def update(self):
        self.y-=0.6; self.life-=1

    def draw(self,surf,cx,cy):
        if self.life>0:
            alpha=int(255*(self.life/self.max_life))
            s=self.font.render(self.text,True,self.color)
            s.set_alpha(alpha)
            surf.blit(s,(self.x-cx-s.get_width()//2,self.y-cy))

# ==========================================
# partículas de chuva e neve
# ==========================================
class RainDrop:
    def __init__(self, sw, sh):
        self.x=random.uniform(0,sw)
        self.y=random.uniform(-sh,0)
        self.speed=random.uniform(8,14)
        self.length=random.randint(10,20)

    def update(self,sh):
        self.y+=self.speed
        self.x-=self.speed*0.2
        if self.y>sh: self.y=-random.randint(20,60)

    def draw(self,surf):
        pygame.draw.line(surf,(150,190,240,150),(int(self.x),int(self.y)),
                         (int(self.x-self.length*0.2),int(self.y+self.length)),1)

class SnowFlake:
    def __init__(self,sw,sh):
        self.x=random.uniform(0,sw); self.y=random.uniform(-sh,0)
        self.speed=random.uniform(1,3); self.drift=random.uniform(-0.5,0.5)
        self.size=random.randint(2,5)

    def update(self,sh):
        self.y+=self.speed; self.x+=self.drift
        if self.y>sh: self.y=-10

    def draw(self,surf):
        pygame.draw.circle(surf,(220,235,255),(int(self.x),int(self.y)),self.size)

# ==========================================
# npcs (comerciante e trabalhador)
# ==========================================
class NPC:
    def __init__(self, name, npc_type, tile_x, tile_y):
        self.name=name; self.type=npc_type
        self.tx=tile_x; self.ty=tile_y
        self.x=float(tile_x*TILE); self.y=float(tile_y*TILE)
        self.waypoints=[] # rota de patrulha em coordenadas de tile
        self.wp_idx=0
        self.move_timer=0
        self.idle_timer=random.randint(60,180)
        self.direction="down"
        self.frame=0

    def set_patrol(self, waypoints):
        self.waypoints=waypoints

    def update(self, world):
        self.frame+=1
        self.idle_timer-=1
        if self.idle_timer>0:
            return
        if not self.waypoints:
            self.idle_timer=random.randint(60,180)
            return
        # move em direção ao próximo ponto da rota
        wp=self.waypoints[self.wp_idx]
        tx_px=wp[0]*TILE; ty_px=wp[1]*TILE
        dx=tx_px-self.x; dy=ty_px-self.y
        speed=1.5
        dist=math.hypot(dx,dy)
        if dist<speed+1:
            self.x=tx_px; self.y=ty_px
            self.wp_idx=(self.wp_idx+1)%len(self.waypoints)
            self.idle_timer=random.randint(30,90)
        else:
            self.x+=dx/dist*speed
            self.y+=dy/dist*speed
            if abs(dx)>abs(dy):
                self.direction="right" if dx>0 else "left"
            else:
                self.direction="down" if dy>0 else "up"

    def draw(self, surf, cx, cy):
        sx=int(self.x-cx); sy=int(self.y-cy)
        # corpo simplificado do npc
        color=(120,80,40) if self.type=="merchant" else (200,180,100)
        pygame.draw.circle(surf,(250,200,160),(sx+12,sy+7),9) # cabeça
        pygame.draw.rect(surf,color,(sx+4,sy+14,18,16),border_radius=3) # corpo
        pygame.draw.rect(surf,(80,50,20),(sx+3,sy+26,10,10),border_radius=2) # bota esquerda
        pygame.draw.rect(surf,(80,50,20),(sx+13,sy+26,10,10),border_radius=2) # bota direita
        # etiqueta com o nome do npc
        font_tiny=pygame.font.SysFont("segoeui",11)
        nt=font_tiny.render(self.name,True,(255,255,200))
        bg=pygame.Surface((nt.get_width()+6,nt.get_height()+4),pygame.SRCALPHA)
        bg.fill((0,0,0,120))
        surf.blit(bg,(sx+12-bg.get_width()//2,sy-18))
        surf.blit(nt,(sx+12-nt.get_width()//2,sy-16))

# ==========================================
# mundo (mapa, plantas, geração)
# ==========================================
class World:
    def __init__(self, cols, rows):
        self.cols=cols; self.rows=rows
        self.grid=[]; self.decorations={}
        self.crop_state={}; self.crop_timer={}; self.soil_wetness={}
        self.npcs=[]
        self.sprites={}
        self._load_sprites()
        self.generate()

    def _load_sprites(self):
        self.sprites={
            'player': load_sprite("assets/personagem.png",TILE),
            'house':  load_sprite("assets/casa.png",TILE*2),
            'barn':   load_sprite("assets/celeiro.png",TILE*2),
            'fence':  load_sprite("assets/cerca.png",TILE),
            'soil':   load_sprite("assets/terra.jpeg",TILE),
            'grass':  load_sprite("assets/grama.png",TILE),
        }

    def generate(self):
        self.grid=[[T_GRASS]*self.cols for _ in range(self.rows)]
        # cercas na borda do mapa
        for x in range(self.cols):
            self.grid[0][x]=T_FENCE
            self.grid[self.rows-1][x]=T_FENCE
        for y in range(self.rows):
            self.grid[y][0]=T_FENCE
            self.grid[y][self.cols-1]=T_FENCE

        # caminho horizontal pelo meio do mapa
        mid=self.rows//2
        for x in range(1,self.cols-1):
            self.grid[mid][x]=T_PATH
        # caminho vertical
        for y in range(1,self.rows-1):
            self.grid[y][self.cols//2]=T_PATH

        # área da casa (topo esquerdo)
        for dr in range(3):
            for dc in range(3):
                self.grid[2+dr][2+dc]=T_BLOCK
        self.grid[2][2]=T_HOUSE

        # área do celeiro (topo direito)
        bc=self.cols-6
        for dr in range(3):
            for dc in range(3):
                self.grid[2+dr][bc+dc]=T_BLOCK
        self.grid[2][bc]=T_BARN

        # mercado (área inferior esquerda)
        mc=3; mr=self.rows-6
        for dr in range(3):
            for dc in range(3):
                self.grid[mr+dr][mc+dc]=T_BLOCK
        self.grid[mr][mc]=T_MARKET

        # lago de água
        wr=5; wc=self.cols//2-3
        for dr in range(3):
            for dc in range(5):
                self.grid[wr+dr][wc+dc]=T_WATER

        # área de terra para plantio
        fx0,fy0=4,7
        fw=max(8,self.cols//2-6)
        fh=max(6,self.rows-12)
        for r in range(fy0,min(self.rows-2,fy0+fh)):
            for c in range(fx0,min(self.cols-2,fx0+fw)):
                if self.grid[r][c]==T_GRASS:
                    self.grid[r][c]=T_SOIL

        # pomar (quadrante superior direito)
        orx=self.cols//2+2; ory=3
        for r in range(ory,min(self.rows-3,ory+4)):
            for c in range(orx,min(self.cols-3,orx+6)):
                if self.grid[r][c]==T_GRASS:
                    self.grid[r][c]=T_ORCHARD

        # configura os npcs do mapa
        self._setup_npcs()

    def _setup_npcs(self):
        merchant = NPC("Carlos","merchant",self.cols-5,self.rows-5)
        merchant.set_patrol([(self.cols-5,self.rows-5),(self.cols-3,self.rows-5),(self.cols-3,self.rows-3),(self.cols-5,self.rows-3)])
        self.npcs.append(merchant)

        worker = NPC("Ana","worker",5,self.rows-4)
        worker.set_patrol([(5,self.rows-4),(8,self.rows-4),(8,self.rows-7),(5,self.rows-7)])
        self.npcs.append(worker)

    def is_blocked(self,r,c):
        if r<0 or r>=self.rows or c<0 or c>=self.cols: return True
        return self.grid[r][c] in (T_FENCE,T_HOUSE,T_BARN,T_BLOCK,T_WATER,T_MARKET)

    def draw_tile(self, surf, r, c, cx, cy, tick=0, season="Primavera"):
        x=c*TILE-int(cx); y=r*TILE-int(cy)
        if x<-TILE or x>SW+TILE or y<-TILE or y>SH+TILE: return
        t=self.grid[r][c]
        if t==T_GRASS or t==T_BLOCK:
            draw_grass_tile(surf,x,y,variant=(r*7+c*3)%5==0,season=season)
        elif t==T_FENCE:
            draw_fence_tile(surf,x,y)
        elif t==T_SOIL:
            wet=self.soil_wetness.get((r,c),0)>0
            draw_soil_tile(surf,x,y,wet)
        elif t==T_PATH:
            draw_path_tile(surf,x,y)
        elif t==T_WATER:
            draw_water_tile(surf,x,y,tick)
        elif t==T_ORCHARD:
            draw_grass_tile(surf,x,y,season=season)
            # árvore simples do pomar
            pygame.draw.rect(surf,(100,60,20),(x+TILE//2-3,y+TILE//2,6,TILE//2))
            pygame.draw.circle(surf,(60,140,60),(x+TILE//2,y+TILE//2),16)
            pygame.draw.circle(surf,(80,170,50),(x+TILE//2-4,y+TILE//2-4),8)

    def draw_buildings(self, surf, cx, cy):
        for r in range(self.rows):
            for c in range(self.cols):
                t=self.grid[r][c]
                x=c*TILE-int(cx); y=r*TILE-int(cy)
                if t==T_HOUSE:
                    spr=self.sprites.get('house')
                    if spr: surf.blit(spr,(x,y))
                    else: draw_house(surf,x,y,TILE)
                elif t==T_BARN:
                    spr=self.sprites.get('barn')
                    if spr: surf.blit(spr,(x,y))
                    else: draw_barn(surf,x,y,TILE)
                elif t==T_MARKET:
                    draw_market(surf,x,y,TILE)

    def draw_crops(self, surf, cx, cy, tick=0):
        for (r,c),plant in self.crop_state.items():
            x=c*TILE-int(cx); y=r*TILE-int(cy)
            if x<-TILE or x>SW+TILE or y<-TILE or y>SH+TILE: continue
            draw_crop(surf,x,y,plant["type"],plant["stage"],tick)

# ==========================================
# câmera (segue o jogador com suavidade)
# ==========================================
class Camera:
    def __init__(self):
        self.x=0.0; self.y=0.0
        self.tx=0.0; self.ty=0.0  # alvo da câmera
        self.smooth=8.0

    def update(self, px, py, map_w, map_h, view_w, view_h):
        self.tx=px-view_w//2
        self.ty=py-view_h//2
        # segue suavemente com lerp
        self.x+=(self.tx-self.x)/self.smooth
        self.y+=(self.ty-self.y)/self.smooth
        # limita para não sair do mapa
        self.x=max(0,min(self.x,map_w-view_w))
        self.y=max(0,min(self.y,map_h-view_h))

# ==========================================
# jogador
# ==========================================
class Player:
    def __init__(self, x, y):
        self.x=float(x); self.y=float(y)
        self.speed=200.0; self.direction="down"
        self.frame=0; self.moving=False
        self.coins=100
        self.seed_inventory={k:(5 if k=="trigo" else 0) for k in PLANT_LIST}
        self.growth_boost=0  # reduz o tempo de crescimento em %
        self.sprite=load_sprite("assets/personagem.png",TILE)
        self.hunger=100.0   # mecânica futura de fome
        self.xp=0
        self.level=1

    def gain_xp(self,amt):
        self.xp+=amt
        needed=self.level*100
        if self.xp>=needed:
            self.xp-=needed
            self.level+=1
            return True
        return False

# ==========================================
# sistema de clima
# ==========================================
class WeatherSystem:
    def __init__(self, sw, sh):
        self.sw=sw; self.sh=sh
        self.weather="Ensolarado"
        self.transition_timer=0
        self.cloud_surf=None
        self.rain_drops=[RainDrop(sw,sh) for _ in range(200)]
        self.snow_flakes=[SnowFlake(sw,sh) for _ in range(100)]
        self.clouds=[{"x":random.uniform(0,sw),"y":random.uniform(30,150),
                      "w":random.uniform(80,200),"speed":random.uniform(0.2,0.6)}
                     for _ in range(8)]

    def update(self, tick, season):
        # move as nuvens da esquerda para a direita
        for cl in self.clouds:
            cl["x"]+=cl["speed"]
            if cl["x"]>self.sw+cl["w"]: cl["x"]=-cl["w"]
        # atualiza chuva e neve
        if self.weather in ("Chuvoso","Tempestade"):
            for r in self.rain_drops: r.update(self.sh)
        if self.weather=="Nevando":
            for s in self.snow_flakes: s.update(self.sh)

    def roll_weather(self, season):
        weights={"Primavera":{"Ensolarado":40,"Nublado":25,"Chuvoso":30,"Tempestade":5,"Nevando":0},
                 "Verão":    {"Ensolarado":55,"Nublado":20,"Chuvoso":15,"Tempestade":10,"Nevando":0},
                 "Outono":   {"Ensolarado":30,"Nublado":35,"Chuvoso":25,"Tempestade":5,"Nevando":5},
                 "Inverno":  {"Ensolarado":15,"Nublado":30,"Chuvoso":10,"Tempestade":5,"Nevando":40}}
        w=weights.get(season,weights["Primavera"])
        choices=[]; wts=[]
        for k,v in w.items(): choices.append(k); wts.append(v)
        self.weather=random.choices(choices,wts)[0]

    def draw_sky(self, surf, hour, minute):
        # gradiente do céu baseado na hora do dia
        t=hour+minute/60.0
        if 6<=t<8:
            alpha=(t-6)/2.0
            sky=lerp_color(C_SKY_DAWN,C_SKY_DAY,alpha)
        elif 8<=t<18: sky=C_SKY_DAY
        elif 18<=t<20:
            alpha=(t-18)/2.0
            sky=lerp_color(C_SKY_DAY,C_SKY_DUSK,alpha)
        elif 20<=t<22:
            alpha=(t-20)/2.0
            sky=lerp_color(C_SKY_DUSK,C_SKY_NIGHT,alpha)
        else: sky=C_SKY_NIGHT

        if self.weather in ("Nublado","Chuvoso","Tempestade"):
            sky=lerp_color(sky,(100,100,110),0.5)
        elif self.weather=="Nevando":
            sky=lerp_color(sky,(180,185,200),0.4)
        surf.fill(sky,(0,0,self.sw,SH//4))

    def draw_clouds(self, surf):
        for cl in self.clouds:
            alpha=200 if self.weather in ("Nublado","Chuvoso","Tempestade","Nevando") else 120
            s=pygame.Surface((int(cl["w"]),50),pygame.SRCALPHA)
            pygame.draw.ellipse(s,(240,240,240,alpha),(0,15,int(cl["w"]),35))
            pygame.draw.ellipse(s,(240,240,240,alpha),(int(cl["w"])//4,5,int(cl["w"])//2,40))
            surf.blit(s,(int(cl["x"]),int(cl["y"])))

    def draw_weather_fx(self, surf):
        if self.weather in ("Chuvoso","Tempestade"):
            rs=pygame.Surface((self.sw,self.sh),pygame.SRCALPHA)
            for r in self.rain_drops: r.draw(rs)
            surf.blit(rs,(0,0))
            if self.weather=="Tempestade":
                s=pygame.Surface((self.sw,self.sh),pygame.SRCALPHA)
                s.fill((100,100,180,15))
                surf.blit(s,(0,0))
        elif self.weather=="Nevando":
            for s in self.snow_flakes: s.draw(surf)

    def get_auto_water(self):
        """retorna verdadeiro se o clima causa rega automática."""
        return self.weather in ("Chuvoso","Tempestade")

# ==========================================
# gerenciador de interface (ui)
# ==========================================
class UIManager:
    def __init__(self, sw, sh):
        self.sw=sw; self.sh=sh
        self.sidebar_w=280
        self.topbar_h=52
        self.active_tab=0   # 0=inventário, 1=loja, 2=obras
        self.hotbar_items=["regador"]+PLANT_LIST
        self.active_slot=1
        self.font=   pygame.font.SysFont("segoeui",18,bold=True)
        self.font_sm=pygame.font.SysFont("segoeui",14)
        self.font_md=pygame.font.SysFont("segoeui",22,bold=True)
        self.font_lg=pygame.font.SysFont("segoeui",30,bold=True)
        self.shop_message=""
        self.shop_msg_timer=0
        self.tooltip=""
        self.show_help=False

    # ---- barra superior ----
    def draw_topbar(self, surf, player, day, hour, minute, season, weather):
        game_w=self.sw-self.sidebar_w
        pygame.draw.rect(surf,(22,26,32),(0,0,game_w,self.topbar_h))
        pygame.draw.line(surf,C_UI_BORDER,(0,self.topbar_h),(game_w,self.topbar_h),2)
        # ícone de ouro + quantidade
        pygame.draw.circle(surf,C_GOLD,(20,26),12)
        coin_draw=self.font.render("$",True,(50,30,0))
        surf.blit(coin_draw,(15,16))
        amt=self.font_md.render(str(player.coins),True,C_YELLOW)
        surf.blit(amt,(38,12))
        # emblema de nível
        lvl_rect=pygame.Rect(120,10,70,30)
        draw_rounded_rect(surf,(60,90,160),lvl_rect,6,1,(80,120,200))
        lvl_txt=self.font_sm.render(f"Nv {player.level}",True,C_WHITE)
        surf.blit(lvl_txt,(lvl_rect.x+8,lvl_rect.y+7))
        # barra de xp
        needed=player.level*100
        xp_rect=pygame.Rect(120,44,70,6)
        pygame.draw.rect(surf,(40,40,55),xp_rect,border_radius=3)
        xp_fill=int(70*(player.xp/needed))
        if xp_fill>0:
            pygame.draw.rect(surf,(80,220,255),(120,44,xp_fill,6),border_radius=3)
        # hora do jogo
        time_str=f"☀ Dia {day} – {hour:02d}:{minute:02d}"
        ts=self.font.render(time_str,True,C_YELLOW)
        surf.blit(ts,(game_w-ts.get_width()-130,15))
        # bolha da estação
        scol={"Primavera":(80,200,80),"Verão":(250,180,30),"Outono":(230,100,20),"Inverno":(150,190,240)}.get(season,(200,200,200))
        sr=pygame.Rect(game_w-120,10,115,30)
        draw_rounded_rect(surf,(*scol,200),sr,8)
        sx=self.font_sm.render(f"{season}",True,(20,20,20))
        surf.blit(sx,(sr.x+(sr.w-sx.get_width())//2,sr.y+7))
        # ícone do clima
        wst={"Ensolarado":"☀","Nublado":"⛅","Chuvoso":"🌧","Tempestade":"⛈","Nevando":"❄"}.get(weather,"?")
        wt=self.font.render(wst,True,C_WHITE)
        surf.blit(wt,(game_w-148,12))

    # ---- painel lateral ----
    def draw_sidebar(self, surf, player, mouse_pos, world):
        sx=self.sw-self.sidebar_w
        pygame.draw.rect(surf,(22,26,32),(sx,0,self.sidebar_w,self.sh))
        pygame.draw.line(surf,(60,70,85),(sx,0),(sx,self.sh),2)

        # abas do painel
        tabs=["🎒 Bag","🛒 Loja","⚗ Obras"]
        tw=self.sidebar_w//len(tabs)
        for i,tab in enumerate(tabs):
            tr_=pygame.Rect(sx+i*tw,0,tw,42)
            bg=(45,60,80) if self.active_tab==i else (28,32,40)
            draw_rounded_rect(surf,bg,tr_,0)
            tt=self.font_sm.render(tab,True,C_WHITE if self.active_tab==i else (120,130,150))
            surf.blit(tt,(tr_.x+(tr_.w-tt.get_width())//2,tr_.y+12))
        pygame.draw.line(surf,C_UI_ACTIVE,(sx+self.active_tab*tw,42),(sx+(self.active_tab+1)*tw,42),3)

        results=[]
        y0=52

        if self.active_tab==0:
            results=self._draw_inventory_tab(surf,player,mouse_pos,sx,y0)
        elif self.active_tab==1:
            results=self._draw_store_tab(surf,player,mouse_pos,sx,y0,world)
        elif self.active_tab==2:
            results=self._draw_upgrades_tab(surf,player,mouse_pos,sx,y0)

        # mensagem de feedback da loja
        if self.shop_msg_timer>0:
            mbox=pygame.Rect(sx+10,self.sh-60,self.sidebar_w-20,44)
            c=(60,160,80) if "!" in self.shop_message else (160,60,60)
            draw_rounded_rect(surf,c,mbox,6)
            mt=self.font_sm.render(self.shop_message,True,C_WHITE)
            surf.blit(mt,(mbox.x+(mbox.w-mt.get_width())//2,mbox.y+12))

        return results

    def _draw_inventory_tab(self, surf, player, mouse_pos, sx, y0):
        # grade de sementes no inventário
        label=self.font_sm.render("SEMENTES:",True,(150,170,200))
        surf.blit(label,(sx+10,y0))
        y0+=22
        for i,plant in enumerate(PLANT_LIST):
            data=PLANT_DB[plant]
            box=pygame.Rect(sx+8,y0+i*52,self.sidebar_w-16,46)
            active=(self.hotbar_items[self.active_slot]==plant) if self.active_slot<len(self.hotbar_items) else False
            bg=(45,70,100) if active else (35,40,50)
            if box.collidepoint(mouse_pos): bg=tuple(min(255,x+10) for x in bg)
            draw_rounded_rect(surf,bg,box,6,1,(70,80,100))
            # bolinha colorida
            pygame.draw.circle(surf,data["color"],(sx+24,y0+i*52+23),10)
            # nome da planta
            nt=self.font_sm.render(plant.capitalize(),True,C_WHITE)
            surf.blit(nt,(sx+40,y0+i*52+8))
            # quantidade em estoque
            qty=player.seed_inventory.get(plant,0)
            qcolor=C_GREEN_BRIGHT if qty>0 else C_RED
            qbg=pygame.Rect(sx+self.sidebar_w-54,y0+i*52+12,40,22)
            draw_rounded_rect(surf,(40,50,60),qbg,4)
            qt=self.font_sm.render(str(qty),True,qcolor)
            surf.blit(qt,(qbg.x+(qbg.w-qt.get_width())//2,qbg.y+3))
        return []

    def _draw_store_tab(self, surf, player, mouse_pos, sx, y0, world):
        results=[]
        label=self.font_sm.render("COMPRAR SEMENTES:",True,(150,170,200))
        surf.blit(label,(sx+10,y0)); y0+=22
        for i,plant in enumerate(PLANT_LIST):
            data=PLANT_DB[plant]
            box=pygame.Rect(sx+8,y0+i*58,self.sidebar_w-16,50)
            hover=box.collidepoint(mouse_pos)
            bg=(50,75,55) if hover else (35,45,42)
            if player.coins>=data["buy"]: border=(60,150,80)
            else: border=(80,50,50)
            draw_rounded_rect(surf,bg,box,6,1,border)
            pygame.draw.circle(surf,data["color"],(sx+24,y0+i*58+25),10)
            nt=self.font_sm.render(plant.capitalize(),True,C_WHITE)
            surf.blit(nt,(sx+40,y0+i*58+8))
            rwd=self.font_sm.render(f"+{data['reward']}$",True,C_YELLOW)
            surf.blit(rwd,(sx+40,y0+i*58+26))
            cost=self.font.render(f"${data['buy']}",True,C_GOLD)
            surf.blit(cost,(sx+self.sidebar_w-60,y0+i*58+16))
            if hover and player.coins>=data["buy"]:
                results.append(("buy_seed",plant,data["buy"]))
        return results

    def _draw_upgrades_tab(self, surf, player, mouse_pos, sx, y0):
        results=[]
        upgrades=[
            ("Expansão do Terreno","Aumenta cols/rows (+6×4)",200,"expand"),
            ("Adubo Premium","Crops crescem 25% mais rápido",300,"growth"),
            ("Regador de Ouro","Solo fica molhado mais tempo",250,"wetness"),
            ("Silo de Armazenamento","Capacidade de sementes ilimitada",500,"silo"),
        ]
        label=self.font_sm.render("MELHORIAS:",True,(150,170,200))
        surf.blit(label,(sx+10,y0)); y0+=22
        for i,upg in enumerate(upgrades):
            name,desc,cost,key=upg
            box=pygame.Rect(sx+8,y0+i*76,self.sidebar_w-16,68)
            hover=box.collidepoint(mouse_pos)
            can_afford=player.coins>=cost
            bg=(50,60,80) if hover else (35,40,55)
            border=C_UI_ACTIVE if can_afford else (80,50,50)
            draw_rounded_rect(surf,bg,box,6,1,border)
            nt=self.font_sm.render(name,True,C_WHITE)
            surf.blit(nt,(sx+14,y0+i*76+8))
            dt=self.font_sm.render(desc,True,(140,155,175))
            surf.blit(dt,(sx+14,y0+i*76+26))
            ct=self.font.render(f"${cost}",True,C_GOLD if can_afford else C_RED)
            surf.blit(ct,(sx+self.sidebar_w-70,y0+i*76+24))
            if hover and can_afford:
                results.append(("upgrade",key,cost))
        return results

    def draw_hotbar(self, surf, player, mouse_pos):
        game_w=self.sw-self.sidebar_w
        slot_w=54; spacing=6
        count=len(self.hotbar_items)
        total=(slot_w+spacing)*count-spacing
        bx=(game_w-total)//2; by=self.sh-slot_w-14

        # fundo com sombra do hotbar
        bg=pygame.Rect(bx-12,by-8,total+24,slot_w+16)
        draw_rounded_rect(surf,(18,22,28),bg,12,1,(50,60,75))

        for i,item in enumerate(self.hotbar_items):
            x=bx+i*(slot_w+spacing); y=by
            r=pygame.Rect(x,y,slot_w,slot_w)
            active=(i==self.active_slot)
            bg2=(55,85,130) if active else (35,42,55)
            border=C_UI_ACTIVE if active else C_UI_BORDER
            draw_rounded_rect(surf,bg2,r,8,2,border)
            if active:
                # brilho do slot ativo
                glow=pygame.Surface((slot_w+8,slot_w+8),pygame.SRCALPHA)
                pygame.draw.rect(glow,(80,140,220,40),(0,0,slot_w+8,slot_w+8),border_radius=10)
                surf.blit(glow,(x-4,y-4))

            # ícone do item
            if item=="regador":
                pygame.draw.rect(surf,C_BLUE,(x+14,y+14,24,20),border_radius=4)
                pygame.draw.line(surf,(50,110,200),(x+38,y+18),(x+46,y+24),3)
                pygame.draw.circle(surf,(120,180,255),(x+20,y+22),6)
            else:
                data=PLANT_DB.get(item)
                if data:
                    pygame.draw.circle(surf,data["color"],(x+slot_w//2,y+slot_w//2),14)
                    pygame.draw.circle(surf,data["color2"],(x+slot_w//2,y+slot_w//2),14,2)
                    # quantidade em estoque
                    qty=player.seed_inventory.get(item,0)
                    qc=C_GREEN_BRIGHT if qty>0 else C_RED
                    qs=self.font_sm.render(str(qty),True,qc)
                    surf.blit(qs,(x+slot_w-qs.get_width()-2,y+slot_w-16))
            # número do slot
            sn=self.font_sm.render(str(i+1),True,(130,140,160))
            surf.blit(sn,(x+3,y+3))

    def draw_night_overlay(self, surf, hour, minute):
        t=hour+minute/60.0
        if 8<=t<18: alpha=0
        elif 18<=t<22: alpha=int(160*(t-18)/4)
        elif 22<=t or t<5: alpha=160
        elif 5<=t<8: alpha=int(160*(1-(t-5)/3))
        else: alpha=0
        if alpha>0:
            s=pygame.Surface((SW,SH),pygame.SRCALPHA)
            s.fill((8,10,30,alpha))
            surf.blit(s,(0,0))
            # estrelas à noite
            if alpha>80:
                random.seed(42)
                for _ in range(40):
                    sx2=random.randint(0,SW-self.sidebar_w)
                    sy2=random.randint(0,SH//3)
                    star_a=min(alpha,random.randint(100,220))
                    sc=pygame.Surface((4,4),pygame.SRCALPHA)
                    sc.fill((255,255,220,star_a))
                    surf.blit(sc,(sx2,sy2))

    def handle_click(self, mouse_pos):
        if mouse_pos[0]>self.sw-self.sidebar_w:
            if mouse_pos[1]<42:
                tw=self.sidebar_w//3
                self.active_tab=min(2,(mouse_pos[0]-(self.sw-self.sidebar_w))//tw)
            return True
        if mouse_pos[1]<self.topbar_h: return True
        return False

    def handle_hotbar_click(self, mouse_pos):
        game_w=self.sw-self.sidebar_w
        slot_w=54; spacing=6
        count=len(self.hotbar_items)
        total=(slot_w+spacing)*count-spacing
        bx=(game_w-total)//2; by=self.sh-slot_w-14
        for i in range(count):
            x=bx+i*(slot_w+spacing)
            r=pygame.Rect(x,by,slot_w,slot_w)
            if r.collidepoint(mouse_pos):
                self.active_slot=i; return True
        return False
