
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

from threading import Thread

class WebcamVideoStream:
    def __init__(self, src=0, width=320, height=240):
        self.stream = cv2.VideoCapture(src)
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.stream.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.stream.set(cv2.CAP_PROP_FPS, 30)
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False

    def start(self):
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        while True:
            if self.stopped:
                return
            (self.grabbed, self.frame) = self.stream.read()
    
    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True
        self.stream.release()

def main():
    # Identify camera index
    cam_index = 0
    for i in [-1, 0, 1]:
        try:
            temp = cv2.VideoCapture(i)
            if temp.isOpened():
                cam_index = i
                temp.release()
                break
        except: pass
        
    print(f"Starting Threaded Video Stream on Camera {cam_index}...")
    
    # Start threaded stream
    vs = WebcamVideoStream(src=cam_index, width=320, height=240).start()
    # Allow camera to warm up
    time.sleep(2.0)
    
    tracker = HumanTracker()
    servo = ServoManager(pan_pin=17, tilt_pin=27) 
    
    img_center = (160, 120)
    p_time = 0

    while True:
        img = vs.read()
        if img is None:
            break

        # Flip for mirror effect (optional, feels more natural)
        img = cv2.flip(img, 1)

        # Optimization: process every frame, but keep math simple
        img, faces = tracker.find_faces(img)

        if faces:
            face_center = faces[0][2]
            pan, tilt = servo.update(face_center, img_center)
            # visual feedback
            cv2.line(img, img_center, face_center, (255, 0, 0), 2)
        
        c_time = time.time()
        fps = 1 / (c_time - p_time) if (c_time - p_time) > 0 else 0
        p_time = c_time
        
        cv2.putText(img, f'FPS: {int(fps)}', (10, 30), cv2.FONT_HERSHEY_PLAIN,
                    2, (0, 255, 0), 2)
        
        cv2.imshow("Face Tracking", img)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    vs.stop()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
