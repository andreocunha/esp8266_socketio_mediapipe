import cv2
import mediapipe as mp
import time
import socketio

sio = socketio.Client()

frameWidth = 640
frameHeight = 480
cap = cv2.VideoCapture(0)
cap.set(3, frameWidth)
cap.set(4, frameHeight)

mpHands=mp.solutions.hands
hands=mpHands.Hands()
mpDraw = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

pTime = 0
cTime = 0

tipIds = [4, 8, 12, 16, 20]

conectedToServer = False

# funcoes do SocketIO
@sio.event
def connect():
    print("Conectado!")
    sio.emit('data', "Hello World")

@sio.event
def connect_error():
    print("A conexao falhou!")

@sio.on('info')
def on_message(data):
    print('Info:', data)

# conecta ao socketio
try:
    sio.connect('http://localhost:4000')
    conectedToServer = True
except:
    print("Erro ao conectar ao socketio")

while True:
    success, img = cap.read()
    img= cv2.flip(img,1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
    # print(results.multi_hand_landmarks)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks: 
        #handLMs are 21 points. so we need conection too-->mpHands.HAND_CONNECTIONS
            lmList = []
            for id, lm in enumerate(handLms.landmark):
                # print(id, lm)
                #lm = x,y cordinate of each landmark in float numbers. lm.x, lm.y methods
                #So, need to covert in integer
                h, w, c =img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                # print(id, cx, cy)
                lmList.append([id, cx, cy])
                # if id == 4: #(To draw 4th point)
                cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
            # print(lmList)

            if len(lmList) != 0:
                fingers = []

                # Dedao
                if lmList[tipIds[0]][1] < lmList[tipIds[0]-1][1]:
                    fingers.append(1)
                else:
                    fingers.append(0)

                # Para os outros 4 dedos
                for id in range(1,5):
                    if lmList[tipIds[id]][2] < lmList[tipIds[id]-2][2]:
                        fingers.append(1)
                    else:
                        fingers.append(0)
                print(fingers)
                if conectedToServer:
                    sio.emit('data', fingers)
            #drawing points and lines(=handconections)
            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS, mp_drawing_styles.get_default_hand_landmarks_style(),mp_drawing_styles.get_default_hand_connections_style())

    #Write frame rate
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, "FPS: "+ str(int(fps)), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    cv2.imshow('image', img)
    if cv2.waitKey(1)==27:
        break