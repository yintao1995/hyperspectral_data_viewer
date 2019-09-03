# !usr/bin/env python
# -*- coding:utf-8 -*-
# # @Author: Yin Tao
# @File: display_image_dialog.py
# @Time: 2019/08/19
# 


from display_spectrum_dialog import DisplaySpectrumDialog
from display_wavelength_distribution_dialog import DisplayWavelengthDistributionDialog
from my_canvas import MyCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from hyper_spectral_data import HyperSpectralData
from seeking_deep import show_deep
from P_d_dialog import MyPdDialog
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from matplotlib import *
import time
import numpy as np
import cv2
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use("Qt5Agg")


class CalculateThread(QThread):
    """
    A thread to calculate wavelength distribution specifically.
    """
    finish_calculate_signal = pyqtSignal()
    update_progress_signal = pyqtSignal(int)

    def __init__(self):
        super(CalculateThread, self).__init__()
        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0
        self.data = HyperSpectralData()
        self.fitting_order = 4
        self.fitting_range = 25
        self.result = []
        self.average = 0

    def run(self):
        """
        While processing, send <update_progress_signal> to update progress bar.
        After processing, send <finish_calculate_signal> to display the result.
        """
        self.result = []
        total_sum = 0
        present_progress = 0
        for y in range(self.y1, self.y2):
            temp = []
            present_progress += 1
            self.update_progress_signal.emit(present_progress)
            for x in range(self.x1, self.x2):
                point_xy = self.data.get_point_xy_data(x, y)
                temp_resonance_wavelength = show_deep(self.data.spectral_band, point_xy,
                                                      fit_order=self.fitting_order, fit_range=self.fitting_range)[0]
                temp.append(temp_resonance_wavelength)
            total_sum += sum(temp)
            self.result.append(temp)
        self.average = total_sum/(self.y2-self.y1)/(self.x2-self.x1)
        self.finish_calculate_signal.emit()
        

