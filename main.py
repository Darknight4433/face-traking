
import cv2
import mediapipe as mp
import time
from servo_controller import ServoManager

class HumanTracker:
    def __init__(self, detection_confidence=0.5, tracking_confidence=0.5):
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(
            min_detection_confidence=detection_confidence)
        self.mp_draw = mp.solutions.drawing_utils

    def find_faces(self, img, draw=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.face_detection.process(img_rgb)
        
        faces = []
        if self.results.detections:
            for id, detection in enumerate(self.results.detections):
                bboxC = detection.location_data.relative_bounding_box
                ih, iw, ic = img.shape
                bbox = int(bboxC.xmin * iw), int(bboxC.ymin * ih), \
                       int(bboxC.width * iw), int(bboxC.height * ih)
                
                cx = bbox[0] + (bbox[2] // 2)
                cy = bbox[1] + (bbox[3] // 2)
                
                faces.append([id, bbox, (cx, cy), detection.score])
                
                if draw:
                    cv2.rectangle(img, bbox, (255, 0, 255), 2)
                    cv2.circle(img, (cx, cy), 5, (0, 255, 0), cv2.FILLED)
                    cv2.putText(img, f'{int(detection.score[0] * 100)}%',
                                (bbox[0], bbox[1] - 20), cv2.FONT_HERSHEY_PLAIN,
                                2, (255, 0, 255), 2)

        return img, faces

def main():
    cap = cv2.VideoCapture(0)
    tracker = HumanTracker()
    servo = ServoManager(pan_pin=17, tilt_pin=27)  # Adjust pins as needed
    
    # Set camera resolution (lower is faster on Pi)
    w, h = 640, 480
    cap.set(3, w)
    cap.set(4, h)
    
    img_center = (w // 2, h // 2)

    p_time = 0

    while True:
        success, img = cap.read()
        if not success:
            break

        img, faces = tracker.find_faces(img)

        if faces:
            # Get the center of the first detected face
            face_center = faces[0][2]
            
            # Update servos
            pan, tilt = servo.update(face_center, img_center)
            
            # Display servo values
            cv2.putText(img, f'Pan: {pan} Tilt: {tilt}', (20, 110), 
                        cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
            cv2.circle(img, img_center, 5, (255, 0, 0), cv2.FILLED) # Show center of image
            cv2.line(img, img_center, face_center, (255, 0, 0), 2) # Line to face
        
        c_time = time.time()
        fps = 1 / (c_time - p_time)
        p_time = c_time
        
        cv2.putText(img, f'FPS: {int(fps)}', (20, 70), cv2.FONT_HERSHEY_PLAIN,
                    3, (0, 255, 0), 3)
        
        cv2.imshow("Image", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
