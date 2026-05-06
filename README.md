# 🖐️ Gesture Recognition System
**by Mahesh Bhardwaj**

A real-time hand gesture recognition web application built with Python, MediaPipe, OpenCV, and Flask. Runs fully on localhost with a beautiful live dashboard.

---

## 🚀 Quick Start

### Windows
```
Double-click run.bat
```

### Mac / Linux
```bash
chmod +x run.sh
./run.sh
```

### Manual (any OS)
```bash
pip install -r requirements.txt
python app.py
```

Then open **http://localhost:5000** in your browser.

---

## 🎯 Gestures Supported

| Gesture | Name |
|---------|------|
| ✊ | Fist |
| 🖐️ | Open Hand |
| 👍 | Thumbs Up |
| ✌️ | Peace / Victory |
| ☝️ | Pointing Up |
| 🤙 | Call Me |
| 🤘 | Rock On |
| 🖖 | Four Fingers |
| 🤞 | Three Fingers |
| 🤟 | Three Middle |

---

## 🛠️ Tech Stack

- **Python 3.8+**
- **MediaPipe** — Hand landmark detection (21 points per hand)
- **OpenCV** — Camera capture & frame processing
- **Flask** — Web server + live video streaming
- **Vanilla JS** — Real-time dashboard updates (polling every 200ms)

---

## 📁 Project Structure

```
gesture_recognition/
├── app.py              # Main Flask app + gesture logic
├── requirements.txt    # Python dependencies
├── run.sh              # Linux/Mac launcher
├── run.bat             # Windows launcher
├── README.md           # This file
└── templates/
    └── index.html      # Dashboard UI
```

---

## ⚙️ How It Works

1. **Camera capture** — OpenCV reads webcam frames
2. **Hand detection** — MediaPipe detects 21 hand landmarks per hand
3. **Gesture classification** — Custom algorithm checks which fingers are raised using landmark Y-coordinates
4. **Live streaming** — Flask streams frames via MJPEG to browser
5. **Dashboard updates** — JS polls `/gesture_data` endpoint every 200ms

---

## 💡 Requirements

- Python 3.8 or higher
- Webcam / built-in camera
- Modern browser (Chrome recommended)
- ~500MB disk space (for MediaPipe models)

---

## 📝 Troubleshooting

**Camera not working?**
- Make sure no other app is using the camera
- Try changing `cv2.VideoCapture(0)` to `cv2.VideoCapture(1)` in `app.py`

**Slow performance?**
- Reduce resolution in app.py: change 640x480 to 320x240
- Works best with good lighting

**Installation errors?**
- Make sure Python 3.8+ is installed
- On Linux: `sudo apt install python3-opencv`

---

*Built for Gesture Recognition System project — Mahesh Bhardwaj, GL Bajaj Group of Institutions*
