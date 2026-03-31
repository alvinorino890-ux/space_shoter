import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
BLUE = (100, 149, 237)
DARK_BLUE = (25, 25, 112)
PURPLE = (128, 0, 128)

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invader Game")

# Clock for FPS
clock = pygame.time.Clock()

# Font
font = pygame.font.Font(None, 36)
game_over_font = pygame.font.Font(None, 74)
watermark_font = pygame.font.SysFont("Arial", 10, italic=True)

class Player:
    def __init__(self):
        self.width = 40
        self.height = 40
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - 80
        self.speed = 5
        self.bullets = []
        
    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed
            
    def shoot(self):
        bullet = Bullet(self.x + self.width // 2, self.y)
        self.bullets.append(bullet)
        
    def draw(self, screen):
        pygame.draw.polygon(screen, WHITE, [
            (self.x + self.width // 2, self.y),
            (self.x, self.y + self.height),
            (self.x + self.width, self.y + self.height)
        ])
        pygame.draw.circle(screen, BLUE, (self.x + self.width // 2, self.y + 15), 8)
        pygame.draw.polygon(screen, RED, [
            (self.x, self.y + self.height),
            (self.x - 10, self.y + self.height + 10),
            (self.x + 5, self.y + self.height)
        ])
        pygame.draw.polygon(screen, RED, [
            (self.x + self.width, self.y + self.height),
            (self.x + self.width + 10, self.y + self.height + 10),
            (self.x + self.width - 5, self.y + self.height)
        ])

class Enemy:
    def __init__(self, x, y):
        self.width = 40
        self.height = 30
        self.x = x
        self.y = y
        self.speed_x = 2
        self.speed_y = 20
        
    def move(self, enemies):
        self.x += self.speed_x
        change_direction = False
        for enemy in enemies:
            if enemy.x <= 0 or enemy.x >= SCREEN_WIDTH - enemy.width:
                change_direction = True
                break
        if change_direction:
            for enemy in enemies:
                enemy.speed_x *= -1
                enemy.y += enemy.speed_y
                
    def draw(self, screen):
        pygame.draw.rect(screen, ORANGE, (self.x + 5, self.y + 10, 30, 15))
        pygame.draw.rect(screen, ORANGE, (self.x + 10, self.y, 20, 15))
        pygame.draw.circle(screen, BLACK, (self.x + 15, self.y + 7), 3)
        pygame.draw.circle(screen, BLACK, (self.x + 25, self.y + 7), 3)
        pygame.draw.rect(screen, ORANGE, (self.x, self.y + 25, 8, 5))
        pygame.draw.rect(screen, ORANGE, (self.x + 12, self.y + 25, 8, 5))
        pygame.draw.rect(screen, ORANGE, (self.x + 24, self.y + 25, 8, 5))
        pygame.draw.rect(screen, ORANGE, (self.x + 32, self.y + 25, 8, 5))

class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 7
        self.radius = 3
        
    def move(self):
        self.y -= self.speed
        
    def draw(self, screen):
        pygame.draw.circle(screen, YELLOW, (self.x, self.y), self.radius)

class Star:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.size = random.randint(1, 3)
        self.speed = random.uniform(0.5, 2)
        
    def move(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randint(0, SCREEN_WIDTH)
            
    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.size)

class Asteroid:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(-SCREEN_HEIGHT, 0)
        self.speed = random.uniform(1, 3)
        self.rotation = random.randint(0, 360)
        self.size = random.randint(15, 30)
        
    def move(self):
        self.y += self.speed
        self.rotation += 2
        if self.y > SCREEN_HEIGHT + 50:
            self.y = random.randint(-100, -50)
            self.x = random.randint(0, SCREEN_WIDTH)
            
    def draw(self, screen):
        points = []
        for i in range(6):
            angle = math.radians(60 * i + self.rotation)
            offset = random.randint(-3, 3) if i % 2 == 0 else 0
            x = self.x + (self.size + offset) * math.cos(angle)
            y = self.y + (self.size + offset) * math.sin(angle)
            points.append((int(x), int(y)))
        pygame.draw.polygon(screen, (139, 69, 19), points)

class Planet:
    def __init__(self, x, y, radius, color, has_ring=False):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.has_ring = has_ring
        
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        pygame.draw.circle(screen, tuple(max(0, c - 30) for c in self.color),
                         (self.x - 5, self.y - 5), self.radius, 2)
        if self.has_ring:
            pygame.draw.ellipse(screen, (200, 150, 200),
                              (self.x - self.radius - 20, self.y - 10,
                               (self.radius + 20) * 2, 20), 3)

def check_collision(bullet, enemy):
    distance = math.sqrt((bullet.x - (enemy.x + enemy.width // 2)) ** 2 +
                        (bullet.y - (enemy.y + enemy.height // 2)) ** 2)
    return distance < 20

def draw_watermark(screen):
    # Watermark / credit
    watermark_text = watermark_font.render("by Alvino Aldorino", True, WHITE)
    x = SCREEN_WIDTH // 2 - watermark_text.get_width() // 2
    y = SCREEN_HEIGHT - 10 - watermark_text.get_height() // 2
    screen.blit(watermark_text, (x, y))

def draw_background(screen, stars, asteroids, planets):
    screen.fill(DARK_BLUE)
    for planet in planets:
        planet.draw(screen)
    for star in stars:
        star.draw(screen)
    for asteroid in asteroids:
        asteroid.draw(screen)

def main():
    player = Player()
    
    enemies = []
    for row in range(3):
        for col in range(8):
            enemy = Enemy(col * 80 + 100, row * 60 + 50)
            enemies.append(enemy)
    
    stars = [Star() for _ in range(100)]
    asteroids = [Asteroid() for _ in range(5)]
    planets = [
        Planet(700, 100, 40, (150, 150, 150)),
        Planet(650, 300, 50, (255, 100, 150), True),
        Planet(100, 150, 30, (100, 200, 255)),
    ]
    
    score = 0
    game_over = False
    running = True
    
    while running:
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over:
                    player.shoot()
                if event.key == pygame.K_r and game_over:
                    return main()
                    
        if not game_over:
            keys = pygame.key.get_pressed()
            player.move(keys)
            
            if enemies:
                enemies[0].move(enemies)
            
            for bullet in player.bullets[:]:
                bullet.move()
                if bullet.y < 0:
                    player.bullets.remove(bullet)
                    
            for bullet in player.bullets[:]:
                for enemy in enemies[:]:
                    if check_collision(bullet, enemy):
                        if bullet in player.bullets:
                            player.bullets.remove(bullet)
                        enemies.remove(enemy)
                        score += 10
                        break
                        
            for star in stars:
                star.move()
            for asteroid in asteroids:
                asteroid.move()
                
            for enemy in enemies:
                if enemy.y > SCREEN_HEIGHT - 100:
                    game_over = True
                    
            if len(enemies) == 0:
                game_over = True
        
        draw_background(screen, stars, asteroids, planets)
        
        player.draw(screen)
        
        for enemy in enemies:
            enemy.draw(screen)
            
        for bullet in player.bullets:
            bullet.draw(screen)
            
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        # Draw watermark
        draw_watermark(screen)
        
        if game_over:
            if len(enemies) == 0:
                win_text = game_over_font.render("YOU WIN!", True, YELLOW)
                win_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                screen.blit(win_text, win_rect)
            else:
                game_over_text = game_over_font.render("GAME OVER", True, WHITE)
                text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                screen.blit(game_over_text, text_rect)
            
            restart_text = font.render("Press R to Restart", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
            screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()
