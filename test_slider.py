from custom_widgets.slider_widget import Slider
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gauge Widget Example")
        self.setGeometry(100, 100, 800, 600)

        # Create a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        self.slider = Slider(parent=self)
        self.left_slider = Slider(parent=self)

        self.slider.set_alignment("Center")
        self.left_slider.set_alignment("Center")


        layout.addWidget(self.slider)
        layout.addWidget(self.left_slider)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())