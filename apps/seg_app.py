import json
from PyQt5.QtCore import  QThread, pyqtSlot,Qt
from PyQt5.QtGui import QImage, QPixmap, QColor
from PyQt5.QtWidgets import QWidget, QHBoxLayout,QGridLayout,QComboBox,QFileDialog,QMainWindow,QAction, QDockWidget
import cv2 as cv
from custom_widgets.output_widget import OutputWidget
from custom_widgets.tools_widget import SegmentationToolWidget
from custom_workers.segmentation_worker import SegmentationClass, SegmentationWorker
from utils import qimage_to_cv_image
from custom_widgets.video_widget import VideoWidget
from custom_widgets.class_list_widget import ClassListWidget
from custom_widgets.morph_transform_widget import MorphTransformWidget
from custom_widgets.contours_widget import ContoursWidget

class SegmentationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_worker()
        self.init_ui()
        self._init_slots()
        self.external_windows = []
        self.morph_widget = None

    def init_ui(self):
        menubar = self.menuBar()
        self.tool_menu = menubar.addMenu("Tools")
        self.camera_feed = VideoWidget(0)
        self.results_widget = OutputWidget(self)
        container = QGridLayout()
        options_layout = QHBoxLayout()
        layout = QHBoxLayout()
        central_widget = QWidget()
        self.contour_widget = None

        self.seg_tools = SegmentationToolWidget(parent=self)
        self.class_list_widget = ClassListWidget(parent=self)
        self.color_spaces = QComboBox()

        self.camera_feed.image_label.setFixedSize(640, 510)
        self.camera_feed.image_label.setScaledContents(True)
        self.camera_feed.image_label.setStyleSheet("background-color: black")
        self.class_list_widget.setFixedSize(100,600)


        # ==================== add items to the color space combo box ========================
        self.color_spaces.addItem("RGB",cv.COLOR_BGR2RGB)
        self.color_spaces.addItem("HSV",cv.COLOR_BGR2HSV)
        self.color_spaces.addItem("LUV",cv.COLOR_BGR2LUV)
        self.color_spaces.addItem("YUV",cv.COLOR_BGR2YUV)
        self.color_spaces.addItem("LAB",cv.COLOR_BGR2LAB)
        self.color_spaces.addItem("YCrCb",cv.COLOR_BGR2YCrCb)

        # ==================== layout ========================
        options_layout.addWidget(self.color_spaces)

        container.addWidget(self.seg_tools,0,0)
        container.addLayout(options_layout,1,0)
        
        layout.addLayout(container)
        layout.addWidget(self.class_list_widget)
        layout.addWidget(self.camera_feed)
        layout.addWidget(self.results_widget)
        
        # self.setLayout(layout)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
        self.setFixedSize(self.minimumWidth(), self.minimumHeight())

    def _init_slots(self):
        self.morph_action = QAction("Morph Transform Tool", self)
        self.contour_action = QAction("Contour Tool", self)
        
        self.setWindowTitle("Segmentation App")
        self.tool_menu.addAction(self.morph_action)
        self.tool_menu.addAction(self.contour_action)
                # ==================== connect signals to slots ========================
            # connect the color space combo box to the change color space slot
        self.color_spaces.currentIndexChanged.connect(self.change_color_space)
        self.seg_tools.color_space.first_channel_slider.value_changed.connect(self.update_bounds)
        self.seg_tools.color_space.second_channel_slider.value_changed.connect(self.update_bounds)
        self.seg_tools.color_space.third_channel_slider.value_changed.connect(self.update_bounds)

        # connect the class list widget to the add segmentation class slot
        self.class_list_widget.class_added.connect(self.add_segmentation_class)
        # connect the class list widget to the edit segmentation class slot
        self.class_list_widget.class_edited.connect(self.edit_segmentation_class)
        # connect the class list widget to the remove segmentation class slot
        self.class_list_widget.class_removed.connect(self.remove_segmentation_class)

        self.morph_action.triggered.connect(self.open_morph_transform_widget)
        self.contour_action.triggered.connect(self.open_contour_widget)

        # connect the camera feed to the process slot
        self.camera_feed.new_frame_emitter.new_frame.connect(self.worker.process)

    def init_tools(self):
        print("init tools")
    
    def init_worker(self):
        self.thread = QThread()
        self.worker = SegmentationWorker()
        self.worker.moveToThread(self.thread)
        self.worker.processed.connect(self.update_image)
        self.thread.start()

    def start_processing(self):
        self.worker.start()

    def change_color_space(self,color_space):
        if color_space == 0:
            self.worker.color_space = cv.COLOR_BGR2RGB 
            self.camera_feed.worker.color_space = cv.COLOR_BGR2RGB
            self.seg_tools.color_space.change_color_space("RGB")
        elif color_space == 1:
            self.worker.color_space = cv.COLOR_BGR2HSV
            self.camera_feed.worker.color_space = cv.COLOR_BGR2HSV
            self.seg_tools.color_space.change_color_space("HSV")
        elif color_space == 2:
            self.worker.color_space = cv.COLOR_BGR2LUV
            self.camera_feed.worker.color_space = cv.COLOR_BGR2LUV
            self.seg_tools.color_space.change_color_space("LUV")
        elif color_space == 3:
            self.worker.color_space = cv.COLOR_BGR2YUV
            self.camera_feed.worker.color_space = cv.COLOR_BGR2YUV
            self.seg_tools.color_space.change_color_space("YUV")
        elif color_space == 4:
            self.worker.color_space = cv.COLOR_BGR2LAB
            self.camera_feed.worker.color_space = cv.COLOR_BGR2LAB
            self.seg_tools.color_space.change_color_space("LAB")
        elif color_space == 5:
            self.worker.color_space = cv.COLOR_BGR2YCrCb
            self.camera_feed.worker.color_space = cv.COLOR_BGR2YCrCb
            self.seg_tools.color_space.change_color_space("YCrCb")

    @pyqtSlot()
    def update_bounds(self):
        top_channel_range = self.seg_tools.color_space.first_channel_slider.get_range()
        second_channel_range = self.seg_tools.color_space.second_channel_slider.get_range()
        third_channel_range = self.seg_tools.color_space.third_channel_slider.get_range()

        self.worker.lower_bound = (top_channel_range[0],second_channel_range[0],third_channel_range[0])
        self.worker.upper_bound = (top_channel_range[1],second_channel_range[1],third_channel_range[1])
    
    def update_ui(self):
            print("Updating UI")

    @pyqtSlot(QImage)
    def update_image(self, image):
        try: 
            qimage_to_cv_image(image)
            pixmap = QPixmap.fromImage(image)
            self.results_widget.label.setPixmap(pixmap)
            self.results_widget.label.setScaledContents(True)
        except Exception as e:
            if image.format() != QImage.Format_Invalid:
                print("Unknown error exception",e)

    @pyqtSlot(str,QColor)
    def add_segmentation_class(self,class_name,color):
        top_channel_range = self.seg_tools.color_space.first_channel_slider.get_range()
        second_channel_range = self.seg_tools.color_space.second_channel_slider.get_range()
        third_channel_range = self.seg_tools.color_space.third_channel_slider.get_range()

        lower_bounds = (top_channel_range[0],second_channel_range[0],third_channel_range[0])
        
        upper_bounds = (top_channel_range[1],second_channel_range[1],third_channel_range[1])
        
        new_class = SegmentationClass(class_name,color,lower_bounds,upper_bounds,self.worker.color_space)
        
        self.worker.class_list.append(new_class)

        if self.results_widget.saving_masks:
            self._save_class_list()
    
    @pyqtSlot(str,QColor,int)
    def edit_segmentation_class(self,class_name,color,index):
        self.worker.class_list[index].name = class_name
        self.worker.class_list[index].color = color

        if self.results_widget.saving_masks:
            self._save_class_list()

    @pyqtSlot(int)
    def remove_segmentation_class(self,index):
        self.worker.class_list.pop(index)

    @pyqtSlot()
    def save_mask(self):
        self.results_widget.saving_masks = not self.results_widget.saving_masks
        if self.results_widget.saving_masks:
            if self.worker.save_worker.save_path is None:
                directory = QFileDialog.getExistingDirectory(self, "Select Save Directory")
                self.worker.toggle_saving_mask(directory)
                self._save_class_list()
        else:
            self.worker.save_worker.stop = True

    @pyqtSlot()
    def toggle_mask_mode(self):
        self.worker.binary_mode = not self.worker.binary_mode


    def _save_class_list(self):
        file_name = "class_lists/classes.json" #QFileDialog.getSaveFileName(self, "Save Class List", "", "JSON Files (*.json)")
        with open(file_name, 'w') as f:
            class_list = []
            for i,segmentation_class in enumerate(self.worker.class_list):
                class_list.append({
                    "name": segmentation_class.name,
                    "id": i,
                    "color_space": segmentation_class.color_space,
                    "color": segmentation_class.color.name(),
                    "lower_bound": segmentation_class.lower_bound,
                    "upper_bound": segmentation_class.upper_bound
                })
            f.write(json.dumps(class_list, indent=4))

        f.close()

    def open_morph_transform_widget(self):
        if self.morph_widget is None:
            dock = QDockWidget("Morph Transform Tool", self)
            self.morph_widget = MorphTransformWidget(parent=dock)

            self.morph_widget.value_changed.connect(self.update_morph_transform)

            self.morph_widget.setFixedSize(600, 600)
            dock.setWidget(self.morph_widget)
            dock.setFloating(True)
            dock.setAttribute(Qt.WA_DeleteOnClose, True)
            dock.show()
            self.external_windows.append(dock)
            self.worker.morphological_operations = True

    def update_morph_transform(self):
        self.worker.morph_type = self.morph_widget.morph_type
        self.worker.dilate_iterations = self.morph_widget.dilate_iterations
        self.worker.erode_iterations = self.morph_widget.erode_iterations
        self.worker.erode_kernel_size = self.morph_widget.erosion_gauge.current_value
        self.worker.dilate_kernel_size = self.morph_widget.dilation_gauge.current_value


    def open_contour_widget(self):
        dock = QDockWidget("Contour Tool", self)
        
        self.contour_widget = ContoursWidget(parent=dock)

        self.contour_widget.value_changed.connect(self.update_contour_settings)

        dock.setWidget(self.contour_widget)
        dock.setFloating(True)
        dock.setAttribute(Qt.WA_DeleteOnClose, True)
        dock.show()
        self.external_windows.append(dock)

        self.contour_worker = self.contour_widget.worker

        self.worker.processed.connect(self.contour_worker.process_data)

        self.contour_widget.start_worker()

    def update_contour_settings(self):
        print("Updating contour settings")
