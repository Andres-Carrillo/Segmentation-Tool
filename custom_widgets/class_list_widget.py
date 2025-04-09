from PyQt5.QtWidgets import (QWidget,  QPushButton,QColorDialog,QInputDialog,QVBoxLayout,QListWidget,QMessageBox)
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5 import QtWidgets
from random import randint

class  ClassListWidget(QWidget):
    class_added = pyqtSignal(str,QColor)
    class_edited = pyqtSignal(str,QColor,int)
    class_removed = pyqtSignal(int)

    def __init__(self,parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.list_widget = QListWidget()
        self.list_widget.setFixedWidth(200)
        self.add_class_button = QPushButton("Add Class")    
        layout.addWidget(self.list_widget)
        layout.addWidget(self.add_class_button)
        self.setLayout(layout)

        self.add_class_button.clicked.connect(self.add_class)
        self.list_widget.itemClicked.connect(self.item_clicked)
        self.list_widget.itemDoubleClicked.connect(self.remove_item)

        self.setSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding
        )

    def add_class(self):
        class_name,_ = QInputDialog.getText(self,"Class Name","Enter Class Name")

        init_color = QColor(randint(0,255),randint(0,255),randint(0,255),175)
        self.list_widget.addItem(class_name)
        self.list_widget.item(self.list_widget.count()-1).setBackground(init_color)
        self.class_added.emit(class_name,init_color)

    def item_clicked(self,i):
        edit_class_name,_ = QInputDialog.getText(self,"Class Name","Enter Class Name")
        
        if edit_class_name:
            i.setText(edit_class_name)
        
        color = QColorDialog.getColor()
        
        if color.isValid():
            i.setBackground(color)

        self.class_edited.emit(edit_class_name,color,self.list_widget.row(i))

    def remove_item(self,i):
        should_remove =QMessageBox(self)
        should_remove.setWindowTitle("Remove Class?")
        should_remove.setText("Are you sure you want to remove this class?")
        should_remove.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        button = should_remove.exec_()

        if button == QMessageBox.Yes:
            self.list_widget.takeItem(self.list_widget.row(i))

        self.class_removed.emit(self.list_widget.row(i))
    
    def import_classes(self,classes):
        self.list_widget.clear()
        for class_name,color in classes:
            item = QtWidgets.QListWidgetItem(class_name)
            item.setBackground(QColor(color))
            self.list_widget.addItem(item)