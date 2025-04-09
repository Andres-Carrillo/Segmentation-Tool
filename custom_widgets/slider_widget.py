from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui, QtWidgets
from utils import in_bounds, clip_value

class Slider(QtWidgets.QWidget):
    value_changed = QtCore.pyqtSignal()

    def __init__(self,parent=None, min_value=0, max_value=100, handle_color=QtGui.QColor('gray'), track_bar_color=QtGui.QColor('red'), background_color=QtGui.QColor('black'), widget_width=None, widget_height=None, padding=10, handle_width=10, handle_height=10, x_offset=0, y_offset=0, *args, **kwargs):
        super().__init__(parent=parent,*args, **kwargs)
        self.setMouseTracking(True)

        self.x_offset = x_offset
        self.y_offset = y_offset

        self._range = (min_value, max_value)

        self.dragging_handle = False

        self.padding = padding
    
        if parent != None:
            if self.parent(). width() > 250:
                self.widget_width = int(self.parent().width() / 4 )
            else:
                self.widget_width = int(self.parent().width() *2)

            if self.parent().height() > 250:
                self.widget_height = int(self.parent().height() / 16 )
            else:
                self.widget_height = int(self.parent().height()/4)
        else:
            if widget_height is not None:
                self.widget_height = widget_height - self.padding

            if widget_width is  not None:
                self.widget_width = int(widget_height) - self.padding

        self.handle_width = handle_width
        self.handle_height = handle_height

        self.starting_position = (self.padding + self.x_offset, self.padding + self.y_offset)
        self.ending_position = (int((self.widget_width + self.x_offset) + self.padding / 2), int(self.widget_height) + self.y_offset)

        # self.min_handle_position = self.x_offset + self.padding
        self.handle_position = int((self.widget_width + self.x_offset) + self.padding / 2)

        self.track_bar_color = track_bar_color
        self.bckgrnd_color = background_color
        self.handle_color = handle_color

        self.setSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding
        )

    def paintEvent(self, e):
        track_bar_width = abs(self.handle_position - self.starting_position[0])

        painter = QtGui.QPainter(self)

        brush = QtGui.QBrush()
        brush.setColor(self.bckgrnd_color)
        brush.setStyle(Qt.SolidPattern)

        painter.setBrush(brush)

        # draw the background
        background = QtCore.QRect(self.x_offset + self.padding, self.y_offset, self.widget_width, self.widget_height)
        painter.drawRoundedRect(background, 5, 5)

        # draw the filled in range bar
        painter.setBrush(self.track_bar_color)
        track_bar = QtCore.QRect(self.starting_position[0], self.y_offset, track_bar_width, self.ending_position[1] - self.y_offset)
        painter.drawRoundedRect(track_bar, 5, 5)

        painter.setBrush(self.handle_color)
        max_handle = QtCore.QRect(self.handle_position, self.y_offset, self.handle_width, self.handle_height)
        painter.drawRoundedRect(max_handle, 5, 5)

        painter.end()

    def sizeHint(self):
        return QtCore.QSize(self.widget_width, self.widget_height)

    def _trigger_refresh(self):
        self.update()

    def mousePressEvent(self, e):
        # skip if we are already dragging
        if self.dragging_handle:
            return

        # Convert global position to local position
        local_pos = self.mapFromGlobal(e.globalPos())

        if in_bounds(local_pos.x(), local_pos.y(), self.handle_position, self.y_offset, self.handle_width, self.handle_height):
            self.dragging_handle = True  # clicked on the max handle

    def mouseReleaseEvent(self, e):
        self.dragging_handle = False

    def mouseMoveEvent(self, e):
        if e.buttons() & QtCore.Qt.LeftButton:
            position = clip_value(e.x(), self.starting_position[0], int((self.widget_width + self.x_offset) + self.padding / 2))

            if self.dragging_handle:
                self.handle_position = position

            self._trigger_refresh()
            self.value_changed.emit()

    def get_value(self):
        max_distance = self.handle_position - self.starting_position[0]
        absolute_distance = self.ending_position[0] - self.starting_position[0]

        max_val = int(max_distance / (absolute_distance) * self._range[1]) 
        max_val = clip_value(max_val, self._range[0], self._range[1])

        return  max_val