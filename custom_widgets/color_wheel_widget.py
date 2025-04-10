from PyQt5.QtWidgets import ( QWidget,QVBoxLayout,QStackedLayout)
from PyQt5 import QtWidgets
from custom_workers.color_space_worker import ColorSpaceWorker
from utils import get_colors_and_componets
from custom_widgets.range_widget import RangeSlider
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class ColorSpacePlot(FigureCanvasQTAgg):

    def __init__(self, parent=None,dpi=100,color_space='RGB',c1_range = (0,256),c2_range = (0,256),c3_range = (0,256)):
        self.running = True
        fig = Figure( dpi=dpi)
        self.ax = fig.add_subplot(111, projection='3d')
        self.angle = 0
        
        # get colors and components
        c1,c2,c3,colors = get_colors_and_componets(color_space,c1_range,c2_range,c3_range)
        
        # Create 3D plot
        self.ax.scatter(c1, c2, c3, c=colors, marker='o')
        
        # Set labels
        self.ax.set_axis_off()
        self.ax.set_facecolor("None")
        self.ax.disable_mouse_rotation()
        self.ax.set_box_aspect([1,1,1])
        fig.set_facecolor("None")

        super().__init__(fig)

        self.setParent(parent) 
        
        self.setSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding
        )

    def update_plot(self,c1,c2,c3,colors):
            self.ax.cla()
            self.ax.scatter(c1,c2, c3, c=colors, marker='o')
            self.ax.set_axis_off()
            self.ax.set_box_aspect([1,1,1])
            self.ax.set_facecolor("None")

            eval,azim,roll = self._calc_rotation()
            self.ax.view_init(elev=eval, azim=azim, roll=roll)
            
            self.draw()

    def _tick(self):
        self.angle += 1
        if self.angle > 360:
            self.angle = 0

    def _calc_rotation(self):
        self._tick()

        normal = (self.angle + 180) % 360 - 180

        eval = azim = roll = normal

        return eval,azim,roll

class ColorSpaceWidget(QWidget):
    def __init__(self, parent =None):
        super().__init__(parent)
        self.plot = ColorSpacePlot(parent=self)
        self._init_worker()
            
        self.first_channel_slider = RangeSlider(min_value=0, max_value=255,parent=self)
        self.second_channel_slider = RangeSlider(min_value=0, max_value=255,parent=self)
        self.third_channel_slider = RangeSlider(min_value=0, max_value=255,parent=self)

        self._set_slider_titles("RGB")
        self._init_layout()
        self._init_events()

        self.setSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding
        )

    def _init_worker(self):
        self.plot_thread = ColorSpaceWorker(self.plot,parent=self,time_interval=100)
        self.plot_thread.start()
        self.color_space = self.plot_thread.color_space

    def _init_layout(self):
        # stacked layout
        # to hold the plot and the sliders
        stack = QStackedLayout()
        
        #layout for the sliders
        options_layout = QVBoxLayout()

        # widget to hold the sliders
        # this is needed to since stacked layout only works with widgets
        slider_widget = QWidget()
        
        #layout for the sliders
        options_layout.addWidget(self.first_channel_slider)
        options_layout.addWidget(self.second_channel_slider)
        options_layout.addWidget(self.third_channel_slider)
        
        #set the layout for the slider widget
        # which contains the sliders
        slider_widget.setLayout(options_layout)
        
        # set stack mode so that all widgets are shown at once
        stack.setStackingMode(QStackedLayout.StackAll)
        
        # add the plot and the sliders to the stack
        stack.addWidget(self.plot)
        stack.addWidget(slider_widget)

        # set the size constraint for the stack
        stack.setSizeConstraint(QStackedLayout.SetMinimumSize)

        # set the layout for the widget
        self.setLayout(stack)

    def _init_events(self):
        self.first_channel_slider.value_changed.connect(self.update_plot)
        self.second_channel_slider.value_changed.connect(self.update_plot)
        self.third_channel_slider.value_changed.connect(self.update_plot)
    
    def _set_slider_titles(self,color_space):
        if color_space == "RGB":
            self.first_channel_slider.title = "Red"
            self.second_channel_slider.title = "Green"
            self.third_channel_slider.title = "Blue"
        elif color_space == "LAB":
            self.first_channel_slider.title = "Luma"
            self.second_channel_slider.title = "Red-Green"
            self.third_channel_slider.title = "Blue-Yellow"
        elif color_space == "HSV":
            self.first_channel_slider.title = "Hue"
            self.second_channel_slider.title = "Saturation"
            self.third_channel_slider.title = "Value"
        elif color_space == "YCrCb":
            self.first_channel_slider.title = "Luma"
            self.second_channel_slider.title = "Blue Diff."
            self.third_channel_slider.title = "Red Diff."
        elif color_space == "YUV":
            self.first_channel_slider.title = "Luma"
            self.second_channel_slider.title = "Red prjct."
            self.third_channel_slider.title = "Blue prjct."
        elif color_space == "LUV":
            self.first_channel_slider.title = "Luma"
            self.second_channel_slider.title = "Green-Red"
            self.third_channel_slider.title = "Blue-Yellow"
        else:
            print("Color space not supported")

    def update_plot(self):
        self.plot_thread.c1_range = self.first_channel_slider.get_range()
        self.plot_thread.c2_range = self.second_channel_slider.get_range()
        self.plot_thread.c3_range = self.third_channel_slider.get_range()

        self.update()

    def change_color_space(self,color_space):
        self.plot_thread.color_space = color_space
        self._set_slider_titles(color_space)
        self.update_plot()
        self.update()