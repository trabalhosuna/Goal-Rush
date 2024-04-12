import cv2
import mediapipe as mp
import pygame
import random
import threading

"""Esta foi a primeira verso do jogo onde a jogabilidade foi definida e estava funcional"""

# Defina a velocidade dos jogadores
VELOCIDADE_JOGADOR = 1000

class Bola:
    def __init__(self, x, y, velocidade, imagem):
        self.x = x
        self.y = y
        self.velocidade_x = velocidade
        self.velocidade_y = velocidade
        self.imagem = imagem
        self.rect = self.imagem.get_rect(center=(x, y))
        self.angulo = 0

    def atualizar(self):
        self.x += self.velocidade_x
        self.y += self.velocidade_y
        self.rect.center = (self.x, self.y)
        self.angulo += 5

    def desenhar(self, tela):
        self.atualizar()
        imagem_rotacionada = pygame.transform.rotate(self.imagem, self.angulo)
        retangulo_rotacionado = imagem_rotacionada.get_rect(center=self.rect.center)
        tela.blit(imagem_rotacionada, retangulo_rotacionado)
        
    def colide_jogador(self, jogador):
        return self.rect.colliderect(jogador.rect)

class Jogador:
    def __init__(self, x, y, imagem):
        self.x = x
        self.y = y
        self.imagem = imagem
        self.rect = self.imagem.get_rect(center=(x, y))

    def mover(self, movimento):
        self.y += movimento
        if self.y < 0:
            self.y = 0
        elif self.y > 520:
            self.y = 520
        self.rect.center = (self.x, self.y)

    def desenhar(self, tela):
        tela.blit(self.imagem, self.rect)

def jogo():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption('O Jogo')
    clock = pygame.time.Clock()
    FPS = 60
    fonte = pygame.font.Font(None, 36)

    jogador_esquerda_imagem = pygame.image.load('imagens/bat1.png')
    jogador_direita_imagem = pygame.image.load('imagens/bat2.png')
    bola_imagem = pygame.image.load('imagens/ball.png')

    jogador_esquerda = Jogador(100, 360, jogador_esquerda_imagem)
    jogador_direita = Jogador(1180, 360, jogador_direita_imagem)
    speed = random.choice([-10, 10])
    bola_objeto = Bola(615, 255, speed, bola_imagem)
    bola_objeto.rect.inflate_ip(20, 20)

    # Inicialize o MediaPipe Hands.
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5)
    mp_drawing = mp.solutions.drawing_utils
    cap = cv2.VideoCapture(0)
    y_esquerda_anterior = 0
    y_direita_anterior = 0

    rodando = True
    pontos_D = 0
    pontos_E = 0

    while rodando:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False

        # Captura de vídeo e rastreamento de mãos
        success, image = cap.read()
        if success:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = hands.process(image_rgb)

            if results.multi_hand_landmarks and len(results.multi_hand_landmarks) >= 2:
                for hand_landmarks in results.multi_hand_landmarks:
                    if hand_landmarks == results.multi_hand_landmarks[0]:
                        landmark_esquerda = hand_landmarks.landmark[8] # 8 é o índice do landmark que representa a ponta do dedo indicador
                        y_esquerda = landmark_esquerda.y
                        if y_esquerda_anterior != 0: # Se o valor for diferente de zero, significa que o valor anterior foi armazenado
                            movimento_esquerda = (y_esquerda - y_esquerda_anterior) * VELOCIDADE_JOGADOR
                            jogador_direita.mover(movimento_esquerda) # Move o jogador
                        y_esquerda_anterior = y_esquerda

                    elif hand_landmarks == results.multi_hand_landmarks[1]:  
                        landmark_direita = hand_landmarks.landmark[8]
                        y_direita = landmark_direita.y
                        if y_direita_anterior != 0:
                            movimento_direita = (y_direita - y_direita_anterior) * VELOCIDADE_JOGADOR
                            jogador_esquerda.mover(movimento_direita) # Move o jogador
                        y_direita_anterior = y_direita

                    mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            cv2.imshow('MediaPipe Hands', image)
            key = cv2.waitKey(1)
            if key == ord('q'):
                break

        screen.fill((0, 0, 0))
        imagem_fundo = pygame.image.load('imagens/Background.png')
        screen.blit(imagem_fundo, (0, 0))

        jogador_esquerda.desenhar(screen)
        jogador_direita.desenhar(screen)
        bola_objeto.desenhar(screen)

        linha_campo = pygame.draw.rect(screen, (100, 255, 0), pygame.Rect(55, 13, 1173, 534), 6)
        if bola_objeto.rect.colliderect(linha_campo):
            if bola_objeto.rect.left <= linha_campo.left or bola_objeto.rect.right >= linha_campo.right:
                bola_objeto.velocidade_x *= -1
            if bola_objeto.rect.top <= linha_campo.top or bola_objeto.rect.bottom >= linha_campo.bottom:
                bola_objeto.velocidade_y *= -1

        if bola_objeto.colide_jogador(jogador_esquerda) or bola_objeto.colide_jogador(jogador_direita):
            bola_objeto.velocidade_x *= -1

        linha_gol_E = pygame.draw.rect(screen, (255, 10, 10), pygame.Rect(55, 226, 6, 116), 6)
        if bola_objeto.rect.colliderect(linha_gol_E):
            bola_objeto.x = (615)
            bola_objeto.y = (255)
            bola_objeto.velocidade_x *= -1
            pontos_D += 1
            
        linha_gol_D = pygame.draw.rect(screen, (255, 10, 10), pygame.Rect(1222, 225, 6, 116), 6)
        if bola_objeto.rect.colliderect(linha_gol_D):
            bola_objeto.x = (615)
            bola_objeto.y = (255)
            bola_objeto.velocidade_y *= -1
            pontos_E += 1
        
        texto_placar = fonte.render(f'Placar: {pontos_E} x {pontos_D}', True, (255, 255, 255))
        screen.blit(texto_placar, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    cap.release()
    cv2.destroyAllWindows()
    hands.close()

if __name__ == "__main__":
    jogo()