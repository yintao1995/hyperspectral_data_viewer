# !usr/bin/env python
# -*- coding:utf-8 -*-
# # @Author: Yin Tao
# @File: display_spectrum_dialog.py
# @Time: 2019/08/20
# 


from my_canvas import MyCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import *
from matplotlib import *
import matplotlib
# import matplotlib.pyplot as plt
matplotlib.use("Qt5Agg")


class DisplaySpectrumDialog(QDialog):
    """
    Dialog to display spectrum of selected pixel.
    """

    def __init__(self, parent=None):
        super(DisplaySpectrumDialog, self).__init__(parent)
        self.setWindowTitle("Display Point Spectrum")
        self.setStyleSheet(
            "QWidget{background-color:white;}"
            "QPushButton{border:2px groove gray; border-radius: 5px}"
            "QPushButton:hover{background-color:#CDC9C9}"
            "QPushButton:pressed{background-color:#9C9C9C}"
            )

        # widgets: canvas, buttons, check box, navigation bar...
        self.spectrum_canvas = MyCanvas()
        self.spectrum_nav_btn = NavigationToolbar(self.spectrum_canvas, parent=None)
        self.fit_check_box = QCheckBox("Display Fit")
        self.normalize_check_box = QCheckBox("Normalize")

        # alignment of widgets
        self.btn_layout = QHBoxLayout()
        self.btn_layout.addWidget(self.fit_check_box)
        self.btn_layout.addWidget(self.normalize_check_box)
        self.btn_layout.addStretch()
        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.spectrum_canvas)
        self.main_layout.addLayout(self.btn_layout)
        self.main_layout.addWidget(self.spectrum_nav_btn)

        # signals and slots
        # noinspection PyUnresolvedReferences


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = DisplaySpectrumDialog()
    mw.show()
    sys.exit(app.exec_())
