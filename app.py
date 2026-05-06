import cv2
import mediapipe as mp
import numpy as np
from flask import Flask, render_template, Response, jsonify
import threading
import time

app = Flask(__name__)

# MediaPipe setup
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_face_mesh = mp.solutions.face_mesh

# Global state
gesture_data = {
    "current_gesture": "No Hand Detected",
    "confidence": 0,
    "hand_count": 0,
    "gesture_history": [],
    "fps": 0,
    "session_stats": {},
    "face_expression": "No Face Detected",
    "face_confidence": 0,
}
lock = threading.Lock()
gesture_counter = {}

def classify_gesture(hand_landmarks):
    landmarks = hand_landmarks.landmark
    fingers_up = []
    wrist = landmarks[0]
    thumb_tip = landmarks[4]
    index_mcp = landmarks[5]
    pinky_mcp = landmarks[17]
    is_right = index_mcp.x > pinky_mcp.x
    wrist_y = wrist.y
    if is_right:
        thumb_open = thumb_tip.x > index_mcp.x + 0.02
    else:
        thumb_open = thumb_tip.x < index_mcp.x - 0.02
    fingers_up.append(1 if thumb_open else 0)
    finger_tips = [8, 12, 16, 20]
    finger_pips = [6, 10, 14, 18]
    for tip, pip in zip(finger_tips, finger_pips):
        fingers_up.append(1 if landmarks[tip].y < landmarks[pip].y else 0)
    total_fingers = sum(fingers_up)
    other_fingers_curled = fingers_up[1:] == [0, 0, 0, 0]
    if fingers_up[0] == 1 and other_fingers_curled and thumb_tip.y < wrist_y - 0.1:
        return "👍 Thumbs Up", 95
    if fingers_up[0] == 1 and other_fingers_curled and thumb_tip.y > wrist_y + 0.05:
        return "👎 Thumbs Down", 95
    if total_fingers == 0:
        return "✊ Fist", 95
    elif total_fingers == 5:
        return "🖐️ Open Hand", 95
    elif fingers_up == [0, 1, 1, 0, 0]:
        return "✌️ Peace", 92
    elif fingers_up == [0, 1, 0, 0, 0]:
        return "☝️ Pointing Up", 92
    elif fingers_up == [1, 0, 0, 0, 1]:
        return "🤙 Call Me", 90
    elif fingers_up == [1, 1, 0, 0, 1]:
        return "🤘 Rock On", 90
    elif fingers_up == [0, 1, 1, 1, 0]:
        return "🤟 Three Middle", 85
    elif fingers_up == [1, 1, 1, 0, 0]:
        return "🤞 Three Fingers", 85
    elif fingers_up == [0, 1, 1, 1, 1]:
        return "🖖 Four Fingers", 85
    elif total_fingers == 1:
        return "☝️ One Finger", 78
    elif total_fingers == 2:
        return "✌️ Two Fingers", 78
    elif total_fingers == 3:
        return "🤟 Three Fingers", 78
    elif total_fingers == 4:
        return "🖖 Four Fingers", 78
    else:
        return "🤔 Unknown", 60


def detect_expression_mediapipe(face_landmarks, w, h):
    """Detect face expression using MediaPipe face mesh landmarks."""
    lm = face_landmarks.landmark

    # --- MOUTH ---
    # Upper lip: 13, Lower lip: 14
    mouth_open = abs(lm[13].y - lm[14].y) * h
    # Mouth corners: 61 (left), 291 (right), center top: 0
    left_corner = lm[61]
    right_corner = lm[291]
    mouth_center_y = (lm[13].y + lm[14].y) / 2
    smile_left = mouth_center_y - left_corner.y
    smile_right = mouth_center_y - right_corner.y
    smile_score = (smile_left + smile_right) * h

    # --- EYEBROWS ---
    # Left brow: 70, Left eye top: 159
    left_brow_eye = (lm[159].y - lm[70].y) * h
    right_brow_eye = (lm[386].y - lm[300].y) * h
    brow_raise = -(left_brow_eye + right_brow_eye) / 2

    # --- EYES ---
    left_eye_open = abs(lm[159].y - lm[145].y) * h
    right_eye_open = abs(lm[386].y - lm[374].y) * h
    eye_open_avg = (left_eye_open + right_eye_open) / 2

    # --- CLASSIFY ---
    if smile_score > 8 and mouth_open > 8:
        return "😄 Happy", 88
    elif smile_score > 5:
        return "🙂 Happy", 78
    elif mouth_open > 15 and brow_raise > 3:
        return "😲 Surprised", 82
    elif brow_raise > 4:
        return "😲 Surprised", 75
    elif smile_score < -4:
        return "😢 Sad", 72
    elif left_brow_eye < 12 and right_brow_eye < 12:
        return "😠 Angry", 70
    else:
        return "😐 Neutral", 80


