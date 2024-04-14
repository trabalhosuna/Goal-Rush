import pygame
import sys

pygame.init()

largura = 800
altura = 600

tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Animação de Pulsar")

clock = pygame.time.Clock()

imagem = pygame.image.load('imagens/Pressione_enter.png')  # Substitua "exemplo_imagem.png" pelo caminho da sua imagem
largura_original, altura_original = imagem.get_size()

fator = 0.5  # Fator de escala inicial
velocidade_pulsar = 0.02  # Velocidade de pulsar

rodando = True
while rodando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

    # Aumenta ou diminui o fator de escala
    fator += velocidade_pulsar
    if fator > 1.5 or fator < 0.5:
        velocidade_pulsar *= -1

    # Redimensiona a imagem com base no fator de escala
    largura_nova = int(largura_original * fator)
    altura_nova = int(altura_original * fator)
    imagem_redimensionada = pygame.transform.scale(imagem, (largura_nova, altura_nova))

    #tela.fill((255, 255, 255))  # Preenche a tela com branco
    tela.blit(imagem_redimensionada, ((largura - largura_nova) // 2, (altura - altura_nova) // 2))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
