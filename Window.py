from threading import Thread
import numpy as np
import cv2
import time
from tracking_utils import Box, Countdown, which_is_foreground, calculate_iou


class Window(Thread):
    def __init__(self, trackers):
        """
        This class defines the perception of the robot and implements the various detection and tracking algorithms needed
        :type name: Window
        """
        self.img = cv2.imread('images/Snapshots/test6.jpg')
        self.disp_img = cv2.imread('images/Snapshots/test6.jpg')
        self.first_frame = np.zeros((1080, 1920, 3), dtype=np.int32)
        self.trackers = trackers
        self.all_boxes = []
        self.box_tracked = Box((0,0,0,0))
        self.box_detected = (0,0,0,0)
        self.box_center = (0,0)

    def detect_body_haar(self):
        """
        Summary line.
        implement fullbody detection with an haarcascade detector

        Parameters:
        self.img

        Returns:
        draw a box around the detected object, if a person is detected on self.img
        """
        fullbody_cascade = cv2.CascadeClassifier("haarcascade_fullbody.xml")

        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        bodies = fullbody_cascade.detectMultiScale(gray)
        for (x, y, w, h) in bodies:
            cv2.rectangle(self.img, (x, y), (x + w, y + h), (255, 0, 0), 10)

        return bodies

    def init_tracker(self, roi):
        """
        Summary line.
        used on the first frame to draw a box around the object to be tracked

        Parameters:
        self.first frame is used to define the ROI that initializes tracking

        Returns:
        set the new value for self.tracker_roi and self.tracker
        """
        roi = tuple(map(int, roi))
        tracker = cv2.TrackerMOSSE_create()
        self.trackers.add(tracker, self.img, roi)

    def tracker_update(self, boxes_multi_tracking):
        """
        Summary line.
        implement tracking

        Parameters:
        the current value of self.tracker stored from the previous frame is used

        Returns:
        draw a box on self.img to keep track of the moving object. the value of self.roi is also modified and stored
        """
        if len(boxes_multi_tracking) > len(self.all_boxes):
            self.box_tracked = Box(boxes_multi_tracking[-1])
            self.all_boxes.append(self.box_tracked)

        for i, box in enumerate(self.all_boxes):
            if not box.is_discarded:
                box.update(boxes_multi_tracking[i])

        for b in self.all_boxes:
            if not b.is_discarded and not b.is_being_discarded:
                cv2.rectangle(self.disp_img, (b.x, b.y), (b.x + b.w, b.y + b.h), (0, 255, 0), 2)
                self.box_center = (b.x + b.w/2, b.y + b.h/2)
            elif not b.is_discarded and b.is_being_discarded:
                cv2.rectangle(self.disp_img, (b.x, b.y), (b.x + b.w, b.y + b.h), (0, 0, 255), 2)

        #TODO release lock

    def get_frame(self):
        """
        Summary line.
        simple accessor
        """
        return self.img

    def get_frame_display_frame(self):
        return self.disp_img

    def set_frame(self, frame):
        """
        Summary line.
        accessor used on every image received in UdpSocket except the first one to store the current frame in the
        window object for further treatment

        Parameters:
        the value of the current frame, of type np.array and normal shape is (1080, 1920, 3)

        Returns:
        set the value of self.img with value passed in argument
        """
        self.img = frame
        self.disp_img = frame

    def set_first_frame(self, first_frame):
        """
        Summary line.
        accessor only used once in UdpSocket to set the first frame coming through the server

        Parameters:
        the value of the first frame, of type np.array and normal shape is (1080, 1920, 3)

        Returns:
        set the value of self.first_frame with value passsed in argument
        """
        self.first_frame = first_frame

    def reliable_tracking(self, boxes_multi_tracking, boxes_yolo_detection):
        if boxes_yolo_detection is not None:
            self.box_detected = which_is_foreground(boxes_yolo_detection)

            if len(boxes_multi_tracking) == 0:
                self.init_tracker(self.box_detected)
                return False

            elif self.box_tracked.is_discarded:
                self.init_tracker(self.box_detected)
                return False
            else:
                iou = calculate_iou(self.box_detected, self.box_tracked)
                if iou < 0.3:
                    th1 = Countdown(self.box_tracked)
                    self.box_tracked.is_being_discarded = True
                    return True

        else:
            if len(boxes_multi_tracking) != 0:
                th2 = Countdown(self.box_tracked)
                self.box_tracked.is_being_discarded = True
                return True
