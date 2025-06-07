from PyQt5.QtWidgets import QWidget,QLabel, QVBoxLayout,QHBoxLayout,QDoubleSpinBox,QMenuBar
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtGui import QPainter, QColor,QPixmap,QImage
from custom_widgets.gauge_widget import Gauge
from PyQt5.QtCore import pyqtSignal
import cv2 as cv
import pathlib
import enum

class MorphTransformTypeSet(enum.Enum):
    BASE = 0,
    INTERMEDIATE = 1,
    ADVANCED = 2


# Get the package directory
package_dir = str(pathlib.Path(__file__).resolve().parents[1])

class MorphTransformWidget(QWidget):
    value_changed = pyqtSignal()

    """This widget should contain two gauges, one for dilation and one for erosion.
    It should also have a white circle in the middle surrounded by a black region.
    This is to visually represent the effects of dilation and erosion on an image.
    The user can drag the gauges to tune the kernel size of the dilation and erosion operations.
    Below each gauge there should be a number input field to represent the number of iterations for each operation."""
    def __init__(self, parent = None, kernel_size=5, iterations=1, background_color=QColor(0, 0, 0), handle_color=QColor(255, 255, 255), outline_color=QColor(0, 0, 0)):
       
        super().__init__(parent)
        self._init_variables(kernel_size, iterations, background_color, handle_color, outline_color)
        self.morph_type = MorphTransformTypeSet.BASE
        self._init_ui()
        self._init_events()
        self.setStyleSheet("background-color: #415a77;")
      
    def _init_variables(self, kernel_size, iterations, background_color, handle_color, outline_color):
        self.kernel_size = kernel_size
        self.erode_iterations = iterations
        self.dilate_iterations = iterations
        self.max = 7
        self.min = 1

        self.background_color = background_color
        self.handle_color = handle_color
        self.outline_color = outline_color
        self.dragging = False

        self.image_label = QLabel(self)

        self.erosion_gauge = Gauge(parent=self, min=self.min, max=self.max, handle_color=handle_color)
        self.dilation_gauge = Gauge(parent=self, min=self.min, max=self.max,  handle_color=handle_color)

        self.dialtion_iterations_input = QDoubleSpinBox(self)
        self.erosion_iterations_input = QDoubleSpinBox(self)

        self.dialtion_iterations_input.setRange(1, 10)
        self.erosion_iterations_input.setRange(1, 10)


    def _init_ui(self):
        main_layout = QVBoxLayout()
        erosion_layout = QVBoxLayout()
        dilation_layout = QVBoxLayout()
        gauge_layout = QHBoxLayout()
        self.dilation_spinbox_label = QLabel("Dilation Iterations:")
        self.erosion_spinbox_label = QLabel("Erosion Iterations:")
        file_menu = QMenuBar(self)
        file_menu.addMenu("")
        file_menu.addAction("Base", lambda: self._update_morph_type(MorphTransformTypeSet.BASE))
        file_menu.addAction("Intermediate", lambda: self._update_morph_type(MorphTransformTypeSet.INTERMEDIATE))
        file_menu.addAction("Advanced", lambda: self._update_morph_type(MorphTransformTypeSet.ADVANCED))

        self.setMouseTracking(True)
        self.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        
        self.setMinimumSize(200, 200)
        self.setStyleSheet("background-color: #415a77;")

        self.image_label.setScaledContents(True)
        self.image_path = "images/morph_visual.jpg"
        self.image_label.setPixmap(QPixmap(self.image_path))

        main_layout.addWidget(self.image_label)
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)

        self.erosion_gauge.set_title("Erosion Kern")
        self.dilation_gauge.set_title("Dilation Kern")

        self.erosion_gauge.setFixedWidth(300)
        self.dilation_gauge.setFixedWidth(300)

        self.erosion_gauge.setFixedHeight(300)
        self.dilation_gauge.setFixedHeight(300)

        erosion_layout.addWidget(self.erosion_gauge)
        erosion_layout.addWidget(self.erosion_spinbox_label,alignment=QtCore.Qt.AlignCenter)
        erosion_layout.addWidget(self.erosion_iterations_input,alignment=QtCore.Qt.AlignCenter)
        erosion_layout.setAlignment(QtCore.Qt.AlignCenter)

        dilation_layout.addWidget(self.dilation_gauge)
        dilation_layout.addWidget(self.dilation_spinbox_label,alignment=QtCore.Qt.AlignCenter)
        dilation_layout.addWidget(self.dialtion_iterations_input,alignment=QtCore.Qt.AlignCenter)
        dilation_layout.setAlignment(QtCore.Qt.AlignCenter)

        self.dialtion_iterations_input.setFixedWidth(150)
        self.dialtion_iterations_input.setFixedHeight(30)
        
        self.erosion_iterations_input.setFixedWidth(150)
        self.erosion_iterations_input.setFixedHeight(30)

        gauge_layout.addLayout(erosion_layout)
        gauge_layout.addLayout(dilation_layout)
        main_layout.addLayout(gauge_layout)

        self.setLayout(main_layout)

    def _init_events(self):
        self.setMouseTracking(True)
        self.erosion_gauge.value_changed.connect(self.update_visualization)
        self.dilation_gauge.value_changed.connect(self.update_visualization)

        self.dialtion_iterations_input.valueChanged.connect(self.update_visualization)
        self.erosion_iterations_input.valueChanged.connect(self.update_visualization)

    def _update_morph_type(self, morph_type):
        """Update the morph type and adjust the UI accordingly."""
        self.morph_type = morph_type
        if morph_type == MorphTransformTypeSet.BASE:
            self.erosion_gauge.set_title("Erosion Kern")
            self.dilation_gauge.set_title("Dilation Kern")
            self.erosion_spinbox_label.setText("Erosion Iterations:")
            self.dilation_spinbox_label.setText("Dilation Iterations:")

        elif morph_type == MorphTransformTypeSet.INTERMEDIATE:
            self.erosion_gauge.set_title("Opening Kern")
            self.dilation_gauge.set_title("Closing Kern")
            self.erosion_spinbox_label.setText("Opening Iterations:")
            self.dilation_spinbox_label.setText("Closing Iterations:")

        elif morph_type == MorphTransformTypeSet.ADVANCED:
            self.erosion_gauge.set_title("Gradient Kern")
            self.dilation_gauge.set_title("Top Hat Kern")
            self.erosion_spinbox_label.setText("Gradient Iterations:")
            self.dilation_spinbox_label.setText("Top Hat Iterations:")

        self.update_visualization()
            

    def resizeEvent(self, event):
        img_size = min(self.width(), self.height()) // 2
        x = (self.width() - img_size) // 2
        y = 0
        self.image_label.setGeometry(x, y, img_size, img_size)
        
        super().resizeEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtCore.Qt.black)
        rounded_rect = rect.adjusted(0, 0, 0, -int(self.height() / 2))

        
        painter.drawRoundedRect(rounded_rect, 12, 12) 

        painter.end()

    def update_visualization(self):
        self.erode_iterations = int(self.erosion_iterations_input.value() if self.erosion_iterations_input.value() > 0 else 1)
        self.dilate_iterations = int(self.dialtion_iterations_input.value() if self.dialtion_iterations_input.value() > 0 else 1)

        image = cv.imread(self.image_path)

        # Get the current values from the gauges
        erosion_value = self.erosion_gauge.current_value
        dilation_value = self.dilation_gauge.current_value

        # Create the kernel for erosion and dilation
        self.erosion_kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (erosion_value * 2 + 1, erosion_value * 2 + 1))
        self.dilation_kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (dilation_value * 2 + 1, dilation_value * 2 + 1))
       
        # # Apply erosion and dilation
        processed_image = self.apply_morphological_transformations(image)
       
        # Convert the processed image back to QPixmap
        processed_image = cv.cvtColor(processed_image, cv.COLOR_BGR2RGB)
        qimage = QImage(processed_image.data, processed_image.shape[1], processed_image.shape[0], processed_image.strides[0], QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)

        # Update the image label with the processed image
        self.image_label.setPixmap(pixmap)
        self.image_label.setScaledContents(True)
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)   

        self.value_changed.emit() 

        self.update()


    def apply_morphological_transformations(self, image):
            
            if self.morph_type == MorphTransformTypeSet.BASE:
                image = cv.erode(image, self.erosion_kernel, iterations=self.erode_iterations)
                image = cv.dilate(image, self.dilation_kernel, iterations=self.dilate_iterations)
            elif self.morph_type == MorphTransformTypeSet.INTERMEDIATE:
                image = cv.morphologyEx(image, cv.MORPH_OPEN, self.erosion_kernel, iterations=self.erode_iterations)
                image = cv.morphologyEx(image, cv.MORPH_CLOSE, self.dilation_kernel, iterations=self.dilate_iterations)
            elif self.morph_type == MorphTransformTypeSet.ADVANCED:
                image = cv.morphologyEx(image, cv.MORPH_GRADIENT, self.erosion_kernel, iterations=self.erode_iterations)
                image = cv.morphologyEx(image, cv.MORPH_TOPHAT, self.dilation_kernel, iterations=self.dilate_iterations)
            
            return image