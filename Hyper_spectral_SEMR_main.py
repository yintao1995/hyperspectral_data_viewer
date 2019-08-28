#!/user/bin/env python3
# -*- coding: utf-8 -*-
# Time : 2019/5/31 16:06
# Author : "YinTao"
# ============== #


from display_image_dialog import DisplayImageDialog
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from matplotlib import *
import matplotlib
matplotlib.use("Qt5Agg")


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
        self.action_set_path = QAction("Set Path")
        self.set_menus()

        # child window
        self.image_dialog = DisplayImageDialog(self)

        # signals and slots
        self.action_exit.triggered.connect(self.close)
        self.action_open_file.triggered.connect(self.open_file)

    def set_menus(self):
        """
        Settings of menu.
        """
        self.setMenuBar(self.menu_bar)
        self.menu_file.addAction(self.action_open_file)
        self.menu_file.addAction(self.action_exit)
        self.menu_setting.addAction(self.action_set_path)
        self.menu_bar.addMenu(self.menu_file)
        self.menu_bar.addMenu(self.menu_setting)

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
        self.image_dialog.load_file(file_name)
        self.image_dialog.setWindowTitle(file_name.split('/')[-1])
        self.image_dialog.show()
        self.image_dialog.spectrum_dialog.show()
        self.image_dialog.move(240, 200)
        self.image_dialog.spectrum_dialog.move(250+self.image_dialog.width(), 200)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MyWindow()
    mw.show()
    sys.exit(app.exec_())
