from PyQt5.QtWidgets import QPushButton, QWidget, QLabel, QComboBox, QFileDialog, QGridLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt5.QtGui import QImage
from PyQt5.QtCore import QThread, pyqtSignal,pyqtSlot
from PyQt5.QtGui import QImage
import cv2 as cv
import time

class VideoWorker(QThread):
    frame_processed = pyqtSignal(QImage)
    finished = pyqtSignal()
    recording = pyqtSignal()
    video_number = 0

    def __init__(self, video_path):
        super().__init__()
        self.reset(video_path,is_live_stream=True)

    def reset(self, video_path,is_live_stream):
        self.is_live_stream = is_live_stream
        self.video_path = video_path
        self.running = False
        self.capture = None
        self.writer = None
        self.color_space = cv.COLOR_BGR2RGB
        self.fps = 60

    def run(self):
        self.running = True
 
        try:
            self.capture = cv.VideoCapture(self.video_path)
            if not self.is_live_stream:
                self.fps = self.capture.get(cv.CAP_PROP_FPS)
            if not self.capture.isOpened():
                raise Exception("Failed to open video source")
        except Exception as e:
            print("caught exception",e)
            self.running = False

        while self.running:
            ret, frame = self.capture.read()
         
            if ret:
                rgb_image = cv.cvtColor(frame, self.color_space)
                h, w, ch = rgb_image.shape

                if(self.writer is not None ):
                    self.writer.write(frame)
                
                bytes_per_line = ch * w
                qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                
                self.frame_processed.emit(qt_image)

                if not self.is_live_stream:
                    time.sleep(1/self.fps)
            else:
                break

        self.capture.release()
        if(self.writer is not None): self.writer.release()
        self.finished.emit()

    def stop(self):
        self.running = False
        self.wait()

    @pyqtSlot()
    def start_recording(self):
        if self.writer is None:
            save_path = str(self.video_path) +'_output_'+ str(VideoWorker.video_number) + '.mp4'
            
            video_shape = (int(self.capture.get(cv.CAP_PROP_FRAME_WIDTH)), int(self.capture.get(cv.CAP_PROP_FRAME_HEIGHT)))
            
            video_fps = self.capture.get(cv.CAP_PROP_FPS)

            self.writer = cv.VideoWriter(save_path, cv.VideoWriter_fourcc(*'mp4v'), video_fps, video_shape)
            
            VideoWorker.video_number += 1
    
    def stop_recording(self):
        if self.writer is not None:
            self.writer.release()
            self.writer = None

    def change_video_source(self, video_path,is_live_stream=False):
        self.stop() 
        
        if(self.capture is not None):
            self.capture.release()
        
        self.reset(video_path,is_live_stream)

class RecordingEmmitter(QObject):
    recording = pyqtSignal()

class NewFrameEmmitter(QObject):
    new_frame = pyqtSignal(QImage)

class VideoWidget(QWidget):
    file_number = 0
   
    def __init__(self,video_path):
        super().__init__()
        self.video_path = video_path
        self.save_path ='video_output_'+ str(VideoWidget.file_number) + '.mp4'
        self.init_ui()
        self.init_worker()

        self.writer = None

        # increment the file number for the next video
        VideoWidget.file_number += 1

        self.record_emitter = RecordingEmmitter()
        self.new_frame_emitter = NewFrameEmmitter()

    def init_ui(self):
        self.image_label = QLabel()
        # self.image_label.setFixedSize(640, 480)
        self.play_button =  QPushButton("Play",clicked=self.toggle_play)
        self.recorder_button = QPushButton("Record",clicked=self.toggle_record)

        self.video_source = QComboBox()
        self.video_source.addItem("Camera")
        self.video_source.addItem("Video File")
        self.video_source.currentIndexChanged.connect(self.change_video_source)

        self.image_label.setAlignment(Qt.AlignCenter)
        main_layout = QGridLayout()
    
        main_layout.addWidget(self.image_label,0,0)
        main_layout.addWidget(self.video_source,1,0)
        main_layout.addWidget(self.play_button,2,0,1,1)
    
        self.setLayout(main_layout)

    def init_worker(self):
        self.thread = QThread()
        self.worker = VideoWorker(self.video_path)
        self.worker.moveToThread(self.thread)
        self.worker.started.connect(self.worker.run)
        self.worker.recording.connect(self.toggle_record)
        self.worker.finished.connect(self.stop_thread)
        self.worker.frame_processed.connect(self.update_frame)
        self.thread.start()
        self.playing = False
        self.recording = False

    def toggle_record(self):
        if self.recording:
            self.recorder_button.setText("Record")
            self.worker.stop_recording()
        else:
            self.recorder_button.setText("Stop Recording")
            self.worker.start_recording()

        self.recording = not self.recording

    def toggle_play(self):
        if self.playing:
            self.worker.stop()
            self.play_button.setText("Play")
        else:
            try:
                self.worker.start()
                self.play_button.setText("Stop")
            except Exception as e:
                print("caught exception",e)

        self.playing = not self.playing
        
    def update_frame(self,image):
        pixmap = QPixmap.fromImage(image)
        self.image_label.setPixmap(pixmap)  
        self.new_frame_emitter.new_frame.emit(image)

    def change_video_source(self,index):
        self.stop_thread()
        if index == 0:
            self.video_path = 0
        else:
            try:
                file_path, _ = QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mov)")
            
                if file_path:
                    self.video_path = file_path
                    self.worker.change_video_source(self.video_path,is_live_stream=False)
                else:
                    raise Exception("Error: Could not open video file")
            except Exception as e:
                    print("caught exception: ",e)
                
    def stop_thread(self):
        self.thread.quit()
        self.thread.wait()
        self.play_button.setText("Play")
        self.playing = False

    def closeEvent(self, event):
        self.worker.stop()
        self.thread.quit()
        self.thread.wait()
        event.accept()  