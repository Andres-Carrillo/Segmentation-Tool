import pathlib
import sys

# Get the package directory
package_dir = str(pathlib.Path(__file__).resolve().parents[1])
# Add the package directory into sys.path if necessary
if package_dir not in sys.path:
    sys.path.insert(0, package_dir)


from PyQt5.QtWidgets import QMainWindow,QApplication
from custom_widgets.backgrnd_sub_widget import BackgroundSubWidget


class TestBackGroundSubWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Background Subtraction Widget Example")
        self.setGeometry(100, 100, 800, 600)

        # Create the BackgroundSubWidget
        self.background_sub_widget = BackgroundSubWidget(parent=self)
        
        # Set the background subtraction widget as the central widget
        self.setCentralWidget(self.background_sub_widget)

        self.setFixedSize(650, 550)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = TestBackGroundSubWidget()
    main_window.show()
    sys.exit(app.exec())