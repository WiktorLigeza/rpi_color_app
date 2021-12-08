import pyaudio
import struct
import numpy as np
from utils import GPIO_manager as gm


class AudioAnalyzer:

    def __init__(self):
        self.CHUNK = 1024 * 2  # samples per frame
        self.FORMAT = pyaudio.paInt16  # audio format (bytes per sample?)
        self.CHANNELS = 1  # single channel for microphone
        self.RATE = 44100  # samples per second
        self.stream = self.init_stream()
        self.color = None
        self.pm = gm.PinsManager()
        self.pm.R_pin = 27
        self.pm.G_pin = 22
        self.pm.B_pin = 17

    def init_stream(self):
        p = pyaudio.PyAudio()
        return p.open(format=self.FORMAT,
                      channels=self.CHANNELS,
                      rate=self.RATE,
                      input=True,
                      output=True,
                      frames_per_buffer=self.CHUNK)

    def show_color(self):
        self.pm.set_RGB(*self.color)

    def animator(self):
        while True:
            data = self.stream.read(self.CHUNK)
            data_int = struct.unpack(str(2 * self.CHUNK) + 'B', data)
            data_np = np.array(data_int, dtype='b')[::2]
            sound_median = np.median(abs(data_np)) / 5
            sound_mean = np.mean(abs(data_np)) / 5
            power_mean = round(sound_mean * sound_mean)
            power_median = round(sound_median * sound_median)

            self.color = [0, power_median, power_mean]
            self.show_color()



aa = AudioAnalyzer()
