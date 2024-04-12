import pygame
import cv2
import random
import sys

def Jogo():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption('O Jogo')

    # Definindo a taxa de atualização
    clock = pygame.time.Clock()
    FPS = 60  # Defina o valor desejado para FPS

    # Carregando a fonte
    fonte = pygame.font.Font(None, 36)

    class Objeto:
        def __init__(self, x, y, velocidade, imagem):
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
    
    # Criando uma instância do objeto fora do loop principal do jogo
    bola_imagem = pygame.image.load('imagens/ball.png')
    speed = random.choice([-10,10]) # random entre 8 e -8 é o ideal para sainda de bola
    bola_objeto = Objeto(615, 255, speed, bola_imagem)
    bola_objeto.rect.inflate_ip(20,20)

    def capturar_video():
            # Inicializa a captura de vídeo da webcam
                cap = cv2.VideoCapture(0)

                while True:
                    ret, frame = cap.read()  # Captura um frame da webcam

            # Redimensiona o frame para que ele tenha uma altura menor e largura proporcional
                    frame = cv2.resize(frame, (int(200 * frame.shape[1] / frame.shape[0]), 200))

            # Converte o frame para o formato RGB (Pygame utiliza RGB)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Exibe o frame na tela do jogo
                    pygame.surfarray.blit_array(screen, frame)

            # Atualiza a tela do jogo
                    pygame.display.flip()
    capturar_video()    

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

            # Desenha a bola
            bola_objeto.desenhar(screen)

            linha_campo = pygame.draw.rect(screen, (100, 255, 0), pygame.Rect(55, 13, 1173, 534), 6) # Retangulo do campo
            if bola_objeto.rect.colliderect(linha_campo):
                # Se houver colisão, inverte a direção da bola na direção correspondente
                if bola_objeto.rect.left <= linha_campo.left or bola_objeto.rect.right >= linha_campo.right:
                    bola_objeto.velocidade_x *= -1
                if bola_objeto.rect.top <= linha_campo.top or bola_objeto.rect.bottom >= linha_campo.bottom:
                    bola_objeto.velocidade_y *= -1

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
    Rodando()

Jogo()

