import RPi.GPIO as GPIO
import logging
import paho.mqtt.client as paho
import serial
import glob


class PinsManager:
    def __init__(self):
        self.R_pin = None
        self.G_pin = None
        self.B_pin = None
        self.W_pin = None
        self.pinless = False
        self.logger = None
        self.set_logger()
        self.hz = 100
        self.pwm_red = None
        self.pwm_green = None
        self.pwm_blue = None
        self.pwm_white = None
        self.mosquitto_client = None
        self.serial_dict = {}
        self.set_remote_client()
        self.scan_serial()

    def set_logger(self):
        logging.basicConfig(filename="logs.log",
                            format='%(asctime)s %(message)s',
                            filemode='w')
        self.logger = logging.getLogger()

    def set_pins(self):
        print("setting pins")
        self.logger.warning("setting pins")
        GPIO.setmode(GPIO.BCM)  # Tell the GPIO library we are using the breakout board pin numbering system
        GPIO.setwarnings(False)  # Tell the GPIO library not to issue warnings

        if self.R_pin == 0 and self.G_pin == 0 and self.B_pin == 0:
            print("pinless")
            self.pinless = True

        else:
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

        if self.W_pin != -1:
            GPIO.setup(self.W_pin, GPIO.OUT)
            self.pwm_white = GPIO.PWM(self.W_pin, self.hz)
            self.pwm_white.start(0)

    def set_remote_client(self):
        self.mosquitto_client = paho.Client()
        if self.mosquitto_client.connect("localhost", 1883, 60) != 0:
            self.mosquitto_client = None
            print("connecting to mosquitto host failed miserably")
            self.logger.error("connecting to mosquitto host failed miserably")

    def set_serial_client(self, path, TAG):
        print(f"found device: {path} with tag: {TAG}")
        self.logger.warning(f"found device: {path} with tag: {TAG}")
        self.serial_dict[TAG] = serial.Serial(path, 250000, timeout=1)
        self.serial_dict[TAG].reset_input_buffer()

    def set_remote_RGB(self, TAG, R, G, B):
        try:
            if self.mosquitto_client is not None:
                self.mosquitto_client.publish(TAG, f"{R}, {G}, {B}", 0)
        except Exception as e:
            print(str(e))
            self.logger.error(f"{str(e)}")

    def set_local_RGB(self, R, G, B):
        if not self.pinless:
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
                print(str(e))
                if "smth" in str(e):
                    self.logger.error(f"{str(e)}")
                    del self.serial_dict[TAG]
                    self.scan_serial()

    def set_local_W(self, brightness):
        if self.pwm_white is not None and not self.pinless:
            self.pwm_white.ChangeDutyCycle(brightness)

    def set_remote_W(self, TAG, brightness):
        try:
            if self.mosquitto_client is not None:
                self.mosquitto_client.publish(TAG, f"{-1}, {-1}, {brightness}", 0)
        except Exception as e:
            print(str(e))
            self.logger.error(f"{str(e)}")

    def set_serial_W(self, TAG, brightness):
        if TAG in self.serial_dict:
            try:
                self.serial_dict[TAG].write(bytes(f"{-1},{-1},{brightness}\n", 'utf8'))
                self.serial_dict[TAG].readline().decode('utf-8').rstrip()
            except Exception as e:
                print(str(e))
                if "smth" in str(e):
                    self.logger.error(f"{str(e)}")
                    del self.serial_dict[TAG]
                    self.scan_serial()

    def set_W(self, TAG, connection, brightness):
        if connection == "local":
            self.set_local_W(brightness)
        else:
            if connection == "serial":
                self.set_serial_W(TAG, brightness)
            else:
                self.set_remote_W(TAG, brightness)

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
        self.logger.warning("scanning for USB devices..")
        for dev in glob.glob("/dev/*"):
            if "ttyUSB" in dev:
                try:
                    temp_ser = serial.Serial(dev, 250000, timeout=0.1)
                    temp_ser.write(b"#")
                    msg = temp_ser.readline().decode('utf-8').rstrip()
                    if "2137#" in msg:
                        msg = msg.split("#")
                        self.set_serial_client(path=dev, TAG=msg[1])
                except:
                    pass

    @staticmethod
    def clean():
        print("cleaning up")
        GPIO.cleanup()
