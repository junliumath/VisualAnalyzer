import sys
import os, math, shutil
from PyQt5.QtWidgets import *#QApplication, QDesktopWidget, QButtonGroup,QMessageBox, QLayout, QMainWindow, \
    #QRadioButton, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QWidget, QGridLayout, QSplitterHandle, QSplitter
from PyQt5 import QtGui
from PyQt5.QtGui import QIcon, QFont, QPen
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import *
from imageLabel import ImageLabel
from random import sample 
import globals
import datetime

count_anals = 6 #number of opposite
LOG_FILE = 'best_log.txt'
def fprintf(stream, format_spec, *args):
    stream.write(format_spec % args)
def swapPositions(list, pos1, pos2): 
  
    # Storing the two elements 
    # as a pair in a tuple variable get 
    get = list[pos1], list[pos2] 
    
    # unpacking those elements 
    list[pos2], list[pos1] = get 
    
    return list
class SplitterHandle(QSplitterHandle):
    clicked = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(SplitterHandle, self).__init__(*args, **kwargs)
        # 如果不设置这个，则鼠标只能在按下后移动才能响应mouseMoveEvent
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        super(SplitterHandle, self).mousePressEvent(event)
        if event.pos().y() <= 24:
            # 发送点击信号
            self.clicked.emit()

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        # 当y坐标小于24时,也就是顶部的矩形框高度
        if event.pos().y() <= 24:
            # 取消鼠标样式
            self.unsetCursor()
            event.accept()
        else:
            # 设置默认的鼠标样式并可以移动
            self.setCursor(Qt.SplitHCursor if self.orientation()
                           == Qt.Horizontal else Qt.SplitVCursor)
            super(SplitterHandle, self).mouseMoveEvent(event)

    def paintEvent(self, event):
        # 绘制默认的样式
        super(SplitterHandle, self).paintEvent(event)
        # 绘制顶部扩展按钮
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.setPen(Qt.black)
        # 画矩形
        painter.drawRect(0, 20, 2, self.height()-40)
        # 画三角形
        #painter.setBrush(Qt.red)
        #painter.drawPolygon(QtGui.QPolygonF([
        #    QPointF(0, (24 - 8) / 2),
        #    QPointF(self.width() - 2, 24 / 2),
        #    QPointF(0, (24 + 8) / 2)
        #]))


class Splitter(QSplitter):

    def onClicked(self):
        print('clicked')

    def createHandle(self):
        if self.count() == 1:
            # 这里表示第一个分割条
            handle = SplitterHandle(self.orientation(), self)
            handle.clicked.connect(self.onClicked)
            return handle
        return super(Splitter, self).createHandle()
