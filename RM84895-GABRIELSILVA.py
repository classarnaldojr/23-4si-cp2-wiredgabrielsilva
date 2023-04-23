import cv2
import mediapipe as mp
import time

#captura de tela
cap = cv2.VideoCapture(0)

#declaracao de variaveis
maosMediaPipe = mp.solutions.hands
maos = maosMediaPipe.Hands(max_num_hands=2, min_detection_confidence=0.01)
desenharMediaPipe = mp.solutions.drawing_utils
timer_start = time.time()
timer_resultado = None
score_p1 = 0
score_p2 = 0

#determinar o ganhador da rodada
def Ganhador(p1, p2):
    if p1 == p2:
        return "Empate"
    if (p1 == "Pedra" and p2 == "Tesoura") or (p1 == "Tesoura" and p2 == "Papel") or (p1 == "Papel" and p2 == "Pedra"):
        return "Jogador 1 Venceu"
    return "Jogador 2 Venceu"

#detectar a pedra
def Pedra(hand_landmarks):
    pontaDedos = [8, 12, 16, 20]
    comparando = [6, 10, 14, 18]

#feito desta forma com a tentativa de detectar o video, contudo .y e .x nao sofreram diferenca
    for i in range(len(pontaDedos)):
        tip_x = hand_landmarks.landmark[pontaDedos[i]].x
        comparar_x = hand_landmarks.landmark[comparando[i]].x

        if tip_x > comparar_x:
            return False

    return True

#detectar papel
def Papel(hand_landmarks):
    #verificando se as pontas do dedo estao acima
    if hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y and \
       hand_landmarks.landmark[12].y < hand_landmarks.landmark[10].y and \
       hand_landmarks.landmark[16].y < hand_landmarks.landmark[14].y and \
       hand_landmarks.landmark[20].y < hand_landmarks.landmark[18].y:
        return True
    return False

#detectar tesoura
def Tesoura(hand_landmarks):
    if hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y and \
       hand_landmarks.landmark[12].y < hand_landmarks.landmark[10].y and \
       hand_landmarks.landmark[16].y > hand_landmarks.landmark[14].y and \
       hand_landmarks.landmark[20].y > hand_landmarks.landmark[18].y:
        return True
    return False

#video
while True:
    ret, frame = cap.read()
    if not ret:
        break

    #linha na tela para dividir
    h, w, _ = frame.shape
    cv2.line(frame, (w//2, 0), (w//2, h), (255, 255, 255), 1)

#timer para rounds e resultado
    if timer_resultado is None or time.time() - timer_resultado < 10: 
        if time.time() - timer_start < 5:
            cv2.putText(frame, 'Tempo: {:.2f}'.format(5 - (time.time() - timer_start)), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
        else:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = maos.process(rgb)

            p1Mao = ""
            p2Mao = ""
            if results.multi_hand_landmarks:
                #verificando aonde esta a mao
                for hand_landmarks in results.multi_hand_landmarks:
                    hand_center = hand_landmarks.landmark[0]
                    x, y = int(hand_center.x * w), int(hand_center.y * h)

                    if x < w//2:
                        if Pedra(hand_landmarks):
                            p1Mao = "Pedra"
                        elif Papel(hand_landmarks):
                            p1Mao = "Papel"
                        elif Tesoura(hand_landmarks):
                            p1Mao = "Tesoura"
                    else:
                        if Pedra(hand_landmarks):
                            p2Mao = "Pedra"
                        elif Papel(hand_landmarks):
                            p2Mao = "Papel"
                        elif Tesoura(hand_landmarks):
                            p2Mao = "Tesoura"

                    desenharMediaPipe.draw_landmarks(
                        frame, hand_landmarks, maosMediaPipe.HAND_CONNECTIONS,
                        desenharMediaPipe.DrawingSpec(color=(255, 255, 255), thickness=2, circle_radius=4),
                        desenharMediaPipe.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2)
                    )
                    #pontuacao
            if p1Mao and p2Mao:
                winner = Ganhador(p1Mao, p2Mao)
                if winner == "Jogador 1 Venceu":
                    score_p1 += 1
                elif winner == "Jogador 2 Venceu":
                    score_p2 += 1
                print("O jogador 1 tem: ", score_p1, " pontos")
                print("O jogador 2 tem: ", score_p2, " pontos")
                timer_start = time.time()
                timer_resultado =time.time()

            cv2.putText(frame, f'Jogador 1: {p1Mao}', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(frame, f'Jogador 2: {p2Mao}', (w//2 + 50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(frame, f'Placar: {score_p1} x {score_p2}', (w//2 - 100, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        cv2.imshow('PedraPapelTesoura', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
maos.close()
cv2.destroyAllWindows()
