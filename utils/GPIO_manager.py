import RPi.GPIO as GPIO
import paho.mqtt.client as paho
import serial
import glob


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
        self.serial_dict = {}
        self.set_remote_client()
        self.scan_serial()

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

    def set_serial_client(self, path, TAG):
        print(f"found device: {path} with tag: {TAG}")
        self.serial_dict[TAG] = serial.Serial(path, 250000, timeout=1)
        self.serial_dict[TAG].reset_input_buffer()

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

    def set_serial_RGB(self, TAG, R, G, B):
        if TAG in self.serial_dict:
            try:
                self.serial_dict[TAG].write(bytes(f"{R},{G},{B}\n", 'utf8'))
                self.serial_dict[TAG].readline().decode('utf-8').rstrip()
            except Exception as e:
                if "smth" in str(e):
                    del self.serial_dict[TAG]
                    self.scan_serial()

    def set_RGB(self, TAG, connection, R, G, B):
        if connection == "local":
            self.set_local_RGB(R, G, B)
        else:
            if connection == "serial":
                self.set_serial_RGB(TAG, R, G, B)
            else:
                self.set_remote_RGB(TAG, R, G, B)

    def scan_serial(self):
        print("scanning for USB devices..")
        for dev in glob.glob("/dev/*"):
            if "ttyUSB" in dev:
                try:
                    temp_ser = serial.Serial(dev, 250000, timeout=0.1)
                    temp_ser.write(b"#")
                    msg = temp_ser.readline().decode('utf-8').rstrip()
                    if "2137#" in msg:
                        msg = msg.split("#")
                        self.set_serial_client(path=dev, TAG=msg[1])
                except: pass

    @staticmethod
    def clean():
        print("cleaning up")
        GPIO.cleanup()
