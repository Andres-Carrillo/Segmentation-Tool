import pathlib
import sys

# Get the package directory
package_dir = str(pathlib.Path(__file__).resolve().parents[1])
# Add the package directory into sys.path if necessary
if package_dir not in sys.path:
    sys.path.insert(0, package_dir)


from custom_widgets.morph_transform_widget import MorphTransformWidget
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget


if __name__ == "__main__":


    app = QApplication(sys.argv)
    main_window = QMainWindow()
    main_window.setWindowTitle("Morph Transform Widget Example")
    main_window.setGeometry(100, 100, 800, 600)

    # Create a central widget
    central_widget = QWidget()
    central_widget.setStyleSheet("background-color: #415a77;")
    main_window.setCentralWidget(central_widget)

    # Create a layout
    layout = QVBoxLayout()
    central_widget.setLayout(layout)

    morph_widget = MorphTransformWidget(parent=main_window)
    layout.addWidget(morph_widget)

    main_window.show()
    sys.exit(app.exec())