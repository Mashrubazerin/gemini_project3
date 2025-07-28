
import pygame
import random
import sys

# --- Initialization ---
pygame.init()
pygame.mixer.init()

# --- Screen Dimensions ---
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Starship Dodger")

# --- Colors ---
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
blue = (0, 0, 255)

# --- Game Clock ---
clock = pygame.time.Clock()
fps = 60

# --- Asset Loading (with placeholders) ---
try:
    player_img = pygame.image.load("player.png").convert_alpha()
    player_img = pygame.transform.scale(player_img, (200, 150))
except pygame.error:
    player_img = pygame.Surface((200, 150))
    player_img.fill(blue)

asteroid_images = {}
try:
    asteroid_base_img = pygame.image.load("asteroid.png").convert_alpha()
    asteroid_images['large'] = pygame.transform.scale(asteroid_base_img, (80, 80))
    asteroid_images['small'] = pygame.transform.scale(asteroid_base_img, (30, 30))
except pygame.error:
    asteroid_images['large'] = pygame.Surface((80, 80))
    asteroid_images['large'].fill(red)
    asteroid_images['small'] = pygame.Surface((30, 30))
    asteroid_images['small'].fill(red)


try:
    background_img = pygame.image.load("background.png").convert()
    background_img = pygame.transform.scale(background_img, (screen_width, screen_height))
except pygame.error:
    background_img = pygame.Surface((screen_width, screen_height))
    background_img.fill(black)

try:
    pygame.mixer.music.load("music.mp3")
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(loops=-1)  # Play on loop
except pygame.error:
    print("Could not load music.mp3")

try:
    explosion_sound = pygame.mixer.Sound("explosion.wav")
    explosion_sound.set_volume(0.8)
except pygame.error:
    # Dummy sound object if file is not found
    class DummySound:
        def play(self): pass
    explosion_sound = DummySound()
    print("Could not load explosion.wav")


# --- Player Class ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.centerx = screen_width // 2
        self.rect.bottom = screen_height - 10
        self.speed_x = 0

    def update(self):
        self.speed_x = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speed_x = -8
        if keystate[pygame.K_RIGHT]:
            self.speed_x = 8
        self.rect.x += self.speed_x

        # Keep player on the screen
        if self.rect.right > screen_width:
            self.rect.right = screen_width
        if self.rect.left < 0:
            self.rect.left = 0

# --- Asteroid Class ---
class Asteroid(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.type = random.choice(['large', 'small'])
        self.image = asteroid_images[self.type]
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(screen_width - self.rect.width)
        self.rect.y = random.randrange(-150, -100)
        
        if self.type == 'large':
            self.speed_y = random.randrange(1, 4)
            self.points = 1
        else: # small
            self.speed_y = random.randrange(4, 10)
            self.points = 3


    def update(self):
        self.rect.y += self.speed_y
        # Let the game loop handle respawning

# --- Game Functions ---
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(pygame.font.match_font('arial'), size)
    text_surface = font.render(text, True, white)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

def show_start_screen():
    screen.blit(background_img, (0,0))
    draw_text(screen, "STARSHIP DODGER", 64, screen_width / 2, screen_height / 4)
    draw_text(screen, "Arrow keys to move, hit asteroids to score points!", 22, screen_width / 2, screen_height / 2)
    draw_text(screen, "Large asteroids are worth 1 point, small are worth 3.", 22, screen_width / 2, screen_height / 2 + 40)
    draw_text(screen, "Don't let them get past you! You have 5 lives.", 22, screen_width / 2, screen_height / 2 + 80)
    draw_text(screen, "Press any key to begin", 18, screen_width / 2, screen_height * 3 / 4)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYUP:
                waiting = False

# --- Game Loop ---
def game_loop():
    all_sprites = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    player = Player()
    all_sprites.add(player)

    for i in range(8):
        a = Asteroid()
        all_sprites.add(a)
        asteroids.add(a)

    score = 0
    lives = 5
    running = True
    music_paused_until = 0
    music_paused = False

    while running:
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Unpause music if it's time
        if music_paused and pygame.time.get_ticks() > music_paused_until:
            pygame.mixer.music.unpause()
            music_paused = False

        # Update
        all_sprites.update()

        # Check for asteroids that have gone off the bottom of the screen
        for asteroid in list(asteroids): # Iterate over a copy
            if asteroid.rect.top > screen_height + 10:
                lives -= 1
                asteroid.kill()
                a = Asteroid()
                all_sprites.add(a)
                asteroids.add(a)
        
        if lives <= 0:
            running = False

        # Check for collisions
        hits = pygame.sprite.spritecollide(player, asteroids, True)
        for hit in hits:
            score += hit.points
            pygame.mixer.music.pause()
            music_paused = True
            # Safely get sound length
            try:
                sound_length = int(explosion_sound.get_length() * 1000)
            except:
                sound_length = 500 # fallback to 500ms
            music_paused_until = pygame.time.get_ticks() + sound_length
            explosion_sound.play()
            a = Asteroid()
            all_sprites.add(a)
            asteroids.add(a)

        # Draw / render
        screen.blit(background_img, (0,0))
        all_sprites.draw(screen)
        draw_text(screen, f"Score: {score}", 28, screen_width / 2, 10)
        draw_text(screen, f"Lives: {lives}", 28, 70, 10)


        pygame.display.flip()
        clock.tick(fps)

    return score

# --- Main Execution ---
show_start_screen()
final_score = game_loop()

# Game over screen
screen.blit(background_img, (0,0))
draw_text(screen, "GAME OVER", 64, screen_width / 2, screen_height / 4)
draw_text(screen, f"Final Score: {final_score}", 30, screen_width / 2, screen_height / 2)
draw_text(screen, "Press any key to quit", 18, screen_width / 2, screen_height * 3 / 4)
pygame.display.flip()

waiting = True
while waiting:
    clock.tick(fps)
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.KEYUP:
            waiting = False

pygame.quit()
sys.exit()
