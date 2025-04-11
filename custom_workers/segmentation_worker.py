from PyQt5.QtCore import  QThread, pyqtSignal,pyqtSlot
from PyQt5.QtGui import QImage
import cv2 as cv
from utils import qimage_to_cv_image,cv_image_to_qimage
import numpy as np

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

        #variables for morphological operations to clean up masks
        self.erode = False
        self.dilate = False
        self.erode_iterations = 1
        self.dilate_iterations = 1
        self.erode_kernel_size = 3
        self.dilate_kernel_size = 3

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

        # apply morphological operations to clean up the mask
        if self.erode:
            kernel = cv.getStructuringElement(cv.MORPH_RECT, (self.erode_kernel_size, self.erode_kernel_size))
            mask = cv.erode(mask, kernel, iterations=self.erode_iterations)
        
        if self.dilate:
            kernel = cv.getStructuringElement(cv.MORPH_RECT, (self.dilate_kernel_size, self.dilate_kernel_size))
            mask = cv.dilate(mask, kernel, iterations=self.dilate_iterations)
        
        # convert the mask to 3 channels
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

        if self.erode:
            kernel = np.ones((self.erode_kernel_size, self.erode_kernel_size), np.uint8)
            mask = cv.erode(mask, kernel, iterations=self.erode_iterations)

        if self.dilate:
            kernel = cv.getStructuringElement(cv.MORPH_RECT, (self.dilate_kernel_size, self.dilate_kernel_size))
            mask = cv.dilate(mask, kernel, iterations=self.dilate_iterations)

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