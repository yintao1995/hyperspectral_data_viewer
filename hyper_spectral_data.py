#!/user/bin/env python3
# -*- coding: utf-8 -*-
# Time : 2019/6/28 18:49
# Author : "YinTao"
# ============== #


import numpy as np


# 高光谱型号：  .raw格式 无header  产商：双利合谱
class HyperSpectralData(object):
    def __init__(self, file_name=''):
        self.filename = file_name
        self.header = 0
        self.data_type = 12     # 12: 小端,uint16；    4: 小端,float32
        self.samples = 960      # 图片的高
        self.lines = 1101        # 图片的宽
        self.bands = 1456  # 波段数
        self.length = 0  # 总的图像数据的长度
        self.data = np.zeros(0)   # 二维数组
        self.r_band = 0
        self.g_band = 0
        self.b_band = 0
        # self.calibration_filename = ''
        # self.integral_time = 0
        self.spectral_band = [
            391.9, 395.1, 398.3, 401.6, 404.8, 408.0, 411.2, 414.5, 417.7, 420.9, 424.2, 427.4, 430.7, 433.9, 437.2,
            440.4, 443.7, 446.9, 450.2, 453.5, 456.7, 460.0, 463.3, 466.6, 469.8, 473.1, 476.4, 479.7, 483.0, 486.3,
            489.6, 492.9, 496.2, 499.5, 502.8, 506.2, 509.5, 512.8, 516.1, 519.4, 522.8, 526.1, 529.5, 532.8, 536.1,
            539.5, 542.8, 546.2, 549.5, 552.9, 556.3, 559.6, 563.0, 566.4, 569.7, 573.1, 576.5, 579.9, 583.3, 586.7,
            590.0, 593.4, 596.8, 600.2, 603.6, 607.1, 610.5, 613.9, 617.3, 620.7, 624.1, 627.6, 631.0, 634.4, 637.9,
            641.3, 644.7, 648.2, 651.6, 655.1, 658.5, 662.0, 665.5, 668.9, 672.4, 675.9, 679.3, 682.8, 686.3, 689.8,
            693.2, 696.7, 700.2, 703.7, 707.2, 710.7, 714.2, 717.7, 721.2, 724.7, 728.3, 731.8, 735.3, 738.8, 742.3,
            745.9, 749.4, 752.9, 756.5, 760.0, 763.6, 767.1, 770.7, 774.2, 777.8, 781.4, 784.9, 788.5, 792.1, 795.6,
            799.2, 802.8, 806.4, 810.0, 813.5, 817.1, 820.7, 824.3, 827.9, 831.5, 835.1, 838.7, 842.4, 846.0, 849.6,
            853.2, 856.8, 860.5, 864.1, 867.7, 871.4, 875.0, 878.7, 882.3, 886.0, 889.6, 893.3, 896.9, 900.6, 904.3,
            907.9, 911.6, 915.3, 918.9, 922.6, 926.3, 930.0, 933.7, 937.4, 941.1, 944.8, 948.5, 952.2, 955.9, 959.6,
            963.3, 967.0, 970.7, 974.5, 978.2, 981.9, 985.7, 989.4, 993.1, 996.9, 1000.6]
        self.get_info_from_hdr_dci_file()

    def get_info_from_hdr_dci_file(self):
        """
        while init, read info from hdr files.
        """
        if not self.filename:
            return
        hdr_filename = self.filename[:-4] + '.hdr'
        dci_filename = self.filename[:-4] + '.dci'
        try:
            with open(hdr_filename, 'r') as f:
                info_list = f.readlines()
                self.data_type = int(info_list[6].split('=')[1])
                self.samples = int(info_list[1].split('=')[1])
                self.lines = int(info_list[2].split('=')[1])
                self.bands = int(info_list[3].split('=')[1])

                self.spectral_band = [float(i[:-2]) for i in info_list[12:-1]]
            with open(dci_filename, 'r') as f:
                info_list = f.readlines()
                self.r_band = int(info_list[2][4:].strip())
                self.g_band = int(info_list[4][6:].strip())
                self.b_band = int(info_list[6][5:].strip())
        except:
            print('Errors encountered')

    def get_data_from_file(self, reflectivity_calibration=False):
        """get all data from file and store it as a 2-d array.
        reflectivity_calibration: if data is been reflectivity calibrated, size becomes 2x. data type is '<f4', float32

        :return : numpy array
        """
        if reflectivity_calibration:
            self.data = np.reshape(np.fromfile(self.filename, dtype='<f4'), (self.lines * self.bands, self.samples),
                                   order='C')  # '<'表示小端字节序  'f4'表示32位浮点数
        else:
            self.data = np.reshape(np.fromfile(self.filename, dtype='<u2'), (self.lines * self.bands, self.samples),
                                   order='C')    # '<'表示小端字节序  'u2'表示16位无符号整数

    def get_band_n_data(self, n):
        """Get data of the n-th band ,on the condition of having read all data to memory

        :param n: int (>0)
        :return: List[int]
        """
        if n > self.bands or n < 1:
            return
        n = int(n)  # 以免有人输了小数
        band_n_data = []
        for i in range(len(self.data)):
            if (i + 1 - n) % self.bands == 0:
                band_n_data.append(self.data[i])
        return band_n_data

    def get_point_xy_data(self, x, y):
        """Get data of the point (x,y) ,on the condition of having read all data to memory

        :param x: int
        :param y: int
        :return: List[int]
        """
        point_xy_data = []
        temp_data = self.data[self.bands * y: self.bands * y + self.bands]
        # print(len(temp_data), len(temp_data[0]))
        for sub_flow in temp_data:
            point_xy_data.append(sub_flow[x])
        return point_xy_data


if __name__ == '__main__':
    filename = "D:\\0-学习!学习!学习!学习!\\电子所里的研二研三\\高光谱相关\\测试数据\\20191023\\data\\20191023-pmma-7-max-max.raw"
    hsd = HyperSpectralData(filename)
    hsd.get_info_from_hdr_dci_file()
    print(hsd.samples)
    print(hsd.lines)
    print(hsd.bands)
    print(hsd.spectral_band)
    hsd.get_data_from_file()
    print(hsd.get_point_xy_data(100, 100))

