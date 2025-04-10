import json
from PyQt5.QtCore import  QThread, pyqtSignal, Qt, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap, QColor
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout,QGridLayout,QComboBox,QFileDialog,QPushButton
import cv2 as cv
from utils import qimage_to_cv_image,cv_image_to_qimage
from custom_widgets.color_wheel_widget import ColorSpaceWidget
import numpy as np
from custom_widgets.video_widget import VideoWidget
from custom_widgets.class_list_widget import ClassListWidget

class ImageBlob():
    def __init__(self, image, save_path):
        self.image = image
        self.save_path = save_path

class SegmentationClass():
    def __init__(self, name, color, lower_bound, upper_bound, color_space = cv.COLOR_BGR2RGB):
        self.name = name
        self.color = color
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.color_space = color_space

class SaveImageWorker(QThread):
    saved = pyqtSignal()
    empty_queue = pyqtSignal()
    image_list = []
    stop = False

    def __init__(self,save_path):
        super().__init__()
        self.save_path = save_path
        print("built save image worker")
    
    def run(self):

        while not self.stop and len(self.image_list) > 0:
            image_blob = self.image_list.pop(0)
            self.save(image_blob[0],image_blob[1])
        
        self.saved.emit()

    def save(self,image,save_path):
        cv.imwrite(save_path,image)

    def add_to_save_queue(self,image,file_name):
            cv_image = qimage_to_cv_image(image)

            full_path = self.save_path + "/" + file_name

            self.image_list.append([cv_image,full_path]) 

    @pyqtSlot(QImage,str)
    def add_to_queue(self,image,file_name):
        self.image_list.append(ImageBlob(image,file_name))
            
    @pyqtSlot(str)
    def set_save_path(self,save_path): 
        self.save_path = save_path
    
    def add_to_queue(self,image,file_name):
        self.image_list.append(ImageBlob(image,file_name))

    def stop_thread(self):
        self.data = None
        self.stop = True
        self.wait()

class BaseWorker(QThread):
    processed = pyqtSignal(QImage)

    def __init__(self):
        super().__init__()
        self.data = None

    @pyqtSlot(QImage)
    def process(self,data):

        self.process_data(data)
        
        if self.data is None:
            self.processed.emit(QImage())
        
        else:
            self.processed.emit(self.data)
        
        self.finished.emit()

    def process_data(self, data):
        self.data = data

    def stop_thread(self):
        self.data = None
        self.wait()

