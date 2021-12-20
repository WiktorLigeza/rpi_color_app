import RPi.GPIO as GPIO
import paho.mqtt.client as paho


class PinsManager:
    def __init__(self):
        self.R_pin = None
        self.G_pin = None
        self.B_pin = None
        self.hz = 100
        self.pwm_red = None
        self.pwm_green = None
        self.pwm_blue = None
        self.mosquitto_client = None
        self.set_remote_client()

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

    def set_remote_client(self):
        self.mosquitto_client = paho.Client()
        if self.mosquitto_client.connect("localhost", 1883, 60) != 0:
            self.mosquitto_client = None
            print("connecting to mosquitto host failed miserably")

    def set_remote_RGB(self, TAG, R, G, B):
        if self.mosquitto_client is not None:
            self.mosquitto_client.publish(TAG, f"{R}, {G}, {B}", 0)

    def set_local_RGB(self, R, G, B):
        R = R / 255 * 100
        G = G / 255 * 100
        B = B / 255 * 100
        self.pwm_red.ChangeDutyCycle(R)
        self.pwm_green.ChangeDutyCycle(G)
        self.pwm_blue.ChangeDutyCycle(B)

    def set_RGB(self, TAG, R, G, B):
        if TAG == "local":
            self.set_local_RGB(R, G, B)
        else:
            print("d")
            self.set_remote_RGB(TAG, R, G, B)

    @staticmethod
    def clean():
        print("cleaning up")
        GPIO.cleanup()
