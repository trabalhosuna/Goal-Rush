import cv2
import mediapipe as mp

# Inicialize o MediaPipe Hands.
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5) #recebe o processamento das maos

# Inicialize o DrawingSpec para desenhar as landmarks.
mp_drawing = mp.solutions.drawing_utils

# Inicialize a captura de vídeo.
def TrakingDasMaos():
    cap = cv2.VideoCapture(0) #recebe o video da cam
    Camera_ligada= True
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

        cv2.imshow('MediaPipe Hands', image) # Mostre a imagem com as landmarks detectadas.

    # Adicione a lógica para fechar o programa quando a tecla 'q' for pressionada.
        key = cv2.waitKey(1)
        if key == ord('q'):
            Camera_ligada= False

# Ligando o video.
TrakingDasMaos()
hands.close()
cv2.destroyAllWindows()
