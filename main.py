import tkinter
from UdpSocket import UdpSocket

from Window import Window
import threading
from DetectAndTrack import Tracking

import time
import cv2
import os
from application import App

from detection import get_classes, detect_image

os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'

threading_event = threading.Event()
trackers = cv2.MultiTracker_create()
door_to_heaven = Window(trackers)
time.sleep(1)

if __name__ == "__main__":
    server = UdpSocket(door_to_heaven, threading_event)
    server.start_socket("127.0.0.1", 50000, "test")
    serverSensors = UdpSocket(door_to_heaven, threading_event)
    serverSensors.start_socket("127.0.0.1", 50009, "test")
    tracking = Tracking(threading_event, trackers, door_to_heaven)

    tracking.start()

    tk_app = App(tkinter.Tk(), "Projet IA Ingé 2", door_to_heaven, server, serverSensors)

