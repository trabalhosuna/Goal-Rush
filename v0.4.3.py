import cv2
import mediapipe as mp
import pygame
import random
import sys
import threading
import math

"""Versão estavel, adicionado luckybox(classe Evento), novo calculo para sainda de bola, importa nova biblioteca (math)"""

class Jogo:
    class Bola: #define a classe bola
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.speed = 15 # define velocidade da bola
            self.velocidade_x, self.velocidade_y = self.gerar_velocidade_aleatoria()
            self.imagem = pygame.image.load('imagens/Bola.png')
            self.rect = self.imagem.get_rect(center=(x, y)) #define o hitbox pelo centro da bola
            self.rect.inflate_ip(25, 25) # aumenta o tamanho do hitbox da bola
            self.angulo = 0 #define o angulo de rotação inicial

        def atualizar(self):
            self.x += self.velocidade_x
            self.y += self.velocidade_y
            self.rect.center = (self.x, self.y)
            self.angulo += 5 #define o angulo de rotação da bola

        def desenhar(self, tela):
            self.atualizar()
            imagem_rotacionada = pygame.transform.rotate(self.imagem, self.angulo) # Faz a bola girar em seu proprio eixo
            retangulo_rotacionado = imagem_rotacionada.get_rect(center=self.rect.center)
            tela.blit(imagem_rotacionada, retangulo_rotacionado)

        def gerar_velocidade_aleatoria(self):
            min_angle = 30  # ângulo mínimo
            max_angle = 150  # ângulo máximo
            angle = random.randint(min_angle, max_angle) # Escolhe aleatoriamente um ângulo dentro do intervalo
            angle_radianos = math.radians(angle) # Converte o ângulo de graus para radianos
            xSpeed = self.speed * math.sin(angle_radianos) # Calcula as velocidades x e y
            ySpeed = self.speed * math.cos(angle_radianos)
            self.velocidade_x = xSpeed
            self.velocidade_y = ySpeed
            return self.velocidade_x, self.velocidade_y
        
        def bola_meio(self):
            self.speed *= 1
            self.x = (960) #centraliza a bola
            self.y = (540)
            self.angulo = 0
            self.gerar_velocidade_aleatoria
            self.atualizar
            
        def colide_jogador(self, jogador):
            return self.rect.colliderect(jogador.rect)
 
    class Jogador: #define a classe jogador
        def __init__(self, x, y, imagem):
            self.x = x
            self.y = y
            self.imagem = imagem
            self.rect = self.imagem.get_rect(center=(x, y))
            self.velocidade= 500

        def mover(self, movimento):
            self.y += movimento*1.8
            if self.y < 160:
                self.y = 160
            elif self.y > 900:
                self.y = 900
            self.rect.center = (self.x, self.y)

        def desenhar(self, tela):
            tela.blit(self.imagem, self.rect)

    class HandTracker(threading.Thread): #Classe para detectar as mãos em thread reparado do loop principal
        def __init__(self, jogador_esquerda, jogador_direita):
            super().__init__()
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
            self.running = True

        def run(self):
            while self.running:
                success, image = self.cap.read() #Captura a imagem
                if not success: #Se não conseguir capturar a imagem, para o loop
                    print("Erro na captura de imagem.")
                    break
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  #Converte para RGB
                results = self.hands.process(image_rgb)

                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks: #Desenha as linhas das mãos
                        self.mp_drawing.draw_landmarks(image, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

                    for hand_landmarks in results.multi_hand_landmarks: 
                        landmark_atual = hand_landmarks.landmark[8] #landmark 8 é o dedo indicador
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

        def stop(self):
            self.running = False

        def desenhar_linha_vertical(self, image):
            cv2.line(image, (self.meio_x, 0), (self.meio_x, self.altura_video), (0, 0, 255), 1) 
    
    class Radio: #Classe que define as funcoes uteis para gerenciar os sons
        def __init__(self):
            pygame.mixer.init()
            self.volume = 0.5  # Volume padrão (0.0 a 1.0)
            self.musica_atual = None

        def carregar_musica(self, efeito):
            pygame.mixer.music.load(efeito)

        def reproduzir_musica(self, loops=0, start=0.0):
            pygame.mixer.music.play(loops=loops, start=start) #Reproduz a música carregada.

        def pausar_musica(self): #Pausa a reprodução da música.
            pygame.mixer.music.pause()

        def continuar_musica(self): #Continua a reprodução da música após ela ter sido pausada.
            pygame.mixer.music.unpause()

        def parar_musica(self): #Reiniciar a reprodução da música atual.
            pygame.mixer.music.stop()

        def definir_volume(self, volume): #Define o volume da música.
            self.volume = max(0.0, min(1.0, volume))  # Garante que o volume esteja entre 0.0 e 1.0
            pygame.mixer.music.set_volume(self.volume)

        def verificar_musica_reproduzindo(self): #Verifica se a música está sendo reproduzida.
            return pygame.mixer.music.get_busy()
    midia= Radio()

    class Vida():
        def __init__(self, x, bol):
            self.sentido = bol
            self.x = x
            self.max_vida = 8
            self.vida = 0
            self.coracao = []
            self.coracao_vazio = []
            self.imagem_coracao = pygame.image.load('imagens/Coracao.png')
            self.imagem_coracao_vazio = pygame.image.load('imagens/Coracao_vazio.png')

        def add_coracao(self):
            y = 20
            if self.vida < self.max_vida:
                self.vida += 1
                self.coracao.append((self.x, y))
                self.coracao_vazio.append((self.x, y))
                if self.sentido:
                    self.x += 37
                else:
                    self.x -= 37

        def remover_coracao(self):
            if self.vida > 0:
                self.vida -= 1
                self.coracao.pop()

        def desenha_coracao(self):
            for i in range(self.max_vida):
                if i < self.vida:
                    self.screen.blit(self.imagem_coracao, self.coracao[i])
                else:
                    self.screen.blit(self.imagem_coracao_vazio, self.coracao_vazio[i])
        
    class Evento():
        def __init__(self):
            self.evento = random.randint(1,4)
            self.y = random.randint(245, 830)
            self.x = random.randint(500,1420)
            self.imagem_box = pygame.image.load("imagens/Luckybox.png")
            self.caixa = self.imagem_box.get_rect(center=(self.x, self.y))
        
        def desenhar_luckybox(self):
            self.screen.blit(self.imagem_box, self.caixa)



    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN) #define o tamanho da tela do jogo (1920 x 1080) "meio 960/961"
        pygame.display.set_caption('Goal Rush')
        self.clock = pygame.time.Clock()
        self.FPS = 60
        self.fonte = pygame.font.SysFont("Pixeled Regular", 30)
        self.fonte2 = pygame.font.SysFont("Pixeled Regular", 20)
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.rodando_menu = True
        self.rodando_partida = False
        self.rodando_winscreen = False
        self.pontos_D = 0
        self.pontos_E = 0


    def abrir_menu(self):   # implementa a lógica do menu
        self.midia.carregar_musica('musicas/Musica_theme.mp3')
        self.midia.reproduzir_musica(loops=-1)
        self.midia.definir_volume(0.4)

        imagem_fundo = pygame.image.load('imagens/Tela_Inicial_sem_texto.png') #imagem ao fundo do menu
        pressione_ENTER = pygame.image.load('imagens/Pressione_enter.png') #imagem de texto para pressionar enter
        pressione_ESC = pygame.image.load('imagens/Pressione_esc.png') #imagem de texto para pressionar ESC
        
        largura = 1885 #animação
        altura = 1750
        largura_original, altura_original = pressione_ENTER.get_size() #pega o tamanho da imagem
        clock = pygame.time.Clock()
        fator = 1  # Fator de escala inicial
        velocidade_pulsar = 0.002  # Velocidade de pulsar

        while self.rodando_menu:    # loop do menu
            fator += velocidade_pulsar# Aumenta ou diminui o fator de escala
            if fator > 1.1 or fator < 1:
                velocidade_pulsar *= -1
            # Redimensiona a imagem com base no fator de escala
            largura_nova = int(largura_original * fator)
            altura_nova = int(altura_original * fator)
            imagem_redimensionada = pygame.transform.scale(pressione_ENTER, (largura_nova, altura_nova))
            self.screen.blit(imagem_fundo, (0, 0))
            self.screen.blit(imagem_redimensionada, ((largura - largura_nova) // 2, (altura - altura_nova) // 2))
            self.screen.blit(pressione_ESC, (654, 942))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.rodando_menu = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:    # Verifica se a tecla ENTER foi pressionada
                        self.midia.parar_musica()
                        self.rodando_menu = False
                        self.rodando_partida = True
                    elif event.key == pygame.K_ESCAPE:    # Verifica se a tecla ESC foi pressionada
                        pygame.quit()
                        sys.exit()

            pygame.display.flip()
            clock.tick(60)

    def abrir_partida(self): # implementa a lógica da partida
        vidas_jogador_D = Jogo.Vida(((1920/2)+180), True) #cria o objeto da classe Vida que controla as vidas do jogador
        vidas_jogador_E = Jogo.Vida(((1920/2)-228), False)
        vidas_jogador_D.screen = self.screen #permite o uso da "screen" na instancia
        vidas_jogador_E.screen = self.screen
        arroz= [1,2,3,4,5,6,7,8] #lista para adicionar os pontos de vidas iniciais
        for _ in arroz:
            vidas_jogador_D.add_coracao()
            vidas_jogador_E.add_coracao()
        
        sorte = Jogo.Evento()
        sorte.screen = self.screen

        playlist = ['musicas/Musica_2.mp3', 'musicas/Kickin_Pixels.mp3', 'musicas/Samba_on_the_Soccer_Field.mp3', 'musicas/Samba_on_the_Soccer_Field_2.mp3', 'musicas/The_Ballers_Tango.mp3']
        musica=random.choice(playlist)
        self.midia.carregar_musica(musica)
        self.midia.reproduzir_musica(loops=-1)
        self.midia.definir_volume(0.3) # define o volume da música

        self.pontos_D = 0 #zera os pontos antes do loop
        self.pontos_E = 0

        #adicionando imagens aos objetos
        #Randomiza a escolha dos imagens
        caminhos_esq = ['imagens/goleiros/Goleiro1_esq.png','imagens/goleiros/Goleiro2_esq.png','imagens/goleiros/Goleiro3_esq.png','imagens/goleiros/Goleiro4_esq.png']
        caminhos_dir = ['imagens/goleiros/Goleiro1_dir.png','imagens/goleiros/Goleiro2_dir.png','imagens/goleiros/Goleiro3_dir.png','imagens/goleiros/Goleiro4_dir.png']
        imagens_esq = [pygame.image.load(img) for img in caminhos_esq]  # carrega as imagens dos goleiros em uma lista
        imagens_dir = [pygame.image.load(img2) for img2 in caminhos_dir]
        imagem_placar = pygame.image.load('imagens/placar2.png')
        imagem_fundo = pygame.image.load('imagens/Campo3novo.png') #imagem ao fundo do jogo
        #define as imagens das instancias
        jogador_esquerda_imagem = random.choice(imagens_esq)#Randomiza a escolha dos imagens
        jogador_direita_imagem = random.choice(imagens_dir)
        #define as instancias dos objetos
        jogador_esquerda = Jogo.Jogador(175, 550, jogador_esquerda_imagem)
        jogador_direita = Jogo.Jogador(1745, 550, jogador_direita_imagem)
        bola_objeto = self.Bola(960, 540) # define instancia bola

        hand_instance = Jogo.HandTracker(jogador_esquerda, jogador_direita)
        hand_instance.start()

        tempo_inicial= pygame.time.get_ticks()
        while self.rodando_partida: #loop principal da partida
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.rodando_partida = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:# Verifica se a tecla pressionada é a tecla ESC
                        self.rodando_partida = False
                        self.rodando_menu = True

            self.screen.fill((0, 0, 0)) #avaliar utilidade************************
            self.screen.blit(imagem_fundo, (0, 0))    #desenha a imagem ao fundo
            self.screen.blit(imagem_placar,(788, 20)) #desenha o placar

            jogador_esquerda.desenhar(self.screen)    #desenha os objetos
            jogador_direita.desenhar(self.screen)
            bola_objeto.desenhar(self.screen)

            linha_campo = pygame.draw.rect(self.screen, (0, 255, 0), pygame.Rect(142, 109 , 1636, 848), 3)    # Linha do campo
            if bola_objeto.rect.colliderect(linha_campo):
                if bola_objeto.rect.left <= linha_campo.left or bola_objeto.rect.right >= linha_campo.right:
                    bola_objeto.velocidade_x *= -1
                if bola_objeto.rect.top <= linha_campo.top or bola_objeto.rect.bottom >= linha_campo.bottom:
                    bola_objeto.velocidade_y *= -1

            if bola_objeto.colide_jogador(jogador_esquerda) or bola_objeto.colide_jogador(jogador_direita):
                bola_objeto.velocidade_x *= -1


            linha_gol_E = pygame.draw.rect(self.screen, (255, 10, 10), pygame.Rect(140, 400, 6, 263), 6)
            if bola_objeto.rect.colliderect(linha_gol_E): # Verifica se a bola colidiu com a linha do gol
                self.pontos_D += 1
                vidas_jogador_E.remover_coracao()
                bola_objeto.bola_meio()
                
            linha_gol_D = pygame.draw.rect(self.screen, (255, 10, 10), pygame.Rect(1773, 400, 6, 263), 6)    # Linha do gol
            if bola_objeto.rect.colliderect(linha_gol_D): # Verifica se a bola colidiu com a linha do gol
                self.pontos_E += 1
                vidas_jogador_D.remover_coracao()
                bola_objeto.bola_meio()
            
            if self.pontos_E == 8 or self.pontos_D == 8: #numero de gol para o fim da partida
                self.rodando_winscreen = True
                self.rodando_partida = False

            tempo_decorrido = 60-((pygame.time.get_ticks() - tempo_inicial)// 1000) # Calcula o tempo decorrido em segundos
            if tempo_decorrido == 0:
                self.rodando_menu= True
                self.rodando_partida = False

            texto_placar_E = self.fonte.render(f'{self.pontos_E}', True, (255, 255, 255))  # Texto do placar esquerdo
            texto_placar_D = self.fonte.render(f'{self.pontos_D}', True, (255, 255, 255))  # Texto do placar esquerdo
            texto_cronometro = self.fonte2.render(f'0:{tempo_decorrido}', True, (255, 255, 255))
            self.screen.blit(texto_placar_E, (900, 7)) #desenha o placar
            self.screen.blit(texto_placar_D, (1000, 7)) #desenha o placar
            self.screen.blit(texto_cronometro, (928, 74))
            vidas_jogador_D.desenha_coracao()
            vidas_jogador_E.desenha_coracao()
            sorte.desenhar_luckybox()
            pygame.display.flip()  # Atualiza a tela
            self.clock.tick(self.FPS)

        # Parar a thread de detecção de mão quando sair do loop principal
        hand_instance.stop()

    def abrir_winscreen(self):   # implementa a lógica da tela de vitoria
        self.midia.carregar_musica('musicas/Pixelated_Champion.mp3')
        self.midia.reproduzir_musica(loops=-1)
        self.midia.definir_volume(0.4)

        imagem_fundo = pygame.image.load('imagens/Fim_partida___Reiniciar.png') #imagem ao fundo do menu
        clock = pygame.time.Clock()

        while self.rodando_winscreen:  # loop do menu
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.rodando_winscreen = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:    # Verifica se a tecla R foi pressionada
                        self.rodando_winscreen = False
                        self.rodando_menu = True
                    elif event.key == pygame.K_ESCAPE:    # Verifica se a tecla ESC foi pressionada
                        self.rodando_winscreen = False
                        pygame.quit()
                        sys.exit()
            texto_placar_E = self.fonte.render(f'{self.pontos_E}', True, (255, 255, 255))  # Texto do placar esquerdo
            texto_placar_D = self.fonte.render(f'{self.pontos_D}', True, (255, 255, 255))  # Texto do placar esquerdo
            self.screen.blit(imagem_fundo, (0, 0))
            self.screen.blit(texto_placar_E, (785, 415)) #desenha o placar
            self.screen.blit(texto_placar_D, (1110, 415)) #desenha o placar            
            
            pygame.display.flip()
            clock.tick(60)


    def executar(self):
        while True:
            if self.rodando_menu:
                self.abrir_menu()
            elif self.rodando_partida:
                self.abrir_partida()
            elif self.rodando_winscreen:
                self.abrir_winscreen()


if __name__ == "__main__": # Executa o jogo
    jogo = Jogo()
    jogo.executar()
