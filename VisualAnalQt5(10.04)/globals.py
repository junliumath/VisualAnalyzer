import os
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon, QFont, QPen
BEST_DIR_LABEL = 'best'

solidRedPen = QPen(Qt.red, 2, Qt.SolidLine)
blDrawContrainerFrame = 0
savePatchPath = os.path.join(os.getcwd(), "saved")
saveBestPath = os.path.join(os.getcwd(), BEST_DIR_LABEL)