from PyQt5 import QtWidgets, QtCore, QtGui, Qt
from PyQt5.Qt import QImageReader
from PyQt5.QtWidgets import QLabel, QMainWindow,QScrollArea
from PyQt5.QtGui import QPixmap, QPen
from PyQt5.QtCore import Qt, QPoint, QRect
import os
import anal 
import globals

class ImageLabel(QMainWindow):
    scaleFactor = 1
    
    def __init__(self, parendWidget, paramLabel):
        super().__init__()

        self.pixList = []
        self.paramLabel = paramLabel
        #setBackgroundRole(QPalette::Base)
        self.initUI()
        self.parentAnal = parendWidget
        p = self.palette()
        p.setColor(self.backgroundRole(), QtCore.Qt.red)
        self.imageLabel.setPalette(p)

        self.imageLabel.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)

        self.scrollArea.setBackgroundRole(QtGui.QPalette.Dark)
        self.scrollArea.setWidget(self.imageLabel)
        self.scrollArea.setVisible(False)
        self.setCentralWidget(self.scrollArea)

        self.dragging = False
        self.pressedLButton = False
        self.lastPoint = QPoint()
        self.rtSelectedRegion = QRect()
        self.popMenu = QtWidgets.QMenu(self)
        act = QtWidgets.QAction('save as', self)
        act.triggered.connect(self.onImaSaveAs)
        act = self.popMenu.addAction(act)

        self.screenshot = None
        #self.popMenu.addSeparator()
        #self.popMenu.addAction(QtWidgets.QAction('test2', self))        
    def onImaSaveAs(self):
        #    print(file)
        text, ok = QtWidgets.QInputDialog.getText(self, 'Input file name', 'Enter file name:')
		
        if ok:
            self.parentAnal.saveCurrentImgs(str(text))
            #print("saved roi regions and those ancestral frameworks.")
            print("saved roi regions and those containers.")
    def saveImg(self, filename1, filename2):
        """
        ext = os.path.splitext(filename1)[1]
        if not ext: #default type of image is jpeg format.
            ext = '.jpg'
            filename1 = filename1 + ext
            filename2 = filename2 + ext
        """
        if self._displayed_pixmap is not None and not self._displayed_pixmap.isNull():
            self._displayed_pixmap.save(filename1)
            if self.screenshot is not None and not self.screenshot.isNull():
                self.screenshot.save(filename2)
                return True
        return False
    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            if event.button() == Qt.LeftButton:
                print(obj.objectName(), "Left click")
            elif event.button() == Qt.RightButton:
                print(obj.objectName(), "Right click")
            elif event.button() == Qt.MiddleButton:
                print(obj.objectName(), "Middle click")
            return self.event(obj, event)
    def initUI(self):    
        self.imageLabel = QLabel(self)
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(1)
        self._displayed_pixmap = QPixmap("")
        self.screen = QtWidgets.QApplication.primaryScreen()

    '''
    def on_mouse(self, event, x, y, flags, param):
        pt = (x, y)
        if event == cv2.EVENT_LBUTTONDOWN:
            self.prev_pt = pt
        elif event == cv2.EVENT_LBUTTONUP:
            self.prev_pt = None

        if self.prev_pt and flags & cv2.EVENT_FLAG_LBUTTON:
            for dst, color in zip(self.dests, self.colors_func()):
                cv2.line(dst, self.prev_pt, pt, color, 5)
            self.dirty = True
            self.prev_pt = pt
            self.show()
    '''
    def loadFile(self, stringFile):
        reader = QtGui.QImageReader(stringFile)
        reader.setAutoTransform(True)
        newImage = reader.read()

        if (newImage.isNull()):
            return False
        return True
    def adjustScrollBar(self, scrollBar, factor):
        scrollBar.setValue(int(factor * scrollBar.value()
                            + ((factor - 1) * scrollBar.pageStep()/2)))
    def adjustScrollBar(self, scrollBar, factor):
        return
    def set_image(self, image):
        # No need to check image (path of image file)
        qimg = QPixmap(image, "1") # I am not sure why the second parameter is needed, but otherwise, fail to load 
        self.pixList.clear()
        self.pixList.append(qimg)
        self._displayed_pixmap = qimg
        self.screenshot = None
        self.update()

    def zoom_image(self):
        image_size = self._displayed_pixmap.size()
        image_size.setWidth(image_size.width() * 0.9)
        image_size.setHeight(image_size.height() * 0.9)
        self._displayed_pixmap = self._displayed_pixmap.scaled(image_size, QtCore.Qt.KeepAspectRatio)
        self.update()  # call paintEvent()
    def mousePressEvent(self, event):
        #print("mousePressEvent")

        if event.button() == Qt.LeftButton and self.rtShown.contains(event.pos()):
            self.pressedLButton = True
            self.lastPoint = event.pos()
            x = self.lastPoint.x()
            y = self.lastPoint.y()

            self.setMouseTracking(True)
            self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
    def checkRect(self, rect):
        return
    def goPrevImage(self):
        if len(self.pixList) > 1:
            self._displayed_pixmap = self.pixList.pop()
            self.update()
    def updateView(self, rect):
        if self._displayed_pixmap.isNull():
            return False
        self.pixList.append(self._displayed_pixmap)

        curPix = self._displayed_pixmap.copy(rect)
        self._displayed_pixmap = curPix
        self.update()
        return True
    def cacheFrameWithShot(self, rtSel2Draw):
        #draw highlighted patch region with red line
        if self._displayed_pixmap is None or self._displayed_pixmap.isNull():
            return False
        self.screenshot = self._displayed_pixmap.copy(self._displayed_pixmap.rect())
        if globals.blDrawContrainerFrame:
            painter = QtGui.QPainter(self.screenshot)
            painter.setPen(globals.solidRedPen)
            painter.drawRect(rtSel2Draw)#rtSel mappedRect
            painter.end()
        self.rtSelectedRegion = rtSel2Draw
        return True
    def mouseReleaseEvent(self, event):
        #print("mouseReleaseEvent")

        if event.button() == Qt.RightButton:
            self.popMenu.exec_(QtGui.QCursor.pos()) 
        if event.button() == Qt.LeftButton and self.pressedLButton and self.dragging:
            self.dragging = False
            self.checkRect(self.rtSelectedRegion)

            painter = QtGui.QPainter(self._displayed_pixmap)
            tr = QtGui.QTransform()

            tr.scale(self._displayed_pixmap.width()/self.rtShown.width(), 
                    self._displayed_pixmap.height()/self.rtShown.height())
            
            rectWid = self.rtSelectedRegion.width()
            rectHei = self.rtSelectedRegion.height()
            self.rtSelectedRegion.setLeft(self.rtSelectedRegion.left() - self.rtShown.left())
            self.rtSelectedRegion.setTop(self.rtSelectedRegion.top() - self.rtShown.top())
            self.rtSelectedRegion.setWidth(rectWid)
            self.rtSelectedRegion.setHeight(rectHei)
            mappedRect = tr.mapRect(self.rtSelectedRegion)
            
            self.parentAnal.cacheCurrentShot(mappedRect)
            self.parentAnal.showSyncView(mappedRect)

            self.setMouseTracking(False)
            self.update()
            painter.end()
        if event.button() == Qt.LeftButton:
            self.pressedLButton = False
            self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))

    def mouseMoveEvent(self, event):
        if event.buttons()==Qt.LeftButton and self.pressedLButton and self.rtShown.contains(event.pos()):
            # painter = QtGui.QPainter(self._displayed_pixmap)
            self.dragging = True
            rectangle = QRect(self.lastPoint.x(), self.lastPoint.y(), 
                            event.pos().x() - self.lastPoint.x(), event.pos().y() - self.lastPoint.y())
            self.rtSelectedRegion = rectangle
            self.update()

    def dragEnterEvent(self, event):
        event.acceptProposedAction()
    def wheelEvent(self, event):
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        # if modifiers == QtCore.Qt.ControlModifier:
        #     self._zoom_image(event.angleDelta().y())

    def paintEvent(self, paint_event):
        canvasRect = self.rect()
        #(canvasRect.left(), canvasRect.top(), canvasRect.width(), canvasRect.height())

        width = self._displayed_pixmap.width()
        extrax = canvasRect.width() - width
        if extrax < 0:
            extrax = 0
        x = int(extrax / 2.)
        height = self._displayed_pixmap.height()
        extray = canvasRect.height() - height
        if extray < 0:
            extray = 0
        y = int(extray / 2.)
        target = QRect(x, y, min(canvasRect.width(), width), min(canvasRect.height(), height))
        painter = QtGui.QPainter(self)

        if self._displayed_pixmap is not None and not self._displayed_pixmap.isNull():
            drawRt = self.rect()
            imgSize = self._displayed_pixmap.size()
            imgAspectRatio = imgSize.width() / imgSize.height()
            if ((drawRt.height() * imgAspectRatio) > drawRt.width()): #ideal width is small than real widget size
                #horizontal direction is first
                drawWid = drawRt.width()
                drawHei = drawWid / imgAspectRatio
                drawRt.setTop(drawRt.height() / 2 - drawHei / 2)
                drawRt.setHeight(int(drawHei))
            else:
                #vertical direction is first
                drawHei = drawRt.height()
                drawWid = drawHei * imgAspectRatio
                drawRt.setLeft(drawRt.width() / 2 - drawWid / 2)
                drawRt.setWidth(int(drawWid))
            painter.drawPixmap(drawRt, self._displayed_pixmap)
            self.rtShown = drawRt

        if self.dragging:
            painter.setPen(globals.solidRedPen)
            painter.drawRect(self.rtSelectedRegion)
        painter.end()
