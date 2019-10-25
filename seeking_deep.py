"""
Seek resonance wavelength.
"""
import matplotlib.pyplot as plt
import numpy as np


def show_deep(x, y, fit_order=4, fit_range=25, section=None, manual_point=None):
    """
    Calculate the resonance wavelength of given data (x[], y[]),
    In case of hyper spectrum, array only contains 100-200 numbers(bands).

    :param x:  List[num]
    :param y:  List[num]
    :param fit_order:  int
    :param fit_range:  int
    :param section: Tuple -- (r1, r2)
    :param manual_point: int -- manually give an approximate point, so that we find deep after it.
    :return: (num0, num1, List2, List3)
    --------
    num0:    resonance wavelength after fitted
    num1:    amplitude at resonance wavelength
    List2:      fitted x[] around resonance wavelength
    List3:      fitted y[] around resonance wavelength
    --------
    """
    x1 = x.copy()
    y1 = y.copy()

    smooth_order = 3
    for i in range(smooth_order):
        y1 = mean_smooth(y1)

    # Firstly, find a rough estimate of resonance wavelength(relative minimum value).
    # Secondly, if a rough estimate is found, take a section around it out for fitting.
    # if manual_point:
    #     section = (manual_point - 20, manual_point + 20)
    if not section:
        temp = find_min(x1, y1, manual_point)
        if not temp:
            return False

        length = fit_range  # unit : (nm)
        index = cut_list(x1, x1[temp[0]] - length, x1[temp[0]] + length)
        cut_x = x[index[0]: index[1]]
        cut_y = y[index[0]: index[1]]
        #   here has to use 'y' not 'y1', cause 'y1' has been smoothed.
    else:
        # if a section is assigned manually to correct .
        index = cut_list(x, section[0], section[1])
        cut_x = x[index[0]: index[1]]
        cut_y = y[index[0]: index[1]]

    cut_x = np.array(cut_x)
    cut_y = np.array(cut_y)
    z = np.polyfit(cut_x, cut_y, fit_order)
    p = np.poly1d(z)
    # z: Polynomial coefficients
    # p: polynomial equation

    sampling_precision = 0.01
    fitted_x = np.arange(cut_x[0], cut_x[-1], sampling_precision)
    fitted_y = p(fitted_x)

    min_y = min(fitted_y)
    resonance_wavelength = 0
    resonance_amplitude = 0
    for i in range(0, len(fitted_x)):
        if fitted_y[i] == min_y:
            resonance_wavelength = fitted_x[i]
            resonance_amplitude = fitted_y[i]
            break
    return round(resonance_wavelength, 2), resonance_amplitude, fitted_x, fitted_y


def cut_list(list_a, x1, x2):
    """
    Give an increasing sequence, find the chosen section which satisfy: x1<x<x2.

    :param list_a:   List[num]
    :param x1:       num
    :param x2:       num
    :return:    Tuple, index at start and end
    """
    index1 = index2 = 0
    for i in range(len(list_a)):
        if list_a[i] < x1:
            pass
        else:
            index1 = i
            break
    if list_a[-1] < x2:
        return index1, -1
    for i in range(index1, len(list_a)):
        if list_a[i] < x2:
            pass
        else:
            index2 = i
            break
    return index1, index2


def mean_smooth(data_y):
    """Median Filter
    Smooth the data before next step of processing to reduce errors
    :param data_y:  List[num]
    :return:               List[num]
    """
    temp = data_y
    for i in range(1, len(data_y) - 1):
        temp[i] = (data_y[i - 1] + data_y[i + 1]) / 2
    return temp


def find_min(list_x, list_y, start_from):
    """
    rough estimate of relative minimum value
    start_from: find deep from value-start_from, it's wavelength, not index.
    """
    sampling_interval = len(list_y) // 170
    new_list_x = [list_x[i] for i in range(0, len(list_x), sampling_interval)]
    new_list_y = [list_y[i] for i in range(0, len(list_y), sampling_interval)]
    start_point = 10
    while start_from and new_list_x[start_point] < start_from:
        start_point += 1
    for i in range(start_point, len(new_list_y)):
        if new_list_y[i - 1] < new_list_y[i] or new_list_y[i + 1] < new_list_y[i]:
            pass
        else:
            if new_list_y[i - 2] > new_list_y[i] and new_list_y[i + 2] > new_list_y[i]:
                if new_list_y[i - 3] > new_list_y[i] and new_list_y[i + 3] > new_list_y[i]:
                    return i * sampling_interval, new_list_y[i]


if __name__ == '__main__':
    # filename="C:/Users/yintao/Desktop/495,340"
    # num_list=[]
    # with open(filename, 'r') as file_obj:
    #     for f in file_obj:
    #         temp=f.strip().split(' ')[-1]
    #         try:
    #             num=float(temp)
    #             num_list.append(num)
    #         except:
    #             pass
    spectral_band = [
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
    point_xy = [
        800, 800, 904, 964, 1024, 1096, 1124, 1300, 1396, 1456, 1584, 1884, 1812, 2028, 2232, 2396, 2724,
        2608, 2816, 3024, 3264, 3552, 3668, 3868, 4312, 3932, 4276, 4844, 5108, 5480, 5912, 6316, 6732,
        6920, 7488, 8244, 9312, 9484, 10616, 10932, 12216, 12372, 13976, 15384, 15256, 16208, 17096,
        19020, 20816, 23108, 24840, 25940, 26376, 26612, 29268, 30492, 32800, 33596, 34548, 35528,
        37224, 38388, 38676, 40016, 41132, 41976, 43380, 46876, 49236, 50796, 50208, 50468, 50700,
        50668, 50500, 49824, 48416, 46140, 45536, 44016, 43360, 43300, 44368, 47588, 50296, 51744,
        55720, 57640, 57660, 56088, 54292, 50576, 47084, 42732, 33768, 23032, 13700, 7264, 4020, 2608,
        1552, 1136, 908, 676, 700, 576, 452, 544, 452, 500, 428, 368, 424, 452, 404, 480, 348, 436, 500, 448,
        384, 428, 508, 432, 384, 496, 332, 368, 480, 348, 344, 468, 408, 396, 504, 468, 492, 404, 428, 404, 456,
        452, 484, 344, 444, 424, 404, 428, 376, 504, 512, 424, 592, 488, 448, 664, 456, 468, 472, 636, 416, 584, 500,
        476, 412, 504, 356, 556, 452, 480, 588, 528, 544, 540, 500, 460]

    a = show_deep(spectral_band, point_xy)
    plt.plot(spectral_band, point_xy)
    plt.axvline(a[0], c='red', alpha=0.5)
    plt.plot(a[2], a[3])
    plt.text(500, 0.2, "resonance wavelength=" + str(a[0]) + "nm")
    plt.show()
