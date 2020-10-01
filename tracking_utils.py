import threading
import time
import numpy as np


class Box:
    def __init__(self, x_y_w_h):
        self.x, self.y, self.w, self.h = [int(v) for v in x_y_w_h]
        self.is_discarded: bool = False
        self.is_being_discarded: bool = False

    def update(self, x_y_w_h):
        self.x, self.y, self.w, self.h = map(lambda x: int(x), x_y_w_h)

    def discard(self):
        if self.is_being_discarded:
            self.is_discarded =True

    def area(self):
        return self.w*self.h

    def __str__(self):
        return "({}, {}, {}, {})".format(self.x, self.y, self.w, self.h)


class Countdown(object):
    def __init__(self, obj_box):
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()
        self.b = obj_box

    def run(self):
        for i in range(2):
            print("is discarding now")
            time.sleep(1)
        self.b.discard()


def which_is_foreground(bodies):
    def area(box):
        (x, y, w, h) = box
        return w * h

    return bodies[list(map(area, bodies)).index(max(map(area, bodies)))]


def calculate_iou(box_d, box_t):
    (x1, y1, w1, h1) = box_d
    (x2, y2, w2, h2) = (box_t.x, box_t.y, box_t.w, box_t.h)

    w_intersec = min(x1 + w1, x2 + w2) - max(x1, x2)
    h_intersec = min (y1 + h1, y2 + h2) - max(y1,  y2)

    if w_intersec <=0 or h_intersec<=0:
        iou = 0

    I = w_intersec * h_intersec
    U = w1 * h1 + w2 * h2 - I
    iou = I/U
    return iou

