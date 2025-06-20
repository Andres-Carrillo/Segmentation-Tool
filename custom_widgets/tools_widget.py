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
    
        tools_layout = QGridLayout()
        tools_layout.addWidget(self.color_space,0,0)
        tools_layout.setContentsMargins(0, 0, 0, 0)
        tools_layout.setSpacing(0)

        self.setLayout(tools_layout)

