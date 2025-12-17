
from time import sleep

# Try importing gpiozero, but mock it if running on non-Pi (e.g. Windows dev env)
try:
    from gpiozero import AngularServo
    from gpiozero.pins.pigpio import PiGPIOFactory
    IS_PI = True
except ImportError:
    IS_PI = False
    print("Not running on Pi or gpiozero not found. Servo commands will be simulated.")
    class AngularServo:
        def __init__(self, pin, min_angle, max_angle, min_pulse_width, max_pulse_width):
            self.angle = 90
            pass

class ServoManager:
    def __init__(self, pan_pin=17, tilt_pin=27):
        self.pan_pin = pan_pin
        self.tilt_pin = tilt_pin
        
        # Servo Configuration (Adjust these for your specific hardware)
        self.min_pulse = 0.0005
        self.max_pulse = 0.0025
        self.min_angle = 0
        self.max_angle = 180
        
        # PID Constants
        self.kp = 0.1  # Proportional gain
        self.dead_zone = 30 # Pixel margin from center where no movement occurs
        
        if IS_PI:
            # tailored for smooth movement using pigpio factory
            try:
                from gpiozero.pins.pigpio import PiGPIOFactory
                factory = PiGPIOFactory()
                print("Using PiGPIOFactory for smooth servo control.")
            except Exception:
                factory = None
                print("PiGPIOFactory failed. Using default pin factory (may be jittery).")

            self.pan_servo = AngularServo(pan_pin, min_angle=self.min_angle, max_angle=self.max_angle, 
                                          min_pulse_width=self.min_pulse, max_pulse_width=self.max_pulse,
                                          pin_factory=factory)
            self.tilt_servo = AngularServo(tilt_pin, min_angle=self.min_angle, max_angle=self.max_angle, 
                                           min_pulse_width=self.min_pulse, max_pulse_width=self.max_pulse,
                                           pin_factory=factory)
            
            # Initialize to center
            self.curr_pan = 90
            self.curr_tilt = 90
            self.pan_servo.angle = self.curr_pan
            self.tilt_servo.angle = self.curr_tilt
        else:
            self.curr_pan = 90
            self.curr_tilt = 90

    def map_range(self, x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

    def update(self, face_center, img_center):
        cx, cy = face_center
        ix, iy = img_center
        
        # PAN (X-axis)
        diff_x = cx - ix
        if abs(diff_x) > self.dead_zone:
            # If face is to the right (cx > ix), we need to decrease angle (turn right)
            # or increase depending on servo orientation. Assume: 0 is right, 180 is left?
            # Usually: 
            # 0 deg -> Right
            # 180 deg -> Left
            # If face is right of center (positive diff_x), we need to turn Right (decrease angle).
            # This directionality often needs tuning.
            
            error_x = diff_x * self.kp
            self.curr_pan -= error_x
            
            # Constrain
            if self.curr_pan > self.max_angle: self.curr_pan = self.max_angle
            if self.curr_pan < self.min_angle: self.curr_pan = self.min_angle
            
        # TILT (Y-axis)
        diff_y = cy - iy
        if abs(diff_y) > self.dead_zone:
            # If face is below center (positive diff_y), we need to look down.
            error_y = diff_y * self.kp
            self.curr_tilt += error_y # Assuming increasing angle looks down
            
            # Constrain
            if self.curr_tilt > self.max_angle: self.curr_tilt = self.max_angle
            if self.curr_tilt < self.min_angle: self.curr_tilt = self.min_angle

        # Apply to generic servos
        if IS_PI:
            self.pan_servo.angle = self.curr_pan
            self.tilt_servo.angle = self.curr_tilt
            
        return int(self.curr_pan), int(self.curr_tilt)
