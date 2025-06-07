import pathlib
import sys

# Get the package directory
package_dir = str(pathlib.Path(__file__).resolve().parents[1])
# Add the package directory into sys.path if necessary
if package_dir not in sys.path:
    sys.path.insert(0, package_dir)


from PyQt5.QtWidgets import QMainWindow,QApplication
from custom_widgets.contours_widget import ContoursWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Contours Widget Example")
        self.setGeometry(100, 100, 800, 600)

        # Create the ContoursWidget
        self.contours_widget = ContoursWidget(parent=self)
        
        # Set the contours widget as the central widget
        self.setCentralWidget(self.contours_widget)




if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())