class DisplayImageDialog(QDialog):
    """
    This is main GUI.
    """
    def __init__(self, parent=None):
        super(DisplayImageDialog, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setWindowTitle("Display Band Image")
        self.setMouseTracking(True)
        self.setStyleSheet(
                           "QWidget{background-color:white; }"
                           "QPushButton{border:2px groove gray; border-radius: 5px}"
                           "QPushButton:hover{background-color:#CDC9C9}"
                           "QPushButton:pressed{background-color:#9C9C9C}"
                           "QComboBox{selection-color:black;selection-background-color:white}"
                           )

        # widgets: canvas, button, label, combo box...
        self.image_canvas = MyCanvas()
        self.image_nav_btn = NavigationToolbar(self.image_canvas, parent=None)
        self.band_label = QLabel("Band=")
        self.band_combo_box = QComboBox()
        self.save_img_btn = QPushButton(" Save Image ")
        self.convert_to_rgb_btn = QPushButton(" RGB ")
        self.calc_thickness_btn = QPushButton(" Thickness ")
        self.wavelength_distribution_btn = QPushButton(" Distribution ")
        min_height_for_buttons = 23
        self.band_combo_box.setMinimumHeight(min_height_for_buttons)
        self.band_combo_box.setMinimumHeight(min_height_for_buttons)
        self.save_img_btn.setMinimumHeight(min_height_for_buttons)
        self.convert_to_rgb_btn.setMinimumHeight(min_height_for_buttons)
        self.calc_thickness_btn.setMinimumHeight(min_height_for_buttons)

        # alignment of widgets
        self.btn_layout = QHBoxLayout()
        self.btn_layout.addWidget(self.band_label, stretch=1)
        self.btn_layout.addWidget(self.band_combo_box, stretch=1)
        self.btn_layout.addWidget(self.save_img_btn, stretch=1)
        self.btn_layout.addWidget(self.convert_to_rgb_btn, stretch=1)
        self.btn_layout.addWidget(self.calc_thickness_btn, stretch=1)
        self.btn_layout.addWidget(self.wavelength_distribution_btn, stretch=1)
        self.btn_layout.addStretch(1)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.image_canvas)
        self.main_layout.addLayout(self.btn_layout)
        self.main_layout.addWidget(self.image_nav_btn)

        # data
        self.hs_data = HyperSpectralData()
        self.image_height = self.hs_data.lines
        self.image_width = self.hs_data.samples
        self.n_th = 0
        self.image_title = ''
        self.band_n = np.zeros(0)
        self.rgb_flag = 0
        self.fitting_order = 4
        self.fitting_range = 25
        self.red = 74
        self.green = 50
        self.blue = 21

        # child widgets
        self.spectrum_dialog = DisplaySpectrumDialog(parent=self)
        self.calc_thickness_dialog = MyPdDialog(parent=self)
        self.distribution_dialog = DisplayWavelengthDistributionDialog(parent=self)

        # other threads
        self.calc_distribution_thread = CalculateThread()

        # signals and slots
        self.band_combo_box.currentIndexChanged.connect(
            lambda: self.view_band_gray_image(self.band_combo_box.currentIndex() + 1))
        self.save_img_btn.clicked.connect(self.save_image_as_png)
        self.convert_to_rgb_btn.clicked.connect(self.convert_to_rgb)
        self.calc_thickness_btn.clicked.connect(self.open_calc_thickness_dialog)
        self.image_canvas.mpl_connect("motion_notify_event", lambda event: self.view_pixel_spectrum(event, 0))
        self.image_canvas.mpl_connect("axes_enter_event", lambda event: self.open_spectrum_dialog(event))
        self.image_canvas.mpl_connect("button_press_event", lambda event: self.view_pixel_spectrum(event, 1))
        self.image_canvas.mpl_connect("button_press_event", lambda event: self.my_press_event(event))
        self.image_canvas.mpl_connect("button_release_event", lambda event: self.my_release_event(event))
        self.image_canvas.mpl_connect("motion_notify_event", lambda event: self.my_move_event(event))
        self.wavelength_distribution_btn.clicked.connect(self.open_wavelength_distribution_dialog)
        self.distribution_dialog.selection_signal.connect(self.update_selection_rectangle)
        self.distribution_dialog.hide_widget_signal.connect(self.clear_selection_rectangle)
        self.distribution_dialog.select_btn.clicked.connect(self.view_selection_wavelength_distribution)

    def set_fitting_paras(self, fitting_order, fitting_range):
        """
        Change fitting parameters real-time.
        """
        self.fitting_order = fitting_order
        self.fitting_range = fitting_range

    def load_file(self, file_name):
        """
        Load SEMR hyper spectral data.
        Data format should be .raw created by Dualix HS Camera.
        """
        self.hs_data.filename = file_name
        self.hs_data.get_data_from_file()
        for i in self.hs_data.spectral_band:
            self.band_combo_box.addItem("{}nm".format("%.2f" % i))
        self.band_combo_box.setCurrentIndex(self.hs_data.bands//2)
        self.view_band_gray_image(self.band_combo_box.currentIndex() + 1)

    def view_band_gray_image(self, n):
        """
        Display the gray image of any chosen spectral band.
        """
        self.n_th = n
        self.band_n = self.hs_data.get_band_n_data(self.n_th)
        self.image_title = "Gray image of the band {n}, $\\lambda={r}nm$".format(
            n=self.n_th, r=round(self.hs_data.spectral_band[self.n_th-1], 2))
        self.image_canvas.my_draw(self.band_n, title=self.image_title)
        self.rgb_flag = 0

    def save_image_as_png(self):
        """
        Save the image which is displayed at present.
        It can be gray image or RGB image.
        """
        if self.hs_data.data.__len__() == 0:
            return
        if self.band_n.__len__() == 0:
            return
        if self.rgb_flag:
            file_path = self.hs_data.filename.replace(self.windowTitle(), "RGB image")+".png"
            # noinspection PyUnresolvedReferences
            matplotlib.pyplot.imsave(file_path, self.band_n)
        else:
            file_path = self.hs_data.filename.replace(self.windowTitle(), self.band_combo_box.currentText()) + ".png"
            # noinspection PyUnresolvedReferences
            matplotlib.pyplot.imsave(file_path, self.band_n, cmap="gray")

    def convert_to_rgb(self):
        """
        Display the RGB colorful image of the hyper spectral data.
        By choosing three specific bands and merge them to get RGB array.
        """
        if self.hs_data.data.__len__() == 0:
            return
        red_band = self.red
        green_band = self.green
        blue_band = self.blue
        band_r = self.hs_data.get_band_n_data(red_band)
        band_g = self.hs_data.get_band_n_data(green_band)
        band_b = self.hs_data.get_band_n_data(blue_band)
        max_num = max(np.max(band_r), np.max(band_g), np.max(band_b))
        self.band_n = cv2.merge([band_r/max_num, band_g/max_num, band_b/max_num])
        self.image_canvas.my_draw(self.band_n, title="Displaying as RGB mode")
        self.rgb_flag = 1

    def open_calc_thickness_dialog(self):
        """
        Call out the "calculate thickness and porosity" widget.
        """

        # calc_thickness_dialog = MyPdDialog(self)
        # calc_thickness_dialog.setAttribute(Qt.WA_DeleteOnClose)
        self.calc_thickness_dialog.show()

    def open_spectrum_dialog(self, event):
        """
        If spectrum dialog is closed somehow, it can be summoned by entering axes.
        """
        if not self.spectrum_dialog.isVisible():
            self.spectrum_dialog.show()

    def view_pixel_spectrum(self, event, freeze_flag):
        """
        While the mouse pointer is placing over left canvas, the right canvas show spectrum of the point.
        And u can choose whether to display the original data/fitted curve by enable/disable the corresponding CheckBox.
        """
        try:
            x = int(round(event.xdata))
            y = int(round(event.ydata))
            point_xy = self.hs_data.get_point_xy_data(x, y)
            painter = self.spectrum_dialog.spectrum_canvas
            painter.ax.clear()
            xy_max = max(point_xy)
            if self.spectrum_dialog.normalize_check_box.isChecked():
                point_xy = [i / xy_max for i in point_xy]
                xy_max = 1.0
            painter.ax.plot(self.hs_data.spectral_band, point_xy)
            # seek deep and fit.
            result = show_deep(self.hs_data.spectral_band, point_xy, fit_order=self.fitting_order,
                               fit_range=self.fitting_range)
            painter.ax.plot([result[0], result[0]], [0, xy_max], alpha=0.4)
            if not result[0]:
                painter.ax.text(result[0], 0, "Not Found", alpha=0.6)
            else:
                painter.ax.text(result[0], 0, str(result[0]) + 'nm', alpha=0.6)
                if self.spectrum_dialog.fit_check_box.isChecked():
                    painter.ax.scatter(self.hs_data.spectral_band, point_xy, s=5)
                    painter.ax.plot(result[2], result[3], c='red')
            painter.ax.set_xlabel("wavelength/(nm)")
            painter.fig.suptitle('spectrum of the point({x},{y})'.format(x=x, y=y))
            painter.draw()
            if freeze_flag and event.button == 3:
                # press right button of mouse to freeze canvas for one sec.
                time.sleep(1)
        except (TypeError, ValueError):
            # TypeError:    when the cursor is out of canvas
            # ValueError:   when no data been loaded, function 'max' won't work
            pass

    def open_wavelength_distribution_dialog(self):
        self.distribution_dialog.show()

    def view_selection_wavelength_distribution(self):
        """
        Make a rectangular selection, draw it's resonance wavelength distribution.
        Put it in a separated thread to separate calculation and GUI.
        (x1, y1): top-left corner of the selection
        (x2, y2): bottom-right corner of the selection.
        """
        x1 = self.distribution_dialog.spin_box_x1.value()
        y1 = self.distribution_dialog.spin_box_y1.value()
        w1 = self.distribution_dialog.spin_box_w1.value()
        h1 = self.distribution_dialog.spin_box_h1.value()
        self.calc_distribution_thread.x1 = x1
        self.calc_distribution_thread.y1 = y1
        self.calc_distribution_thread.x2 = x1 + w1
        self.calc_distribution_thread.y2 = y1 + h1
        self.calc_distribution_thread.data = self.hs_data
        self.calc_distribution_thread.fitting_order = self.fitting_order
        self.calc_distribution_thread.fitting_range = self.fitting_range
        self.calc_distribution_thread.start()
        self.distribution_dialog.progress_bar.setRange(0, h1)
        self.calc_distribution_thread.update_progress_signal.connect(self.update_progress)
        self.calc_distribution_thread.finish_calculate_signal.connect(self.finish_calculation)

    def update_progress(self, present_progress):
        """
        Update progress bar's status.
        """
        self.distribution_dialog.progress_bar.setValue(present_progress)

    def finish_calculation(self):
        """
        After finishing calculation, display the result on canvas.
        """
        self.calc_distribution_thread.finish_calculate_signal.disconnect(self.finish_calculation)
        # This is important. Have to disconnect connection since this connection is in function.
        x_start = self.calc_distribution_thread.x1 - 0.5
        x_end = self.calc_distribution_thread.x2 - 0.5
        y_start = self.calc_distribution_thread.y2 - 0.5
        y_end = self.calc_distribution_thread.y1 - 0.5
        canvas_3 = self.distribution_dialog.distribution_canvas
        canvas_3.ax.clear()
        pic = canvas_3.ax.imshow(self.calc_distribution_thread.result, cmap="rainbow",
                                 extent=(x_start, x_end, y_start, y_end))
        canvas_3.fig.suptitle("Average: "+"%.2f" % self.calc_distribution_thread.average)
        # print(self.calc_distribution_thread.average)
        if self.distribution_dialog.color_bar:
            # Remove color bar created before
            self.distribution_dialog.color_bar.remove()
        self.distribution_dialog.color_bar = canvas_3.fig.colorbar(mappable=pic)
        self.distribution_dialog.color_bar.set_label("$\\lambda$/nm")
        canvas_3.draw()

    def clear_selection_rectangle(self):
        """
        Re-draw the gray image to clear selection area.
        """
        self.image_canvas.my_draw(self.band_n, title=self.image_title)

    def update_selection_rectangle(self):
        """
        If any spin box on distribution dialog change, update selection area.
        """
        present_x1 = self.distribution_dialog.spin_box_x1.value()
        present_y1 = self.distribution_dialog.spin_box_y1.value()
        present_w1 = self.distribution_dialog.spin_box_w1.value()
        present_h1 = self.distribution_dialog.spin_box_h1.value()
        present_x2 = present_x1 + present_w1
        present_y2 = present_y1 + present_h1

        self.image_canvas.my_clear_lines()
        self.image_canvas.my_draw_rectangle(present_x1, present_y1, present_x2, present_y2)

    def my_press_event(self, event):
        """
        Draw selection event.
        """
        self.image_canvas.press_flag = True
        try:
            self.image_canvas.x1 = int(round(event.xdata))
            self.image_canvas.y1 = int(round(event.ydata))
        except TypeError:
            pass

    def my_release_event(self, event):
        """
        Draw selection event.
        """
        self.image_canvas.press_flag = False

    def my_move_event(self, event):
        """
        Draw selection event.
        """
        try:
            if self.image_canvas.press_flag and self.distribution_dialog.isVisible():
                self.image_canvas.my_clear_lines()
                self.distribution_dialog.spin_box_x1.setValue(self.image_canvas.x1)
                self.distribution_dialog.spin_box_y1.setValue(self.image_canvas.y1)
                self.distribution_dialog.spin_box_w1.setValue(int(round(event.xdata)) - self.image_canvas.x1)
                self.distribution_dialog.spin_box_h1.setValue(int(round(event.ydata)) - self.image_canvas.y1)
                self.image_canvas.my_draw_rectangle(self.image_canvas.x1, self.image_canvas.y1, event.xdata, event.ydata)
        except TypeError:
            pass

    def closeEvent(self, event):
        """
        While close this widget, delete it's data to free memory.
        """
        self.hs_data.data = np.zeros(0)
        self.band_n = np.zeros(0)
        del self


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = DisplayImageDialog()
    mw.show()
    sys.exit(app.exec_())
