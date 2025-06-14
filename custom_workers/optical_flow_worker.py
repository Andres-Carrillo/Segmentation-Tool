from custom_workers.segmentation_worker import BaseWorker
from utils import cv_image_to_qimage, qimage_to_cv_image
import cv2 as cv
import numpy as np


class OpticalFlowWorker(BaseWorker):
    def __init__ (self,method= "Lucas-Kanade",wind_size=(15,15),max_level=2,criteria=(cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 0.03)):
        super().__init__()
        self.input_image = None
        self.prev_image = None
        self.output_image = None
        self.method = method
        self.wind_size = wind_size
        self.max_level = max_level
        self.criteria = criteria
        self._iteration = 0
        self._track_points = None

    def process_data(self, data):
        if data is None:
            self.data = None
        else:
            self.input_image = qimage_to_cv_image(data)
            if self.prev_image is None:
                self.prev_image = self.input_image.copy()
                self.data = cv_image_to_qimage(self.prev_image)
            else:
                # for now update track points every 10 iterations
                if self._iteration % 10 == 0 or self._track_points is None:
                    self._update_track_points()

                self._apply_optical_flow()
                self.data = cv_image_to_qimage(self.output_image)
                self.prev_image = self.input_image.copy()

            # make sure we have the correct prev_image for collecting new track points on the next iteration
            if self._iteration % 9 == 0:
                self.prev_image = self.input_image.copy()

            self._iteration += 1

    def _apply_optical_flow(self):
        if self.method == "Lucas-Kanade":
            lk_params = dict(winSize=self.wind_size, maxLevel=self.max_level, criteria=self.criteria)

            prev_gray = cv.cvtColor(self.prev_image, cv.COLOR_BGR2GRAY)
            curr_gray = cv.cvtColor(self.input_image, cv.COLOR_BGR2GRAY)
 

            new_points, st, err = cv.calcOpticalFlowPyrLK(prev_gray, curr_gray, self._track_points, None, **lk_params)

            self.draw_tracks(new_points, st)

    def _update_track_points(self):

        feature_params = dict(maxCorners=100, qualityLevel=0.3, minDistance=7, blockSize=7)
        self._track_points = cv.goodFeaturesToTrack(cv.cvtColor(self.prev_image, cv.COLOR_BGR2GRAY), mask=None, **feature_params)

    def draw_tracks(self, new_points, status):
        good_new = None
        good_old = None
        self.output_image = self.input_image.copy()
        
        # If new_points is None, we cannot draw tracks
        if new_points is not None:
            # Filter out points where status is 1 (good points)
            good_new = new_points[status == 1]
            good_old = self._track_points[status == 1]

        # If we have good new and old points, draw the tracks
        if good_new is not None and good_old is not None:
            for i, (new, old) in enumerate(zip(good_new, good_old)):
                a, b = new.ravel()
                c, d = old.ravel()
                cv.line(self.output_image, (int(a), int(b)), (int(c), int(d)), (0, 255, 0), 2)
                cv.circle(self.output_image, (int(a), int(b)), 5, (0, 0, 255), -1)        
