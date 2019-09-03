#!/user/bin/env python3
# -*- coding: utf-8 -*-
# Time : 2019/5/31 16:06
# Author : "YinTao"
# ============== #


from display_image_dialog import DisplayImageDialog
from setting_hs_parameter import Ui_Dialog as Ui_Dialog_hs
from setting_fitting_parameter import Ui_Dialog as Ui_Dialog_fitting
from setting_rgb_parameter import Ui_Dialog as Ui_Dialog_rgb
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from matplotlib import *
import matplotlib
matplotlib.use("Qt5Agg")


class SetHsParameterDialogHsFitting(QDialog, Ui_Dialog_hs):
    hs_paras_signal = pyqtSignal(int, int, int)

    def __init__(self, parent=None):
        super(SetHsParameterDialogHsFitting, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Hyper spectral data parameters")
        self.pushButton.clicked.connect(self.setting)
        self.pushButton_2.clicked.connect(self.resetting)

    def setting(self):
        samples = int(self.lineEdit.text())
        lines = int(self.lineEdit_2.text())
        bands = int(self.lineEdit_3.text())
        self.hs_paras_signal.emit(samples, lines, bands)
        info = QMessageBox()
        info.information(info, "Done", "Setting Done", buttons=QMessageBox.Ok)
        self.hide()

    def resetting(self):
        self.lineEdit.setText("960")
        self.lineEdit_2.setText("1101")
        self.lineEdit_3.setText("176")
        self.setting()


class SetFittingParameterDialog(QDialog, Ui_Dialog_fitting):
    fitting_paras_signal = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super(SetFittingParameterDialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Fitting parameters")
        self.pushButton.clicked.connect(self.setting)
        self.pushButton_2.clicked.connect(self.resetting)

    def setting(self):
        fitting_order = int(self.lineEdit.text())
        fitting_range = int(self.lineEdit_2.text())
        self.fitting_paras_signal.emit(fitting_order, fitting_range)
        info = QMessageBox()
        info.information(info, "Done", "Setting Done", buttons=QMessageBox.Ok)
        self.hide()

    def resetting(self):
        self.lineEdit.setText("4")
        self.lineEdit_2.setText("25")
        self.setting()


class SetRgbParameterDialog(QDialog, Ui_Dialog_rgb):
    rgb_paras_signal = pyqtSignal(int, int, int)

    def __init__(self, parent=None):
        super(SetRgbParameterDialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("RGB parameters")
        self.pushButton.clicked.connect(self.setting)
        self.pushButton_2.clicked.connect(self.resetting)

    def setting(self):
        red = int(self.lineEdit.text())
        green = int(self.lineEdit_2.text())
        blue = int(self.lineEdit_3.text())
        self.rgb_paras_signal.emit(red, green, blue)
        info = QMessageBox()
        info.information(info, "Done", "Setting Done", buttons=QMessageBox.Ok)
        self.hide()

    def resetting(self):
        self.lineEdit.setText("74")
        self.lineEdit_2.setText("50")
        self.lineEdit_3.setText("21")
        self.setting()


class MyWindow(QMainWindow):
    def __init__(self, parent=None):
        # noinspection PyArgumentList
        super(MyWindow, self).__init__(parent)

        # size, title, icon, background color
        self.resize(1600, 800)
        self.setWindowTitle("Hyper Spectral SEMR")
        self.setWindowIcon(QIcon('img/icon.png'))
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setStyleSheet("background-color:white;background-image:url('img/iecas_logo.png');"
                                          "background-position:center;background-repeat:no-repeat;")

        # menus
        self.menu_bar = QMenuBar()
        self.menu_file = QMenu("File")
        self.menu_setting = QMenu("Setting")
        self.action_open_file = QAction("Open File")
        self.action_exit = QAction("Exit")
        self.action_set_hs_paras = QAction("Set Hyper Spectral Parameters")
        self.action_set_fitting_paras = QAction("Set Fitting Parameters")
        self.action_set_rgb_paras = QAction("Set RGB Parameters")
        self.set_menus()

        # child window
        self.image_dialog = DisplayImageDialog()
        self.hs_para_dialog = SetHsParameterDialogHsFitting()
        self.fitting_para_dialog = SetFittingParameterDialog()
        self.rgb_para_dialog = SetRgbParameterDialog()

        # parameters
        self.samples = 960
        self.lines = 1101
        self.bands = 176
        self.fitting_order = 4
        self.fitting_range = 25
        self.red = 74
        self.green = 50
        self.blue = 21

        # signals and slots
        self.action_exit.triggered.connect(self.close)
        self.action_open_file.triggered.connect(self.open_file)
        self.action_set_hs_paras.triggered.connect(self.open_set_hs_paras)
        self.action_set_fitting_paras.triggered.connect(self.open_set_fitting_paras)
        self.action_set_rgb_paras.triggered.connect(self.open_set_rgb_paras)
        self.hs_para_dialog.hs_paras_signal.connect(self.set_hs_paras)
        self.fitting_para_dialog.fitting_paras_signal.connect(self.set_fitting_paras)
        self.rgb_para_dialog.rgb_paras_signal.connect(self.set_rgb_paras)

    def set_menus(self):
        """
        Settings of menu.
        """
        self.setMenuBar(self.menu_bar)
        self.menu_file.addAction(self.action_open_file)
        self.menu_file.addAction(self.action_exit)
        self.menu_setting.addAction(self.action_set_hs_paras)
        self.menu_setting.addAction(self.action_set_fitting_paras)
        self.menu_setting.addAction(self.action_set_rgb_paras)
        self.menu_bar.addMenu(self.menu_file)
        self.menu_bar.addMenu(self.menu_setting)

    def open_set_hs_paras(self):
        self.hs_para_dialog.show()

    def set_hs_paras(self, samples, lines, bands):
        self.samples = samples
        self.lines = lines
        self.bands = bands

    def open_set_fitting_paras(self):
        self.fitting_para_dialog.show()

    def set_fitting_paras(self, fitting_order, fitting_range):
        self.fitting_order = fitting_order
        self.fitting_range = fitting_range

    def open_set_rgb_paras(self):
        self.rgb_para_dialog.show()

    def set_rgb_paras(self, r, g, b):
        self.red = r
        self.green = g
        self.blue = b

    def open_file(self):
        """
        Choose and load a *.raw hyper spectral data.
        Can open multi-windows at the same time.
        """
        file_name = QFileDialog.getOpenFileName(self, 'Choose Files', '', "Raw(*.raw)",
                                                None, QFileDialog.DontUseNativeDialog)[0]
        if not file_name:
            return
        # Every time new a new DisplayImageDialog object so that multi-windows are supported.
        self.image_dialog = DisplayImageDialog(self)
        # Parameters about fitting should be more real-time.
        self.fitting_para_dialog.fitting_paras_signal.connect(self.image_dialog.set_fitting_paras)
        self.image_dialog.hs_data.samples = self.samples
        self.image_dialog.hs_data.lines = self.lines
        self.image_dialog.hs_data.bands = self.bands
        self.image_dialog.fitting_order = self.fitting_order
        self.image_dialog.fitting_range = self.fitting_range
        self.image_dialog.red = self.red
        self.image_dialog.green = self.green
        self.image_dialog.blue = self.blue
        self.image_dialog.load_file(file_name)
        self.image_dialog.setWindowTitle(file_name.split('/')[-1])
        self.image_dialog.show()
        self.image_dialog.spectrum_dialog.show()
        self.image_dialog.move(240, 200)
        self.image_dialog.spectrum_dialog.move(250+self.image_dialog.width(), 200)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MyWindow()
    # mw = SetHsParameterDialog()
    mw.show()
    sys.exit(app.exec_())
