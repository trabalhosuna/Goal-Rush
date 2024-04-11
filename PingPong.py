import cv2
import mediapipe as mp
import pygame
import random
import threading

# Função para o jogo
def jogo():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption('O Jogo')

    # Definindo a taxa de atualização
    clock = pygame.time.Clock()
    FPS = 60  # Defina o valor desejado para FPS

    # Carregando a fonte
    fonte = pygame.font.Font(None, 36)

    class Bola:
        def _init_(self, x, y, velocidade, imagem):
            self.x = x
            self.y = y
            self.velocidade_x = velocidade
            self.velocidade_y = velocidade
            self.imagem = imagem
            self.rect = self.imagem.get_rect(center=(x, y))  # Obtém o retângulo de colisão da imagem
            self.angulo = 0

        def atualizar(self):
            # Atualiza a posição da bola com base na velocidade
            self.x += self.velocidade_x
            self.y += self.velocidade_y

            # Atualiza o retângulo de colisão com a nova posição da bola
            self.rect.center = (self.x, self.y)

            self.angulo += 5  # Define a velocidade de rotação

        def desenhar(self, tela):
            # Atualiza a posição da bola
            self.atualizar()
            imagem_rotacionada = pygame.transform.rotate(self.imagem, self.angulo)
            # Desenha a bola rotacionada
            retangulo_rotacionado = imagem_rotacionada.get_rect(center=self.rect.center)
            tela.blit(imagem_rotacionada, retangulo_rotacionado)
            
        def colide_jogador(self, jogador):
            return self.rect.colliderect(jogador.rect)

    class Jogador:
        def _init_(self, x, y, imagem):
            self.x = x
            self.y = y
            self.imagem = imagem
            self.rect = self.imagem.get_rect(center=(x, y))

        def atualizar(self, movimento):
            # Atualiza a posição do jogador com base no movimento
            self.y += movimento

            # Garante que o jogador permaneça dentro dos limites da tela
            if self.y < 0:
                self.y = 0
            elif self.y > 520:
                self.y = 520

            # Atualiza o retângulo de colisão
            self.rect.center = (self.x, self.y)

        def desenhar(self, tela):
            # Desenha o jogador na tela
            tela.blit(self.imagem, self.rect)

    # Carregue as imagens dos jogadores e da bola uma vez fora do loop principal
    jogador_esquerda_imagem = pygame.image.load('imagens/bat1.png')
    jogador_direita_imagem = pygame.image.load('imagens/bat2.png')
    bola_imagem = pygame.image.load('imagens/ball.png')

    # Crie instâncias dos jogadores
    jogador_esquerda = Jogador(100, 360, jogador_esquerda_imagem)
    jogador_direita = Jogador(1180, 360, jogador_direita_imagem)

    # Criando uma instância da bola fora do loop principal
    speed = random.choice([-10,10]) # random entre 8 e -8 é o ideal para sainda de bola
    bola_objeto = Bola(615, 255, speed, bola_imagem)
    bola_objeto.rect.inflate_ip(20,20)

    def Rodando():
        # Loop principal do jogo
        rodando = True
        pontos_D = 0
        pontos_E = 0
        while rodando:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    rodando = False

            # Limpa a tela
            screen.fill((0, 0, 0))

            # Desenha a imagem de fundo na posição (0, 0)
            imagem_fundo = pygame.image.load('imagens/Background.png')
            screen.blit(imagem_fundo, (0, 0))

            # Desenha os jogadores
            jogador_esquerda.desenhar(screen)
            jogador_direita.desenhar(screen)

            # Desenha a bola
            bola_objeto.desenhar(screen)

            linha_campo = pygame.draw.rect(screen, (100, 255, 0), pygame.Rect(55, 13, 1173, 534), 6) # Retangulo do campo
            if bola_objeto.rect.colliderect(linha_campo):
                # Se houver colisão, inverte a direção da bola na direção correspondente
                if bola_objeto.rect.left <= linha_campo.left or bola_objeto.rect.right >= linha_campo.right:
                    bola_objeto.velocidade_x *= -1
                if bola_objeto.rect.top <= linha_campo.top or bola_objeto.rect.bottom >= linha_campo.bottom:
                    bola_objeto.velocidade_y *= -1

            # Verifica colisões entre a bola e os jogadores
            if bola_objeto.colide_jogador(jogador_esquerda) or bola_objeto.colide_jogador(jogador_direita):
                bola_objeto.velocidade_x *= -1

            #Placar de gols
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
            
            # Renderiza o placar na tela
            texto_placar = fonte.render(f'Placar: {pontos_E} x {pontos_D}', True, (255, 255, 255))
            screen.blit(texto_placar, (10, 10))

            # Atualiza a tela
            pygame.display.flip()

            # Controla a taxa de atualização
            clock.tick(FPS)

        # Quando o loop do jogo terminar, encerre o pygame
        pygame.quit()

    # Iniciar o loop do jogo
    Rodando()

# Função para o hand tracking
def hand_tracking():
    # Inicialize o MediaPipe Hands.
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5)
    mp_drawing = mp.solutions.drawing_utils

    # Inicialize a captura de vídeo.
    cap = cv2.VideoCapture(0)
    while True:
        success, image = cap.read()
        if not success:
            break
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image_rgb)

        # Desenhe as landmarks da mão na imagem.
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        cv2.imshow('MediaPipe Hands', image)

        # Adicione a lógica para fechar o programa quando a tecla 'q' for pressionada.
        key = cv2.waitKey(1)
        if key == ord('q'):
            break

    # Libere a captura da webcam
    cap.release()
    cv2.destroyAllWindows()
    hands.close()

# Iniciar o jogo e o hand tracking em threads separadas
thread_jogo = threading.Thread(target=jogo)
thread_hand_tracking = threading.Thread(target=hand_tracking)

# Iniciar as threads
thread_jogo.start()
thread_hand_tracking.start()