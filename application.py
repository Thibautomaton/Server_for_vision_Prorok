import tkinter
import cv2
import time
import PIL.Image, PIL.ImageTk
import numpy as np
import math
from Message import Message
from pynput import keyboard
from tkinter import messagebox

import sys

server_ep = ("192.168.1.88", 50000)
time.sleep(1)


class App:
    def __init__(self, window, window_title, door_to_heaven, server):
        self.window = window
        self.window.title(window_title)
        self.window.configure(background='#cfcfcf')
        self.door_to_heaven = door_to_heaven
        self.server = server
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

        self.keypressed = 'z'
        self.keyreleased = True

        # LABELS
        self.title_label = tkinter.Label(self.window, text="Robot Controller and Intrusion Detection Interface",
                                         font=("calibri", 30), fg='#cfcfcf',
                                         background='#3d3b3b')
        self.title_label.grid(row=0, column=0, columnspan=2, sticky='nesw')

        self.command_label = tkinter.Label(self.window, text="Press ZQSD to move Robot", font=("calibri", 20),
                                           fg='#3d3b3b',
                                           background='#cfcfcf')
        self.command_label.grid(row=1, column=0)

        # IMAGES

        self.down_green_arrow = PIL.Image.open("green_arrow.png")
        self.down_white_arrow = PIL.Image.open("white_arrow.png")
        self.down_green_arrow_img = PIL.ImageTk.PhotoImage(self.down_green_arrow)
        self.down_white_arrow_img = PIL.ImageTk.PhotoImage(self.down_white_arrow)

        self.up_green_arrow = self.down_green_arrow.rotate(180)
        self.up_white_arrow = self.down_white_arrow.rotate(180)
        self.up_green_arrow_img = PIL.ImageTk.PhotoImage(self.up_green_arrow)
        self.up_white_arrow_img = PIL.ImageTk.PhotoImage(self.up_white_arrow)

        self.left_green_arrow = self.down_green_arrow.rotate(-90)
        self.left_white_arrow = self.down_white_arrow.rotate(-90)
        self.left_green_arrow_img = PIL.ImageTk.PhotoImage(self.left_green_arrow)
        self.left_white_arrow_img = PIL.ImageTk.PhotoImage(self.left_white_arrow)

        self.right_green_arrow = self.down_green_arrow.rotate(90)
        self.right_white_arrow = self.down_white_arrow.rotate(90)
        self.right_green_arrow_img = PIL.ImageTk.PhotoImage(self.right_green_arrow)
        self.right_white_arrow_img = PIL.ImageTk.PhotoImage(self.right_white_arrow)

        self.forward_canvas = tkinter.Canvas(window, width=300, height=250, background='#cfcfcf', highlightthickness=0)
        self.forward_canvas.create_image(150, 0, anchor=tkinter.N, image=self.up_white_arrow_img, tags='forward')
        self.forward_canvas.create_image(150, 150, anchor=tkinter.N, image=self.down_white_arrow_img, tags='backwards')
        self.forward_canvas.create_image(75, 75, anchor=tkinter.N, image=self.left_white_arrow_img, tags='left')
        self.forward_canvas.create_image(225, 75, anchor=tkinter.N, image=self.right_white_arrow_img, tags='right')
        # self.forward_canvas.pack(side ='left', anchor = 'sw')
        self.forward_canvas.grid(row=2, column=0, sticky='nsw')

        self.canvas = tkinter.Canvas(window, width=960, height=540, highlightthickness=0)
        self.canvas.grid(column=1, row=2)

        self.dic_command = {
            "move_forward": False,
            "move_backwards": False,
            "rotate_left": False,
            "rotate_right": False
        }

        self.delay = 15
        self.update_frame()

        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.window.mainloop()

    def update_frame(self):
        # self.window.resizable(width = 0 if self.window.winfo_width()>self.window.winfo_height()*16/9 else 200, height = 1)
        frame = self.door_to_heaven.get_frame_display_frame()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        frame = cv2.resize(frame, (
        math.floor(self.canvas.winfo_height() * 16 / 9) if self.canvas.winfo_height() > 100 else math.floor(
            100 * 16 / 9), self.canvas.winfo_height() if self.canvas.winfo_height() > 100 else 100))
        self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
        self.canvas.create_image(0, 0, imag=self.photo, anchor=tkinter.NW)
        self.window.after(self.delay, self.update_frame)

    def keydown(self, key):
        if (key == 'z'):
            self.dic_command["move_forward"] = True
            self.forward_canvas.delete("forward")
            self.forward_canvas.create_image(150, 0, anchor=tkinter.N, image=self.up_green_arrow_img, tags='forward')
        elif (key == 's'):
            self.dic_command["move_backwards"] = True
            self.forward_canvas.delete("backwards")
            self.forward_canvas.create_image(150, 150, anchor=tkinter.N, image=self.down_green_arrow_img,
                                             tags='backwards')
        elif (key == 'q'):
            self.dic_command["rotate_left"] = True
            self.forward_canvas.delete("left")
            self.forward_canvas.create_image(75, 75, anchor=tkinter.N, image=self.left_green_arrow_img, tags='left')
        elif (key == 'd'):
            self.dic_command["rotate_right"] = True
            self.forward_canvas.delete("right")
            self.forward_canvas.create_image(225, 75, anchor=tkinter.N, image=self.right_green_arrow_img, tags='right')

        self.window.update()
        self.server.send_to(server_ep, Message.command_message(self.dic_command["move_forward"],
                                                               self.dic_command["move_backwards"],
                                                               self.dic_command["rotate_left"],
                                                               self.dic_command["rotate_right"]))

    def keyup(self, key):

        if (key == 'z'):
            self.dic_command["move_forward"] = False
            self.forward_canvas.delete("forward")
            self.forward_canvas.create_image(150, 0, anchor=tkinter.N, image=self.up_white_arrow_img, tags='forward')

        elif (key == 's'):
            self.dic_command["move_backwards"] = False
            self.forward_canvas.delete("backwards")
            self.forward_canvas.create_image(150, 150, anchor=tkinter.N, image=self.down_white_arrow_img,
                                             tags='backwards')

        elif (key == 'q'):
            self.dic_command["rotate_left"] = False
            self.forward_canvas.delete("left")
            self.forward_canvas.create_image(75, 75, anchor=tkinter.N, image=self.left_white_arrow_img, tags='left')
        elif (key == 'd'):
            self.dic_command["rotate_right"] = False
            self.forward_canvas.delete("right")
            self.forward_canvas.create_image(225, 75, anchor=tkinter.N, image=self.right_white_arrow_img, tags='right')

        self.window.update()
        self.server.send_to(server_ep, Message.command_message(self.dic_command["move_forward"],
                                                               self.dic_command["move_backwards"],
                                                               self.dic_command["rotate_left"],
                                                               self.dic_command["rotate_right"]))

    def on_press(self, key):
        try:
            print('alphanumeric key {0} pressed'.format(
                key.char))
            if key.char == 'z' or key.char == 'q' or key.char == 's' or key.char == 'd':
                self.keydown(key.char)
            else:
                pass

        except AttributeError:
            print('special key {0} pressed'.format(
                key))

    def on_release(self, key):
        print('{0} released'.format(
            key))
        try :
            if key.char == 'z' or key.char == 'q' or key.char == 's' or key.char == 'd':
                self.keyup(key.char)
            else:
                pass
        except AttributeError:
            print('special key {0} released'.format(
                key))

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            sys.exit()
            self.window.destroy()



