import sys
from PyQt5.QtWidgets import QApplication
from apps.seg_app import SegmentationApp
from pathlib import Path



if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(Path('style_core.qss').read_text())
    main_window = SegmentationApp()
    main_window.show()
    sys.exit(app.exec_())




