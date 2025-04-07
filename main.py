import sys
from PyQt5.QtWidgets import QHBoxLayout,QApplication, QVBoxLayout, QWidget
from custom_widgets.seg_widget import SegmentationWidget
from pathlib import Path

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.canvas = SegmentationWidget()

        layout = QVBoxLayout()
        hlayout = QHBoxLayout()

        hlayout.addWidget(self.canvas)
        
        self.canvas.show()
        self.setLayout(layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(Path('style_core.qss').read_text())
    main_window = SegmentationWidget()
    main_window.show()
    sys.exit(app.exec_())




