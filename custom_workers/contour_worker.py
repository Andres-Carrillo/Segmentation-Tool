from custom_workers.segmentation_worker import BaseWorker
from utils import cv_image_to_qimage, qimage_to_cv_image
import cv2 as cv
import numpy as np

class ContourWorker(BaseWorker):
    def __init__(self, retrieval_mode=cv.RETR_EXTERNAL, approximation_method=cv.CHAIN_APPROX_SIMPLE,contour_color=(0, 255, 0), contour_thickness=2,
                 filter_contours=False,min_cnt_area=100, max_cnt_area=float('inf')):
        super().__init__()
        self.input_image = None
        self.contours = []
        self.hierarchy = None
        self.retrieval_mode = retrieval_mode
        self.approximation_method = approximation_method
        self.filter_contours = filter_contours
        self.min_cnt_area = min_cnt_area
        self.max_cnt_area = max_cnt_area
        self.contour_color = contour_color
        self.contour_thickness = contour_thickness


    # data is a 2d image mask
    def process_data(self, data):
        if data is None:
            self.processed.emit(None)
            self.finished.emit()
        else:
            print("type of data:", type(data))
            # print("shape of data:", data.shape)
            self.input_image = data
            self.input_image = qimage_to_cv_image(data)
            print("type of input_image after conversion:", type(self.input_image))
            print("shape of input_image after conversion:", self.input_image.shape)
            self.input_image = cv.cvtColor(self.input_image, cv.COLOR_RGBA2GRAY)
            self._find_contours()
            self.input_image = cv.cvtColor(self.input_image, cv.COLOR_GRAY2BGR)
            self._draw_contours()
            # self.input_image = cv.cvtColor(self.input_image, cv.COLOR_GRAY2RGBA)
            self.processed.emit(cv_image_to_qimage(self.output_image))
            self.finished.emit()

    def _find_contours(self):
        if self.input_image is not None:
            print("type of input_image:", type(self.input_image))
            print("shape of input_image:", self.input_image.shape)
            contours, hierarchy = cv.findContours(self.input_image, self.retrieval_mode, self.approximation_method)
            self.contours = contours
            self.hierarchy = hierarchy

            if self.filter_contours:
                self.contours = [cnt for cnt in self.contours if self.min_cnt_area <= cv.contourArea(cnt) <= self.max_cnt_area]


    def _draw_contours(self):
        self.output_image = np.zeros_like(self.input_image)
        if self.input_image is not None:
            cv.drawContours(self.output_image, self.contours, -1, self.contour_color, 1)
            print("Contours drawn on the image.")
