import pygame
import random
import time
import os

# ==========================================
# GEO-MOTO MATRIX (Bike Racing Edition)
# Developed for Computer Graphics Lab
# Author: Md. Anisur Rahman Bhuiyan (Ayaan)
# ==========================================

# 1. Initialization and Setup
pygame.init()
WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Geo-Moto Matrix")
clock = pygame.time.Clock()

# Colors
BG_COLOR = (20, 24, 30)          # Darker asphalt environment
ROAD_COLOR = (45, 52, 54)        # Road surface
LINE_COLOR = (223, 230, 233)     # Road lines
PLAYER_BIKE = (16, 185, 129)     # Neon Green Player Bike
ENEMY_BIKE = (255, 118, 117)     # Red/Pink Enemy Bike
TEXT_COLOR = (0, 206, 201)       # Cyan UI text
COIN_COLOR = (253, 203, 110)     # Golden Coin
SHIELD_COLOR = (108, 92, 231)    # Purple Shield

# Fonts
font_large = pygame.font.SysFont("Courier New", 42, bold=True)
font_small = pygame.font.SysFont("Arial", 20, bold=True)

# File I/O for High Score
def load_high_score():
    if os.path.exists("bike_highscore.txt"):
        with open("bike_highscore.txt", "r") as file:
            try:
                return float(file.read())
            except:
                return 0.0
    return 0.0

def save_high_score(score):
    with open("bike_highscore.txt", "w") as file:
        file.write(f"{score:.2f}")

high_score = load_high_score()

# 2. Modular Drawing Function (Geometric Bike Construction)
def draw_bike(surface, x, y, color):
    # Front Tire (Dark grey rectangle)
    pygame.draw.rect(surface, (15, 20, 25), (x + 10, y, 10, 18), border_radius=3)
    # Rear Tire (Dark grey rectangle)
    pygame.draw.rect(surface, (15, 20, 25), (x + 10, y + 52, 10, 18), border_radius=3)
    # Main Body (Slim colored rectangle)
    pygame.draw.rect(surface, color, (x + 6, y + 12, 18, 45), border_radius=6)
    # Handlebars (Horizontal line)
    pygame.draw.rect(surface, (178, 190, 195), (x, y + 20, 30, 4), border_radius=2)
    # Headlight (Bright glowing circle at the front)
    pygame.draw.circle(surface, (255, 255, 255), (x + 15, y + 5), 5)
    pygame.draw.circle(surface, (253, 224, 71), (x + 15, y + 5), 7, 1) # Glow ring

# 3. Object Classes
class PlayerBike:
    def __init__(self):
        self.width = 30 # Slimmer hitbox for bike
        self.height = 70
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - 120
        self.speed = 9 # Bikes are slightly faster
        self.shield_active = False
        self.shield_timer = 0

    def move(self, keys):
        # Option 1: Mouse Swipe Logic
        if pygame.mouse.get_pressed()[0]: 
            mouse_x = pygame.mouse.get_pos()[0]
            target_x = mouse_x - (self.width // 2)
            self.x += (target_x - self.x) * 0.20 # Faster steering response for bike
            
        # Option 2: Keyboard Logic
        if keys[pygame.K_LEFT]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.x += self.speed
            
        # Boundary Detection
        if self.x < 100:
            self.x = 100
        elif self.x > WIDTH - 100 - self.width:
            self.x = WIDTH - 100 - self.width

        # Check shield expiration
        if self.shield_active and time.time() > self.shield_timer:
            self.shield_active = False

    def draw(self, surface):
        draw_bike(surface, self.x, self.y, PLAYER_BIKE)
        if self.shield_active:
            # Forcefield effect
            pygame.draw.ellipse(surface, SHIELD_COLOR, (self.x - 15, self.y - 10, 60, 90), 3)
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class EnemyBike:
    def __init__(self, speed_multiplier=1.0):
        self.width = 30
        self.height = 70
        self.x = random.choice([120, 220, 320, 420]) # Adjusted lanes for bikes
        self.y = random.randint(-500, -100)
        self.base_speed = random.uniform(6.0, 10.0)
        self.dy = self.base_speed * speed_multiplier

    def move(self, speed_multiplier):
        self.dy = self.base_speed * speed_multiplier
        self.y += self.dy
        if self.y > HEIGHT:
            self.y = random.randint(-500, -100)
            self.x = random.choice([120, 220, 320, 420])

    def draw(self, surface):
        draw_bike(surface, self.x, self.y, ENEMY_BIKE)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Collectible:
    def __init__(self, c_type):
        self.type = c_type
        self.radius = 15
        self.x = random.choice([150, 250, 350, 450])
        self.y = random.randint(-800, -200)
        self.dy = 6.0

    def move(self, speed_multiplier):
        self.y += self.dy * speed_multiplier
        if self.y > HEIGHT:
            self.y = random.randint(-1500, -500)
            self.x = random.choice([150, 250, 350, 450])
            self.type = random.choices(['coin', 'shield'], weights=[80, 20])[0]

    def draw(self, surface):
        color = COIN_COLOR if self.type == 'coin' else SHIELD_COLOR
        pygame.draw.polygon(surface, color, [
            (self.x, self.y - 15), (self.x + 15, self.y), 
            (self.x, self.y + 15), (self.x - 15, self.y)
        ]) # Drawn as a diamond shape for a different look
        pygame.draw.circle(surface, (255, 255, 255), (self.x, int(self.y)), 4)

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius*2, self.radius*2)

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx = random.uniform(-5, 5)
        self.dy = random.uniform(-5, 5)
        self.radius = random.randint(3, 8)
        self.life = 35 

    def move_and_draw(self, surface):
        self.x += self.dx
        self.y += self.dy
        self.radius = max(0, self.radius - 0.2)
        self.life -= 1
        color = random.choice([(255, 100, 0), (255, 200, 0), (200, 200, 200)])
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), int(self.radius))

