import cv2
import mediapipe as mp
import pygame
import random
import sys
import threading
import math

"""Versão estavel, refeito sistema de vidas, completo o primeiro evento do jogo"""

class Jogo:
    class Bola: #define a classe bola
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.speed = 15 # define velocidade da bola
            self.velocidade_x, self.velocidade_y = self.gerar_velocidade_aleatoria()
            self.imagem = pygame.image.load('imagens/Bola2.png')
            self.rect = self.imagem.get_rect(center=(x, y)) #recebe as dimencoes da imagem da bola
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
        
        def bola_meio(self, bool):
            quem = bool #define quem é o jogador que fez a pontuação
            self.x = (960) #centraliza a bola
            self.y = (540)
            self.angulo = 0
            x, self.velocidade_y = self.gerar_velocidade_aleatoria()
            if quem:
                self.velocidade_x = abs(x) # torna X positivo e velocidade positiva
            else:
                self.velocidade_x = (abs(x))* -1  # torna X positivo, multiplica por -1 e torna velocidade negativa
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

        def calcular_resposta_colisao(bola_objeto, objeto_colisao): # Calcula o vetor normal da superfície de colisão do objeto em relação à bola
            normal_surface = pygame.Vector2(objeto_colisao.rect.center) - pygame.Vector2(bola_objeto.rect.center)
            normal_surface.normalize_ip()  # Normaliza o vetor normal para 1
            velocidade_bola = pygame.Vector2(bola_objeto.velocidade_x, bola_objeto.velocidade_y)# Calcula o vetor de velocidade da bola
            componente_normal = normal_surface.dot(velocidade_bola) * normal_surface #Projeta o vetor de velocidade da bola no vetor normal da superfície de colisão
            bola_objeto.velocidade_x -= 2 * componente_normal.x # Subtrai duas vezes o componente da velocidade original da bola para simular a colisão elástica
            bola_objeto.velocidade_y -= 2 * componente_normal.y

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

    class Vida:
        def __init__(self, x, bol): #37
            self.x = x
            self.y = 20
            self.vida = 0
            self.vida_max = 5
            self.imagem_coracao = pygame.image.load('imagens/Coracao.png')
            self.imagem_coracao_vazio = pygame.image.load('imagens/Coracao_vazio.png')
            self.coracao_surface = self.imagem_coracao
            self.coracao = []
            self.coracao_vazio = []
            if bol:
                self.dist = 37
            if not bol:
                self.dist = -37
            
        def add_coracao(self):
            self.vida += 1
            self.gerenciar_coracao()

        def remover_coracao(self):
            self.vida -= 1
            self.gerenciar_coracao()

        def gerenciar_coracao(self):
            self.coracao = []
            self.coracao_vazio = []
            self.nc = 0
            ncv = self.vida_max + 1
            for _ in range(self.vida):
                self.nc += 1
                self.coracao.append((self.coracao_surface, self.x, self.nc)) 
            for _ in range(self.vida_max - self.vida):
                ncv -= 1
                self.coracao_vazio.append((self.imagem_coracao_vazio, self.x, ncv))

        def desenha_coracao(self):
            for i in (self.coracao):
                localX = (i[1] + (self.dist * i[2]))
                self.screen.blit(i[0], (localX, self.y))
            for i in (self.coracao_vazio):
                localcvX = (i[1] + (self.dist * i[2]))
                self.screen.blit(i[0], (localcvX, self.y))
                
        
    class Evento:
        def __init__(self):
            self.y = random.randint(245, 830)
            self.x = random.randint(500,1420)
            self.imagem_box = pygame.image.load("imagens/Luckybox.png")
            self.caixa = self.imagem_box.get_rect(center=(self.x, self.y))

        def gerar_caixa(self):
            self.y = random.randint(245, 830)
            self.x = random.randint(500,1420)
            self.caixa = self.imagem_box.get_rect(center=(self.x, self.y))

        def desenhar_luckybox(self):    #desenha a luckybox
            self.screen.blit(self.imagem_box, self.caixa)
        
        def escolher_evento(self):    #escolhe um evento
            self.evento = random.randint(1, 4) #escolhe um evento entre os eventos
            return self.evento
        
        def termina_evento(self):
            self.y = 50
            self.x = 50
            self.caixa = self.imagem_box.get_rect(center=(self.x, self.y))
            self.desenhar_luckybox()
        
        class EventoVida():
            def __init__(self, screen):
                self.screen = screen
                self.rect_icon = None
                self.verificacao_evento = False

            def desenhar_icone(self, caixa):
                x = caixa[0]
                y = caixa[1]
                self.imagem_evento = pygame.image.load("imagens/Vida_evento.png")
                self.rect_icon = self.imagem_evento.get_rect(center=(x, y))
                self.rect_icon.inflate_ip(-5, -5)
                self.screen.blit(self.imagem_evento, caixa)
                return self.rect_icon

        
        def evento_fogo(self):    #evento fogo, cria um fogo atras da bola e causa o dobro do dano ao jogador caso sofra gol
            self.imagem_evento = pygame.image.load("imagens/Pimenta_evento.png")
            rect_icon = self.imagem_evento.get_rect(center=(self.x, self.y))
            rect_icon.inflate_ip(-5, -5)
            self.screen.blit(self.imagem_evento, self.caixa)
            return rect_icon
        
        def evento_bola(self):    #evento bola, duplica a bola do jogo
            self.imagem_evento = pygame.image.load("imagens/Bola_Evento.png")
            rect_icon = self.imagem_evento.get_rect(center=(self.x, self.y))
            rect_icon.inflate_ip(-5, -5)
            self.screen.blit(self.imagem_evento, self.caixa)
            return rect_icon
        
        def evento_portal(self): #evento portal, adiciona dois portais no mapa para fazer o transporte da bola
            self.imagem_evento = pygame.image.load("imagens/Portal_Evento.png")
            rect_icon = self.imagem_evento.get_rect(center=(self.x, self.y))
            rect_icon.inflate_ip(-5, -5)
            self.screen.blit(self.imagem_evento, self.caixa)
            return rect_icon
            

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

        imagem_fundo = pygame.image.load('imagens/Tela_Inicial_sem_texto2.png') #imagem ao fundo do menu
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
        #class Vida
        vidas_jogador_D = Jogo.Vida(((1920/2)+180), True) #cria o objeto da classe Vida que controla as vidas do jogador
        vidas_jogador_E = Jogo.Vida(((1920/2)-228), False)
        vidas_jogador_D.screen = self.screen #permite o uso da "screen" na instancia
        vidas_jogador_E.screen = self.screen
        arroz= [1,2,3,4,5] #lista para adicionar os pontos de vidas iniciais
        for _ in arroz:
            vidas_jogador_D.add_coracao()   #adiciona os pontos de vida iniciais
            vidas_jogador_E.add_coracao()
        #class Radio
        playlist = ['musicas/Musica_2.mp3', 'musicas/Kickin_Pixels.mp3', 'musicas/Samba_on_the_Soccer_Field.mp3', 'musicas/Samba_on_the_Soccer_Field_2.mp3', 'musicas/The_Ballers_Tango.mp3']
        musica=random.choice(playlist) #escolhe uma música aleatória da lista
        self.midia.carregar_musica(musica) #carrega a música
        self.midia.reproduzir_musica(loops=-1) #reproduz a música infinitamente
        self.midia.definir_volume(0.3) # define o volume da música

        self.pontos_D = 0 #zera os pontos antes do loop
        self.pontos_E = 0

        #adicionando imagens aos objetos
        caminhos_dir = ['imagens/goleiros/Goleiro1_dir.png','imagens/goleiros/Goleiro2_dir.png','imagens/goleiros/Goleiro3_dir.png','imagens/goleiros/Goleiro4_dir.png']
        caminhos_esq = ['imagens/goleiros/Goleiro1_esq.png','imagens/goleiros/Goleiro2_esq.png','imagens/goleiros/Goleiro3_esq.png','imagens/goleiros/Goleiro4_esq.png']
        imagens_esq = [pygame.image.load(img) for img in caminhos_esq]  # carrega as imagens dos goleiros em uma lista
        imagens_dir = [pygame.image.load(img2) for img2 in caminhos_dir]
        imagem_placar = pygame.image.load('imagens/placar2.png')
        imagem_fundo = pygame.image.load('imagens/Campo4novo.png') #imagem ao fundo do jogo
        imagem_bandeira_esquerda = pygame.image.load('imagens/Bandeira_esquerda.png')
        imagem_bandeira_direita = pygame.image.load('imagens/Bandeira_direita.png')
        imagem_fogo= pygame.image.load('imagens/Fogo1.png') #aguardando aplicacao**********
        #define as imagens das instancias
        jogador_esquerda_imagem = random.choice(imagens_esq)#Randomiza a escolha dos imagens
        jogador_direita_imagem = random.choice(imagens_dir)
        #define as instancias dos objetos
        jogador_esquerda = Jogo.Jogador(175, 550, jogador_esquerda_imagem) # define instancia jogador_esquerda
        jogador_direita = Jogo.Jogador(1745, 550, jogador_direita_imagem)   # define instancia jogador_direita
        bola_objeto = self.Bola(960, 540) # define instancia bola

        #class Evento
        sorte = Jogo.Evento() #cria o objeto da classe Evento que controla os eventos
        sorte.screen = self.screen  # permite o uso da "screen" na instancia
        evento_vida = sorte.EventoVida(self.screen)

        hand_instance = Jogo.HandTracker(jogador_esquerda, jogador_direita) #define a instancia do hand tracker
        hand_instance.start()

        tempo_inicial= pygame.time.get_ticks() #define o tempo inicial
        lucky = False #diz se há caixa no mapa
        evento = 0 #diz qual evento selecionado
        verificacao_evento = False #diz se o evento foi verificado
        verificacao_lucky = False #diz se há caixa no mapa
        ultimo_contato = bool

        while self.rodando_partida: #loop principal da partida
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.rodando_partida = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:# Verifica se a tecla pressionada é a tecla ESC
                        self.rodando_partida = False
                        self.rodando_menu = True

            self.screen.blit(imagem_fundo, (0, 0))    #desenha a imagem ao fundo

            jogador_esquerda.desenhar(self.screen)    #desenha os objetos
            jogador_direita.desenhar(self.screen)
            bola_objeto.desenhar(self.screen)

            linha_campo = pygame.draw.rect(self.screen, (255, 255, 255), pygame.Rect(142, 109 , 1636, 848), 3)    # Linha do campo
            self.screen.blit(imagem_bandeira_esquerda, (129, 81)) #desenha as bandeiras
            self.screen.blit(imagem_bandeira_esquerda, (129, 930)) #desenha as bandeiras
            self.screen.blit(imagem_bandeira_direita, (1756, 78)) #desenha as bandeiras
            self.screen.blit(imagem_bandeira_direita, (1756, 927)) #desenha as bandeiras
            self.screen.blit(imagem_placar,(788, 20)) #desenha o placar
            if bola_objeto.rect.colliderect(linha_campo):
                if bola_objeto.rect.left <= linha_campo.left or bola_objeto.rect.right >= linha_campo.right:
                    bola_objeto.velocidade_x *= -1
                elif bola_objeto.rect.top <= linha_campo.top or bola_objeto.rect.bottom >= linha_campo.bottom:
                    bola_objeto.velocidade_y *= -1

            if bola_objeto.colide_jogador(jogador_esquerda):
                bola_objeto.velocidade_x *= -1
                ultimo_contato = False
 
            elif bola_objeto.colide_jogador(jogador_direita):
                bola_objeto.velocidade_x *= -1
                ultimo_contato = True

            linha_gol_E = pygame.draw.rect(self.screen, (255, 10, 10), pygame.Rect(140, 400, 6, 263), 6) #verificar efetividade das linhas laterais***
            if bola_objeto.rect.colliderect(linha_gol_E): # Verifica se a bola colidiu com a linha do gol
                self.pontos_D += 1
                marcou = True
                vidas_jogador_E.remover_coracao()
                bola_objeto.bola_meio(marcou)
                
            linha_gol_D = pygame.draw.rect(self.screen, (255, 10, 10), pygame.Rect(1773, 400, 6, 263), 6)    # Linha do gol
            if bola_objeto.rect.colliderect(linha_gol_D): # Verifica se a bola colidiu com a linha do gol
                self.pontos_E += 1
                marcou = False
                vidas_jogador_D.remover_coracao()
                bola_objeto.bola_meio(marcou)
            
            if self.pontos_E == 8 or self.pontos_D == 8: #numero de gol para o fim da partida
                self.rodando_winscreen = True   
                self.rodando_partida = False

            tempo_decorrido = 60-((pygame.time.get_ticks() - tempo_inicial)// 1000) # Calcula o tempo decorrido em segundos
            if tempo_decorrido == 0:    # Se o tempo acabar, o jogo acaba
                self.rodando_winscreen= True
                self.rodando_partida = False

            #evento
            if self.pontos_E + self.pontos_D >= 2 and verificacao_lucky== False:
                verificacao_lucky = True
                sorte.gerar_caixa()
                lucky = True

            if lucky:
                sorte.desenhar_luckybox()  # Desenha o luckybox
                if bola_objeto.rect.colliderect(sorte.caixa):  # Verifica se a bola colidiu com o luckybox
                    normal_surface = pygame.Vector2(sorte.caixa.center) - pygame.Vector2(bola_objeto.rect.center) #Calcula o vetor normal da superfície de colisão da caixa
                    normal_surface.normalize_ip() # Normaliza o vetor normal para 1
                    velocidade_bola = pygame.Vector2(bola_objeto.velocidade_x, bola_objeto.velocidade_y) # Calcula o vetor de velocidade da bola
                    componente_normal = normal_surface.dot(velocidade_bola) * normal_surface # Projeta o vetor de velocidade da bola no vetor normal da superfície de colisão
                    bola_objeto.velocidade_x -= 2 * componente_normal.x # Subtrai duas vezes o componente da velocidade original da bola para simular a colisão elástica
                    bola_objeto.velocidade_y -= 2 * componente_normal.y
                    evento = 1#sorte.escolher_evento()
                    print(evento)
                    verificacao_evento  = False
                    lucky = False

            if evento == 1:
                rect_icon = evento_vida.desenhar_icone(sorte.caixa)    # Desenha o icone do evento
                if bola_objeto.rect.colliderect(rect_icon) and verificacao_evento == False:  # Verifica se a bola ja colidiu com o icone do evento
                    print ('colidiu')
                    verificacao_evento = True
                    if ultimo_contato:
                        vidas_jogador_D.add_coracao() # Adiciona um coração ao jogador
                        evento= 0 # termina o evento
                        sorte.termina_evento()
                        verificacao_lucky = False
                        pass

                    elif not ultimo_contato:
                        vidas_jogador_E.add_coracao()
                        evento= 0
                        sorte.termina_evento()
                        verificacao_lucky = False
                        pass

                    else:
                        print("nada")
                        evento= 0
                        sorte.termina_evento()
                        verificacao_lucky = False
                        pass

            if evento == 2:
                rect_icon= sorte.evento_fogo()
                if bola_objeto.rect.colliderect(rect_icon) and verificacao_evento == False:  # Verifica se a bola colidiu com o icone do evento
                    verificacao_evento = True
                    print ('colidiu')
                    
            
            if evento == 3:
                rect_icon= sorte.evento_bola()
                if bola_objeto.rect.colliderect(rect_icon) and verificacao_evento == False:  # Verifica 
                    verificacao_evento = True
                    print("colidiu")


            if evento == 4:
                rect_icon= sorte.evento_portal()
                if bola_objeto.rect.colliderect(rect_icon) and verificacao_evento == False:  # verifica
                    verificacao_evento = True
                    print("colidiu")

            vidas_jogador_E.screen = self.screen
            texto_placar_E = self.fonte.render(f'{self.pontos_E}', True, (255, 255, 255))  # Texto do placar esquerdo
            texto_placar_D = self.fonte.render(f'{self.pontos_D}', True, (255, 255, 255))  # Texto do placar esquerdo
            texto_cronometro = self.fonte2.render(f'0:{tempo_decorrido}', True, (255, 255, 255))  # Texto do cronometro
            self.screen.blit(texto_placar_E, (900, 7)) #desenha o placar
            self.screen.blit(texto_placar_D, (1000, 7)) #desenha o placar
            self.screen.blit(texto_cronometro, (928, 74))    #desenha o cronometro
            vidas_jogador_D.desenha_coracao()    #desenha os corações
            vidas_jogador_E.desenha_coracao()    #desenha os corações
            
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
