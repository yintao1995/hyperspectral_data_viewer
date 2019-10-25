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
        self.show_deep_check_box = QCheckBox("Show Deep")
        self.fit_check_box = QCheckBox("Display Fit")
        self.normalize_check_box = QCheckBox("Normalize")
        self.manual_calibration_check_box = QCheckBox("Manual Cali")
        self.spin_box = QSpinBox()
        self.spin_box.setRange(400, 900)
        self.spin_box.setDisabled(True)

        # alignment of widgets
        self.btn_layout = QHBoxLayout()
        self.btn_layout.addWidget(self.show_deep_check_box)
        self.btn_layout.addWidget(self.fit_check_box)
        self.btn_layout.addWidget(self.normalize_check_box)
        self.btn_layout.addWidget(self.manual_calibration_check_box)
        self.btn_layout.addWidget(self.spin_box)
        self.btn_layout.addStretch()
        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.spectrum_canvas)
        self.main_layout.addLayout(self.btn_layout)
        self.main_layout.addWidget(self.spectrum_nav_btn)

        # signals and slots
        # noinspection PyUnresolvedReferences
        self.manual_calibration_check_box.stateChanged.connect(self.manual_cali_check_or_not)

    def manual_cali_check_or_not(self):
        if self.manual_calibration_check_box.checkState() == 2:
            self.spin_box.setDisabled(False)
        else:
            self.spin_box.setDisabled(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = DisplaySpectrumDialog()
    mw.show()
    sys.exit(app.exec_())