class Analyzer(QMainWindow):
    itemCnt = 0
    currentIndex = 0
    gt_dir_label = ""
    activeParam = ""

    dirList = []
    paramList = []
    dispLables = []
    paramRadios = []
    szImgsExt = ".jpg"
    blDeployOK = False
    gtFileList = []
    arrIndexProcessed = []
    arrIndexToProcess = []
    arrIndexAlreadyProcessed = []
    #blDrawContrainerFrame = 0
    #solidRedPen = QPen(Qt.red, 2, Qt.SolidLine) #default hightlighting color:red, linewidth:2
    def cacheCurrentShot(self, rtSel2Draw):
        for item in self.dispLables:
            if item.cacheFrameWithShot(rtSel2Draw) == False:
                continue
    def saveCurrentImgs(self, filename): # save ROI and its highlighted image with rectangle frame
        if os.path.isdir(globals.savePatchPath) == False:
            os.makedirs(globals.savePatchPath)
        ext = os.path.splitext(filename)[1]
        if not ext:  # default type of image is jpeg format.
            ext = '.jpg'
            filename = filename + ext
        for item in self.dispLables:
            '''
            i.screenshot: 
            '''
            if item.screenshot == None:
                continue
            #file_predix = '[('+str(i.rtSelectedRegion.left())+','+str(i.rtSelectedRegion.top())+')-'+'('+str(i.rtSelectedRegion.right())+','+str(i.rtSelectedRegion.bottom())+')]'
            file_predix = '[(' + '%.2f'% (item.rtSelectedRegion.left()/item.screenshot.width()) + ',' +'%.2f'% (1 - item.rtSelectedRegion.bottom()/item.screenshot.height()) + ')-' + '(' + \
                          '%.2f'% (item.rtSelectedRegion.right()/item.screenshot.width()) + ',' + '%.2f'% (1 - item.rtSelectedRegion.top()/item.screenshot.height()) + ')]'
            w_filename4Patch = item.paramLabel + '_' + file_predix + '_' + filename
            w_filename4Entire = item.paramLabel + '#' + file_predix + '_' + filename

            w_filename4Patch = os.path.join(globals.savePatchPath, w_filename4Patch)
            w_filename4Entire = os.path.join(globals.savePatchPath, w_filename4Entire)
            
            if item.saveImg(w_filename4Patch, w_filename4Entire) == False:
                continue
    def showSyncView(self, rect):
        for item in self.dispLables:
            #print(len(i.pixList))
            if item.updateView(rect) == False:
                continue
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Backspace:
            # self.dispLables[0].goPrevImage()
            for item in self.dispLables:
                item.goPrevImage()
    def getPrevSituation(self):
        return
    def btnstateRadio(self, b):
        # radioBtn = b.sender()
        # if QRadioButton(radioBtn) != None and radioBtn.isChecked():
        #     self.activeParam = radioBtn.text()
        idx = self.cs_group.id(b)
        self.activeParam = self.paramRadios[idx].text().strip()
        return
    def logging_best(self, blWriteTimestamp = False):
        gtDir = self.dirList[0]
        datadir = os.path.dirname(gtDir)
        
        try:
            file_object = open(os.path.join(os.getcwd(), LOG_FILE), 'at')
        except IOError:
            print('Error: logging best')
            return
        #file_object =  open(os.path.join(datadir, LOG_FILE), 'at', encoding='utf-8')
        if blWriteTimestamp:
            now = datetime.datetime.now()
            timestamp = str(now.strftime("%Y%m%d_%H-%M-%S"))
            fprintf(file_object, "On:%s\t at:%s\t for:%s\n",
                    timestamp, datadir, self.gt_param)
            file_object.close()
            return
        fprintf(file_object, "file:%s\t best:%s\n",
            self.gtFileList[self.arrIndexProcessed[-1]], self.activeParam)
        file_object.close()

        saveImgPathSource = os.path.join(datadir, self.activeParam, 
                self.gtFileList[self.currentIndex])
        if os.path.exists(saveImgPathSource) and os.path.exists(globals.saveBestPath):
            #globals.saveBestPath = os.path.join(datadir, BEST_DIR_LABEL)
            saveImgFileTarget = os.path.join(globals.saveBestPath, self.gtFileList[self.currentIndex])
            if os.path.exists(saveImgFileTarget):
                if os.path.samefile(saveImgPathSource, saveImgFileTarget):
                    return
                os.remove(saveImgFileTarget)
            shutil.copy(saveImgPathSource, globals.saveBestPath)
    def nextSuite(self, b):
        if b:
            idx = self.cs_group.checkedId()
            if idx >= 0 and self.paramRadios[idx].isEnabled() == False:
                return
            if self.currentIndex > -1:
                self.arrIndexProcessed += [self.currentIndex]
                self.logging_best()
                self.arrIndexToProcess.remove(self.currentIndex)
            if len(self.arrIndexToProcess) > 0:
                index = sample(self.arrIndexToProcess, 1)
                self.showImageSuite(index[0])

            else:
                self.currentIndex = -1
                return
            
        else:
            index = sample(self.arrIndexToProcess, 1)
            self.showImageSuite(index[0])
    def msgButtonClick(self):
        return
    def buildGtFileList(self):
        if len(self.dirList) == 0:
            return False
        gtDir = self.dirList[0]
        if os.path.exists(gtDir) == False:
            return False
        self.gtFileList = []
        # for f in os.listdir(gtDir):
        #     if f.endswith(self.szImgsExt):
        #         self.gtFileList += [os.path.join(self.dirList[0], f)]
        self.gtFileList = [each for each in os.listdir(gtDir) if each.endswith(self.szImgsExt)]
        if len(self.gtFileList) == 0:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)

            msg.setText("No files exist in selected directory, or care about the image format.")
            msg.setWindowTitle("warning")
            msg.setStandardButtons(QMessageBox.Ok)
                
            msg.exec_()
            return False
        self.arrIndexToProcess = list(range(len(self.gtFileList)))
        self.arrIndexProcessed = []

        #saveImgPath = os.path.join(os.path.dirname(gtDir), BEST_DIR_LABEL)
        if os.path.isdir(globals.saveBestPath) == False:
            os.makedirs(globals.saveBestPath)
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)

            msg.setText("The repository for best result is already exist")
            msg.setWindowTitle("warning")
            msg.setStandardButtons(QMessageBox.Ok)
                
            # retval = msg.exec_()
        return True
    def showImageSuite(self, index):
        if len(self.gtFileList) <= index:
            return
        self.dispLables[0].set_image(os.path.join(self.dirList[0], self.gtFileList[index]))
        self.lblCurFile.setText(self.gtFileList[index])

        self.currentIndex = index
        for i in range(1, self.itemCnt):
            filePath = os.path.join(self.dirList[i], self.gtFileList[index])
            self.dispLables[i].set_image(filePath)
            bExistFile = os.path.lexists(filePath)
            self.paramRadios[i - 1].setEnabled(bExistFile)
    ################
    ### 
    ### dirList(0) : gt directory name
    #################
    def updateAnalList(self):#prepare directory and file structure
        self.paramList.clear()
        self.itemCnt = 0
        tempParamList = []
        maxLenOfParam = 0
        gt_index = -1
        for item in self.dirList:
            basename = os.path.basename(item)
            if basename == self.gt_dir_label:
                gt_index = self.itemCnt
                self.gt_param = basename
            else:
                tempParamList.append(basename)
                if maxLenOfParam < len(basename):
                    maxLenOfParam = len(basename)
            self.itemCnt = self.itemCnt + 1
        if gt_index == -1:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setText("Please check if you have selected the directory containing ground truth images!")
            msgBox.setWindowTitle("Data error")
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec()
            return False
        for itemParam in tempParamList:
            newItem = itemParam.center(maxLenOfParam, ' ')
            self.paramList.append(newItem)
        swapPositions(self.dirList, 0, gt_index)
        # swapPositions(self.paramList, 0, gt_index)
        return self.buildGtFileList()
    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()
                elif child.layout() is not None:
                    self.clearLayout(child.layout())

    ########################
    #
    #self.itemCnt(total count of items) - 1(subject) =
    #  number of opponents 
    ###########################
    def renewDeploy(self):
        if self.updateAnalList() == False:
            self.blDeployOK = False
            return
        
        count_anals = self.itemCnt - 1

        self.blDeployOK = True
        self.dispLables.clear
        self.paramRadios.clear
        self.dispLables = []
        self.paramRadios = []

        self.clearLayout(self.vlayoutSubj)
        self.clearLayout(self.vlayoutOppo)

        self.cs_group = QButtonGroup(self)

        self.dispLables.append(ImageLabel(self, self.gt_param)) #for groud truth
        for i in range(count_anals):
            paramLabel = self.paramList[i].strip()
            self.dispLables.append(ImageLabel(self, paramLabel))
            self.paramRadios.append(QRadioButton(self))
            self.cs_group.addButton(self.paramRadios[i], i)
        self.cs_group.buttonClicked.connect(self.btnstateRadio)

        self.lblCurFile = QLabel(self)
        self.lblCurFile.setText("")
        self.lblCurFile.setFont(QFont('Arial', 20))
        
        self.btnNext = QPushButton(self)
        self.btnNext.clicked.connect(lambda:self.nextSuite(True))
        self.btnNext.setText("Next")

        self.vlayoutSubj.addWidget(self.lblCurFile)
        self.vlayoutSubj.addWidget(self.dispLables[0])
        self.vlayoutSubj.addWidget(self.btnNext)
        #self.vlayoutSubj.setAlignment(Qt.AlignCenter)

        # set suitable number of columns 
        # we fix the number of rows to be 2.
        num_rows = 1 if count_anals < 4 else 2
        num_cols = math.ceil(count_anals / num_rows)
        
        for r in range(num_rows):
            for c in range(num_cols):
                inx = r * num_cols + c
                if inx < self.itemCnt - 1:
                    self.vlayoutOppo.addWidget(self.dispLables[inx + 1], r * num_rows, c)
                    self.vlayoutOppo.addWidget(self.paramRadios[inx], r * num_rows + 1, c, Qt.AlignJustify)
                    self.vlayoutOppo.setAlignment(Qt.AlignCenter)
                    self.paramRadios[inx].setText(self.paramList[inx] 
                            if inx < self.itemCnt else "")
        self.activeParam = self.gt_param #temporal setting to handle the case of just  one folder.
        if count_anals > 0:
            self.paramRadios[0].setChecked(True)
            self.btnstateRadio(self.paramRadios[0])

        #self.layout.addLayout(self.vlayoutSubj)
        #self.layout.addLayout(self.vlayoutOppo)
        #self.setLayout(self.layout)
        self.logging_best(True)
        self.nextSuite(False)
    def __init__(self, itemList, gt_label, img_ext):
        super().__init__()
        self.penColor = Qt.red
        self.lineWidth = 2
        self.dirList = itemList
        self.gt_dir_label = gt_label
        self.szImgsExt = img_ext

        #self.layout = QHBoxLayout()
        self.vlayoutSubj = QVBoxLayout()
        self.vlayoutOppo = QGridLayout()

        self.renewDeploy()
        self.initUI()

        #updated on 2021/7/2
        splitter = Splitter(self)
        splitter.setHandleWidth(8)
        self.left_widget = QWidget(self)
        self.left_widget.setLayout(self.vlayoutSubj)

        self.right_widget = QWidget(self)
        self.right_widget.setLayout(self.vlayoutOppo)
        splitter.addWidget(self.left_widget)
        splitter.addWidget(self.right_widget)
        # Qt.Vertical 垂直   Qt.Horizontal 水平
        splitter.setOrientation(Qt.Horizontal)
        self.setCentralWidget(splitter)

        #self.solidRedPen = QPen(self.penColor, self.lineWidth, Qt.SolidLine)
    def initUI(self):
        self.setWindowTitle("Analyzer")
        scriptDir = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QtGui.QIcon(scriptDir + os.path.sep + 'icon.png'))

        initWidth = 600
        initHeigh = 450
        screen = QDesktopWidget().screenGeometry()
        # self.setMinimumSize(screen.size() * 0.8)
        size = self.geometry()
        x_center = (screen.width() - size.width()) / 2
        y_center = (screen.height() - size.height()) / 2
        self.move(x_center, y_center)
        initLeft = x_center - initWidth / 2
        initTop = y_center - initHeigh / 2
        self.setGeometry(initLeft, initTop, initWidth, initHeigh)

        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

    def resizeEvent(self, event):
        w = event.size().width()
        h = event.size().height()
        #if len(self.dispLables) > 0:
        #    self.dispLables[0].setFixedWidth(w / 4)

        #if w < self.width or h < self.height:
            #self.setWidth(self.width)
            #self.setHeight(self.height)
        return  
