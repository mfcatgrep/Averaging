# This Python file uses the following encoding: utf-8

import os
import sys
import shutil
from PyQt5 import uic

from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QProgressBar
from PyQt5.QtWidgets import QListView
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtWidgets import QGraphicsPixmapItem
from PyQt5.QtWidgets import QMessageBox

from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtGui import QStandardItem
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QIcon
import Averaging
import tempfile

class Ui(QMainWindow):
    __outputfile="result.png"
    __gvwOutputImage = ""
    __btnLoadImages = ""
    __prgProgress = ""
    __btnAverage = ""
    __btnRemove = ""
    __lvwImages = ""
    __gvwImage = ""
    __btnClear = ""
    __btnSave = ""
    __model = ""

    __imageSelectedHorizontalScrollBar = ""
    __imageOutputHorizontalScrollBar = ""

    __imageSelectedVerticalScrollBar = ""
    __imageOutputVerticalScrollBar = ""

    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi("AveragingQT.ui", self)
        icon=QIcon("Averaging.svg")
        self.setWindowIcon(icon)        
        self.__outputfile = tempfile.gettempdir()+"/result.png"

        self.__gvwOutputImage = self.findChild(QGraphicsView, "gvwOutputImage")
        self.__btnLoadImages = self.findChild(QPushButton, "btnLoadImages")
        self.__prgProgress = self.findChild(QProgressBar, "prgProgress")
        self.__btnAverage = self.findChild(QPushButton, "btnAverage")
        self.__gvwImage = self.findChild(QGraphicsView, "gvwImage")
        self.__btnRemove = self.findChild(QPushButton, "btnRemove")
        self.__btnClear = self.findChild(QPushButton, "btnClear")
        self.__lvwImages = self.findChild(QListView, "lvwImages")
        self.__btnSave = self.findChild(QPushButton, "btnSave")

        self.__imageOutputHorizontalScrollBar = self.__gvwOutputImage.horizontalScrollBar()
        self.__imageOutputVerticalScrollBar = self.__gvwOutputImage.verticalScrollBar()
        self.__imageSelectedHorizontalScrollBar = self.__gvwImage.horizontalScrollBar()
        self.__imageSelectedHorizontalScrollBar.valueChanged.connect(self.outputHorizontalSetBar)
        self.__imageSelectedVerticalScrollBar = self.__gvwImage.verticalScrollBar()
        self.__imageSelectedVerticalScrollBar.valueChanged.connect(self.outputVerticalSetBar)
        self.__imageOutputVerticalScrollBar.valueChanged.connect(self.selectedVerticalSetBar)
        self.__imageOutputHorizontalScrollBar.valueChanged.connect(self.selectedHorizontalSetBar)

        self.__btnLoadImages.clicked.connect(self.getImages)
        self.__btnClear.clicked.connect(self.clearListView)
        self.__btnRemove.clicked.connect(self.removeItem)
        self.__btnAverage.clicked.connect(self.average)
        self.__btnSave.clicked.connect(self.save)

        self.__btnSave.setEnabled(False)

        self.__model = QStandardItemModel()
        self.__lvwImages.setModel(self.__model)
        self.__lvwImages.selectionModel().currentChanged.connect(self.updateImage)

        self.show()

    def getImages(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFiles)
        dialog.setNameFilters(["Images files (*.jpg *.png *.jpeg *.bmp)"])
        dialog.selectNameFilter("Images files (*.jpg *.png *.jpeg *.bmp)")

        if(dialog.exec_()):
            for file in dialog.selectedFiles():
                item = QStandardItem(file)
                self.__model.appendRow(item)

        if self.__model.rowCount() >= 2:
             self.__btnAverage.setEnabled(True)

    def updateImage(self):
        pixmap = QPixmap(self.__lvwImages.currentIndex().data())
        scene = QGraphicsScene(self)
        item = QGraphicsPixmapItem(pixmap)
        scene.addItem(item)
        self.__gvwImage.setScene(scene)

    def clearListView(self):
        self.__model.clear()
        self.__gvwImage.setScene(None)
        self.__btnAverage.setEnabled(False)

    def removeItem(self):
        index = self.__lvwImages.currentIndex()
        if(index.row() != -1):
            self.__gvwImage.setScene(None)
            self.__model.removeRow(index.row())
            if self.__model.rowCount() >= 2:
                self.__btnAverage.setEnabled(True)
            else:
                self.__btnAverage.setEnabled(False)

    def average(self):
        imagelist = list()

        for index in range(self.__model.rowCount()):
            imagelist.append(self.__model.item(index).text())

        if Averaging.run_verification(imagelist) == True:
            self.setEnable(False)
            averageimage = Averaging.run_core(imagelist, self)
            Averaging.outputResult(self.__outputfile, averageimage)
            pixmap = QPixmap(self.__outputfile)
            item = QGraphicsPixmapItem(pixmap)
            scene = QGraphicsScene(self)
            scene.addItem(item)
            it=self.__model.indexFromItem(self.__model.item(0))
            self.__lvwImages.setCurrentIndex(it)
            self.__btnSave.setEnabled(True)
            self.__gvwOutputImage.setScene(scene)
            self.__prgProgress.setValue(0)
            self.setEnable(True)
        else:
            message=QMessageBox()
            message.setIcon(QMessageBox.Critical)
            message.setText("There is a problem with the image stack (images could has differents sizes or differents shapes")
            message.setWindowTitle("Error")
            message.setStandardButtons(QMessageBox.Ok)
            message.exec()

    def showProgress(self,current,total):
        progress=(int) ((current*100)/total)
        self.__prgProgress.setValue(progress)

    def setEnable(self,value):
        self.__btnClear.setEnabled(value)
        self.__btnRemove.setEnabled(value)
        self.__btnLoadImages.setEnabled(value)
        self.__btnAverage.setEnabled(value)
        self.__lvwImages.setEnabled(value)

    def save(self):
        savefile = QFileDialog.getSaveFileName(self,"Save image","","PNG file (*.png)")
        name = os.path.splitext(savefile[0])[0]
        name = name+".png"
        shutil.copyfile(self.__outputfile,name)

    def outputHorizontalSetBar(self):
        value = self.__imageSelectedHorizontalScrollBar.value()
        self.__imageOutputHorizontalScrollBar.setValue(value)

    def selectedHorizontalSetBar(self):
        value = self.__imageOutputHorizontalScrollBar.value()
        self.__imageSelectedHorizontalScrollBar.setValue(value)

    def outputVerticalSetBar(self):
        value = self.__imageSelectedVerticalScrollBar.value()
        self.__imageOutputVerticalScrollBar.setValue(value)

    def selectedVerticalSetBar(self):
        value = self.__imageOutputVerticalScrollBar.value()
        self.__imageSelectedVerticalScrollBar.setValue(value)


if __name__ == "__main__":
        app = QApplication([''])
        mainwindow = Ui()
        sys.exit(app.exec())
