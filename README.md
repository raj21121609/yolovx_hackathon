# VisionAttend AI

## Camera Configuration

The application supports both local webcams and Android IP Webcams for the recognition pipeline.
The Android phone and laptop must normally be connected to the same local network for the IP camera to work.

### Local Webcam

To use your laptop's default webcam, edit `backend/.env` and set:

```env
CAMERA_TYPE=local
CAMERA_STREAM_URL=0
```

### IP Webcam

To use an Android phone as a network camera, edit `backend/.env` and set the stream URL provided by your IP Webcam app:

```env
CAMERA_TYPE=ip
CAMERA_STREAM_URL=<IP Webcam stream URL>
```

*Note: Replace `<IP Webcam stream URL>` with the actual address (e.g., `http://192.168.1.100:8080/video`).*
