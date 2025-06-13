from custom_workers.segmentation_worker import BaseWorker
from utils import cv_image_to_qimage, qimage_to_cv_image, non_max_suppression
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
        self.bounding_box_color = (0, 0, 255)  # Default color for bounding boxes
        self.contour_thickness = contour_thickness
        self.bounding_boxes_mode = 0 # 0:None 1:Bounding Box, 2:Rotated Box, 3:Minimum Enclosing Circle, 4:Ellipse, 5:Line, 6:Convex Hull

    # data is a 2d image mask
    def process_data(self, data):
        if data is None:
            self.processed.emit(None)
            self.finished.emit()
        else:
            self.input_image = data
            self.input_image = qimage_to_cv_image(data)

            self.input_image = cv.cvtColor(self.input_image, cv.COLOR_RGBA2GRAY)
            self._find_contours()

            self.input_image = cv.cvtColor(self.input_image, cv.COLOR_GRAY2BGR)
            self._draw_contours()

            if self.bounding_boxes_mode > 0:
                self._draw_bounding_boxes()

            self.data = cv_image_to_qimage(self.output_image)

    def _find_contours(self):
        if self.input_image is not None:
            contours, hierarchy = cv.findContours(self.input_image, self.retrieval_mode, self.approximation_method)
            self.contours = contours
            self.hierarchy = hierarchy

            if self.filter_contours:
                self.contours = [cnt for cnt in self.contours if self.min_cnt_area <= cv.contourArea(cnt) <= self.max_cnt_area]

    def _draw_contours(self):
        self.output_image = np.zeros_like(self.input_image)
        if self.input_image is not None:
            cv.drawContours(self.output_image, self.contours, -1, self.contour_color, self.contour_thickness)

    def _draw_bounding_boxes(self):

         # 0:None 1:Bounding Box, 2:Rotated Box, 3:Minimum Enclosing Circle, 4:Ellipse, 5:Line, 6:Convex Hull
        if self.bounding_boxes_mode == 1:
            boxes = []
            for cnt in self.contours:
                x, y, w, h = cv.boundingRect(cnt)
                boxes.append((x, y, w, h))
   
            for (x, y, w, h) in boxes:
                if w > 0 and h > 0:  # Ensure valid dimensions
                    cv.rectangle(self.output_image, (x, y), (x + w, y + h), self.bounding_box_color, self.contour_thickness)

        elif self.bounding_boxes_mode == 2:
            for cnt in self.contours:
                rect = cv.minAreaRect(cnt)
                box = cv.boxPoints(rect)
                box = box.astype(np.int32).reshape((-1, 1, 2))
                
                if box.shape[0] > 0:
                    cv.drawContours(self.output_image, [box], 0, self.bounding_box_color, self.contour_thickness)

        elif self.bounding_boxes_mode == 3:
            for cnt in self.contours:
                (x, y), radius = cv.minEnclosingCircle(cnt)
                center = (int(x), int(y))
                radius = int(radius)
                cv.circle(self.output_image, center, radius, self.bounding_box_color, self.contour_thickness)
        
        elif self.bounding_boxes_mode == 4:
            for cnt in self.contours:
                if len(cnt) < 5:
                    continue
                
                ellipse = cv.fitEllipse(cnt)

                if ellipse[1][0] > 0 and ellipse[1][1] > 0:  # Check if the axes are valid
                    cv.ellipse(self.output_image, ellipse, self.bounding_box_color, self.contour_thickness)

        elif self.bounding_boxes_mode == 5:
            for cnt in self.contours:
                hull = cv.convexHull(cnt)
                cv.drawContours(self.output_image, [hull], 0, self.bounding_box_color, self.contour_thickness)

