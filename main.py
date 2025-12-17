
import cv2
import time
from servo_controller import ServoManager

class HumanTracker:
    def __init__(self):
        # Load the cascade
        # We use the absolute path or relative if in same folder. 
        # OpenCV usually includes this.
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def find_faces(self, img, draw=True):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Detect faces
        # Speed tweak: scaleFactor 1.1 -> 1.3 (Faster, slightly less accurate)
        # minNeighbors 4 -> 5 (Reduces false positives)
        faces_rects = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))
        
        faces = []
        for (x, y, w, h) in faces_rects:
            cx = x + w // 2
            cy = y + h // 2
            
            # Format similar to our previous MP implementation: [id, bbox, center, score]
            # Score is dummy here (1.0)
            faces.append([0, (x, y, w, h), (cx, cy), 1.0])
            
            if draw:
                cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 255), 2)
                cv2.circle(img, (cx, cy), 5, (0, 255, 0), cv2.FILLED)

        return img, faces

def main():
    # Try different camera indices
    cap = None
    for i in [-1, 0, 1]:
        try:
            print(f"Trying camera index {i}...")
            temp_cap = cv2.VideoCapture(i)
            if temp_cap.isOpened():
                cap = temp_cap
                print(f"Success: Camera found at index {i}")
                break
        except:
            continue
            
    if cap is None or not cap.isOpened():
        print("Error: Could not open any camera.")
        return

    tracker = HumanTracker()
    servo = ServoManager(pan_pin=17, tilt_pin=27) 
    
    # Set camera resolution (Lower resolution = faster processing on Pi)
    w, h = 320, 240
    # Sometimes setting resolution causes issues on certain legacy drivers
    try:
        cap.set(3, w)
        cap.set(4, h)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1) # CRITICAL: Reduces delay/lag
        cap.set(cv2.CAP_PROP_FPS, 30)
    except:
        pass
    
    img_center = (w // 2, h // 2)
    p_time = 0

    print("Starting Face Tracking with Haar Cascades...")

    while True:
        success, img = cap.read()
        if not success:
            break

        # Optimization: detection parameters tuned for speed (1.2 scale factor)
        img, faces = tracker.find_faces(img)

        if faces:
            # Get the center of the first detected face and update servos
            face_center = faces[0][2]
            pan, tilt = servo.update(face_center, img_center)
            
            # Visuals
            cv2.line(img, img_center, face_center, (255, 0, 0), 2)
        
        # FPS Calculation
        c_time = time.time()
        fps = 1 / (c_time - p_time) if (c_time - p_time) > 0 else 0
        p_time = c_time
        
        cv2.putText(img, f'FPS: {int(fps)}', (10, 30), cv2.FONT_HERSHEY_PLAIN,
                    2, (0, 255, 0), 2)
        
        # NOTE: If running headless, comment these out!
        # Headless mode enabled by default for speed
        # cv2.imshow("Image", img)
        if int(fps) % 30 == 0: # Print stats every ~1 sec (assuming 30fps loop)
             print(f"FPS: {int(fps)} | Face Center: {face_center if faces else 'None'}")

        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
