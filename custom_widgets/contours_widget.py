# this will be a widget used to contour the contours displayed in the output window
from custom_workers.contour_worker import ContourWorker
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QDoubleSpinBox,QHBoxLayout,QComboBox
from PyQt5.QtCore import pyqtSignal, Qt, QThread
from PyQt5.QtGui import QPainter, QColor, QPixmap, QImage
from utils import qimage_to_cv_image, cv_image_to_qimage
import cv2 as cv

class ContoursWidget(QWidget):
    value_changed = pyqtSignal()

    def __init__(self, parent=None, retrieval_mode=cv.RETR_EXTERNAL, approximation_method=cv.CHAIN_APPROX_SIMPLE,
                 contour_color=(0, 255, 0), contour_thickness=2, filter_contours=False,
                 min_cnt_area=100, max_cnt_area=float('inf')):
        super().__init__(parent)
        self.init_worker(retrieval_mode, approximation_method, contour_color, contour_thickness,
                         filter_contours, min_cnt_area, max_cnt_area)
        self._init_ui()

    
       

    def init_worker(self, retrieval_mode, approximation_method, contour_color, contour_thickness,
                     filter_contours, min_cnt_area, max_cnt_area):
        
        self.thread = QThread()
        
        self.worker = ContourWorker(retrieval_mode=retrieval_mode,
                                    approximation_method=approximation_method,
                                    contour_color=contour_color, contour_thickness=contour_thickness,
                                    filter_contours=filter_contours, min_cnt_area=min_cnt_area,
                                    max_cnt_area=max_cnt_area)    
        self.running = False
    
    def _init_ui(self):
        label_layout = QHBoxLayout()
        options_layout = QHBoxLayout()
        self.layout = QVBoxLayout(self)
        self.canvas = QPixmap(640, 510)
        self.label = QLabel(self)
        retrieval_mode = QComboBox()
        approximation_method = QComboBox()
        bbox_mode = QComboBox()

        retrieval_mode.addItems(["External Only", "Full List", "Tree Mode", "Two Level with Holes"])
        approximation_method.addItems(["Simple", "Full","Teh Chin L1","Teh Chin KCOS"])

        bbox_mode.addItems(["None","Bounding Box", "Rotated Box", "Minimum Enclosing Circle", "Ellipse","Convex Hull"])

        retrieval_mode.currentIndexChanged.connect(self.set_retrieval_mode)
        approximation_method.currentIndexChanged.connect(self.set_approximation_method)
        bbox_mode.currentIndexChanged.connect(self.set_bbox_mode)

        self.retrieval_mode = retrieval_mode
        self.approximation_method = approximation_method
        self.bbox_mode = bbox_mode

        label_layout.addWidget(QLabel("Retrieval Mode:"), alignment=Qt.AlignCenter)
        options_layout.addWidget(self.retrieval_mode)
        
        label_layout.addWidget(QLabel("Approximation Method:"), alignment=Qt.AlignCenter)
        options_layout.addWidget(self.approximation_method)

        label_layout.addWidget(QLabel("Bounding Box Mode:"), alignment=Qt.AlignCenter)
        options_layout.addWidget(self.bbox_mode)

        self.label.setAlignment(Qt.AlignCenter)

        self.canvas.fill(Qt.black)
        self.label.setPixmap(self.canvas)

        self.layout.addWidget(self.label, alignment=Qt.AlignCenter)
        self.layout.addLayout(label_layout)
        self.layout.addLayout(options_layout)
        self.setLayout(self.layout)


    def set_retrieval_mode(self, index):
        retrieval_modes = [cv.RETR_EXTERNAL, cv.RETR_LIST, cv.RETR_TREE, cv.RETR_CCOMP]

        if 0 <= index < len(retrieval_modes):
            self.worker.retrieval_mode = retrieval_modes[index]


    def set_approximation_method(self, index):
        approximation_methods = [cv.CHAIN_APPROX_SIMPLE, cv.CHAIN_APPROX_NONE, cv.CHAIN_APPROX_TC89_L1, cv.CHAIN_APPROX_TC89_KCOS]

        if 0 <= index < len(approximation_methods):
            self.worker.approximation_method = approximation_methods[index]


    def set_bbox_mode(self, index):
        self.worker.bounding_boxes_mode = index


    def start_worker(self):
        self.worker.moveToThread(self.thread)
        self.worker.processed.connect(self.update_canvas)
        self.thread.start()
        self.running = True

    def update_canvas(self, qimage):

        if self.running:    
            if qimage is not None:
                self.canvas = QPixmap.fromImage(qimage)
                self.label.setPixmap(self.canvas)
            else:
                self.start_worker()

        self.value_changed.emit()

    def stop_worker(self):
        if self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()
        self.worker.deleteLater()
        self.thread.deleteLater()
        self.running = False