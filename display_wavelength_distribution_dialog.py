# !usr/bin/env python
# -*- coding:utf-8 -*-
# # @Author: Yin Tao
# @File: display_wavelength_distribution_dialog.py
# @Time: 2019/08/27
# 


from my_canvas import MyCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from matplotlib import *
import matplotlib
matplotlib.use("Qt5Agg")


class DisplayWavelengthDistributionDialog(QDialog):
    """
    Dialog to display resonance wavelength 2-D distribution of selected area.
    """
    selection_signal = pyqtSignal()
    hide_widget_signal = pyqtSignal()
    show_widget_signal = pyqtSignal()

    def __init__(self, parent=None):
        super(DisplayWavelengthDistributionDialog, self).__init__(parent)
        self.setWindowTitle("Display Wavelength Distribution")
        self.setStyleSheet(
            "QWidget{background-color:white;}"
            "QPushButton{border:2px groove gray; border-radius: 5px}"
            "QPushButton:hover{background-color:#CDC9C9}"
            "QPushButton:pressed{background-color:#9C9C9C}"
            )

        # widgets: buttons, canvas, progress bar, navigation tool bar...
        self.spin_box_x1 = QSpinBox()
        self.spin_box_y1 = QSpinBox()
        self.spin_box_w1 = QSpinBox()
        self.spin_box_h1 = QSpinBox()
        self.spin_box_x1.setRange(0, 1200)
        self.spin_box_y1.setRange(0, 1200)
        self.spin_box_w1.setRange(0, 1200)
        self.spin_box_h1.setRange(0, 1200)
        self.select_btn = QPushButton("Select")
        self.progress_bar = QProgressBar()
        self.distribution_canvas = MyCanvas()
        self.distribution_nav_btn = NavigationToolbar(self.distribution_canvas, parent=None)

        # alignment of widgets
        self.selection_layout = QHBoxLayout()
        self.selection_layout.addStretch(1)
        self.selection_layout.addWidget(self.spin_box_x1, stretch=1)
        self.selection_layout.addWidget(self.spin_box_y1, stretch=1)
        self.selection_layout.addWidget(self.spin_box_w1, stretch=1)
        self.selection_layout.addWidget(self.spin_box_h1, stretch=1)
        self.selection_layout.addWidget(self.select_btn, stretch=1)
        self.selection_layout.addStretch(1)

        self.progress_bar_layout = QHBoxLayout()
        self.progress_bar_layout.addStretch(1)
        self.progress_bar_layout.addWidget(self.progress_bar, stretch=5)
        self.progress_bar_layout.addStretch(1)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.addLayout(self.selection_layout)
        self.main_layout.addLayout(self.progress_bar_layout)
        self.main_layout.addWidget(self.distribution_canvas)
        self.main_layout.addWidget(self.distribution_nav_btn)

        # data
        self.color_bar = None

        # signals and slots
        self.spin_box_x1.valueChanged.connect(self.selection_signal_emit)
        self.spin_box_w1.valueChanged.connect(self.selection_signal_emit)
        self.spin_box_y1.valueChanged.connect(self.selection_signal_emit)
        self.spin_box_h1.valueChanged.connect(self.selection_signal_emit)

    def selection_signal_emit(self):
        """
        Any one of the four QSpinBox changes, will send a signal to update selection area over image.
        """
        self.selection_signal.emit()

    def closeEvent(self, event):
        """
        When this dialog is closed(hide), send a signal to hide selection area.
        """
        self.hide_widget_signal.emit()

    def showEvent(self, event):
        """
        When this dialog appears, send a signal to show the selection area which was hidden before.
        """
        self.selection_signal.emit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = DisplayWavelengthDistributionDialog()
    mw.show()
    sys.exit(app.exec_())
