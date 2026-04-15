import cv2
import mediapipe as mp

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

def analyze_hand_gestures(hand_landmarks):
    lm = hand_landmarks.landmark
    wrist_x, wrist_y = lm[0].x, lm[0].y
    index_up = lm[8].y < lm[6].y
    middle_up = lm[12].y < lm[10].y
    ring_up = lm[16].y < lm[14].y
    pinky_up = lm[20].y < lm[18].y
    
    # Laser: Chỉ ngón trỏ giơ lên
    is_laser = index_up and not (middle_up or ring_up or pinky_up)
    
    # Tên lửa: Giơ 3 ngón (Trỏ, Giữa, Áp út), ngón út cụp
    is_missile = index_up and middle_up and ring_up and not pinky_up
    
    return wrist_x, wrist_y, is_laser, is_missile