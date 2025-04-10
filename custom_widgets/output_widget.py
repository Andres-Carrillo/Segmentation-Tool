from PyQt5.QtCore import Qt
from PyQt5.QtGui import  QPixmap
from PyQt5.QtWidgets import QWidget, QLabel,QGridLayout,QComboBox,QPushButton

class OutputWidget(QWidget):
    def __init__(self,parent):
        super().__init__(parent)
        self.saving_masks = False
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Output Widget")
        
        self.canvas = QPixmap(640, 510)
        self.label = QLabel(parent=self)

        self.canvas.fill(Qt.black)
        self.label.setPixmap(self.canvas)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setScaledContents(True)
        self.mask_mode = QComboBox(self)

        self.mask_mode.addItem("Binary Mask")
        self.mask_mode.addItem("Overlay Mask")

        self.mask_mode.currentIndexChanged.connect(self.parent().toggle_mask_mode)

        self.save_masks = QPushButton("Save Masks",clicked=self.parent().save_mask)

        layout = QGridLayout()
        layout.addWidget(self.label, 0, 0)
        layout.addWidget(self.mask_mode, 1, 0)
        layout.addWidget(self.save_masks, 2, 0)

        self.setLayout(layout)