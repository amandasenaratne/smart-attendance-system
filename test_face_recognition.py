import face_recognition
import cv2

# Open webcam
video_capture = cv2.VideoCapture(0)

# Capture one frame
ret, frame = video_capture.read()

if not ret:
    print("Failed to grab frame from webcam.")
else:
    # Detect faces
    face_locations = face_recognition.face_locations(frame)
    print(f"Detected {len(face_locations)} face(s).")

video_capture.release()
cv2.destroyAllWindows()
