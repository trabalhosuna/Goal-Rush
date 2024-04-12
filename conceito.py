import cv2
import mediapipe as mp
import pygame
import random

# Inicialize o MediaPipe Hands.
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Inicialize o Pygame.
pygame.init()
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()

# Cores
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Classe para representar os jogadores
class Player(pygame.sprite.Sprite):
    def __init__(self, color, x, y):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
    
    def update(self, x, y):
        self.rect.center = (x, y)

# Inicialização dos jogadores
player1 = Player(RED, screen_width//4, screen_height//2)
player2 = Player(BLUE, 3*screen_width//4, screen_height//2)
all_sprites = pygame.sprite.Group()
all_sprites.add(player1, player2)

# Inicialize a captura de vídeo.
cap = cv2.VideoCapture(0)

# Variáveis para a bola
ball_radius = 10
ball_pos = [screen_width//2, screen_height//2]
ball_vel = [random.choice([-5, 5]), random.choice([-5, 5])]

# Loop principal do jogo
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Captura e processamento das mãos
    success, image = cap.read()
    if success:
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Obtenha a posição do centro da palma da mão para controlar os jogadores
                for idx, landmark in enumerate(hand_landmarks.landmark):
                    if idx == 0: # Primeiro landmark é o centro da palma
                        hand_x = int(landmark.x * screen_width)
                        hand_y = int(landmark.y * screen_height)
                        # Atualiza a posição dos jogadores
                        if idx == 0:
                            player1.update(hand_x, hand_y)
                        elif idx == 1:
                            player2.update(hand_x, hand_y)

    # Atualiza a posição da bola
    ball_pos[0] += ball_vel[0]
    ball_pos[1] += ball_vel[1]

    # Lógica de colisão da bola com as bordas da tela
    if ball_pos[0] < 0 or ball_pos[0] > screen_width:
        ball_vel[0] = -ball_vel[0]
    if ball_pos[1] < 0 or ball_pos[1] > screen_height:
        ball_vel[1] = -ball_vel[1]

    # Verifica colisão da bola com os jogadores
    if player1.rect.colliderect(ball_pos[0]-ball_radius, ball_pos[1]-ball_radius, ball_radius*2, ball_radius*2):
        ball_vel[0] = -ball_vel[0]
    if player2.rect.colliderect(ball_pos[0]-ball_radius, ball_pos[1]-ball_radius, ball_radius*2, ball_radius*2):
        ball_vel[0] = -ball_vel[0]

    # Desenhe na tela
    screen.fill(WHITE)
    pygame.draw.circle(screen, (0, 0, 0), ball_pos, ball_radius)
    all_sprites.draw(screen)
    pygame.display.flip()

    clock.tick(60)

# Encerra a captura de vídeo e fecha o Pygame
cap.release()
cv2.destroyAllWindows()
pygame.quit()
