import pygame
import sys
import random

pygame.init()

WIDTH, HEIGHT = 800, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Arcade DevOps Game")

WHITE = (255, 255, 255)
BLUE = (50, 100, 255)
YELLOW = (255, 200, 0)
BLACK = (0,0,0)

player_size = 40
player_x = WIDTH // 2
player_y = HEIGHT // 2
speed = 5

coin_radius = 10
coin_x = random.randint(50, WIDTH-50)
coin_y = random.randint(50, HEIGHT-50)

score = 0
font = pygame.font.SysFont(None, 30)

clock = pygame.time.Clock()

while True:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        player_x -= speed
    if keys[pygame.K_RIGHT]:
        player_x += speed
    if keys[pygame.K_UP]:
        player_y -= speed
    if keys[pygame.K_DOWN]:
        player_y += speed

    player_rect = pygame.Rect(player_x, player_y, player_size, player_size)

    # colisão com moeda
    coin_rect = pygame.Rect(coin_x-coin_radius, coin_y-coin_radius, coin_radius*2, coin_radius*2)

    if player_rect.colliderect(coin_rect):
        score += 1
        coin_x = random.randint(50, WIDTH-50)
        coin_y = random.randint(50, HEIGHT-50)

    screen.fill(WHITE)

    pygame.draw.rect(screen, BLUE, player_rect)
    pygame.draw.circle(screen, YELLOW, (coin_x, coin_y), coin_radius)

    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10,10))

    pygame.display.update()