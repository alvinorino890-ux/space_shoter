import pygame
import random
import math
import json
import os
from datetime import datetime

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
GREEN = (0, 255, 100)
CYAN = (0, 255, 255)
GOLD = (255, 215, 0)
LIGHT_GRAY = (200, 200, 200)

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invader Game")

# Clock for FPS
clock = pygame.time.Clock()

# Font
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 28)
large_font = pygame.font.Font(None, 60)
game_over_font = pygame.font.Font(None, 74)
watermark_font = pygame.font.SysFont("Arial", 10, italic=True)

# ─── SCORE SAVING ────────────────────────────────────────────────────────────

SAVE_FILE = "highscores.json"

def load_scores():
    """Load high scores from file."""
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []

def save_score(score, level):
    """Save a new score entry."""
    scores = load_scores()
    entry = {
        "score": score,
        "level": level,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    scores.append(entry)
    # Sort by score descending, keep top 10
    scores.sort(key=lambda x: x["score"], reverse=True)
    scores = scores[:10]
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(scores, f, indent=2)
    except IOError:
        pass
    return scores

# ─── LEVEL CONFIG ─────────────────────────────────────────────────────────────

def get_level_config(level):
    """Return enemy speed, rows, cols, shoot chance based on level."""
    config = {
        "enemy_speed": 1.5 + (level - 1) * 0.5,
        "enemy_rows": min(2 + (level - 1), 5),
        "enemy_cols": min(6 + (level - 1), 10),
        "enemy_shoot": 0.001 * level,       # probability per enemy per frame
        "asteroid_count": 3 + level,
        "enemy_drop": 15 + level * 2,
        "label": f"LEVEL {level}",
        "color": [
            ORANGE,
            (255, 80, 80),
            (200, 80, 255),
            CYAN,
            GOLD,
        ][(level - 1) % 5]
    }
    return config

# ─── CLASSES ──────────────────────────────────────────────────────────────────

class Player:
    def __init__(self):
        self.width = 40
        self.height = 40
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - 80
        self.speed = 5
        self.bullets = []
        self.lives = 3
        self.invincible = 0   # frames of invincibility after hit

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed

    def shoot(self):
        bullet = Bullet(self.x + self.width // 2, self.y, -7, YELLOW)
        self.bullets.append(bullet)

    def hit(self):
        if self.invincible <= 0:
            self.lives -= 1
            self.invincible = 90  # 1.5 seconds at 60fps

    def update(self):
        if self.invincible > 0:
            self.invincible -= 1

    def draw(self, screen):
        # Flash when invincible
        if self.invincible > 0 and (self.invincible // 6) % 2 == 0:
            return
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

    def get_rect(self):
        return pygame.Rect(self.x + 5, self.y + 10, self.width - 10, self.height - 10)


class Enemy:
    def __init__(self, x, y, color=ORANGE, speed_x=2, drop=20):
        self.width = 40
        self.height = 30
        self.x = x
        self.y = y
        self.base_speed = speed_x
        self.speed_x = speed_x
        self.drop = drop
        self.color = color

    def draw(self, screen):
        c = self.color
        pygame.draw.rect(screen, c, (self.x + 5, self.y + 10, 30, 15))
        pygame.draw.rect(screen, c, (self.x + 10, self.y, 20, 15))
        pygame.draw.circle(screen, BLACK, (self.x + 15, self.y + 7), 3)
        pygame.draw.circle(screen, BLACK, (self.x + 25, self.y + 7), 3)
        pygame.draw.rect(screen, c, (self.x, self.y + 25, 8, 5))
        pygame.draw.rect(screen, c, (self.x + 12, self.y + 25, 8, 5))
        pygame.draw.rect(screen, c, (self.x + 24, self.y + 25, 8, 5))
        pygame.draw.rect(screen, c, (self.x + 32, self.y + 25, 8, 5))

    def get_rect(self):
        return pygame.Rect(self.x + 5, self.y, 30, 30)

    def shoot(self):
        return Bullet(self.x + self.width // 2, self.y + self.height, 5, RED)


class Bullet:
    def __init__(self, x, y, speed, color):
        self.x = x
        self.y = y
        self.speed = speed
        self.color = color
        self.radius = 4

    def move(self):
        self.y += self.speed

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                           self.radius * 2, self.radius * 2)


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
        self.reset()

    def reset(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(-SCREEN_HEIGHT, 0)
        self.speed = random.uniform(1, 3)
        self.rotation = random.randint(0, 360)
        self.size = random.randint(15, 30)

    def move(self):
        self.y += self.speed
        self.rotation += 2
        if self.y > SCREEN_HEIGHT + 50:
            self.reset()
            self.y = random.randint(-100, -50)

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


class Explosion:
    def __init__(self, x, y, color=ORANGE):
        self.x = x
        self.y = y
        self.color = color
        self.particles = [
            [random.uniform(-3, 3), random.uniform(-3, 3), random.randint(3, 7)]
            for _ in range(12)
        ]
        self.life = 20

    def update(self):
        self.life -= 1
        for p in self.particles:
            p[0] *= 0.95
            p[1] *= 0.95
            p[2] = max(1, p[2] - 0.3)

    def draw(self, screen):
        alpha = max(0, self.life * 10)
        for px, py, pr in self.particles:
            x = int(self.x + px * (20 - self.life))
            y = int(self.y + py * (20 - self.life))
            pygame.draw.circle(screen, self.color, (x, y), int(pr))

    def done(self):
        return self.life <= 0


# ─── HELPERS ──────────────────────────────────────────────────────────────────

def move_enemies(enemies, config):
    for enemy in enemies:
        enemy.x += enemy.speed_x

    change_direction = any(
        e.x <= 0 or e.x >= SCREEN_WIDTH - e.width for e in enemies
    )

    if change_direction:
        for enemy in enemies:
            enemy.speed_x *= -1
            enemy.y += config["enemy_drop"]


def spawn_enemies(level):
    cfg = get_level_config(level)
    enemies = []
    for row in range(cfg["enemy_rows"]):
        for col in range(cfg["enemy_cols"]):
            x = col * 70 + (SCREEN_WIDTH - cfg["enemy_cols"] * 70) // 2
            y = row * 55 + 60
            e = Enemy(x, y,
                      color=cfg["color"],
                      speed_x=cfg["enemy_speed"],
                      drop=cfg["enemy_drop"])
            enemies.append(e)
    return enemies


def draw_background(screen, stars, asteroids, planets):
    screen.fill(DARK_BLUE)
    for planet in planets:
        planet.draw(screen)
    for star in stars:
        star.draw(screen)
    for asteroid in asteroids:
        asteroid.draw(screen)


def draw_hud(screen, score, level, lives):
    # Score
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    # Level badge
    lvl_text = font.render(f"Level: {level}", True, CYAN)
    screen.blit(lvl_text, (SCREEN_WIDTH // 2 - lvl_text.get_width() // 2, 10))

    # Lives (heart icons)
    for i in range(lives):
        hx = SCREEN_WIDTH - 30 - i * 28
        pygame.draw.polygon(screen, RED, [
            (hx, 12), (hx - 8, 6), (hx - 12, 10),
            (hx - 12, 15), (hx, 24), (hx + 12, 15),
            (hx + 12, 10), (hx + 8, 6)
        ])

    # Watermark
    wm = watermark_font.render("by Alvino Aldorino", True, LIGHT_GRAY)
    screen.blit(wm, (SCREEN_WIDTH // 2 - wm.get_width() // 2, SCREEN_HEIGHT - 14))


def draw_highscores(screen, scores):
    """Draw top scores panel."""
    panel_w, panel_h = 360, 340
    px = (SCREEN_WIDTH - panel_w) // 2
    py = (SCREEN_HEIGHT - panel_h) // 2 + 30

    # Panel background
    s = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    s.fill((10, 10, 40, 210))
    screen.blit(s, (px, py))
    pygame.draw.rect(screen, CYAN, (px, py, panel_w, panel_h), 2)

    title = font.render("🏆  HIGH SCORES", True, GOLD)
    screen.blit(title, (px + panel_w // 2 - title.get_width() // 2, py + 10))

    if not scores:
        no_score = small_font.render("No scores yet!", True, WHITE)
        screen.blit(no_score, (px + panel_w // 2 - no_score.get_width() // 2, py + 80))
        return

    headers = small_font.render(f"{'#':<3}  {'Score':<8}  {'Lvl':<5}  Date", True, CYAN)
    screen.blit(headers, (px + 15, py + 50))
    pygame.draw.line(screen, CYAN, (px + 10, py + 75), (px + panel_w - 10, py + 75), 1)

    for i, entry in enumerate(scores[:8]):
        color = GOLD if i == 0 else WHITE
        line = small_font.render(
            f"{i+1:<3}  {entry['score']:<8}  {entry['level']:<5}  {entry['date']}",
            True, color
        )
        screen.blit(line, (px + 15, py + 85 + i * 28))


# ─── SCREENS ──────────────────────────────────────────────────────────────────

def show_level_banner(screen, level, stars, asteroids, planets, draw_bg_fn):
    """Show a "Level X" banner for ~2 seconds."""
    cfg = get_level_config(level)
    start = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start < 2000:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
        for star in stars:
            star.move()
        for ast in asteroids:
            ast.move()

        draw_bg_fn(screen, stars, asteroids, planets)

        elapsed = pygame.time.get_ticks() - start
        alpha_val = min(255, elapsed * 3) if elapsed < 600 else max(0, 255 - (elapsed - 1400) * 2)
        alpha_val = max(0, min(255, int(alpha_val)))

        # Glow banner
        banner_surf = pygame.Surface((500, 100), pygame.SRCALPHA)
        banner_alpha = max(0, min(255, int(alpha_val * 0.6)))
        banner_surf.fill((0, 0, 0, banner_alpha))
        screen.blit(banner_surf, (150, 230))

        txt = large_font.render(cfg["label"], True, cfg["color"])
        txt.set_alpha(alpha_val)
        screen.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2, 240))

        sub = font.render("GET READY!", True, WHITE)
        sub.set_alpha(alpha_val)
        screen.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, 310))

        pygame.display.flip()
        clock.tick(60)
    return True


# ─── MAIN GAME LOOP ──────────────────────────────────────────────────────────

def main():
    player = Player()

    stars = [Star() for _ in range(100)]
    asteroids = [Asteroid() for _ in range(5)]
    planets = [
        Planet(700, 100, 40, (150, 150, 150)),
        Planet(650, 300, 50, (255, 100, 150), True),
        Planet(100, 150, 30, (100, 200, 255)),
    ]

    level = 1
    score = 0

    enemies = spawn_enemies(level)
    show_level_banner(screen, level, stars, asteroids, planets, draw_background)

    enemy_bullets = []
    explosions = []

    game_over = False
    won_level = False
    score_saved = False
    running = True

    cfg = get_level_config(level)

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
                if event.key == pygame.K_q:
                    running = False

        if not game_over:
            keys = pygame.key.get_pressed()
            player.move(keys)
            player.update()

            # Move enemies
            if enemies:
                move_enemies(enemies, cfg)

            # Enemy shooting
            for enemy in enemies:
                if random.random() < cfg["enemy_shoot"]:
                    enemy_bullets.append(enemy.shoot())

            # Move player bullets
            for b in player.bullets[:]:
                b.move()
                if b.y < 0:
                    player.bullets.remove(b)

            # Move enemy bullets
            for b in enemy_bullets[:]:
                b.move()
                if b.y > SCREEN_HEIGHT:
                    enemy_bullets.remove(b)

            # Player bullet vs enemy
            for b in player.bullets[:]:
                for e in enemies[:]:
                    if b.get_rect().colliderect(e.get_rect()):
                        if b in player.bullets:
                            player.bullets.remove(b)
                        enemies.remove(e)
                        explosions.append(Explosion(e.x + 20, e.y + 15, e.color))
                        score += 10 * level
                        break

            # Enemy bullet vs player
            for b in enemy_bullets[:]:
                if b.get_rect().colliderect(player.get_rect()):
                    enemy_bullets.remove(b)
                    player.hit()
                    explosions.append(Explosion(player.x + 20, player.y + 20, BLUE))
                    if player.lives <= 0:
                        game_over = True

            # Enemies reach bottom
            for e in enemies:
                if e.y + e.height > SCREEN_HEIGHT - 60:
                    game_over = True

            # Explosions
            for ex in explosions[:]:
                ex.update()
                if ex.done():
                    explosions.remove(ex)

            # Move background
            for s in stars:
                s.move()
            for a in asteroids:
                a.move()

            # All enemies dead → level complete
            if len(enemies) == 0 and not game_over:
                # Bonus score for remaining lives
                score += player.lives * 50
                level += 1
                cfg = get_level_config(level)
                enemies = spawn_enemies(level)
                enemy_bullets.clear()
                # Brief banner
                if not show_level_banner(screen, level, stars, asteroids, planets, draw_background):
                    running = False

        # ── DRAW ──────────────────────────────────────────
        draw_background(screen, stars, asteroids, planets)

        player.draw(screen)
        for e in enemies:
            e.draw(screen)
        for b in player.bullets:
            b.draw(screen)
        for b in enemy_bullets:
            b.draw(screen)
        for ex in explosions:
            ex.draw(screen)

        draw_hud(screen, score, level, player.lives)

        # ── GAME OVER OVERLAY ──────────────────────────────
        if game_over:
            if not score_saved:
                save_score(score, level)
                score_saved = True

            scores = load_scores()

            # Dim overlay
            dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            dim.fill((0, 0, 0, 160))
            screen.blit(dim, (0, 0))

            if player.lives <= 0:
                msg = game_over_font.render("GAME OVER", True, RED)
            else:
                msg = game_over_font.render("YOU WIN!", True, YELLOW)

            screen.blit(msg, msg.get_rect(center=(SCREEN_WIDTH // 2, 100)))

            score_msg = font.render(f"Final Score: {score}   Level: {level}", True, WHITE)
            screen.blit(score_msg, score_msg.get_rect(center=(SCREEN_WIDTH // 2, 160)))

            draw_highscores(screen, scores)

            restart = small_font.render("Press R to Restart  |  Q to Quit", True, LIGHT_GRAY)
            screen.blit(restart, restart.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()