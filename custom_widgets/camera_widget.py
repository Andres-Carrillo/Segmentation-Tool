# from camera import CameraWorker
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QWidget,QLabel,QImage
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt,QThread, pyqtSignal
from utils import qlabel_to_cv_image
from utils import cv_image_to_qlabel
import cv2 as cv

class CameraWorker(QThread):
    image = pyqtSignal(QImage)

    def __init__(self, camera_index=0):
        super().__init__()
        self.camera_index = camera_index
        self.running = False

    def run(self):
        self.running = True
        capture = cv.VideoCapture(self.camera_index)
        while self.running:
            print("running")
            ret, frame = capture.read()

            if ret:
                rgb_image = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                qt_image = cv_image_to_qlabel(rgb_image)
                self.image.emit(qt_image)
            
            else:
                break
        capture.release()

    def stop(self):
        self.running = False
        self.wait()

class CameraWidget(QWidget):
    running = False
    
    def __init__(self):
        super().__init__()
        
        self.image_label = QLabel()
        layout = QVBoxLayout()
        self.image_label.setGeometry(0, 0, 640, 480)
        self.image_label.setScaledContents(True)
        
        self.play_button = QPushButton("Start",clicked=self.start)
        self.image_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(self.image_label)
        layout.addWidget(self.play_button)
        self.setLayout(layout)

        self.camera_worker = CameraWorker()
        self.camera_worker.image.connect(self.update_image)

    def start(self):
         self.camera_worker.start()
         CameraWidget.running = True

         self.play_button.setText("Stop")
         self.play_button.clicked.disconnect()
         self.play_button.clicked.connect(self.closeEvent)    

    def update_image(self, q_image):
        pixmap = QPixmap.fromImage(q_image)
        self.image_label.setPixmap(pixmap)
        if CameraWidget.running:
            qlabel_to_cv_image(self.image_label)

    def closeEvent(self, event):
        self.camera_worker.stop()
        event.accept()
        CameraWidget.running = False


