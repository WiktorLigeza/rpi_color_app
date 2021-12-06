import time
import websockets
import asyncio
import json
import pathlib
from utils.python_animator import Animator
from utils import credentials_manager as cm
from utils import GPIO_manager as gm
from threading import Thread
import os


class Client:

    def __init__(self, main_script):
        self.main_script = main_script
        self.ws = None
        self.rPi_TAG = None
        self.secret_key = None
        self.url = "wss://hal9000-color-picker-websockserver.glitch.me"
        self.first = True
        self.global_path = os.getcwd()
        self.thread = None
        self.pm = gm.PinsManager()
        self.animator = Animator(
            ["#00108a", "#152bd1", "#4454ca", "#4454ca", "#9b44ca", "#7319a4", "#550580", "#410462"],
            self.pm)
        self.animator.hex_to_rgb = self.hex_to_rgb

    def run_thread(self):
        print("threading")
        self.thread = Thread(target=self.animator.play, args=())
        self.thread.daemon = True
        self.thread.start()
        return self

    def show_color(self, hex_color):
        color = self.hex_to_rgb(hex_color.replace("#", ""))
        self.pm.set_RGB(*color)

    def get_configs(self):
        cm.get_configs(self)
        self.pm.set_pins()

    def set_configs(self):
        print(self.rPi_TAG)
        cm.set_configs(self)
        print(self.rPi_TAG)

    async def listen(self):
        print("connecting..")
        while True:
            try:
                async with websockets.connect(self.url) as ws:
                    print("connected")
                    while True:
                        if self.first:
                            msg_ = {"head": "first_connection", "TAG": self.rPi_TAG}
                            await ws.send(json.dumps(msg_))
                            self.first = False
                        msg = await ws.recv()
                        type_of_data, dict_msg = self.validate_data(msg)
                        if type_of_data != -1:
                            try:
                                if type_of_data == 1:
                                    if self.animator.play_flag:
                                        print("stopping animation")
                                        self.animator.play_flag = False
                                        self.thread.join()
                                        self.thread = None
                                    self.show_color(dict_msg["payload"]["color"])

                                if type_of_data == 2:
                                    print("mood")
                                    if self.animator.play_flag:
                                        print("stopping animation")
                                        self.animator.play_flag = False
                                        self.thread.join()
                                        self.thread = None
                                    # cv2.destroyWindow("led representation single")
                                    print(dict_msg["payload"]["color_list"].split(","))
                                    self.animator.colour_list = dict_msg["payload"]["color_list"].split(",")
                                    self.animator.time_step = dict_msg["payload"]["speed"]
                                    self.animator.speed = 1/int(dict_msg["payload"]["speed"])
                                    self.animator.loop = dict_msg["payload"]["loop"]
                                    self.animator.play_flag = True
                                    self.run_thread()

                                if type_of_data == 3:
                                    print("changing configs")
                                    self.rPi_TAG = dict_msg["NEW_TAG"]
                                    self.set_configs()
                                    self.first = True
                                    break

                                if type_of_data == 4:
                                    print("changing key")
                                    self.secret_key = dict_msg["new_key"]
                                    self.set_configs()
                                    self.first = True
                                    break

                                if type_of_data == 5:
                                    msg_ = {"head": "pong", "TAG": self.rPi_TAG}
                                    await ws.send(json.dumps(msg_))
                            except Exception as e:
                                print(e)
                        else:
                            print("invalid data")
            except Exception as e:
                print(e)
                time.sleep(5)
                self.first = True
                print("reconnecting...")

    def start(self):
        asyncio.get_event_loop().run_until_complete(self.listen())

    @staticmethod
    def validate_data(input_):
        data = ""
        try:
            data = json.loads(input_)
            if data["type"] == "single":
                return 1, data
            if data["type"] == "mood":
                return 2, data
            if data["type"] == "change_tag":
                return 3, data
            if data["type"] == "change_key":
                return 4, data
            if data["type"] == "ping":
                return 5, data
            else:
                return -1, data
        except Exception as e:
            print(str(e))
            pass
        return -1, data

    @staticmethod
    def hex_to_rgb(hex_):
        rgb = []
        for i in (0, 2, 4):
            decimal = int(hex_[i:i + 2], 16)
            rgb.append(decimal)
        return rgb
