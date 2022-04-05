import time
import websockets
import asyncio
import json
from utils.python_animator import Animator
from utils import credentials_manager as cm
from utils import GPIO_manager as gm
from threading import Thread
import os
import sys
import traceback
import logging


class Client:

    def __init__(self, main_script):
        self.main_script = main_script
        self.ws = None
        self.rPi_TAG = None
        self.secret_key = None
        self.url = "wss://hal9000-color-picker-websockserver.glitch.me"
        self.first = True
        self.global_path = os.getcwd()
        self.threads = {}
        self.msg = None
        self.pm = gm.PinsManager()
        self.logger = None
        self.set_logger()
        self.animators = {"local": Animator([], self.pm)}
        self.TUD = False
        self.KUD = False

    def set_logger(self):
        logging.basicConfig(filename="logs.log",
                            format='%(asctime)s %(message)s',
                            filemode='w')
        self.logger = logging.getLogger()

    def run_thread(self, ctrl_TAG):
        print("threading")
        self.threads[ctrl_TAG] = Thread(target=self.animators[ctrl_TAG].play, args=())
        self.threads[ctrl_TAG].daemon = True
        self.threads[ctrl_TAG].start()
        return self

    def show_color(self, hex_color, ctrl_TAG, connection):
        color = self.hex_to_rgb(hex_color.replace("#", ""))
        self.pm.set_RGB(ctrl_TAG, connection, *color)

    def get_configs(self):
        cm.get_configs(self)
        self.pm.set_pins()

    def set_configs(self):
        print(self.rPi_TAG)
        cm.set_configs(self)
        print(self.rPi_TAG)

    def set_last_state(self):
        if self.msg is not None:
            print("saving last state as: ", self.msg)
            with open(os.path.join(self.global_path, "configs", 'last_state.json'), 'w') as outfile:
                json.dump(self.msg, outfile)

    def get_last_state(self):
        print("loading last state")
        obj = None
        try:
            f = open(os.path.join(self.global_path, "configs", 'last_state.json'))
            obj = json.load(f)
        except Exception as e:
            print(str(e))
        return obj

    def stop_animator(self, ctrl_TAG, connection):
        if ctrl_TAG in self.animators:
            if self.animators[ctrl_TAG].play_flag or self.animators[ctrl_TAG].sparkling:
                print("stopping animation")
                self.logger.warning("stopping animation")
                self.animators[ctrl_TAG].play_flag = False
                self.animators[ctrl_TAG].sparkling = False
                self.threads[ctrl_TAG].join()
                self.threads[ctrl_TAG] = None
        else:
            self.animators[ctrl_TAG] = Animator([], self.pm)
            self.animators[ctrl_TAG].TAG = ctrl_TAG
            self.animators[ctrl_TAG].connection = connection

    def single_color_handler(self, dict_msg):
        color = dict_msg["payload"]["color"]
        if dict_msg["payload"]["loop"] == "steady":
            self.show_color(dict_msg["payload"]["color"], dict_msg["ctrl_TAG"], dict_msg["connection"])
        if dict_msg["payload"]["loop"] == "dimming":
            self.animators[dict_msg["ctrl_TAG"]].TAG = dict_msg["ctrl_TAG"]
            self.animators[dict_msg["ctrl_TAG"]].connection = dict_msg["connection"]
            self.animators[dict_msg["ctrl_TAG"]].speed = (int(dict_msg["payload"]["speed"]))
            self.animators[dict_msg["ctrl_TAG"]].play_breathing(self.hex_to_rgb(color.replace("#", "")),
                                                                amp=int(dict_msg["payload"]["brightness"]))
            self.run_thread(dict_msg["ctrl_TAG"])
        if dict_msg["payload"]["loop"] == "sparks":
            self.animators[dict_msg["ctrl_TAG"]].TAG = dict_msg["ctrl_TAG"]
            self.animators[dict_msg["ctrl_TAG"]].connection = dict_msg["connection"]
            self.animators[dict_msg["ctrl_TAG"]].loop = "sparks"
            self.animators[dict_msg["ctrl_TAG"]].speed = (int(dict_msg["payload"]["speed"]))
            self.animators[dict_msg["ctrl_TAG"]].play_sparks(self.hex_to_rgb(color.replace("#", "")),
                                                             amp=int(dict_msg["payload"]["brightness"]))
            self.run_thread(dict_msg["ctrl_TAG"])

    async def listen(self):
        msg = self.get_last_state()
        print("connecting..")
        self.logger.warning("connecting...")
        while True:
            try:
                async with websockets.connect(self.url) as ws:
                    print("connected")
                    self.logger.warning("connected")
                    while True:
                        if self.first:
                            msg_ = {"head": "first_connection", "TAG": self.rPi_TAG}
                            await ws.send(json.dumps(msg_))
                            self.first = False
                            if self.TUD or self.KUD:
                                self.TUD = False
                                self.KUD = False
                                msg = None
                        else:
                            msg = await ws.recv()
                        type_of_data, dict_msg = self.validate_data(msg)
                        if type_of_data != -1:
                            try:
                                if type_of_data == 1:
                                    self.msg = msg
                                    self.stop_animator(dict_msg["ctrl_TAG"], dict_msg["connection"])
                                    self.single_color_handler(dict_msg)

                                if type_of_data == 2:
                                    self.msg = msg
                                    print("mood")
                                    self.logger.warning("mood")
                                    print(self.animators)
                                    self.stop_animator(dict_msg["ctrl_TAG"], dict_msg["connection"])
                                    print(dict_msg["payload"]["color_list"].split(","))
                                    self.animators[dict_msg["ctrl_TAG"]].colour_list = dict_msg["payload"][
                                        "color_list"].split(",")
                                    self.animators[dict_msg["ctrl_TAG"]].time_step = dict_msg["payload"]["speed"]
                                    self.animators[dict_msg["ctrl_TAG"]].speed = (int(dict_msg["payload"]["speed"]))
                                    self.animators[dict_msg["ctrl_TAG"]].loop = dict_msg["payload"]["loop"]
                                    self.animators[dict_msg["ctrl_TAG"]].play_flag = True
                                    self.run_thread(dict_msg["ctrl_TAG"])

                                if type_of_data == 3:
                                    print("changing configs")
                                    self.logger.warning("changing configs")
                                    self.rPi_TAG = dict_msg["NEW_TAG"]
                                    self.set_configs()
                                    self.first = True
                                    self.TUD = True
                                    break

                                if type_of_data == 4:
                                    print("changing key")
                                    self.logger.warning("changing key")
                                    self.secret_key = dict_msg["new_key"]
                                    self.set_configs()
                                    self.first = True
                                    self.KUD = True
                                    break

                                if type_of_data == 5:
                                    msg_ = {"head": "pong", "TAG": self.rPi_TAG}
                                    await ws.send(json.dumps(msg_))

                                if type_of_data == 6:
                                    self.pm.set_W(dict_msg["ctrl_TAG"],
                                                  dict_msg["connection"],
                                                  int(dict_msg["brightness"]))

                                elif type_of_data == 8:
                                    print("restarting..")
                                    self.logger.warning("restarting..")
                                    self.set_last_state()
                                    os.system('bash restart.sh  &')

                                elif type_of_data == 9:
                                    print("rebooting...")
                                    self.logger.warning("rebooting...")
                                    self.set_last_state()
                                    os.system('sudo reboot')

                            except Exception as e:
                                print(traceback.format_exc())
                                print(e)
                        else:
                            print("invalid data")
                            self.logger.error("invalid data")
            except Exception as e:
                self.set_last_state()
                print(str(e))
                self.logger.error(str(e))
                time.sleep(5)
                self.first = True
                print("reconnecting...")
                self.logger.warning("reconnecting...")

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
            if data["type"] == "white":
                return 6, data
            if data["type"] == "restart":
                return 8, data
            if data["type"] == "reboot":
                return 9, data
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
