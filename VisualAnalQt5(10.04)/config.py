import os, math, shutil
from PyQt5.QtWidgets import *#QApplication, QDesktopWidget, QButtonGroup,QMessageBox, QLayout, QMainWindow, \
    #QRadioButton, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QWidget, QGridLayout, QSplitterHandle, QSplitter
from PyQt5 import QtGui
from PyQt5.QtGui import QIcon, QFont, QPen
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import *
import globals

class QLabel_alterada(QLabel):
    clicked=pyqtSignal()

    def mousePressEvent(self, ev):
        self.clicked.emit()
class ConfigWidget(QDialog):
    def __init__(self, parent=None):
        super(ConfigWidget, self).__init__(parent)
        self.main = parent
        self.lineColor = Qt.red
        self.lineWidth = 2
        self.initUI()

    def closeEvent(self, event):
        #reply = QMessageBox.question(self, 'VisualAnal', "Confirm to quit？", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        #if reply == QMessageBox.Yes:
        if 1:
            globals.solidRedPen = QPen(self.lineColor, self.lineWidth, Qt.SolidLine)
            globals.blDrawContrainerFrame = self.saveMode
            event.accept()
        else:
            event.ignore()

    def initUI(self):
        self.title = 'Configuration'
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        self.setWindowFlags(Qt.Dialog)

        screen = QDesktopWidget().availableGeometry()
        # self.setMinimumSize(screen.size() * 0.8)
        # print(screen)

        self.width = 8 * screen.width() / 28  # 400
        self.height = screen.height() / 8  # 140
        self.left = screen.center().x() - self.width / 2
        self.top = screen.center().y() - self.height / 2

        scr = QApplication.primaryScreen()
        scalingFactor = scr.logicalDotsPerInch() / 96

        scaleW = screen.width() / 1920
        scaleH = screen.height() / 1080
        mainWid = self.width
        mainHei = self.height
        mainWid /= scaleW
        mainHei /= scaleH
        self.setWindowTitle(self.title)
        self.setGeometry(int(self.left), int(self.top), int(mainWid), int(mainHei))

        self.setMinimumSize(int(mainWid), int(mainHei))

        grid = QGridLayout()
        grid.addWidget(self.createSettingGroup1(scalingFactor), 0, 0)
        grid.addWidget(self.createSettingGroup2(scalingFactor), 0, 1)

        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 3)
        self.setLayout(grid)
    def lnWidthChange(self):
        self.lineWidth = self.spin1.value()

        return self.lineWidth

    def lnColorChange(self):
        color = QColorDialog.getColor()

        msgString = "QLabel { background-color : %s; }"%(color.name())
        self.btnColor.setStyleSheet(msgString)
        self.lineColor = color

    def createSettingGroup1(self, scalingFactor):
        groupBox = QGroupBox("Drawing")
        groupBox.setFont(QtGui.QFont('Arial font', int(10 / scalingFactor)))

        hbox1 = QHBoxLayout()
        labl1 = QLabel("Line width")
        labl1.setFont(QtGui.QFont('Arial font', int(10 / scalingFactor)))
        self.spin1 = QSpinBox()
        self.spin1.setMinimum(1)
        self.spin1.setMaximum(5)
        self.spin1.setValue(2)
        self.spin1.valueChanged.connect(self.lnWidthChange)
        self.spin1.setFont(QtGui.QFont('Arial font', int(10 / scalingFactor)))
        hbox1.addWidget(labl1)
        hbox1.addWidget(self.spin1)
        hbox1.setStretchFactor(labl1, 2)
        hbox1.setStretchFactor(self.spin1, 1)

        hbox2 = QHBoxLayout()
        labl2 = QLabel("Line color")
        labl2.setFont(QtGui.QFont('Arial font', int(10 / scalingFactor)))
        self.btnColor = QLabel_alterada()
