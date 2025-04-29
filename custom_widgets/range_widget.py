from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui, QtWidgets
from utils import in_bounds, clip_value

class RangeSlider(QtWidgets.QWidget):
    value_changed = QtCore.pyqtSignal()

    def __init__(self,parent=None, min_value=0, max_value=100, handle_color=QtGui.QColor('gray'), track_bar_color=QtGui.QColor('red'), background_color=QtGui.QColor('black'),
                  widget_width=None, widget_height=None, padding=10, handle_width=10, handle_height=10, x_offset=0, y_offset=0,title=None, *args, **kwargs):
        super().__init__(parent=parent,*args, **kwargs)
        self.setMouseTracking(True)

        self.x_offset = x_offset
        self.y_offset = y_offset

        self._range = (min_value, max_value)

        self.dragging_min_handle = False
        self.dragging_max_handle = False

        self.low = min_value
        self.high = max_value

        self.padding = padding
        self.title = title
        
        self.widget_width = int(self.rect().width()/1.5)

        self.widget_height = int(self.rect().height()/32)
       
        self.handle_width = handle_width
        self.handle_height = handle_height

        self.starting_position = (self.padding + self.x_offset, self.padding + self.y_offset)
        self.ending_position = (int((self.widget_width + self.x_offset) + self.padding / 2), int(self.widget_height) + self.y_offset)

        self.min_handle_position = self.x_offset + self.padding
        self.max_handle_position = int((self.widget_width + self.x_offset) + self.padding / 2)

        self.track_bar_color = track_bar_color
        self.bckgrnd_color = background_color
        self.handle_color = handle_color

        self.setSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding
        )

    def  resizeEvent(self, a0):
        self.widget_width = int(self.rect().width()/1.5)
        self.widget_height = max(int(self.rect().height()/32),11)


        self.starting_position = (self.padding + self.x_offset, self.padding + self.y_offset)
        self.ending_position = (int((self.widget_width + self.x_offset) + self.padding / 2), int(self.widget_height) + self.y_offset)

        self.min_handle_position = self.x_offset + self.padding
        self.max_handle_position = int((self.widget_width + self.x_offset) + self.padding / 2)


    def paintEvent(self, e):
        track_bar_width = abs(self.max_handle_position - self.min_handle_position)

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        brush = QtGui.QBrush()
        brush.setColor(self.bckgrnd_color)
        brush.setStyle(Qt.SolidPattern)

        painter.setBrush(brush)

        font = QtGui.QFont()
        font.setFamily("Times")
        font.setBold(True)
        font.setPointSize(14)
        painter.setFont(font)

        if self.title is not None:
            painter.drawText(int(self.starting_position[0]), 10, 100, 100, Qt.AlignHCenter, self.title)
 
        # draw the background
        background = QtCore.QRect(self.x_offset + self.padding, self.y_offset, self.widget_width, self.widget_height)
        painter.drawRoundedRect(background, 5, 5)

        # draw the filled in range bar
        painter.setBrush(self.track_bar_color)
        track_bar = QtCore.QRect(self.min_handle_position, self.y_offset, track_bar_width, self.ending_position[1] - self.y_offset)
        painter.drawRoundedRect(track_bar, 5, 5)

        # draw the min handle
        painter.setBrush(self.handle_color)
        min_handle = QtCore.QRect(self.min_handle_position, self.y_offset, self.handle_width, self.handle_height)
        painter.drawRoundedRect(min_handle, 5, 5)

        # draw the max handle
        max_handle = QtCore.QRect(self.max_handle_position, self.y_offset, self.handle_width, self.handle_height)
        painter.drawRoundedRect(max_handle, 5, 5)

        painter.end()

    def sizeHint(self):
        return QtCore.QSize(self.widget_width, self.widget_height)

    def _trigger_refresh(self):
        self.update()

    def mousePressEvent(self, e):
        # skip if we are already dragging
        if self.dragging_min_handle or self.dragging_max_handle:
            return

        # Convert global position to local position
        local_pos = self.mapFromGlobal(e.globalPos())

        # check if the mouse is within the bounds of the handle
        if in_bounds(local_pos.x(), local_pos.y(), self.min_handle_position, self.y_offset, self.handle_width, self.handle_height):
            self.dragging_min_handle = True  # clicked on the min handle
        elif in_bounds(local_pos.x(), local_pos.y(), self.max_handle_position, self.y_offset, self.handle_width, self.handle_height):
            self.dragging_max_handle = True  # clicked on the max handle

    def mouseReleaseEvent(self, e):
        self.dragging_min_handle = False
        self.dragging_max_handle = False

    def mouseMoveEvent(self, e):
        if e.buttons() & QtCore.Qt.LeftButton:
            position = clip_value(e.x(), self.starting_position[0], int((self.widget_width + self.x_offset) + self.padding / 2))

            if self.dragging_min_handle:
                # swap the handles if the min handle is moved past the max handle
                if position > self.max_handle_position:
                    self.dragging_min_handle = False
                    self.dragging_max_handle = True
                    self.max_handle_position = position
                    self._trigger_refresh()
                    self.value_changed.emit()
                    return

                self.min_handle_position = position

            elif self.dragging_max_handle:
                # swap the handles if the max handle is moved past the min handle
                if position < self.min_handle_position:
                    self.dragging_max_handle = False
                    self.dragging_min_handle = True
                    self.min_handle_position = position
                    self._trigger_refresh()
                    self.value_changed.emit()
                    return

                self.max_handle_position = position

            self._trigger_refresh()
            self.value_changed.emit()

    def get_range(self):
        min_distance = self.min_handle_position - self.starting_position[0]
        max_distance = self.max_handle_position - self.starting_position[0]
        absolute_distance = self.ending_position[0] - self.starting_position[0]

        min_val = int(min_distance / (absolute_distance) * self._range[1]) #+ self.low
        max_val = int(max_distance / (absolute_distance) * self._range[1]) #+ self.low + self.handle_width

        # clip values to be within the range this prevents the handles from going out of bounds
        min_val = clip_value(min_val, self.low, self.high)
        max_val = clip_value(max_val, self.low, self.high)

        return min_val, max_val

    def update_values(self, low, high):
        self.min_handle_position = low
        self.max_handle_position = high
        self.low = low
        self.high = high

        self._trigger_refresh()