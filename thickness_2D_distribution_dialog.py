# !usr/bin/env python
# -*- coding:utf-8 -*-
# # @Author: Yin Tao
# @File: thickness_2D_distribution_dialog.py
# @Time: 2019/09/17
# 

from thickness_2D_distribution import Ui_Dialog as Distribution_Dialog
from sense_layers import Ui_Dialog as Ui_Dialog_layer
from Thickness_P import calculate_porosity_thickness_curve_intersection, \
    draw_spectrum_3_layers, draw_spectrum_4_layers, effective_n
import sys
import time
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import numpy as np


class SettingSenseLayer(QDialog, Ui_Dialog_layer):
    """
    Configure every layer about the sensor chip.
    Can draw resonance spectrum under given conditions.
    """
    def __init__(self, parent=None):
        super(SettingSenseLayer, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Kretchman结构各层参数设置")

        self.comboBox.addItem("棱镜+玻璃基底")
        self.comboBox_2.addItem("Au")
        self.comboBox_2.addItem("AgAu-50%50%")
        self.comboBox_3.addItem("无")
        self.comboBox_3.addItem("TiO2")
        self.comboBox_4.addItem("水")
        self.comboBox_4.addItem("空气")
        self.comboBox_4.addItem("指定折射率")

        self.wavelength = None
        self.n0 = None
        self.n1 = None
        self.n2 = None
        self.n3 = None
        self.n4 = None
        self.theta = 0
        self.d2 = 0
        self.d3 = 0
        self.porosity = 0.0

        self.hide_or_show_3rd_layer(0)
        self.hide_or_show_4th_layer(0)
        self.pushButton.clicked.connect(self.set_parameters)
        self.comboBox_3.currentIndexChanged.connect(self.hide_or_show_3rd_layer)
        self.comboBox_4.currentIndexChanged.connect(self.hide_or_show_4th_layer)

    def hide_or_show_4th_layer(self, index):
        if index != 2:
            self.label_8.hide()
            self.lineEdit.hide()
        else:
            self.label_8.show()
            self.lineEdit.show()

    def hide_or_show_3rd_layer(self, index):
        if index == 0:
            self.label_6.hide()
            self.spinBox_3.hide()
            self.label_9.hide()
            self.spinBox_4.hide()
        else:
            self.label_6.show()
            self.spinBox_3.show()
            self.label_9.show()
            self.spinBox_4.show()

    def set_parameters(self):
        try:
            self.theta = self.spinBox.value()
            self.wavelength = np.load("RI\\wavelength.npy")
            self.n0 = np.load("RI\\prism.npy")
            self.n1 = np.load("RI\\glass.npy")
            metal_layer = [("RI\\Au_n.npy", "RI\\Au_k.npy"), ("RI\\AgAu_n.npy", "RI\\AgAu_k.npy")]
            metal_layer_number = self.comboBox_2.currentIndex()
            n2_n = np.load(metal_layer[metal_layer_number][0])
            n2_k = np.load(metal_layer[metal_layer_number][1])
            self.n2 = n2_n + 1j*n2_k
            self.d2 = self.spinBox_2.value()
            self.n3 = np.load("RI\\tio2.npy")
            self.d3 = self.spinBox_3.value() if self.comboBox_3.currentIndex() != 0 else 0
            self.porosity = self.spinBox_4.value()/100
            over_layer = self.comboBox_4.currentIndex()
            if over_layer == 0:
                self.n4 = np.load("RI\\water.npy")
            elif over_layer == 1:
                self.n4 = np.load("RI\\air.npy")
            elif over_layer == 2:
                self.n4 = np.full(5001, float(self.lineEdit.text()))
        except:
            QMessageBox.warning(self, "error", "error")
            pass
        else:
            # print("θ：", self.theta, type(self.theta))
            # print("λ：", self.wavelength, type(self.wavelength))
            # print("棱镜：", self.n0, type(self.n0))
            # print("玻璃：", self.n1, type(self.n1))
            # print("金属膜：", self.n2, type(self.n2))
            # print("金属膜厚度：", self.d2, type(self.d2))
            # print("增强层：", self.n3, type(self.n3))
            # print("增强层厚度：", self.d3, type(self.d3))
            # print("增强层孔隙率：", self.porosity, type(self.porosity))
            # print("介质层：", self.n4, type(self.n4))
            if self.d3 == 0:    # 此时修饰层选择的“无”，整体为三层结构
                draw_spectrum_3_layers(self.wavelength, self.n0, self.n1, self.n2, self.n4, self.theta, self.d2)
            else:
                if self.spinBox_4.value() != 0:     # 如果有孔隙率，计算等效折射率
                    # 由于存在空隙，那么修饰层的等效折射率是由修饰层纯介质折射率和检测层物质(空气/水等)决定
                    self.n3 = effective_n(self.porosity, self.n3, self.n4)
                draw_spectrum_4_layers(self.wavelength, self.n0, self.n1, self.n2, self.n3, self.n4, self.theta, self.d2, self.d3)


class CalculateThicknessDistributionThread(QThread):
    """
    A thread to calculate porosity and thickness 2D distribution.
    """
    finish_calculate_signal = pyqtSignal()

    def __init__(self):
        super(CalculateThicknessDistributionThread, self).__init__()
        self.wavelength = self.n_prism = self.n_glass = self.n_metal = self.n_enhance = None
        self.d_gold = self.theta = self.d_enhance_start = self.p_start = self.p_end = None
        self.n4_conditions = None
        self.resonance_matrix_condition_1 = None
        self.resonance_matrix_condition_2 = None
        self.n = self.m = 0
        self.porosity_result = np.zeros(0)
        self.thickness_result = np.zeros(0)

    def set_parameters(self, wavelength, n_prism, n_glass, n_metal, n_enhance, theta, d_gold, d_enhance_start,
                       p_start, p_end, n4_conditions):
        """
        Passing parameters from outer widgets.
        """
        self.wavelength = wavelength
        self.n_prism = n_prism
        self.n_glass = n_glass
        self.n_metal = n_metal
        self.n_enhance = n_enhance
        self.d_gold = d_gold
        self.theta = theta
        self.d_enhance_start = d_enhance_start
        self.p_start = p_start
        self.p_end = p_end
        self.n4_conditions = n4_conditions
        # self.target_resonance_conditions = target_resonance_conditions

    def run(self):
        """
        Main calculation in thread.
        [calculated_database]:
            To store calculated point in form as (wavelength1, wavelength2): (porosity, thickness)
            If a new point is very close to one of point in calculated_database,
                we consider they has same (porosity, thickness), so we can skip calculating.
            Else this new point has to be calculated.
        """
        self.porosity_result = np.zeros((self.n, self.m))
        self.thickness_result = np.zeros((self.n, self.m))
        t1 = time.time()
        calculated_database = {(0, 0): (0, 0)}
        for i in range(self.n):
            for j in range(self.m):
                target_resonance_conditions = (self.resonance_matrix_condition_1[i][j],
                                               self.resonance_matrix_condition_2[i][j])
                distance_range = 0.5
                nearest_point = None
                nearest_distance = 100
                for point in calculated_database:
                    d = abs(target_resonance_conditions[0] - point[0]) + abs(target_resonance_conditions[1] - point[1])
                    if d < nearest_distance and d < distance_range:
                        nearest_distance = d
                        nearest_point = point
                if nearest_point:
                    res = calculated_database[nearest_point]
                else:
                    res = calculate_porosity_thickness_curve_intersection(self.wavelength, self.n_prism, self.n_glass,
                                                                          self.n_metal, self.n_enhance, self.theta,
                                                                          self.d_gold, self.d_enhance_start,
                                                                          self.p_start, self.p_end, self.n4_conditions,
                                                                          target_resonance_conditions)
                    calculated_database[target_resonance_conditions] = res
                self.porosity_result[i][j] = round(res[0], 2)
                self.thickness_result[i][j] = round(res[1], 2)
                # print("({i}, {j})=".format(i=i, j=j), target_resonance_conditions, res)
        t2 = time.time()
        print("Time used: ", t2-t1)
        self.finish_calculate_signal.emit()


class CalculateThicknessDistributionDialog(QDialog, Distribution_Dialog):
    """
    A Dialog containing two part:
        1. sense layers configuration.
        2. calculate thickness/porosity distribution.
    """
    def __init__(self, parent=None):
        super(CalculateThicknessDistributionDialog, self).__init__(parent)
        self.setupUi(self)
        # self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint)

        self.sense_model = SettingSenseLayer()
        self.calc_thread = CalculateThicknessDistributionThread()
        self.calc_thread.finish_calculate_signal.connect(self.display_result)
        self.condition_1 = None
        self.condition_2 = None

        self.pushButton.clicked.connect(self.open_sense_layer_setting)
        self.pushButton_2.clicked.connect(lambda: self.load_resonance_wavelength_data_matrix(1))
        self.pushButton_3.clicked.connect(lambda: self.load_resonance_wavelength_data_matrix(2))
        self.pushButton_4.clicked.connect(self.calculate_thickness_distribution)
        self.pushButton_5.clicked.connect(lambda: self.save_result_data(True))
        self.pushButton_6.clicked.connect(lambda: self.save_result_data(False))

    def open_sense_layer_setting(self):
        self.sense_model.show()

    def load_resonance_wavelength_data_matrix(self, condition_flag):
        """
        Load resonance wavelength data matrix under different conditions.
        """
        file_name = QFileDialog.getOpenFileName(self, 'Choose Files', '', "npy(*.npy)",
                                                None, QFileDialog.DontUseNativeDialog)[0]
        if not file_name:
            return
        if condition_flag == 1:
            self.condition_1 = np.load(file_name)
            self.calc_thread.resonance_matrix_condition_1 = self.condition_1
            self.calc_thread.n, self.calc_thread.m = self.condition_1.shape
        elif condition_flag == 2:
            self.condition_2 = np.load(file_name)
            self.calc_thread.resonance_matrix_condition_2 = self.condition_2

    def calculate_thickness_distribution(self):
        """
        Calculate.
        """
        try:
            # TODO: 改成可调节的
            wavelength = np.load("RI\\wavelength.npy")
            n_prism = np.load("RI\\prism.npy")
            n_glass = np.load("RI\\glass.npy")
            n_metal = np.load("RI\\Au_n.npy") + 1j * np.load("RI\\Au_k.npy")
            n_enhance = np.load("RI\\tio2.npy")
            d_gold = 50
            theta = 10
            d_enhance_start = int(self.lineEdit_3.text())
            p_start = float(self.lineEdit_4.text())
            p_end = float(self.lineEdit_5.text())
            n4_conditions = [float(self.lineEdit.text()), float(self.lineEdit_2.text())]
            self.calc_thread.set_parameters(wavelength, n_prism, n_glass, n_metal, n_enhance,
                                            theta, d_gold, d_enhance_start, p_start, p_end, n4_conditions)
        except:
            pass
        else:
            if self.calc_thread.n == self.calc_thread.m > 0:
                self.pushButton_4.setText("...")
                self.calc_thread.start()
            else:
                QMessageBox.warning(self, "Warning",
                                    "Please load correct resonance wavelength matrix under different conditions")

    def display_result(self):
        """
        After calculating, display result via image.
        """
        self.pushButton_4.setText("计算并绘制")
        porosity = self.calc_thread.porosity_result
        thickness = self.calc_thread.thickness_result

        plt.figure("Porosity Distribution")
        plt.imshow(porosity, cmap=plt.get_cmap('rainbow'))
        plt.colorbar()

        plt.figure("Thickness Distribution")
        plt.imshow(thickness, cmap=plt.get_cmap('rainbow'))
        plt.colorbar()
        plt.show()

    def save_result_data(self, flag):
        if flag:
            data_to_save = self.calc_thread.porosity_result
        else:
            data_to_save = self.calc_thread.thickness_result
        if data_to_save.__len__() == 0:
            QMessageBox.warning(self, "Warning", "No data to be saved!")
        else:
            filename = QFileDialog.getSaveFileName(self, 'Save File', '', "csv file(*.csv)", None,
                                                   QFileDialog.DontUseNativeDialog)[0]
            if filename:
                np.savetxt(filename + ".csv", data_to_save, fmt="%.2f", delimiter=',')
                # np.save(filename + ".npy", data_to_save)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = CalculateThicknessDistributionDialog()
    # mw = SettingSenseLayer()
    mw.show()
    sys.exit(app.exec_())
