from PyQt5.QtWidgets import QVBoxLayout, QCheckBox, QWidget,QLabel,QComboBox,QHBoxLayout,QSlider
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt,QThread
from custom_workers.backgrnd_subtractor_woker import BackgroundSubtractorWorker
from custom_widgets.slider_widget import Slider
import cv2 as cv


# TODO: Add Morphological operations to the background subtraction widget
# TODO: Add Contour tools to the background subtraction widget

class BackgroundSubWidget(QWidget):
    def __init__(self,parent=None,mode="MOG",detect_shadows=True,history=500,dist_threshold=16):
        super().__init__(parent)
        self.init_worker(mode, detect_shadows, history, dist_threshold)
        self._init_ui()
      
    def init_worker(self, mode, detect_shadows, history, dist_threshold):
        if mode == "MOG":
            method = cv.createBackgroundSubtractorMOG2(history=history, detectShadows=detect_shadows)
        elif mode == "KNN":
            method = cv.createBackgroundSubtractorKNN(history=history, detectShadows=detect_shadows,
                                                      dist2Threshold=dist_threshold)
        else:
            raise ValueError("Unsupported background subtraction method. Use 'MOG' or 'KNN'.")
        
        self.thread = QThread()
        
        self.worker = BackgroundSubtractorWorker(method=method, detect_shadows=detect_shadows,
                                                  history=history, dist_threshold=dist_threshold)

        self.running = False

    def _init_ui(self):
        label_layout = QHBoxLayout()
        options_layout = QHBoxLayout()
        self.layout = QVBoxLayout(self)
        self.canvas = QPixmap(640, 480)
        self.label = QLabel(self)

        history_label = QLabel("History:")
        dist_threshold_label = QLabel("Distance Threshold:")
        detect_shadows_checkbox = QCheckBox("Detect Shadows")
        
        self.method_combo = QComboBox()
        self.history_slider = QSlider(Qt.Horizontal,minimum=1, maximum=1000)
        self.history_slider.setValue(500)
        self.dist_threshold_slider = QSlider(Qt.Horizontal,minimum=0, maximum=self.canvas.width() * self.canvas.height())
        self.dist_threshold_slider.setValue(16)

        detect_shadows_checkbox.setChecked(True)
        self.method_combo.addItems(["MOG", "KNN"])
        self.method_combo.currentTextChanged.connect(self.update_method)

        self.canvas.fill(Qt.black)
        self.label.setPixmap(self.canvas)
        
        self.label.setMinimumSize(640, 480)
        self.label.setAlignment(Qt.AlignCenter)
        
        self.layout.addWidget(self.label)
        options_layout.addWidget(self.method_combo)
        label_layout.addWidget(history_label, alignment=Qt.AlignCenter)
        options_layout.addWidget(self.history_slider)
        label_layout.addWidget(dist_threshold_label, alignment=Qt.AlignCenter)
        options_layout.addWidget(self.dist_threshold_slider)
        detect_shadows_checkbox.toggled.connect(self.toggle_shadows)
        self.layout.addLayout(label_layout)
        self.layout.addLayout(options_layout)

        self.setFixedSize(640, 545)

    def update_method(self, method):
        method_type = "MOG" if method == 1 else "KNN"
        self.worker.set_method(method_type)

    def update_history(self, history):
        self.worker.set_history(history)

    def update_dist_threshold(self, dist_threshold):
        self.worker.set_dist_threshold(dist_threshold)

    def toggle_shadows(self, detect):
        self.worker.detect_shadows(detect)

    def start_worker(self):
        if not self.running:
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