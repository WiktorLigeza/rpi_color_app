import time
import random


class Animator:
    def __init__(self, colour_list=None, pm=None, time_step=50):
        if colour_list is None:
            colour_list = []
        self.colour_list = colour_list
        self.colour_list_rev = self.colour_list.copy()
        self.colour_list_rev.reverse()
        self.time_step = time_step
        self.loop = "loop"
        self.grid = 10000
        self.speed = 1 / self.time_step
        self.steps = self.grid / self.time_step
        self.play_flag = False
        self.pm = pm
        self.sparkling = False
        self.color = None
        self.amp = None
        self.TAG = "local"
        self.connection = "local"

        self.R_steps = 0
        self.G_steps = 0
        self.B_steps = 0

        self.from_rbg = [0, 0, 0]
        self.to_rbg = [0, 0, 0]

    def play(self):
        if self.loop == "rep":
            while self.play_flag:
                for i in range(len(self.colour_list) - 1):
                    self.animation(self.colour_list[i], self.colour_list[i + 1])

        if self.loop == "loop":
            while self.play_flag:
                for i in range(len(self.colour_list) - 1):
                    self.animation(self.colour_list[i], self.colour_list[i + 1])
                self.animation(self.colour_list[-1], self.colour_list[0])

        if self.loop == "boomerang":
            while self.play_flag:
                for i in range(len(self.colour_list) - 1):
                    self.animation(self.colour_list[i], self.colour_list[i + 1])

                for i in range(len(self.colour_list) - 1):
                    self.animation(self.colour_list_rev[i], self.colour_list_rev[i + 1])

        if self.loop == "sparks":
            self.animate_sparks()

    def animation(self, from_color, to_color):
        self.from_rbg = self.hex_to_rgb(from_color.replace("#", ""))
        self.to_rbg = self.hex_to_rgb(to_color.replace("#", ""))

        R_dif = self.to_rbg[0] - self.from_rbg[0]
        G_dif = self.to_rbg[1] - self.from_rbg[1]
        B_dif = self.to_rbg[2] - self.from_rbg[2]

        self.R_steps = R_dif / self.steps
        self.G_steps = G_dif / self.steps
        self.B_steps = B_dif / self.steps

        print(from_color, " -> ", to_color, self.steps)
        self.transition()

    @staticmethod
    def apply_amp(color, amp):
        amped = [x - x * amp for x in color]
        for i in range(3):
            if color[i] < 0: color[i] = 0
        return amped

    def play_breathing(self, color, amp):
        amp = amp / 100
        self.loop = "loop"
        self.colour_list = []
        self.colour_list_rev = []
        self.colour_list.append("#{0:02x}{1:02x}{2:02x}".format(self.clamp(color[0]),
                                                                self.clamp(color[1]), self.clamp(color[2])))
        amped = self.apply_amp(color, amp)
        self.colour_list.append("#{0:02x}{1:02x}{2:02x}".format(self.clamp(amped[0]),
                                                                self.clamp(amped[1]), self.clamp(amped[2])))
        self.colour_list.append("#{0:02x}{1:02x}{2:02x}".format(self.clamp(color[0]),
                                                                self.clamp(color[1]), self.clamp(color[2])))
        self.play_flag = True

    def play_sparks(self, color, amp):
        self.color = color
        self.amp = amp
        self.sparkling = True

    def animate_sparks(self):
        while self.sparkling:
            amped = self.apply_amp(self.color, random.randint(1, self.amp)/100)
            self.show_color(amped)

    def show_color(self, color):
        self.pm.set_RGB(self.TAG, self.connection, *color)
        time.sleep(self.speed)

    def transition(self):
        for i in range(1, int(self.steps)):
            r = round(self.from_rbg[0] + self.R_steps * i)
            g = round(self.from_rbg[1] + self.G_steps * i)
            b = round(self.from_rbg[2] + self.B_steps * i)
            color = r, g, b
            self.show_color(color)
            if not self.play_flag:
                break

    @staticmethod
    def clamp(x):
        x = int(x)
        return max(0, min(x, 255))

    @staticmethod
    def hex_to_rgb(hex_):
        rgb = []
        for i in (0, 2, 4):
            decimal = int(hex_[i:i + 2], 16)
            rgb.append(decimal)
        return rgb
