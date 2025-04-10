
from PyQt5.QtCore import QThread, pyqtSignal,QTimer
from utils import get_colors_and_componets

class  ColorSpaceWorker(QThread):
    #signal to update the plot contains  each channles noramilized values and the combines colors
    update_signal = pyqtSignal(object,object,object,object)
    
    def __init__(self, plot,parent=None,time_interval=1000,color_space='RGB',c1_range = (0,256),c2_range = (0,256),c3_range = (0,256)):
        super().__init__(parent)

        self.plot = plot
        self.c1_range = c1_range
        self.c2_range = c2_range
        self.c3_range = c3_range
        self.time_interval = time_interval
        self.color_space = color_space

        self.update_signal.connect(self.plot.update_plot)

    def run(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(self.time_interval)
        self.exec_()

    def update_plot(self):
        c1,c2,c3,colors = get_colors_and_componets(color_space=self.color_space,
                                                   c1_range=self.c1_range,
                                                   c2_range=self.c2_range,
                                                   c3_range=self.c3_range)
        
        self.update_signal.emit(c1,c2,c3,colors)

    def stop(self):
        self.wait()