from custom_workers.segmentation_worker import BaseWorker
from utils import cv_image_to_qimage, qimage_to_cv_image, non_max_suppression
import cv2 as cv
import numpy as np


class BackgroundSubtractorWorker(BaseWorker):
    def __init__(self, method=cv.createBackgroundSubtractorMOG2(),):
        super().__init__()
        self.input_image = None
        self.method = method
        self.output_image = None
        self.should_detect_shadows = True
        self.method_history = 500  # Default history for MOG2
        self.method_dist_threshold = 400 if self.method == cv.createBackgroundSubtractorKNN() else 16  # Default threshold for KNN

    def process_data(self, data):
        if data is None:
            self.processed.emit(None)
            self.finished.emit()
        else:
            self.input_image = qimage_to_cv_image(data)
            self._apply_background_subtraction()
            self.processed.emit(cv_image_to_qimage(self.output_image))
            self.finished.emit()

    def _apply_background_subtraction(self):
        if self.input_image is not None:
            fg_mask = self.method.apply(self.input_image)
            self.output_image = cv.cvtColor(fg_mask, cv.COLOR_GRAY2BGR)

    def set_method(self, method):
        if method == "MOG2":
            self.method = cv.createBackgroundSubtractorMOG2(history=self.method_history,
                                                            detectShadows=self.should_detect_shadows,
                                                            varThreshold=self.method_dist_threshold)
        elif method == "KNN":
            self.method = cv.createBackgroundSubtractorKNN(history=self.method_history,
                                                           detectShadows=self.should_detect_shadows,
                                                           dist2Threshold=self.method_dist_threshold)
        else:
            raise ValueError("Unsupported background subtraction method")
        
    def set_history(self, history):
        self.method_history = history

    def set_dist_threshold(self, dist_threshold):
        self.method_dist_threshold = dist_threshold
        
    def detect_shadows(self, detect):
        self.should_detect_shadows = detect