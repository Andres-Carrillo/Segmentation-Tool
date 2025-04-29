from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui, QtWidgets
from utils import in_bounds, clip_value,in_circle

class Slider(QtWidgets.QWidget):
    value_changed = QtCore.pyqtSignal()

    def __init__(self,parent=None, min_value=0, max_value=100, handle_color=QtGui.QColor('gray'), track_bar_color=QtGui.QColor('red'), background_color=QtGui.QColor('black'),  *args, **kwargs):
        super().__init__(parent=parent,*args, **kwargs)
        self.setMouseTracking(True)

        self._range = (min_value, max_value)
        self.dragging_handle = False    

        self._alignment = 'left'

        self._scale_varaibles(initial=True)        

        self.track_bar_color = track_bar_color
        self.bckgrnd_color = background_color
        self.handle_color = handle_color

        self.cur_value = 0


        self.setSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding
        )

   
    def resizeEvent(self, a0):

        self._scale_varaibles()
        
        return super().resizeEvent(a0)

    def paintEvent(self, e):
        # initialize the painter and brush
        painter = QtGui.QPainter(self)
        brush = QtGui.QBrush()
        brush.setColor(self.bckgrnd_color)
        brush.setStyle(Qt.SolidPattern)
        painter.setBrush(brush)

        # draw the background
        background = QtCore.QRect(self.starting_position[0], self.starting_position[1], self.widget_width, self.widget_height)
        painter.drawRoundedRect(background, 5, 5)

        # draw the filled bar
        painter.setBrush(self.track_bar_color)
        track_bar = QtCore.QRect(self.starting_position[0], self.starting_position[1], int(self.filled_bar_distance + self.handle_width/2), self.widget_height)
        painter.drawRoundedRect(track_bar, 5, 5)

        # set the color for the handle
        painter.setBrush(self.handle_color)

        # draw the handle
        self.hand_rect = QtCore.QRect(self.handle_position, self.starting_position[1], self.handle_width, self.widget_height)
        painter.drawEllipse(self.hand_rect.center(), self.handle_width, self.handle_height)

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

        if in_circle(local_pos.x(), local_pos.y(), self.hand_rect.center().x(),self.hand_rect.center().y(), max(self.handle_width, self.handle_height) ):
            self.dragging_handle = True  # clicked on the max handle

    def mouseReleaseEvent(self, e):
        self.dragging_handle = False

    def mouseMoveEvent(self, e):
        if e.buttons() & QtCore.Qt.LeftButton:
            position = clip_value(e.x(), self.starting_position[0] , int((self.widget_width + self.x_offset )))

            if self.dragging_handle:
                self.handle_position = position
                self.filled_bar_distance = abs(self.handle_position - self.starting_position[0])
                self.cur_value = self.get_value()

            self._trigger_refresh()
            self.value_changed.emit()

    def get_value(self):
        max_distance = self.handle_position - self.starting_position[0]
        absolute_distance = self.ending_position[0] - self.starting_position[0]

        max_val = int(max_distance / (absolute_distance) * self._range[1]) 
        max_val = clip_value(max_val, self._range[0], self._range[1])

        return  max_val
    

    def set_alignment(self, alignment = None):
       
        if alignment is None:
            alignment = self._alignment
        else:
            alignment = alignment.lower()
            self._alignment = alignment
        
        if self._alignment == 'left':
            self.x_offset = 0
            self.y_offset = 0
           
        elif self._alignment == 'center':
            self.x_offset = int(self.rect().width()/5)
            self.y_offset = int(self.rect().height()/2)

        else:
            raise ValueError("Invalid alignment value. Use 'left' or 'center'.")
        
        self._trigger_refresh()

    #calculate the position of the handle based on the value of the slider
    def _calc_handle_position(self):
        pixel_distance = self.ending_position[0] - self.starting_position[0]
        value_range = self._range[1] - self._range[0]
        
        current_percentage = (self.cur_value - self._range[0]) / value_range
        handle_position = int(current_percentage * pixel_distance) + self.starting_position[0]

        clip_value(handle_position, self.starting_position[0], int((self.widget_width + self.x_offset )))

        return handle_position

    def _scale_varaibles(self,initial=False):
        self.set_alignment()

        self.widget_width = int(self.rect().width()/2)
        self.widget_height = int(self.rect().height()/18)

        self.handle_width = int(self.rect().width()/24)
        self.handle_height = self.widget_height

        self.starting_position = (self.handle_width  + self.x_offset,self.handle_height + self.y_offset)
        self.ending_position = (int((self.widget_width * 2) + self.x_offset) ,self.widget_height + self.y_offset)\
        
        self.handle_position = int(self.widget_width) if initial else self._calc_handle_position() 
        
        self.hand_rect = QtCore.QRect(self.handle_position, self.starting_position[1], self.handle_width, self.widget_height)
        
        self.filled_bar_distance = abs(self.hand_rect.center().x() - self.starting_position[0])
        