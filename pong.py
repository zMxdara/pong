import cv2
import numpy as np
import pygame
import sys
import random
from collections import deque

# Initialize Pygame
pygame.init()

# Constants
WIN_WIDTH = 800
WIN_HEIGHT = 600
BALL_RADIUS = 10
PADDLE_WIDTH = 20
PADDLE_HEIGHT = 100
PADDLE_SPEED = 5
SCORE_LIMIT = 7
FONT_SIZE = 30
BALL_MIN_SPEED = 3
BALL_MAX_SPEED = 7
PARTICLE_COUNT = 20

# Colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# Set up the window
win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Pong")

# Load font
font = pygame.font.Font('PressStart2P.ttf', FONT_SIZE)

# Load background image
bg_image = pygame.image.load('background.jpg')
bg_image = pygame.transform.scale(bg_image, (WIN_WIDTH, WIN_HEIGHT))

# Load sound effects
paddle_hit_sound = pygame.mixer.Sound("paddle_hit.wav")

# Load background music
pygame.mixer.music.load("background_music.mp3")
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1)

# Initialize the camera
cap = cv2.VideoCapture(0)

def get_paddle_positions(prev_left_y, prev_right_y):
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define colour range for detecting hands
    lower_range = np.array([0, 20, 70])
    upper_range = np.array([20, 255, 255])

    # Threshold the HSV image to get only the desired colours
    mask = cv2.inRange(hsv_frame, lower_range, upper_range)

    # Find contours in the binary image
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Sort contours by area
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:2]

    positions = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        positions.append((x, y + h // 2))

    # Apply smoothing to the paddle positions
    smoothing_factor = 0.8
    if len(positions) == 2:
        left_paddle_pos, right_paddle_pos = sorted(positions, key=lambda pos: pos[0])
        left_y = int(prev_left_y * smoothing_factor + left_paddle_pos[1] * (1 - smoothing_factor))
        right_y = int(prev_right_y * smoothing_factor + right_paddle_pos[1] * (1 - smoothing_factor))
        return [(left_paddle_pos[0], left_y), (right_paddle_pos[0], right_y)]

    return positions

def detect_hand_side(x, y):
    if x < WIN_WIDTH // 2:
        return 'left'
    else:
        return 'right'

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.randint(-2, 2)
        self.vy = random.randint(-2, 2)
        self.size = random.randint(1, 3)

    def move(self):
        self.x += self.vx
        self.y += self.vy
        self.size -= 0.1

    def draw(self, surface):
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), int(self.size))