class SegmentationWorker(BaseWorker):
    def __init__(self):
        super().__init__()
        self.lower_bound = (0, 0, 0)
        self.upper_bound = (255, 255, 255)
        self.color_space =  cv.COLOR_BGR2RGB
        self.mask = False
        self.saving_masks = False
        self.class_list = []
        self.save_path = None
        self.frame_count = 0
        self.save_worker =  None
        self.binary_mode = True
        self._init_worker()

    def _init_worker(self):
        self.save_thread = QThread()
        self.save_worker = SaveImageWorker(self.save_path)
        self.save_worker.moveToThread(self.save_thread)

    def start_worker(self):
        self.save_thread.start()

    def process_data(self, data):

        if data is None:
            self.processed.emit(QImage())
            self.finished.emit()
        else:
            rgb_image = qimage_to_cv_image(data)
 
            if self.binary_mode:
                output = self.run_binary_mode(rgb_image)
            else:
                output = self.run_overaly_mode(rgb_image)
                    
            data = cv_image_to_qimage(output)

            if self.saving_masks:
                # if in binary mode simply remove the white pixels
                if self.binary_mode:
                    sanatized_data = self._remove_white_pixels(data)
                else:# if in overlay mode need to create a binary mask then remove the white pixels
                    binary_masks = self.run_binary_mode(rgb_image)
                    sanatized_data = self._remove_white_pixels(cv_image_to_qimage(binary_masks))
                
                self.save_worker.add_to_save_queue(sanatized_data, f"frame_{self.frame_count}_masks.png")
                self.frame_count += 1
                self.save_worker.run()

            self.processed.emit(data)
            self.finished.emit()

    def base_segmentation(self, image):
        converted_image = cv.cvtColor(image, self.color_space)    
        mask = cv.inRange(converted_image, self.lower_bound, self.upper_bound)
        mask = cv.merge([mask,mask,mask])
    
        return mask
    
    def run_binary_mode(self,rgb_image):
        mask = self.base_segmentation(rgb_image)

        for segmentation_class in self.class_list:
            self.add_class_mask(segmentation_class,mask,rgb_image)

        return mask
    
    def run_overaly_mode(self,rgb_image):
        rgba_image = cv.cvtColor(rgb_image, cv.COLOR_BGR2BGRA)
        mask = self.base_segmentation(rgb_image)

        rgba_image[mask[:,:,0] == 255] = (255,255,255,150)
        
        for segmentation_class in self.class_list:
            converted_image = cv.cvtColor(rgb_image, segmentation_class.color_space)

            temp_mask = cv.inRange(converted_image, segmentation_class.lower_bound, segmentation_class.upper_bound)
            color = segmentation_class.color.getRgb()[:3]
            rgba_color = (color[0], color[1], color[2], 150)

            rgba_image[temp_mask == 255] = rgba_color
        
        output = cv.cvtColor(rgba_image, cv.COLOR_RGBA2BGR)

        return output
    
    def weighted_mask_segmentation(self, image, lower_bound, upper_bound, color_space):
        if((upper_bound[0] == upper_bound[1]  and upper_bound[1] == upper_bound[2] and upper_bound[2] == 255) and 
           (lower_bound[0] == lower_bound[1] and lower_bound[1] == lower_bound[2] and lower_bound[2] == 0)):
                return image
        
        converted_image = cv.cvtColor(image, color_space)

        mask = cv.inRange(converted_image, lower_bound, upper_bound)
        mask = cv.merge([mask, mask, mask])

        processed_image = cv.addWeighted(image, 0.7, mask, 0.3, 0)

        return processed_image
    
    def add_class_mask(self, segmentation_class,base_mask,rgb_image):
        converted_image = cv.cvtColor(rgb_image, segmentation_class.color_space)

        mask = cv.inRange(converted_image, segmentation_class.lower_bound, segmentation_class.upper_bound)

        base_mask[np.where(mask == 255)] = segmentation_class.color.getRgb()[:3]

        return base_mask

    def create_instance_mask(self, rgb_image):
        """
        Creates an instance mask where each instance is represented by a unique integer value
        In total there can be 225 unique classes, each with at most 255 unique instances
        """
        class_mask = np.zeros((rgb_image.shape[0],rgb_image.shape[1]))
        instance_mask = np.zeros((rgb_image.shape[0],rgb_image.shape[1]))

        for i,segmentation_class in enumerate(self.class_list):
            
            converted_image = cv.cvtColor(rgb_image, segmentation_class.color_space)
            
            threshold_mask = cv.inRange(converted_image, segmentation_class.lower_bound, segmentation_class.upper_bound)
            
            class_mask[np.where(threshold_mask) == 255] = i+1
            
            contours, _ = cv.findContours(threshold_mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

            for j,contour in enumerate(contours):
                temp = np.zeros((rgb_image.shape[0],rgb_image.shape[1]))
                temp = cv.drawContours(temp, [contour], -1, (255, 255, 255), -1)
                points = np.where(temp == 255)

                instance_mask[points] = j+1

        return cv.merge([class_mask,class_mask,instance_mask])
    
    def toggle_saving_mask(self,directory):
        self.saving_masks = not self.saving_masks

        if self.save_worker.save_path == None:
            self.save_worker.save_path = directory
    
    def set_color_space(self, color_space):
        self.color_space = color_space

    def set_bounds(self, lower_bound, upper_bound):
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def set_lower_bound(self, lower_bound):
        self.lower_bound = lower_bound

    def set_upper_bound(self, upper_bound):
        self.upper_bound = upper_bound

    def set_mask(self, mask):
        self.mask = mask

    def _remove_white_pixels(self,image):
        """
        Removes white pixels from the image, this used for saving the image.
        White pixesl represent an unasigned class. So until the user is sure of the class and adds it to the class list
        the white pixels are removed and replaced with black pixels.
        """
        data = image.bits()
        data.setsize(image.byteCount())
        arr = np.array(data).reshape((image.height(), image.width(), 3))

        arr[np.where(arr == 255)] = 0

        return cv_image_to_qimage(arr)

class SegmentationToolWidget(QWidget):

    def __init__(self,parent=None,color_space = 0):
        super().__init__(parent)
        self.color_space = color_space
        self.init_ui()

    def init_ui(self):
        self.color_space = ColorSpaceWidget(parent=self)
        self.color_space.setStyleSheet("background-color: transparent")
            
        tools_layout = QGridLayout()

        tools_layout.addWidget(self.color_space,0,0)

        self.setLayout(tools_layout)

    def change_color_space(self,color_space):
        self.color_space = color_space

        if color_space == 0:
            self.color_space.color_space = "RGB"
            self.worker.color_space = cv.COLOR_BGR2RGB
            self.camera_feed.worker.color_space = cv.COLOR_BGR2RGB
        elif color_space == 1:
            self.color_space.set_color_space("HSV")
            self.worker.color_space = cv.COLOR_BGR2HSV
            self.camera_feed.worker.color_space = cv.COLOR_BGR2HSV
        elif color_space == 2:
            self.color_space.set_color_space("LUV")
            self.worker.color_space = cv.COLOR_BGR2LUV
            self.camera_feed.worker.color_space = cv.COLOR_BGR2LUV
        elif color_space == 3:
            self.color_space.set_color_space("YUV")
            self.worker.color_space = cv.COLOR_BGR2YUV
            self.camera_feed.worker.color_space = cv.COLOR_BGR2YUV
        elif color_space == 4:
            self.color_space.set_color_space("LAB")
            self.worker.color_space = cv.COLOR_BGR2LAB
            self.camera_feed.worker.color_space = cv.COLOR_BGR2LAB
        
        elif color_space == 5:
            self.worker.color_space = cv.COLOR_BGR2YCrCb
            self.camera_feed.worker.color_space = cv.COLOR_BGR2YCrCb 

    def show_binary_mask(self):
        print("Showing binary mask")

class OutputWidget(QWidget):
    def __init__(self,parent):
        super().__init__(parent)
        self.saving_masks = False
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Output Widget")
        
        self.canvas = QPixmap(640, 510)
        self.label = QLabel(parent=self)

        self.canvas.fill(Qt.black)
        self.label.setPixmap(self.canvas)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setScaledContents(True)
        self.mask_mode = QComboBox(self)

        self.mask_mode.addItem("Binary Mask")
        self.mask_mode.addItem("Overlay Mask")

        self.mask_mode.currentIndexChanged.connect(self.parent().toggle_mask_mode)

        self.save_masks = QPushButton("Save Masks",clicked=self.parent().save_mask)

        layout = QGridLayout()
        layout.addWidget(self.label, 0, 0)
        layout.addWidget(self.mask_mode, 1, 0)
        layout.addWidget(self.save_masks, 2, 0)

        self.setLayout(layout)

class SegmentationWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_worker()
        self.init_ui()

    def init_ui(self):
        self.camera_feed = VideoWidget(0)
        self.results_widget = OutputWidget(self)
        container = QGridLayout()
        options_layout = QHBoxLayout()
        layout = QHBoxLayout()

        self.seg_tools = SegmentationToolWidget(parent=self)
        self.class_list_widget = ClassListWidget(parent=self)
        self.color_spaces = QComboBox()

        self.setWindowTitle("Segmentation Widget")
        
        self.camera_feed.image_label.setFixedSize(640, 510)
        self.camera_feed.image_label.setScaledContents(True)
        self.camera_feed.image_label.setStyleSheet("background-color: black")
        self.class_list_widget.setFixedSize(100,600)

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
        
        # connect the camera feed to the process slot
        self.camera_feed.new_frame_emitter.new_frame.connect(self.worker.process)

        # self.
        # self.overlay_mask.stateChanged.connect(self.show_mask_overlay)

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
        
        self.setLayout(layout)
        
        self.setFixedSize(self.minimumWidth(), self.minimumHeight())

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