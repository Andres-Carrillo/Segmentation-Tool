# this will be a widget used to contour the contours displayed in the output window
from custom_workers.contour_worker import ContourWorker
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QDoubleSpinBox
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPainter, QColor, QPixmap, QImage
import cv2 as cv

class ContoursWidget(QWidget):
    value_changed = pyqtSignal()

    def __init__(self, parent=None, retrieval_mode=cv.RETR_EXTERNAL, approximation_method=cv.CHAIN_APPROX_SIMPLE,
                 contour_color=(0, 255, 0), contour_thickness=2, filter_contours=False,
                 min_cnt_area=100, max_cnt_area=float('inf')):
        super().__init__(parent)
        self.worker = ContourWorker(retrieval_mode=retrieval_mode,
                                    approximation_method=approximation_method,
                                    contour_color=contour_color, contour_thickness=contour_thickness,
                                    filter_contours=filter_contours, min_cnt_area=min_cnt_area,
                                    max_cnt_area=max_cnt_area)
        self._init_ui()
        self._init_events()

    def _init_ui(self):
        self.layout = QVBoxLayout(self)
        self.label = QLabel("Contours Widget", self)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

    def _init_events(self):
        self.worker.processed.connect(self.update_image)