class Paddle:
    def __init__(self, x, player_num):
        self.x = x
        self.y = WIN_HEIGHT // 2
        self.rect = pygame.Rect(self.x, self.y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.player_num = player_num
        self.color = BLUE if player_num == 1 else RED

    def move(self, y):
        self.y = y
        self.update()

    def update(self):
        self.rect = pygame.Rect(self.x, self.y - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)

class Ball:
    def __init__(self):
        self.x = WIN_WIDTH // 2
        self.y = WIN_HEIGHT // 2
        self.vx = random.choice([-1, 1]) * random.randint(BALL_MIN_SPEED, BALL_MAX_SPEED)
        self.vy = random.choice([-1, 1]) * random.randint(BALL_MIN_SPEED, BALL_MAX_SPEED)
        self.rect = pygame.Rect(self.x - BALL_RADIUS, self.y - BALL_RADIUS, BALL_RADIUS * 2, BALL_RADIUS * 2)

    def move(self):
        self.x += self.vx
        self.y += self.vy
        self.update()

    def update(self):
        self.rect = pygame.Rect(self.x - BALL_RADIUS, self.y - BALL_RADIUS, BALL_RADIUS * 2, BALL_RADIUS * 2)

def main_menu():
    run = True
    while run:
        win.blit(bg_image, (0, 0))
        title_font = pygame.font.Font('PressStart2P.ttf', 40)
        title_text = title_font.render("PONG", True, WHITE)
        win.blit(title_text, (WIN_WIDTH // 2 - title_text.get_width() // 2, 50))

        keys_font = pygame.font.Font('PressStart2P.ttf', 16)
        keys_text = keys_font.render("Press K for Keyboard or G for Gesture Control", True, WHITE)
        win.blit(keys_text, (WIN_WIDTH // 2 - keys_text.get_width() // 2, 300))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_k:
                    main(control_scheme="keyboard")
                if event.key == pygame.K_g:
                    main(control_scheme="gesture")

    pygame.quit()
    cap.release()
    cv2.destroyAllWindows()
    sys.exit()

def winner_screen(winner):
    run = True
    while run:
        win.blit(bg_image, (0, 0))
        winner_font = pygame.font.Font('PressStart2P.ttf', 30)
        winner_text = winner_font.render(f"Player {winner} wins!", True, WHITE)
        win.blit(winner_text, (WIN_WIDTH // 2 - winner_text.get_width() // 2, 200))

        restart_font = pygame.font.Font('PressStart2P.ttf', 20)
        restart_text = restart_font.render("Press SPACE to restart or ESC to quit", True, WHITE)
        win.blit(restart_text, (WIN_WIDTH // 2 - restart_text.get_width() // 2, 300))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    main_menu()
                if event.key == pygame.K_ESCAPE:
                    run = False

    pygame.quit()
    cap.release()
    cv2.destroyAllWindows()
    sys.exit()

def main(control_scheme="keyboard"):
    # Initialize the game objects
    left_paddle = Paddle(PADDLE_WIDTH, 1)
    right_paddle = Paddle(WIN_WIDTH - PADDLE_WIDTH * 2, 2)
    ball = Ball()
    particles = deque(maxlen=PARTICLE_COUNT)

    # Initialize the scores
    scores = {1: 0, 2: 0}

    run = True
    while run:
        win.blit(bg_image, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # Move paddles
        if control_scheme == "keyboard":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                left_paddle.move(max(0, left_paddle.y - PADDLE_SPEED))
            if keys[pygame.K_s]:
                left_paddle.move(min(WIN_HEIGHT, left_paddle.y + PADDLE_SPEED))
            if keys[pygame.K_UP]:
                right_paddle.move(max(0, right_paddle.y - PADDLE_SPEED))
            if keys[pygame.K_DOWN]:
                right_paddle.move(min(WIN_HEIGHT, right_paddle.y + PADDLE_SPEED))
        elif control_scheme == "gesture":
            positions = get_paddle_positions(left_paddle.y, right_paddle.y)
            if len(positions) == 2:
                left_paddle.move(positions[0][1])
                right_paddle.move(positions[1][1])

        # Move ball
        ball.move()

        # Check for ball collisions
        if ball.y <= 0 or ball.y >= WIN_HEIGHT:
            ball.vy *= -1

        if ball.rect.colliderect(left_paddle.rect) or ball.rect.colliderect(right_paddle.rect):
            paddle_hit_sound.play()
            ball.vx *= -1

            particles.extend([Particle(ball.x, ball.y) for _ in range(PARTICLE_COUNT)])

        # Check for scoring
        if ball.x <= 0:
            scores[2] += 1
            ball = Ball()
        elif ball.x >= WIN_WIDTH:
            scores[1] += 1
            ball = Ball()

        # Draw paddles
        pygame.draw.rect(win, left_paddle.color, left_paddle.rect)
        pygame.draw.rect(win, right_paddle.color, right_paddle.rect)

        # Draw ball
        pygame.draw.circle(win, WHITE, (int(ball.x), int(ball.y)), BALL_RADIUS)

        # Draw particles
        for particle in list(particles):
            particle.move()
            if particle.size <= 0:
                particles.remove(particle)
            else:
                particle.draw(win)

        # Draw scores
        score_text = font.render(f"{scores[1]} - {scores[2]}", True, WHITE)
        win.blit(score_text, (WIN_WIDTH // 2 - score_text.get_width() // 2, 10))

        # Update the display
        pygame.display.update()

                # Check for game over
        if scores[1] == SCORE_LIMIT:
            winner_screen(1)
            run = False
        elif scores[2] == SCORE_LIMIT:
            winner_screen(2)
            run = False

        # Cap the frame rate
        pygame.time.delay(16)

    cap.release()

if __name__ == "__main__":
    main_menu()