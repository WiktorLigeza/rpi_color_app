import os
import time
import wave
from struct import unpack
import numpy as np
import pyaudio

import RPi.GPIO as GPIO

file_name = "i"
file_name = "k"

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
        if R > 100: R = 100
        if G > 100: G = 100
        if B > 100: B = 100
        if R < 0: R = 0
        if G < 0: G = 0
        if B < 0: B = 0

        self.pwm_red.ChangeDutyCycle(R)
        self.pwm_green.ChangeDutyCycle(G)
        self.pwm_blue.ChangeDutyCycle(B)

    @staticmethod
    def clean():
        print("cleaning up")
        GPIO.cleanup()


pm = PinsManager()
pm.R_pin = 27
pm.G_pin = 22
pm.B_pin = 17

pm.set_pins()
pm.set_RGB(42, 42, 42)


spectrum = [1, 2, 3]
matrix = np.array([0, 0, 0])
power = []
weighting = [3, 7, 50]

wavfile = wave.open(f'{file_name}.wav', 'r')
sample_rate = wavfile.getframerate()
no_channels = wavfile.getnchannels()
chunk = 729

f = wave.open(f'{file_name}.wav', "rb")
p = pyaudio.PyAudio()
stream = p.open(format=p.get_format_from_width(f.getsampwidth()),
                channels=f.getnchannels(),
                rate=f.getframerate(),
                output=True)

# time_of_f = 5.442672252655029
# frames = f.getnframes()
# rate = f.getframerate()
# l = (frames / rate)
# n_sec = int(frames/chunk)
# delay = time_of_f/4135
# delay += 0.00274930241
# l_per = l/4135
# l_tot = l_per - delay

def piff(val):
    return int(2 * chunk * val / sample_rate)


def create_blank(width, height, rgb_color=(0, 0, 0)):
    image = np.zeros((height, width, 3), np.uint8)
    color = tuple(reversed(rgb_color))
    image[:] = color
    return image


def calculate_levels(data, chunk, sample_rate):
    global matrix
    try:
        # Convert raw data (ASCII string) to numpy array
        data = unpack("%dh" % (len(data) / 2), data)
        data = np.array(data, dtype='h')

        # Apply FFT - real data
        fourier = np.fft.rfft(data)
        # Remove last element in array to make it the same size as chunk
        fourier = np.delete(fourier, len(fourier) - 1)
        # Find average 'amplitude' for specific frequency ranges in Hz

        power = np.abs(fourier)

        matrix[0] = int(np.mean(power[piff(0):piff(625):1]))
        matrix[1] = int(np.mean(power[piff(625):piff(2500):1]))
        matrix[2] = int(np.mean(power[piff(2500):piff(20000):1]))

        # Tidy up column values for the LED matrix
        matrix = np.divide(np.multiply(matrix, weighting), 1000000)
        # Set floor at 0 and ceiling at 8 for LED matrix
        matrix = matrix.clip(0, 3)
    except:
        pass
    return matrix


def scale(spectrum, max_):
    arr_ = spectrum.copy()
    arr_ *= 255 / max_.max()
    return np.round(arr_)


data = wavfile.readframes(chunk)
i = 0
roll_size = 5
bass_ = []
mid_ = []
treble_ = []
dens = []
os.system(f"aplay {file_name}.wav &")
a =0
start_time = time.time()
while len(data) > 0:
    a += 1
    data = f.readframes(chunk)
    matrix = calculate_levels(data, chunk, sample_rate)
    bass_.append(matrix[0])
    mid_.append(matrix[1])
    treble_.append(matrix[2])
    dens.append(np.sum(matrix))

    for y in range(matrix.shape[0]):
            scaled = scale(matrix, max_=np.array(bass_[-roll_size:]))
            scaled_dens = scale(matrix, max_=np.array(dens[-roll_size:]))
            pm.set_RGB(int(scaled[0]), int(scaled[1]), int(scaled[2]))

print("--- %s seconds ---" % (time.time() - start_time), a)



pm.clean()
stream.stop_stream()
stream.close()
p.terminate()

