import time
import cv2
import threading
from threading import Thread
from model.yolo_model import YOLO
from detection import get_classes, detect_image

class Tracking(Thread):
    def __init__(self, threading_event, trackers, door_to_heaven):
        Thread.__init__(self)
        self.threading_event = threading_event
        self.trackers = trackers
        self.door_to_heaven = door_to_heaven
        self.lock2 = threading.Lock

    def run(self):
        yolo = YOLO(0.3, 0.5)
        file = 'data/coco_classes.txt'
        all_classes = get_classes(file)

        f2 = 'test8.jpg'
        path2 = 'images/Snapshots/' + f2
        image2 = cv2.imread(path2)
        image2, boxes_multi_tracking = detect_image(image2, yolo, all_classes)
        cv2.imwrite('images/res/' + f2, image2)
        print("ok1")
        t_prev = time.time()
        while self.threading_event.wait():
            (success, boxes_multi_tracking) = self.trackers.update(self.door_to_heaven.get_frame())
            self.door_to_heaven.tracker_update(boxes_multi_tracking)
            if time.time() - t_prev > 1:
                print(time.time() - t_prev)
                t_prev = time.time()
                # créer encore un nouveau thread qui effctue cette tâche
                image, boxes_yolo_detection = detect_image(self.door_to_heaven.get_frame(), yolo, all_classes)

                replayDetection = self.door_to_heaven.reliable_tracking(boxes_multi_tracking, boxes_yolo_detection)