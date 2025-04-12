from custom_widgets.gauge_widget import Gauge
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Matplotlib with QThread and QTimer")
        self.setGeometry(100, 100, 800, 600)

        # Create a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Add Matplotlib figure
        # self.canvas = MatplotlibCanvas(self)
        self.dial = Gauge(parent=self)
        self.dial.set_title("Gauge")
        
        layout.addWidget(self.dial)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())