# 4. Game State Variables
player = PlayerBike()
enemies = []
collectibles = []
particles = []
line_offset = 0
game_state = "START"
start_time = 0
time_bonus = 0
speed_multiplier = 1.0

# 5. Main Execution Loop
running = True
while running:
    screen.fill(BG_COLOR)
    
    # Scenery (Road Borders)
    pygame.draw.rect(screen, ROAD_COLOR, (100, 0, 400, HEIGHT))
    # Draw yellow side lines
    pygame.draw.line(screen, (253, 203, 110), (100, 0), (100, HEIGHT), 5)
    pygame.draw.line(screen, (253, 203, 110), (495, 0), (495, HEIGHT), 5)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == "START" or game_state == "GAMEOVER":
                game_state = "PLAYING"
                player = PlayerBike()
                speed_multiplier = 1.0
                enemies = [EnemyBike(speed_multiplier) for _ in range(5)] # 5 enemy bikes
                collectibles = [Collectible('coin'), Collectible('shield')]
                particles = []
                start_time = time.time()
                time_bonus = 0

    if game_state == "START":
        title = font_large.render("GEO-MOTO MATRIX", True, PLAYER_BIKE)
        prompt = font_small.render("USE ARROWS OR MOUSE. CLICK TO START", True, LINE_COLOR)
        hs_text = font_small.render(f"HIGH SCORE: {high_score:.2f} SEC", True, COIN_COLOR)
        
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))
        screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, HEIGHT//2))
        screen.blit(hs_text, (WIDTH//2 - hs_text.get_width()//2, HEIGHT//2 + 40))
        
    elif game_state == "PLAYING":
        elapsed_actual = time.time() - start_time
        speed_multiplier = 1.0 + (elapsed_actual * 0.025) # Bikes accelerate slightly faster
        
        # Draw moving dashed road lines
        line_offset = (line_offset + 7 * speed_multiplier) % 40
        for y in range(-40, HEIGHT, 40):
            pygame.draw.rect(screen, LINE_COLOR, (WIDTH//2 - 5, y + line_offset, 10, 20))
            
        keys = pygame.key.get_pressed()
        player.move(keys)
        player.draw(screen)
        
        for item in collectibles:
            item.move(speed_multiplier)
            item.draw(screen)
            
            if player.get_rect().colliderect(item.get_rect()):
                if item.type == 'coin':
                    time_bonus += 3.0 
                elif item.type == 'shield':
                    player.shield_active = True
                    player.shield_timer = time.time() + 5.0 
                
                item.y = random.randint(-1500, -500)
                item.x = random.choice([150, 250, 350, 450])
        
        for enemy in enemies:
            enemy.move(speed_multiplier)
            enemy.draw(screen)
            
            if player.get_rect().colliderect(enemy.get_rect()):
                if player.shield_active:
                    enemy.y = random.randint(-500, -100)
                    for _ in range(10): # Small spark particles on shield impact
                        particles.append(Particle(enemy.x + 15, enemy.y + 35))
                else:
                    game_state = "GAMEOVER"
                    for _ in range(40):
                        particles.append(Particle(player.x + 15, player.y + 35))
                        
                    final_score = elapsed_actual + time_bonus
                    if final_score > high_score:
                        high_score = final_score
                        save_high_score(high_score)

        # Background Particle processing (Sparks)
        for p in particles[:]:
            p.move_and_draw(screen)
            if p.life <= 0:
                particles.remove(p)

        total_score = elapsed_actual + time_bonus
        score_str = f"SCORE: {total_score:05.2f}"
        score_surface = font_small.render(score_str, True, TEXT_COLOR)
        screen.blit(score_surface, (15, 15))
        
        if player.shield_active:
            shield_text = font_small.render("SHIELD ACTIVE!", True, SHIELD_COLOR)
            screen.blit(shield_text, (WIDTH - 170, 15))
        
    elif game_state == "GAMEOVER":
        for p in particles[:]:
            p.move_and_draw(screen)
            if p.life <= 0:
                particles.remove(p)
                
        end_title = font_large.render("WIPEOUT!", True, ENEMY_BIKE)
        score_text = font_small.render(f"FINAL SCORE: {total_score:.2f}", True, LINE_COLOR)
        hs_text = font_small.render(f"HIGH SCORE: {high_score:.2f}", True, COIN_COLOR)
        restart_prompt = font_small.render("CLICK TO RESTART", True, TEXT_COLOR)
        
        screen.blit(end_title, (WIDTH//2 - end_title.get_width()//2, HEIGHT//3))
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 - 20))
        screen.blit(hs_text, (WIDTH//2 - hs_text.get_width()//2, HEIGHT//2 + 10))
        screen.blit(restart_prompt, (WIDTH//2 - restart_prompt.get_width()//2, HEIGHT//2 + 50))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()