def generate_frames():
    global gesture_data
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    prev_time = time.time()
    frame_count = 0

    with mp_hands.Hands(
        model_complexity=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7,
        max_num_hands=2
    ) as hands, mp_face_mesh.FaceMesh(
        max_num_faces=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        refine_landmarks=False
    ) as face_mesh:

        while True:
            success, frame = cap.read()
            if not success:
                break
            frame = cv2.flip(frame, 1)
            frame_count += 1
            h, w, _ = frame.shape

            curr_time = time.time()
            if curr_time - prev_time >= 1.0:
                fps = frame_count / (curr_time - prev_time)
                frame_count = 0
                prev_time = curr_time
                with lock:
                    gesture_data["fps"] = round(fps, 1)

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Hand detection
            hand_results = hands.process(rgb_frame)
            # Face detection
            face_results = face_mesh.process(rgb_frame)

            detected_gestures = []
            hand_count = 0

            # --- HANDS ---
            if hand_results.multi_hand_landmarks:
                hand_count = len(hand_results.multi_hand_landmarks)
                for hand_landmarks in hand_results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style()
                    )
                    gesture, confidence = classify_gesture(hand_landmarks)
                    detected_gestures.append((gesture, confidence))
                    cx = int(hand_landmarks.landmark[0].x * w)
                    cy = int(hand_landmarks.landmark[0].y * h)
                    cv2.rectangle(frame, (cx - 10, cy - 40), (cx + 200, cy + 10), (0, 0, 0), -1)
                    cv2.putText(frame, gesture, (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 100), 2)

            # --- FACE ---
            face_expr = "No Face Detected"
            face_conf = 0
            if face_results.multi_face_landmarks:
                face_lm = face_results.multi_face_landmarks[0]
                face_expr, face_conf = detect_expression_mediapipe(face_lm, w, h)

                # Draw expression on frame
                cv2.rectangle(frame, (10, 10), (280, 45), (0, 0, 0), -1)
                cv2.putText(frame, face_expr, (14, 36),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 200, 0), 2)

            # --- UPDATE STATE ---
            with lock:
                gesture_data["hand_count"] = hand_count
                gesture_data["face_expression"] = face_expr
                gesture_data["face_confidence"] = face_conf

                if detected_gestures:
                    main_gesture, conf = detected_gestures[0]
                    gesture_data["current_gesture"] = main_gesture
                    gesture_data["confidence"] = conf
                    history = gesture_data["gesture_history"]
                    if not history or history[-1] != main_gesture:
                        history.append(main_gesture)
                        gesture_data["gesture_history"] = history[-10:]
                    key = main_gesture.split(" ", 1)[-1] if " " in main_gesture else main_gesture
                    gesture_counter[key] = gesture_counter.get(key, 0) + 1
                    gesture_data["session_stats"] = dict(
                        sorted(gesture_counter.items(), key=lambda x: x[1], reverse=True)[:6]
                    )
                else:
                    gesture_data["current_gesture"] = "No Hand Detected"
                    gesture_data["confidence"] = 0

            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

    cap.release()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/gesture_data')
def get_gesture_data():
    with lock:
        return jsonify(gesture_data.copy())

if __name__ == '__main__':
    print("\n" + "="*50)
    print("  🖐️  Gesture + Face Expression System")
    print("="*50)
    print("  Open browser: http://localhost:5000")
    print("  Press Ctrl+C to stop")
    print("="*50 + "\n")
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)
