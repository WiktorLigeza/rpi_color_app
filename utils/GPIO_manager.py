import RPi.GPIO as GPIO


class PinsManager:
    def __init__(self):
        self.R_pin = None
        self.G_pin = None
        self.B_pin = None
        self.hz = 100
        self.pwm_red = None
        self.pwm_green = None
        self.pwm_blue = None

    def set_pins(self):
        print("setting pins")
        GPIO.setmode(GPIO.BCM)  # Tell the GPIO library we are using the breakout board pin numbering system
        GPIO.setwarnings(False)  # Tell the GPIO library not to issue warnings

        # Set up the GPIO pin for output
        GPIO.setup(self.R_pin, GPIO.OUT)
        GPIO.setup(self.G_pin, GPIO.OUT)
        GPIO.setup(self.B_pin, GPIO.OUT)

        # Creates software PWM on LED_pin running at 50Hz
        self.pwm_red = GPIO.PWM(self.R_pin, self.hz)
        self.pwm_green = GPIO.PWM(self.G_pin, self.hz)
        self.pwm_blue = GPIO.PWM(self.B_pin, self.hz)
        self.pwm_green.start(0)
        self.pwm_red.start(0)
        self.pwm_blue.start(0)

    def set_RGB(self, R, G, B):
        R = R/255 * 100
        G = G/255 * 100
        B = B/255 * 100
        self.pwm_red.ChangeDutyCycle(R)
        self.pwm_green.ChangeDutyCycle(G)
        self.pwm_blue.ChangeDutyCycle(B)

    @staticmethod
    def clean():
        print("cleaning up")
        GPIO.cleanup()
