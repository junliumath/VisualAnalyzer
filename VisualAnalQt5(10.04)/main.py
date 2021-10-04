import sys, os
from PyQt5 import QtGui, QtCore
from anal import Analyzer
from config import ConfigWidget
from PyQt5.QtWidgets import QSizePolicy, QTextEdit, QAbstractItemView, QButtonGroup, QRadioButton, QListWidgetItem, QDesktopWidget, QMainWindow, QDialog,QComboBox, QListView, QTreeView, QAbstractItemView, QFileDialog, QListWidget,QApplication, QLabel,  QPushButton,  QLineEdit, QMessageBox
from PyQt5.QtGui import QIcon, QPen
from PyQt5.QtCore import pyqtSlot, Qt

class MyMessageBox(QMessageBox):
    def __init__(self):
        QMessageBox.__init__(self)
        self.setSizeGripEnabled(True)

    def event(self, e):
        result = QMessageBox.event(self, e)

        self.setMinimumHeight(0)
        self.setMaximumHeight(16777215)
        self.setMinimumWidth(0)
        self.setMaximumWidth(16777215)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        textEdit = self.findChild(QTextEdit)
        if textEdit != None :
            textEdit.setMinimumHeight(0)
            textEdit.setMaximumHeight(16777215)
            textEdit.setMinimumWidth(0)
            textEdit.setMaximumWidth(16777215)
            textEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        return result
def showAbout():
    msg = MyMessageBox()
    msg.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint);
    msg.setIcon(QMessageBox.Information)
    msg.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding);
    msg.setText("VisualAnalyzer is a light assistant tool for image processing researchers.")
    msg.setInformativeText("This program is copyright of Kyongson Jon & Jun Liu (2021). All rights reserved.")
    msg.setWindowTitle("About VisualAnalyzer")
    msg.setDetailedText("VisualAnalyzer is able to kindly analyze the different suites of resultant images, "+"by zooming-in, comparing, saving the ROI and its container with/without frame.\n"
                        "The images to be analyzed are assumed to:\n"
                        "1) be of equal size (e.g., 256x256, 1024x968, ...), \n"
                        "2) have identical filename as of other directories. \n "
                        "Steps to use this program: \n"
                        "1) Select several directories in which contains some images to analyze. \n"
                        "2) Select a base (i.e., a directory of ground-truth images) directory.\n"
                        "3) Click 'Anal' button. When you click 'Next' button, the best candidate is saved in 'best' sub-folder, logging in 'best_log.txt' file.\n"
                        "4) You can select interesting regions and the zoomed-in patches will be shown continuously. Whenever pressing 'backspace' key, the previous state is reverted.\n"
                        "5) It is also possible to save the current patches and those containers with/without highlighted rectangle, by right-clicking in any image region and go through the 'save as' procedure.\n"
                        "6) Customizing the highlighting color and line-width is possible.\n\n"
                        "If you have any trouble using this program, please contact us via quanjx046@nenu.edu.cn or liuj292@nenu.edu.cn."
                        )

    msg.setStandardButtons(QMessageBox.Ok)

    msg.exec_()
