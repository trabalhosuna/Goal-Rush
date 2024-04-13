import cv2
import mediapipe as mp
import pygame
import random

"""Nesta versao, foram corrigidos bugs no personagens, melhorado o tempo de resposta do tracking, resolvido o problema de desempenho"""
"""Foi adicionado spot para da jogador dentro da web cam, cada um deve permanercer em um lado e podera ultilizar qualquer mao para a jogabilidade"""
"""É considerado para o movimento do jogador somente as coordenadas da landmark(8) que é referente a ponta do dedo indicador"""

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

    jogador_esquerda = Jogador(100, 360, jogador_esquerda_imagem) # define instancia jogador esq
    jogador_direita = Jogador(1180, 360, jogador_direita_imagem) # define instancia jogador dir
    speed = random.choice([-10, 10]) # define velocidade da bola e randomiza a saida
    bola_objeto = Bola(615, 255, speed, bola_imagem) # define instancia bola
    bola_objeto.rect.inflate_ip(20, 20) # aumenta o tamanho do hitbox da bola

    # Inicialize o MediaPipe Hands.
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5)
    mp_drawing = mp.solutions.drawing_utils
    cap = cv2.VideoCapture(0)

    y_esquerda = 0 # armazena o valor inicial da coordenada y
    y_direita = 0
    Velocidade= 1000

    rodando = True
    pontos_D = 0
    pontos_E = 0

    largura_video = 640 # largura da tela (cam)
    altura_video = 480 # altura da tela (cam)

    def desenhar_linha_vertical(image): # Função para desenhar uma linha vertical no meio do vídeo
        meio_x = largura_video // 2
        cv2.line(image, (meio_x, 0), (meio_x, altura_video), (0, 0, 255), 1) # Desenha a linha vertical, cor= (B,G,R) e espessura= 1


    while rodando: #loop principal do jogo
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False

        # Captura de vídeo e rastreamento de mãos
        success, image = cap.read() #verifica se recebe a imagem da cam
        if not success:
            break
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image_rgb) #recebe o processamento das maos em padrao RGB

        desenhar_linha_vertical(image) # chama a funcao para desenhar a linha vertical

        # Desenhe as landmarks da mão na imagem.
        if results.multi_hand_landmarks: #verifica se a mao foi detectada
            for hand_landmarks in results.multi_hand_landmarks: #para cada landmark em result
                mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS) #desenha as conexoes entre os pontos

            # Adicione a lógica para detectar a mão esquerda e direita.
            for hand_landmarks in results.multi_hand_landmarks: #para cada landmark em result
                landmark_atual = hand_landmarks.landmark[8] # 8 é o índice do landmark que representa a ponta do dedo indicador
                if landmark_atual.x < 0.5: #0.5 define o ponto medio da tela em que a coordenada da landmark pode estar
                    #esquerda
                    movimento_esquerda= (landmark_atual.y - y_esquerda) * Velocidade
                    #print(movimento_esquerda)
                    jogador_esquerda.mover(movimento_esquerda) #Move o jogador esq
                    y_esquerda = landmark_atual.y
                if landmark_atual.x > 0.5:
                    #direita
                    movimento_direita= (landmark_atual.y - y_direita) * Velocidade
                    #print(movimento_direita)
                    jogador_direita.mover(movimento_direita) #Move o jogador dir
                    y_direita = landmark_atual.y


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