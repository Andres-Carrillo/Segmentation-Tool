from PyQt5.QtWidgets import ( QWidget,QVBoxLayout,QStackedLayout,QDial)
from PyQt5 import QtWidgets
from PyQt5 import QtCore
# from PyQt5 import QtGui
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush
from custom_widgets.range_widget import RangeSlider


class QDialMarked(QWidget):
    def __init__(self, parent = None, kernel_size=5, iterations=1, flags=None):
        super().__init__(parent)
        self.kernel_size = kernel_size
        self.iterations = iterations
        self.max = 7
        self.min = 1

    def paintEvent(self, event):
        # draw normal dial
        super().paintEvent(event)
        self.setStyleSheet("background-color: None;")

        self.setMinimumSize(200, 200)
        self.setMaximumSize(200, 200)
        # self.setValue(self.kernel_size)

        # # now draw tick marks along the dial
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.setBrush(QBrush(QColor(0, 0, 0)))
        painter.drawEllipse(self.rect().center(), 10, 10)

        # draw arch for the dial
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        
        inner_ring = self.rect().adjusted(20, 20, -20, -20)
        outer_ring = self.rect().adjusted(40, 40, -40, -40)
        painter.drawArc(inner_ring, 0, 180 * 16)
        painter.drawArc(outer_ring, 0, 180 * 16)

        #draw edge cap of the dial
        # painter.setPen(QPen(QColor(0, 255, 255), 2))
        # painter.setBrush(QBrush(QColor(0, 0, 0)))
        # draw arc for the endcap of the dial
        # painter.drawArc(inner_ring, 0, 180 * 16)
        # painter.drawArc(outer_ring, 0, 180 * 16)

        print("innter ring", inner_ring)
        print("outer ring", outer_ring)
        #draw arch that goes from the start of the inner ring to the start of the outer ring
        # encap = self.rect().adjusted(20, 160, -140, -80)
        start_cap = QtCore.QRectF(20, 90, 20, 20)
        end_cap = QtCore.QRectF(160, 90, 20, 20)
        # encap = self.rect().adjusted(20, 20, -20, -20)

        # print("encap", encap)

        # painter.translate(QtCore.QPointF(encap.x(),encap.y()))

        #draw the rectangle around the endcap
        # painter.setPen(QPen(QColor(0, 255, 255), 2))
        # painter.setBrush(QBrush(QColor(0, 0, 0)))

        # painter.rotate(360)
        # painter.drawRect(encap)
        painter.drawArc(start_cap, 0, -180 * 16)
        painter.drawArc(end_cap, 0, -180 * 16)
        # painter.drawEllipse(self.rect().center(), 10, 10)
        # draw tick marks


        # painter.drawText(self.rect().center(), QtCore.Qt.AlignCenter, str(self.kernel_size))
        painter.end()
        