#        btnColor.setAutoFillBackground(True)
        self.btnColor.setStyleSheet("QLabel { background-color : red; }")
        self.btnColor.clicked.connect(self.lnColorChange)

        hbox2.addWidget(labl2)
        hbox2.addWidget(self.btnColor)

        hbox2.setStretchFactor(labl2, 2)
        hbox2.setStretchFactor(self.btnColor, 1)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addStretch(1)
        groupBox.setLayout(vbox)

        return groupBox

    def selectedContainerWithFrame(self, selected):
        if selected:
            self.saveMode = 1
    def selectedContainerWoutFrame(self, selected):
        if selected:
            self.saveMode = 0
    def createSettingGroup2(self, scalingFactor):
        groupBox = QGroupBox("Saving")
        groupBox.setFont(QtGui.QFont('Arial font', int(10 / scalingFactor)))
        self.group = QButtonGroup()

        radio1 = QRadioButton("container w/o frame")
        radio2 = QRadioButton("container with frame")
        radio1.setFont(QtGui.QFont('Arial font', int(10 / scalingFactor)))
        radio2.setFont(QtGui.QFont('Arial font', int(10 / scalingFactor)))
        radio1.toggled.connect(self.selectedContainerWoutFrame)
        radio2.toggled.connect(self.selectedContainerWithFrame)
        self.group.addButton(radio1)
        self.group.addButton(radio2)
        self.group.buttonClicked.connect(self.check_button)  # +++

        radio1.setChecked(True)

        hbox1 = QHBoxLayout()
        hbox2 = QHBoxLayout()
        labl1 = QLabel("patches in")
        labl2 = QLabel("best in")
        labl1.setFont(QtGui.QFont('Arial font', int(10 / scalingFactor)))
        labl2.setFont(QtGui.QFont('Arial font', int(10 / scalingFactor)))
        self.edPath1 = QLineEdit(globals.savePatchPath)
        self.edPath1.setReadOnly(True)
        self.edPath1.setFont(QtGui.QFont('Arial font', int(10 / scalingFactor)))

        self.edPath2 = QLineEdit(globals.saveBestPath)
        self.edPath2.setReadOnly(True)
        self.edPath2.setFont(QtGui.QFont('Arial font', int(10 / scalingFactor)))

        self.btnBrowse1 = QPushButton("...")
        self.btnBrowse1.clicked.connect(self.changeSavingPatchFolder)
        self.btnBrowse1.setFont(QtGui.QFont('Arial font', int(10 / scalingFactor)))

        self.btnBrowse2 = QPushButton("...")
        self.btnBrowse2.clicked.connect(self.changeSavingBestFolder)
        self.btnBrowse2.setFont(QtGui.QFont('Arial font', int(10 / scalingFactor)))
        hbox1.addWidget(labl1)
        hbox1.addWidget(self.edPath1)
        hbox1.addWidget(self.btnBrowse1)
        hbox1.setStretchFactor(labl1, 2)
        hbox1.setStretchFactor(self.edPath1, 6)
        hbox1.setStretchFactor(self.btnBrowse1, 1)

        hbox2.addWidget(labl2)
        hbox2.addWidget(self.edPath2)
        hbox2.addWidget(self.btnBrowse2)
        hbox2.setStretchFactor(labl2, 2)
        hbox2.setStretchFactor(self.edPath2, 6)
        hbox2.setStretchFactor(self.btnBrowse2, 1)
        # self.edPath.setFixedHeight(16)
        # #self.edPath.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        vbox = QVBoxLayout()
        vbox.addWidget(radio1)
        vbox.addWidget(radio2)
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addStretch(1)
        groupBox.setLayout(vbox)

        return groupBox
    def changeSavingPatchFolder(self):
        directory = QFileDialog.getExistingDirectory(None, "Select directory", globals.savePatchPath)
        if directory == "":
            return
        self.edPath1.setText(directory)
        globals.savePatchPath = directory

    def changeSavingBestFolder(self):
        directory = QFileDialog.getExistingDirectory(None, "Select directory", globals.saveBestPath)
        if directory == "":
            return
        self.edPath2.setText(directory)
        globals.saveBestPath = directory

    def check_button(self, radioButton):
        #print(radioButton.text())
        return

