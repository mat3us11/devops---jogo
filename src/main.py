import pygame
import sys
import random
from pathlib import Path

# Inicializa todos os módulos do pygame
pygame.init()

# CONFIGURAÇÃO DA JANELA
WIDTH, HEIGHT = 800, 500

# Cria a janela do jogo
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Título da janela
pygame.display.set_caption("Arcade DevOps Game")

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 200, 0)

# função para encontrar arquivos tanto no python normal quanto no executável
def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return str(Path(sys._MEIPASS) / relative_path)
    return str(Path(__file__).resolve().parent.parent / relative_path)

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"

# CARREGAMENTO DO PERSONAGEM

# Carrega o sprite do personagem
player_img = pygame.image.load(resource_path("assets/personagem.png")).convert_alpha()

# Define tamanho do personagem
PLAYER_SIZE = 108

# Redimensiona o sprite
player_img = pygame.transform.scale(player_img, (PLAYER_SIZE, PLAYER_SIZE))

# CONFIGURAÇÕES DO JOGADOR

player_x = WIDTH // 2
player_y = HEIGHT // 2

speed = 5

# CONFIGURAÇÕES DA MOEDA

coin_radius = 10

# posição aleatória inicial
coin_x = random.randint(50, WIDTH - 50)
coin_y = random.randint(50, HEIGHT - 50)

# SISTEMA DE PONTUAÇÃO

score = 0

font = pygame.font.SysFont(None, 30)

clock = pygame.time.Clock()

# LOOP PRINCIPAL DO JOGO

while True:
    clock.tick(60)

    # Eventos do jogo
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Teclas pressionadas
    keys = pygame.key.get_pressed()

    # Movimentação
    if keys[pygame.K_LEFT]:
        player_x -= speed

    if keys[pygame.K_RIGHT]:
        player_x += speed

    if keys[pygame.K_UP]:
        player_y -= speed

    if keys[pygame.K_DOWN]:
        player_y += speed

    # LIMITAR MOVIMENTO NA TELA

    player_x = max(0, min(WIDTH - PLAYER_SIZE, player_x))
    player_y = max(0, min(HEIGHT - PLAYER_SIZE, player_y))

    # Retângulo do jogador (para colisão)
    player_rect = pygame.Rect(player_x + 35, player_y + 35, PLAYER_SIZE - 70, PLAYER_SIZE - 70)

    # Retângulo da moeda
    coin_rect = pygame.Rect(
        coin_x - coin_radius,
        coin_y - coin_radius,
        coin_radius * 2,
        coin_radius * 2
    )

    # COLISÃO COM MOEDA
    if player_rect.colliderect(coin_rect):

        # aumenta pontuação
        score += 1

        # nova posição aleatória
        coin_x = random.randint(50, WIDTH - 50)
        coin_y = random.randint(50, HEIGHT - 50)

    screen.fill(WHITE)

    # desenha personagem
    screen.blit(player_img, (player_x, player_y))

    # desenha moeda
    pygame.draw.circle(screen, YELLOW, (coin_x, coin_y), coin_radius)

    # texto do score
    score_text = font.render(f"Score: {score}", True, BLACK)

    screen.blit(score_text, (10, 10))

    pygame.display.update()