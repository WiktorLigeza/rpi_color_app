import time


class Animator:
    def __init__(self, colour_list=None, pm=None, time_step=100):
        if colour_list is None:
            colour_list = []
        self.colour_list = colour_list
        self.colour_list_rev = self.colour_list.copy()
        self.colour_list_rev.reverse()
        self.time_step = time_step
        self.loop = "loop"
        self.grid = 10000
        self.speed = 1/self.time_step
        self.steps = self.grid / self.time_step
        self.play_flag = False
        self.hex_to_rgb = None
        self.pm = pm

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

    def show_color(self, color):
        self.pm.set_RGB(*color)
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

