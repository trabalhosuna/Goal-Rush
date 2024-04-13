import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)

largura_video = 640 # largura da tela (cam)
altura_video = 480 # altura da tela (cam)

def desenhar_linha_vertical(image): # Função para desenhar uma linha vertical no meio do vídeo
    meio_x = largura_video // 2
    cv2.line(image, (meio_x, 0), (meio_x, altura_video), (0, 0, 255), 1) # Desenha a linha vertical, cor= (B,G,R) e espessura= 1

# Inicialize a captura de vídeo.
def TrakingDasMaos():
    cap = cv2.VideoCapture(0) #recebe o video da cam
    Camera_ligada= True

    y_esquerda = 0 # armazena o valor inicial da coordenada y
    y_direita = 0
    Velocidade= 1000

    while Camera_ligada:
        success, image = cap.read() #verifica se recebe a imagem da cam
        if not success:
            break
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image_rgb) #recebe o processamento das maos em padrao RGB

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
                    print(movimento_esquerda)
                if landmark_atual.x > 0.5:
                    #direita
                    movimento_direita= (landmark_atual.y - y_direita) * Velocidade
                    print(movimento_direita)


        desenhar_linha_vertical(image) # chama a funcao para desenhar a linha vertical
        cv2.imshow('MediaPipe Hands', image) # Mostre a imagem com as landmarks detectadas.

    # Adicione a lógica para fechar o programa quando a tecla 'q' for pressionada.
        key = cv2.waitKey(1)
        if key == ord('q'):
            Camera_ligada= False

# Ligando o video.
TrakingDasMaos()
hands.close()
cv2.destroyAllWindows()
