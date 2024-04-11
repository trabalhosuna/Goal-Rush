import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import time
import random

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# Importando as imagens
imgBackground = cv2.imread("Resources/Background.png")
imgGameOver = cv2.imread("Resources/gameOver.png")
imgTimeOver = cv2.imread("Resources/timeOver.png")
imgBall = cv2.imread("Resources/Ball.png", cv2.IMREAD_UNCHANGED)
imgBat1 = cv2.imread("Resources/bat1.png", cv2.IMREAD_UNCHANGED)
imgBat2 = cv2.imread("Resources/bat2.png", cv2.IMREAD_UNCHANGED)
imgWelcome = cv2.imread("Resources/welcome.png")

while True:
    cv2.imshow("FutePong ExpoUna", imgWelcome)
    key = cv2.waitKey(1)
    if key == 13:  # Tecla Enter para começar
        break

# Detector de mãos
detector = HandDetector(detectionCon=0.7, maxHands=2)

# Variaveis
PosicaoBola = [640, 360]
velocidadeX = 20
velocidadeY = 20
gameOver = False
timeOver = False
pontuacao = 0
contador_esbarroes = 0

# Iniciar o cronômetro
tempo_inicio = time.time()

while True:
    _, img = cap.read()
    img = cv2.flip(img, 1)
    imgRaw = img.copy()

    # Pontos de referência da mão
    hands, img = detector.findHands(img, flipType=False)

    # Imagem de fundo
    img = cv2.addWeighted(img, 0, imgBackground, 1, 0)

    # Esse código é para o computador ler o movimento da mão pela webcam
    if hands:
        for hand in hands:
            x, y, w, h = hand['bbox']
            h1, w1, _ = imgBat1.shape
            y1 = y - h1 // 2
            y1 = np.clip(y1, 20, 415)

            if hand['type'] == "Left":
                img = cvzone.overlayPNG(img, imgBat1, (64, y1))
                if 59 < PosicaoBola[0] < 62 + w1 and y1 < PosicaoBola[1] < y1 + h1:
                    velocidadeX = -velocidadeX
                    velocidadeY = random.randint(-16, 16)
                    PosicaoBola[0] += 30
                    pontuacao += 1
                    contador_esbarroes += 1  # Aqui conta quando a bola bater no boneco
                    # Aqui a velocidade da bola aumenta na hora que ela esbarrar nos bonecos
                    velocidadeX *= 1.02
                    # Aqui a velocidade da bola aumenta na hora que ela esbarrar nos bonecos no eixo Y
                    velocidadeY *= 1.02

            if hand['type'] == "Right":
                img = cvzone.overlayPNG(img, imgBat2, (1190, y1))
                if 1195 - 50 < PosicaoBola[0] < 1183 and y1 < PosicaoBola[1] < y1 + h1:
                    velocidadeX = -velocidadeX
                    velocidadeY = random.randint(-16, 16)
                    PosicaoBola[0] -= 30
                    pontuacao += 1
                    contador_esbarroes += 1  # Aqui conta quando a bola bater no boneco
                    # Aqui a velocidade da bola aumenta na hora que ela esbarrar nos bonecos
                    velocidadeX *= 1.02
                    # Aqui a velocidade da bola aumenta na hora que ela esbarrar nos bonecos no eixo Y
                    velocidadeY *= 1.02

    # Fim de jogo
    if PosicaoBola[0] < 40 or PosicaoBola[0] > 1200 or pontuacao >= 150:
        gameOver = True

    # Fim de tempo
    if (time.time() - tempo_inicio) >= 120:
        timeOver = True

    if gameOver:
        img = imgGameOver
        cv2.putText(img, str(pontuacao).zfill(2), (590, 360), cv2.CALIB_FIX_PRINCIPAL_POINT,
                    2.5, (230, 88, 30), 5)

    elif timeOver:
        img = imgTimeOver.copy()  # Copia a imagem para não modificar a original
        # Adiciona a pontuação na imagem imgTimeOver
        cv2.putText(img, f'{pontuacao}', (612, 360),
                    cv2.FONT_HERSHEY_SIMPLEX, 2.5, (255, 255, 255), 5)

    else:
        # Isso aqui faz a bola se mover
        if PosicaoBola[1] >= 500 or PosicaoBola[1] <= 10:
            velocidadeY = -velocidadeY

        PosicaoBola[0] += velocidadeX
        PosicaoBola[1] += velocidadeY

        img = cvzone.overlayPNG(
            img, imgBall, [int(PosicaoBola[0]), int(PosicaoBola[1])])

        cv2.putText(img, str(pontuacao), (600, 680),
                    cv2.FONT_HERSHEY_COMPLEX, 3, (255, 255, 255), 5)

        tempo_decorrido = int(time.time() - tempo_inicio)
        minutos = tempo_decorrido // 60
        segundos = tempo_decorrido % 60
        cv2.putText(img, f'{minutos:02d}:{segundos:02d}', (300, 680),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 3)

    img[580:700, 20:233] = cv2.resize(imgRaw, (213, 120))

    cv2.imshow("FutePong ExpoUna", img)
    key = cv2.waitKey(1)
    if key == 27:  # Tecla Esc para fechar
        break
    elif key == 114:  # Tecla r para reiniciar
        PosicaoBola = [260, 280]
        velocidadeX = 20
        velocidadeY = 20
        gameOver = False
        timeOver = False
        pontuacao = 0
        contador_esbarroes = 0
        imgGameOver = cv2.imread("Resources/gameOver.png")
        tempo_inicio = time.time()
        while True:
            cv2.imshow("FutePong ExpoUna", imgWelcome)
            key = cv2.waitKey(1)
            if key == 13:  # Tecla Enter para começar
                break
