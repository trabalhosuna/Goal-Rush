import pygame
import sys
import random
import math

pygame.init()
LARGURA, ALTURA = 800, 600  # Defina a tela
tela = pygame.display.set_mode((LARGURA, ALTURA))
relogio = pygame.time.Clock()

# Cria uma lista de bolas, velocidades e cores
num_objetos = 10
objetos = []
velocidades = []
massas = []
cores = [(255, 0, 0), (0, 255, 0), (0, 0, 255),
          (255, 255, 0), (255, 0, 255), (255, 200, 100),
            (46, 255, 50), (0, 150, 255), (255, 255, 150),
              (255, 200, 255)]  # Cores fixas para cada objeto

# Velocidade máxima
velocidade_maxima = 10  # valor para tornar os objetos mais rápidos

for _ in range(num_objetos):
    x = random.randint(0, LARGURA) # Cria uma posição aleatória para cada objeto
    y = random.randint(0, ALTURA)
    raio = random.randint(10, 25)   # Cria um raio aleatório para cada objeto
    objetos.append((x, y, raio))    # Adiciona a bola à lista

    # Gera velocidades aleatórias para os objetos
    velocidade_x = random.uniform(-velocidade_maxima, velocidade_maxima)
    velocidade_y = random.uniform(-velocidade_maxima, velocidade_maxima)
    velocidades.append([velocidade_x, velocidade_y])  # Adiciona a velocidade à lista
    # Gera massas aleatórias para os objetos
    massas.append(random.uniform(1, 4))  # Adiciona a massa à lista

def colisao_circulo(circulo1, circulo2):  # Verifica se dois círculos colidem
    x1, y1, r1 = circulo1  # desestrutura o círculo 1
    x2, y2, r2 = circulo2  # desestrutura o círculo 2
    dx = x2 - x1  # calcula a distância entre os círculos no eixo
    dy = y2 - y1
    distancia_ao_quadrado = dx * dx + dy * dy  # calcula a distância ao quadrado
    raio_soma_ao_quadrado = (r1 + r2) ** 2  # calcula a soma dos raios ao quadrado
    return distancia_ao_quadrado <= raio_soma_ao_quadrado  # retorna se os círculos colidem

# Loop principal

while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Atualize a posição das bolas
    for i, obj in enumerate(objetos):  # Atualiza a posição de cada objeto
        x, y, raio = obj  # estrutura o objeto
        velocidades[i][0] = max(-velocidade_maxima, min(velocidade_maxima, velocidades[i][0]))  # Limita a velocidade máxima
        velocidades[i][1] = max(-velocidade_maxima, min(velocidade_maxima, velocidades[i][1]))  # Limita a velocidade máxima
        x += velocidades[i][0]
        y += velocidades[i][1]
        if x - raio < 0 or x + raio > LARGURA:  # Verifica se a bola saiu da tela
            velocidades[i][0] = -velocidades[i][0]  # Inverte a velocidade
            x = max(raio, min(LARGURA - raio, x))  # Garante que a bola não saia da tela
        if y - raio < 0 or y + raio > ALTURA: 
            velocidades[i][1] = -velocidades[i][1]
            y = max(raio, min(ALTURA - raio, y))  # Garante que a bola não saia da tela
        objetos[i] = (x, y, raio)  # Atualiza a posição do objeto

    # Verifique as colisões
    for i in range(num_objetos):  # Verifica se a colisão entre cada par de bolas
        for j in range(i + 1, num_objetos): 
            if colisao_circulo(objetos[i], objetos[j]):  # Se as bolas colidirem

                x1, y1, r1 = objetos[i] # Obtem as informações das bolas
                x2, y2, r2 = objetos[j] # Obtem as informações das bolas

                # Calcula as diferenças de posição e velocidade
                dx = x2 - x1  # Diferença de posição
                dy = y2 - y1
                dist = math.sqrt(dx**2 + dy**2)  # Calcula a distância entre as bolas
                if dist == 0:
                    dist = 1
                nx = dx / dist  # Calcula o vetor normal x
                ny = dy / dist

                # Resolve a colisão
                sobreposicao = (r1 + r2 - dist) * 0.5  # Calcula a sobreposição
                x1 -= sobreposicao * nx  # Atualiza a posição das bolas
                y1 -= sobreposicao * ny
                x2 += sobreposicao * nx  # Atualiza a posição das bolas
                y2 += sobreposicao * ny
                objetos[i] = (x1, y1, r1)  # Atualiza a posição das bolas
                objetos[j] = (x2, y2, r2)

                # Calcula as velocidades após a colisão
                dvx = velocidades[j][0] - velocidades[i][0]  # Diferença de velocidade
                dvy = velocidades[j][1] - velocidades[i][1]
                produto_ponto = dvx * nx + dvy * ny  # Calcula o produto escalar
                m1 = massas[i]  
                m2 = massas[j]
                if dist == 0:
                    dist = 1
                impulso = (2 * produto_ponto) / (m1 + m2)  # Calcula o impulso
                impulso_x = impulso * nx
                impulso_y = impulso * ny

                velocidades[i][0] += impulso_x * m2  # Atualiza a velocidade das bolas
                velocidades[i][1] += impulso_y * m2
                velocidades[j][0] -= impulso_x * m1
                velocidades[j][1] -= impulso_y * m1

    # Desenhe as bolas
    tela.fill((0, 0, 0))  # Preenche a tela com a cor preta
    for i, (x, y, raio) in enumerate(objetos):  # Desenha cada bola
        pygame.draw.circle(tela, cores[i], (round(x), round(y)), raio) 

    pygame.display.flip()
    relogio.tick(144)
