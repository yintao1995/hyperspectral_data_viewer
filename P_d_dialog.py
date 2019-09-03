import sys
from P_d import *
from Thickness_P import calc_main,assess_data
import numpy as np
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal
import matplotlib.pyplot as plt


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


class MyPdDialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super(MyPdDialog, self).__init__(parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.calc_result)
        self.pushButton_2.clicked.connect(self.assess_result)
        self.calc_pd_thread = CalculatePdThread()

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
    mw.show()
    sys.exit(app.exec_())
