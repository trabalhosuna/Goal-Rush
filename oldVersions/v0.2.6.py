import cv2
import mediapipe as mp
import pygame
import random
import sys

class Jogo:
    class Bola:
        def __init__(self, x, y, velocidade, imagem):
            self.x = x
            self.y = y
            self.velocidade_x = velocidade
            self.velocidade_y = velocidade
            self.imagem = imagem
            self.rect = self.imagem.get_rect(center=(x, y)) #define o hitbox pelo centro da bola
            self.angulo = 0 #define o angulo de rotação inicial

        def atualizar(self):
            self.x += self.velocidade_x
            self.y += self.velocidade_y
            self.rect.center = (self.x, self.y)
            self.angulo += 5 #define o angulo de rotação

        def desenhar(self, tela):
            self.atualizar()
            imagem_rotacionada = pygame.transform.rotate(self.imagem, self.angulo) # Faz a bola girar em seu proprio eixo
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
            self.velocidade= 1000

        def mover(self, movimento):
            self.y += movimento*1.8
            if self.y < 160:
                self.y = 160
            elif self.y > 900:
                self.y = 900
            self.rect.center = (self.x, self.y)

        def desenhar(self, tela):
            tela.blit(self.imagem, self.rect)

    class HandTracker:
        def __init__(self, jogador_esquerda, jogador_direita):
            self.jogador_esquerda = jogador_esquerda
            self.jogador_direita = jogador_direita
            self.mp_hands = mp.solutions.hands 
            self.hands = self.mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5)
            self.mp_drawing = mp.solutions.drawing_utils
            self.cap = cv2.VideoCapture(0)
            self.y_esquerda = 0
            self.y_direita = 0
            self.velocidade = 1000  
            self.meio_x = 640 // 2
            self.altura_video = 480 

        def desenhar_linha_vertical(self, image):
            cv2.line(image, (self.meio_x, 0), (self.meio_x, self.altura_video), (0, 0, 255), 1) 

        def capturar_mao(self):
            while True:
                success, image = self.cap.read()
                if not success:
                    print("Erro na captura de imagem.")
                    break
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = self.hands.process(image_rgb)

                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        self.mp_drawing.draw_landmarks(image, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

                    for hand_landmarks in results.multi_hand_landmarks: 
                        landmark_atual = hand_landmarks.landmark[8] 
                        if landmark_atual.x < 0.5: 
                            movimento_esquerda = (landmark_atual.y - self.y_esquerda) * self.velocidade
                            self.jogador_esquerda.mover(movimento_esquerda) #Move o jogador esq
                            self.y_esquerda = landmark_atual.y
                        if landmark_atual.x > 0.5:
                            movimento_direita = (landmark_atual.y - self.y_direita) * self.velocidade
                            self.jogador_direita.mover(movimento_direita) #Move o jogador dir
                            self.y_direita = landmark_atual.y    

                self.desenhar_linha_vertical(image)
                cv2.imshow('MediaPipe Hands', image)
                key = cv2.waitKey(1)
                if key == ord('q'):
                    break
        
            self.cap.release()
            cv2.destroyAllWindows()
        
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1920, 1080)) #define o tamanho da tela do jogo (1920 x 1080)
        pygame.display.set_caption('Goal Rush')
        self.clock = pygame.time.Clock()
        self.FPS = 60
        self.fonte = pygame.font.SysFont("arial", 30)
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.rodando_menu = True
        self.rodando_partida = False

    def abrir_menu(self):
        while self.rodando_menu:
            self.screen.fill(self.WHITE)
            self.draw_text("Menu Principal", self.BLACK, 1900 // 2, 100)
            pygame.draw.rect(self.screen, self.BLACK, (300, 200, 200, 50))  # Botão "Jogar"
            self.draw_text("Jogar", self.WHITE, 400, 225)
            pygame.draw.rect(self.screen, self.BLACK, (300, 300, 200, 50))  # Botão "Sair"
            self.draw_text("Sair", self.WHITE, 400, 325)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.rodando_menu = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if 300 <= mouse_pos[0] <= 500 and 200 <= mouse_pos[1] <= 250:  # Verifica se o botão "Jogar" foi clicado
                        self.rodando_menu = False
                        self.rodando_partida = True
                    elif 300 <= mouse_pos[0] <= 500 and 300 <= mouse_pos[1] <= 350:  # Verifica se o botão "Sair" foi clicado
                        pygame.quit()
                        sys.exit()

            pygame.display.flip()

    def abrir_partida(self): # implementa a lógica da partida
        pontos_D = 0 #zera os pontos antes do loop
        pontos_E = 0

        screen = pygame.display.set_mode((1920, 1080)) #define o tamanho da tela do jogo (1920 x 1080)
        pygame.display.set_caption('Goal Rush')
        fonte = pygame.font.Font(None, 36)

        #adicionando imagens aos objetos
        #Randomiza a escolha dos imagens
        Goleiro_1 = pygame.image.load('imagens/Goleiro1.png')
        Goleiro_2 = pygame.image.load('imagens/Goleiro2.png')
        Goleiro_3 = pygame.image.load('imagens/Goleiro3.png')
        Goleiro_4 = pygame.image.load('imagens/Goleiro4.png')
        #define as imagens das instancias
        jogador_esquerda_imagem = random.choice([Goleiro_1, Goleiro_4])
        jogador_direita_imagem = random.choice([Goleiro_2, Goleiro_3])
        bola_imagem = pygame.image.load('imagens/Bola.png')
        #define as instancias dos objetos
        jogador_esquerda = Jogo.Jogador(175, 360, jogador_esquerda_imagem)
        jogador_direita = Jogo.Jogador(1745, 360, jogador_direita_imagem)
        speed = random.choice([-25, 25]) # define velocidade da bola e randomiza a saida
        bola_objeto = self.Bola(960, 540, speed, bola_imagem) # define instancia bola
        bola_objeto.rect.inflate_ip(25, 25) # aumenta o tamanho do hitbox da bola

        hand_instance = Jogo.HandTracker(jogador_esquerda, jogador_direita)
        hand_instance.capturar_mao()

        while self.rodando_partida: #loop principal da partida
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.rodando_partida = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:# Verifica se a tecla pressionada é a tecla ESC
                        self.rodando_partida = False
                        self.rodando_menu = True

            screen.fill((0, 0, 0))
            imagem_fundo = pygame.image.load('imagens/Campo.png') #imagem ao fundo do jogo
            screen.blit(imagem_fundo, (0, 0))

            jogador_esquerda.desenhar(screen)
            jogador_direita.desenhar(screen)
            bola_objeto.desenhar(screen)

            linha_campo = pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(142, 109 , 1636, 848), 3)
            if bola_objeto.rect.colliderect(linha_campo):
                if bola_objeto.rect.left <= linha_campo.left or bola_objeto.rect.right >= linha_campo.right:
                    bola_objeto.velocidade_x *= -1
                if bola_objeto.rect.top <= linha_campo.top or bola_objeto.rect.bottom >= linha_campo.bottom:
                    bola_objeto.velocidade_y *= -1

            if bola_objeto.colide_jogador(jogador_esquerda) or bola_objeto.colide_jogador(jogador_direita):
                bola_objeto.velocidade_x *= -1

            linha_gol_E = pygame.draw.rect(screen, (255, 10, 10), pygame.Rect(140, 400, 6, 263), 6)
            if bola_objeto.rect.colliderect(linha_gol_E):
                bola_objeto.x = (960)
                bola_objeto.y = (540)
                bola_objeto.velocidade_x *= -1
                pontos_D += 1
                
            linha_gol_D = pygame.draw.rect(screen, (255, 10, 10), pygame.Rect(1773, 400, 6, 263), 6)
            if bola_objeto.rect.colliderect(linha_gol_D):
                bola_objeto.x = (960)
                bola_objeto.y = (540)
                bola_objeto.velocidade_y *= -1
                pontos_E += 1
            
            texto_placar = fonte.render(f'Placar: {pontos_E} x {pontos_D}', True, (255, 255, 255))
            screen.blit(texto_placar, (10, 10))

            pygame.display.flip()
            self.clock.tick(self.FPS)

    def draw_text(self, text, color, x, y):
        text_obj = self.fonte.render(text, True, color)
        text_rect = text_obj.get_rect()
        text_rect.center = (x, y)
        self.screen.blit(text_obj, text_rect)

    def executar(self):
        while True:
            if self.rodando_menu:
                self.abrir_menu()
            elif self.rodando_partida:
                self.abrir_partida()


if __name__ == "__main__":
    jogo = Jogo()
    jogo.executar()
