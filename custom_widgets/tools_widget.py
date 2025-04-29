from PyQt5.QtWidgets import QWidget,QGridLayout
import cv2 as cv
from custom_widgets.color_wheel_widget import ColorSpaceWidget
from custom_widgets.gauge_widget import Gauge

class SegmentationToolWidget(QWidget):

    def __init__(self,parent=None,color_space = 0):
        super().__init__(parent)
        self.color_space = color_space
        self.init_ui()

    #change layout to use stacked layout so that all widgets can be seen
    def init_ui(self):
        self.color_space = ColorSpaceWidget(parent=self)
        self.color_space.setStyleSheet("background-color: transparent")

        self.erosion_control = Gauge(parent=self,min=0,max = 7)
        self.erosion_control.set_title("Erode Kernel")
        self.erosion_control.setFixedSize(200, 200)
        self.erosion_control.setStyleSheet("background-color: transparent")

        self.dilation_control = Gauge(parent=self,min=0,max = 7)
        self.dilation_control.set_title("Dilate kernel")
        self.dilation_control.setFixedSize(200, 200)
        self.dilation_control.setStyleSheet("background-color: transparent")
    

        # contour_layout = QGridLayout()
            
        tools_layout = QGridLayout()

        tools_layout.addWidget(self.color_space,0,0)
        tools_layout.addWidget(self.erosion_control,0,1,1,1)
        tools_layout.addWidget(self.dilation_control,1,1,1,1)
        tools_layout.setContentsMargins(0, 0, 0, 0)
        tools_layout.setSpacing(0)

        self.setLayout(tools_layout)

