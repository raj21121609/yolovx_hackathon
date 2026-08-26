# VisionAttend AI 👁️🎓

**An Automated, Zero-Friction Classroom Attendance System using Real-Time Multi-Face Recognition.**

![VisionAttend Banner](https://via.placeholder.com/1200x400.png?text=VisionAttend+AI+-+Smart+Attendance+System)

---

## 🎯 The Problem

Traditional roll-call methods are time-consuming, prone to human error, and easily manipulated (proxy attendance). In a typical 45-minute lecture, marking attendance can waste up to 10 minutes of valuable teaching time. Furthermore, biometric scanners create bottlenecks at classroom doors and raise hygiene concerns.

## 💡 Our Solution

**VisionAttend AI** is a state-of-the-art, non-intrusive attendance system built for modern educational institutes. Using high-definition camera feeds (IP Webcams or CCTV), our AI continuously monitors the classroom, tracks students, and automatically marks their attendance in real-time without them ever needing to stop or swipe an ID card.

---

## ✨ Key Features (Presentation Highlights)

1. **Continuous Multi-Face Tracking**
   - Processes multiple faces concurrently in real-time.
   - Replaces manual "click-to-capture" with seamless background monitoring.
   
2. **Cross-Camera Resilience**
   - Tolerant to variations in focal length, lighting, and camera quality. 
   - Dynamically scales down 1080p+ IP Webcam feeds to maintain high FPS without losing detection accuracy.
   - Calibrated Cosine Distance Thresholds (`0.55`) for the ArcFace model to handle lens distortion.

3. **Faculty Dashboard & Analytics**
   - A beautiful, institutional-grade UI (St. John College Theme).
   - Real-time video streaming of the AI's internal state (Verifying, Verified, Unknown).
   - Auto-generated CSV reports and attendance percentage tracking.
   
4. **Hardware Agnostic (Zero Initial Investment)**
   - No expensive CCTV required for deployment.
   - Works flawlessly with standard laptop webcams or an Android smartphone acting as an IP Camera.

---

## 🛠️ Architecture & Tech Stack

- **Frontend:** React, Vite, Tailwind CSS v4, Recharts, Lucide Icons.
- **Backend:** Python, Django REST Framework, SQLite.
- **AI/ML Pipeline:** 
  - **DeepFace:** High-level API for facial recognition.
  - **MTCNN:** Highly accurate backend face detector.
  - **ArcFace:** State-of-the-art embeddings model for face matching.
  - **OpenCV (cv2):** Frame extraction and resizing.
- **Concurrency:** Dedicated daemon threads for non-blocking AI inference, ensuring the Django server stays responsive.

---

## 🚀 Setup & Camera Configuration

The application supports both local webcams and Android IP Webcams for the recognition pipeline. 

### Local Webcam
To use your laptop's default webcam, edit `backend/.env` and set:
```env
CAMERA_TYPE=local
CAMERA_STREAM_URL=0
```

### IP Webcam (Recommended for High Quality)
To use an Android phone as a network camera, ensure both devices are on the same Wi-Fi network, edit `backend/.env`, and set the stream URL provided by your IP Webcam app:
```env
CAMERA_TYPE=ip
CAMERA_STREAM_URL=<IP Webcam stream URL>
```
*Note: Replace `<IP Webcam stream URL>` with the actual address (e.g., `http://192.168.1.100:8080/video`).*

---

## 🔮 Future Scope
- **Direct CCTV Integration:** Expanding from IP Webcams to RTSP protocols for permanent classroom installations.
- **Liveness Detection:** Preventing spoofing attacks using printed photos or digital screens.
- **Automated SMS Alerts:** Alerting parents when students have critically low attendance or consecutive absences.

---

*Built with ❤️ for the Yolovx Hackathon.*
