from PyQt5.QtWidgets import QWidget,QLabel, QVBoxLayout,QHBoxLayout,QLineEdit,QDoubleSpinBox
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush,QPixmap,QImage
# from utils import calculate_angle_between,calculate_poin_along_arc,in_circle
from custom_widgets.gauge_widget import Gauge
from utils import qimage_to_cv_image
import cv2 as cv

import pathlib
import sys

# Get the package directory
package_dir = str(pathlib.Path(__file__).resolve().parents[1])

print(f"Package directory: {package_dir}")

class MorphTransformWidget(QWidget):
    """This widget should contain two gauges, one for dilation and one for erosion.
    It should also have a white circle in the middle surrounded by a black region.
    This is to visually represent the effects of dilation and erosion on an image.
    The user can drag the gauges to tune the kernel size of the dilation and erosion operations.
    Below each gauge there should be a number input field to represent the number of iterations for each operation."""
    def __init__(self, parent = None, kernel_size=5, iterations=1, background_color=QColor(0, 0, 0), handle_color=QColor(255, 255, 255), outline_color=QColor(0, 0, 0)):
        super().__init__(parent)
        self.kernel_size = kernel_size
        self.erode_iterations = iterations
        self.dilate_iterations = iterations
        self.max = 7
        self.min = 1

        self.background_color = background_color
        self.handle_color = handle_color
        self.outline_color = outline_color
        self.dragging = False
        main_layout = QVBoxLayout()
        gauge_layout = QHBoxLayout()
        iteration_layout = QHBoxLayout()

        self.setMouseTracking(True)
        self.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        
        self.setMinimumSize(200, 200)
        self.setStyleSheet("background-color: #415a77;")

        self.image_label = QLabel(self)
        self.image_label.setScaledContents(True)
        self.image_path = "depositphotos_535761412-stock-video-glitch-circle-icon-black-background.jpg"
        self.image_label.setPixmap(QPixmap(self.image_path))

        main_layout.addWidget(self.image_label)
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.erosion_gauge = Gauge(parent=self, min=self.min, max=self.max, handle_color=handle_color)
        self.dilation_gauge = Gauge(parent=self, min=self.min, max=self.max,  handle_color=handle_color)

        self.erosion_gauge.set_title("Erosion Kern")
        self.dilation_gauge.set_title("Dilation Kern")

        self.erosion_gauge.setFixedWidth(300)
        self.dilation_gauge.setFixedWidth(300)

        self.erosion_gauge.setFixedHeight(300)
        self.dilation_gauge.setFixedHeight(300)

        gauge_layout.addWidget(self.erosion_gauge)
        gauge_layout.addWidget(self.dilation_gauge)


        self.dialtion_iterations_input = QDoubleSpinBox(self)
        # self.dialtion_iterations_input.setPlaceholderText("Dilate Iterations")
        self.dialtion_iterations_input.setFixedWidth(150)
        self.dialtion_iterations_input.setFixedHeight(30)

        self.erosion_iterations_input = QDoubleSpinBox(self)
        # self.erosion_iterations_input.setPlaceholderText("Erode Iterations")
        self.erosion_iterations_input.setFixedWidth(150)
        self.erosion_iterations_input.setFixedHeight(30)

        
        iteration_layout.addWidget(self.erosion_iterations_input)
        iteration_layout.addWidget(self.dialtion_iterations_input)

        main_layout.addLayout(gauge_layout)
        main_layout.addLayout(iteration_layout)
        self.setLayout(main_layout)

        self.erosion_gauge.value_changed.connect(self.update_visualization)
        self.dilation_gauge.value_changed.connect(self.update_visualization)

        self.dialtion_iterations_input.valueChanged.connect(self.update_visualization)
        self.erosion_iterations_input.valueChanged.connect(self.update_visualization)


    def resizeEvent(self, event):
        img_size = min(self.width(), self.height()) // 2
        x = (self.width() - img_size) // 2
        y = 0
        self.image_label.setGeometry(x, y, img_size, img_size)
        
        super().resizeEvent(event)
     
    # def paintEvent(self, event):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()
        rounded_rect = rect.adjusted(0, 0, 0, -int(self.height() / 2))
        
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtCore.Qt.black)
        painter.drawRoundedRect(rounded_rect, 12, 12) 

        painter.end()

    def update_visualization(self):

        self.erode_iterations = int(self.erosion_iterations_input.value() if self.erosion_iterations_input.value() > 0 else 1)
        self.dilate_iterations = int(self.dialtion_iterations_input.value() if self.dialtion_iterations_input.value() > 0 else 1)

        print(f"Erosion Iterations: {self.erode_iterations}, Dilation Iterations: {self.dilate_iterations}")

        image = cv.imread(self.image_path)

        # Get the current values from the gauges
        erosion_value = self.erosion_gauge.current_value
        dilation_value = self.dilation_gauge.current_value
        # Create the kernel for erosion and dilation
        erosion_kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (erosion_value * 2 + 1, erosion_value * 2 + 1))
        dilation_kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (dilation_value * 2 + 1, dilation_value * 2 + 1))
       
        # Apply erosion and dilation
        eroded_image = cv.erode(image, erosion_kernel, iterations=self.erode_iterations)
        dilated_image = cv.dilate(eroded_image, dilation_kernel, iterations=self.dilate_iterations)
       
        # Convert the processed image back to QPixmap
        processed_image = cv.cvtColor(dilated_image, cv.COLOR_BGR2RGB)
        qimage = QImage(processed_image.data, processed_image.shape[1], processed_image.shape[0], processed_image.strides[0], QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        # Update the image label with the processed image
        self.image_label.setPixmap(pixmap)
        self.image_label.setScaledContents(True)
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)    

        self.update()