class App(QMainWindow):
    dirList = []
    def getExistingDirectory(self):
        dlg = QFileDialog(self)

        dlg.setOption(dlg.DontUseNativeDialog, True)
        dlg.setOption(dlg.HideNameFilterDetails, True)
        dlg.setFileMode(dlg.Directory)
        dlg.setOption(dlg.ShowDirsOnly, True)

        dlg.findChildren(QListView)[0].setSelectionMode(QAbstractItemView.ExtendedSelection)
        dlg.findChildren(QTreeView)[0].setSelectionMode(QAbstractItemView.ExtendedSelection)
        if dlg.exec_() == QDialog.Accepted:
            return dlg.selectedFiles()
        return [str(), ]
    def __init__(self):
        super().__init__()

        self.gtLabel = ""
        self.gtIndexInListView = 0
        self.initUI()
        self.configurer = ConfigWidget(self)
    def event(self, event): 
        if event.type() == QtCore.QEvent.EnterWhatsThisMode:
            showAbout()
        return super(App, self).event(event)
    def initUI(self):
        self.title = 'PyQt5 analyzer'
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        self.setWindowFlags(Qt.Dialog)
        self.setWindowFlags(self.windowFlags() | Qt.WindowContextHelpButtonHint)

        screen = QDesktopWidget().availableGeometry()
        # self.setMinimumSize(screen.size() * 0.8)
        #print(screen)

        self.width = screen.width() / 4#400
        self.height = screen.height() / 2#140
        self.left = screen.center().x() - self.width / 2
        self.top = screen.center().y() - self.height / 2

        scr = QApplication.primaryScreen()
        scalingFactor = scr.logicalDotsPerInch() / 96

        scaleW = screen.width() / 1920
        scaleH = screen.height() / 1080
        mainWid = screen.width() / 4
        mainHei = screen.height() / 2
        mainWid /= scaleW
        mainHei /= scaleH
        self.setWindowTitle(self.title)
        self.setGeometry(int(self.left), int(self.top), int(mainWid), int(mainHei))

        self.setMinimumSize(int(mainWid), int(mainHei))
        self.childW = None

        self.label1 = QLabel(self)
        self.label1.move(15, int(mainHei / 20))
        self.label1.resize(int(mainWid / 4), int(mainHei / 20))

        self.label1.setText("Check gt item.")
        self.label1.setFont(QtGui.QFont('Arial font', int(10 / scalingFactor)))
        # Create textbox
        # self.textbox = QLineEdit(self)
        # self.textbox.move(50, 20)
        # self.textbox.resize(30,20)
        
        # Create a button in the window
        self.btnBrowseParent = QPushButton('Image gallery', self)
        self.btnBrowseParent.move(0 + int(mainWid / 4), int(mainHei / 20)) #100
        self.btnBrowseParent.resize(int(mainWid / 4), int(mainHei / 20))#150
        self.btnBrowseParent.setFont(QtGui.QFont('Arial font', int(10 / scalingFactor)))
        self.btnBrowseParent.setToolTip('Select the parent directory contained several image subdirectories(Ctrl+O)')
        self.btnBrowseParent.setShortcut('Ctrl+O')  #shortcut key
        # connect button to function on_click
        self.btnBrowseParent.clicked.connect(self.on_clickBrowse)

        ext_list = ["jpg", "png", "tif", "bmp"] 
        self.combo_ext = QComboBox(self) 
        self.combo_ext.setGeometry(15 + int(mainWid / 4 + mainWid / 4), int(mainHei / 20), int(mainWid / 8), int(mainHei / 20))
        self.combo_ext.addItems(ext_list)
        self.combo_ext.setFont(QtGui.QFont('Arial font', int(10 / scalingFactor)))

        edit1 = QLineEdit(self) 
  
        # setting line edit 
        self.combo_ext.setLineEdit(edit1) 

        self.btnProc = QPushButton('Analyze', self)
        self.btnProc.move(25 + int(mainWid / 4 + mainWid / 4 + mainWid / 8),int(mainHei / 20))
        self.btnProc.resize(int(mainWid / 7), int(mainHei / 20))
        self.btnProc.setFont(QtGui.QFont('Arial font', int(10 / scalingFactor)))

        # connect button to function on_click
        self.btnProc.clicked.connect(self.on_clickAnal)

        self.btnProc = QPushButton('Setting', self)
        self.btnProc.move(35 + int(mainWid / 4 + mainWid / 4 + mainWid / 8 + mainWid / 7),int(mainHei / 20))
        self.btnProc.resize(int(mainWid / 7), int(mainHei / 20))
        self.btnProc.setFont(QtGui.QFont('Arial font', int(10 / scalingFactor)))

        # connect button to function on_click
        self.btnProc.clicked.connect(self.on_clickSetting)

        self.listview = QListWidget(self)
        self.listview.setGeometry(10, 35 + int(mainHei / 20), int(7 * mainWid / 8), int(7 * mainHei / 8))

        self.setFixedSize(self.size())
        self.show()

    @pyqtSlot()
    def onClickedRadio(self):
        b = self.sender()
        if b.isChecked():
            itemTxt = b.text()
            basename = os.path.basename(itemTxt)
            print(basename + ':selected')
            self.gtLabel = basename
        return
    def on_clickBrowse(self):
        # textboxValue = self.textbox.text()
        dirList = self.getExistingDirectory()
        if dirList[0] == str():
            return
        self.listview.clear()

        for i in range(len(dirList)):
            widgetItem = QListWidgetItem(self.listview)
            radioBtn = QRadioButton(dirList[i])
            radioBtn.toggled.connect(self.onClickedRadio)
            radioBtn.setChecked(True if i == 0 else False) 
            self.listview.setItemWidget(widgetItem, radioBtn)
        self.gtIndexInListView = 0
        self.dirList = dirList

    def on_clickSetting(self):
        self.configurer.exec_()
        return
    def on_clickAnal(self):
        if len(self.dirList) == 0:
            return
        szImgExt = self.combo_ext.currentText() 
        if self.childW == None:
            self.childW = Analyzer(self.dirList, self.gtLabel, szImgExt)

        else:
            self.childW.dirList = self.dirList
            self.childW.gt_dir_label = self.gtLabel
            self.childW.szImgsExt = szImgExt
            self.childW.renewDeploy()

        if self.childW.blDeployOK:
            self.childW.setEnabled(True)
            self.childW.show()
        else:
            self.childW.setEnabled(False)

    def closeEvent(self, event):  
        if self.childW:
            self.childW.close()         
    def resizeEvent(self, event):
        w = event.size().width()
        h = event.size().height()
        self.listview.setFixedSize(w - 20, h - 70)
        return
    def showEvent(self, a0: QtGui.QShowEvent) -> None:

        return super().showEvent(a0)
    
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    #app.setAttribute(Qt.AA_EnableHighDpiScaling)
    ex = App()
    sys.exit(app.exec_())
