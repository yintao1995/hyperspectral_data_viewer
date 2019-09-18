import sys
from P_d import Ui_Dialog as Ui_Dialog_pd
from sense_layers import Ui_Dialog as Ui_Dialog_layer
from Thickness_P import calc_main, assess_data, draw_spectrum_3_layers, draw_spectrum_4_layers, effective_n
import numpy as np
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal


class SettingSenseLayer(QDialog, Ui_Dialog_layer):
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


class CalculatePdThread(QThread):
    finish_calculate_pd_signal = pyqtSignal()

    def __init__(self):
        super(CalculatePdThread, self).__init__()
        self.theta_list = []
        self.wavelength_list = []
        self.d_start = 0
        self.P_list = []
        self.accuracy = 0
        self.result = None

    def run(self):
        # result = [[11], [22]]
        self.result = calc_main(self.theta_list, self.wavelength_list, self.d_start, self.P_list, self.accuracy)
        print(self.result[0], self.result[1])
        self.finish_calculate_pd_signal.emit()


class MyPdDialog(QDialog, Ui_Dialog_pd):
    def __init__(self, parent=None):
        super(MyPdDialog, self).__init__(parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.calc_result)
        self.pushButton_2.clicked.connect(self.assess_result)
        self.calc_pd_thread = CalculatePdThread()
        # self.sense_model = SettingSenseLayer()

    def calc_result(self):
        try:
            theta_list = self.lineEdit.text()
            theta_list = [float(theta) for theta in theta_list.split(',')]

            wavelength_list = self.lineEdit_2.text()
            wavelength_list = [float(wavelength) for wavelength in wavelength_list.split(',')]

            d_start = float(self.lineEdit_3.text())
            calc_min = float(self.lineEdit_4.text())
            calc_max = float(self.lineEdit_5.text())
            P_list = np.arange(calc_min, calc_max + 0.01, 0.01)
            # numpy.arange产生的小数可能存在类似0.5000000001的情况,因此后续使用过程中需要
            # 控制精度, 用("%.2f"%P)作为文件名传递参数
            accuracy = float(self.lineEdit_6.text())
            self.calc_pd_thread.theta_list = theta_list
            self.calc_pd_thread.wavelength_list = wavelength_list
            self.calc_pd_thread.d_start = d_start
            self.calc_pd_thread.P_list = P_list
            self.calc_pd_thread.accuracy = accuracy
            self.pushButton.setText("计算中...")
            # self.calc_pd_thread.daemon = True
            self.calc_pd_thread.start()
            self.calc_pd_thread.finish_calculate_pd_signal.connect(self.set_result)
            # plt.show()
            # result = calc_main(theta_list, wavelength_list, d_start, P_list, accuracy)
        except:
            QMessageBox.warning(self, 'Warning', 'Input Format Wrong')
            pass

    def set_result(self):
        self.calc_pd_thread.finish_calculate_pd_signal.disconnect(self.set_result)
        if self.calc_pd_thread.result:
            self.textEdit.setText(str(self.calc_pd_thread.result[1]))
            self.textEdit_2.setText(str(self.calc_pd_thread.result[0]))
            self.pushButton.setText("计算")

    def assess_result(self):
        try:
            d_list = self.textEdit.toPlainText()
            d_list = [float(p) for p in d_list[1:-1].split(',')]
            assess_d = assess_data(d_list)
            self.lineEdit_7.setText(str(round(assess_d[0], 3)))
            self.lineEdit_8.setText(str(round(assess_d[2], 3))+'%')

            P_list = self.textEdit_2.toPlainText()
            P_list = [float(t) for t in P_list[1:-1].split(',')]
            assess_P = assess_data(P_list)
            self.lineEdit_9.setText(str(round(assess_P[0], 3)))
            self.lineEdit_10.setText(str(round(assess_P[2], 3))+'%')
        except:
            pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MyPdDialog()
    # mw = SettingSenseLayer()
    mw.show()
    sys.exit(app.exec_())
