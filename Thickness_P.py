# 同一实验条件下，在不同角度进行光谱采样，
# 由 角度 和 共振波长 可确定 孔隙率-厚度曲线
# 两条曲线可求多孔复合膜的厚度/孔隙率
import xlrd
import numpy as np
import matplotlib.pyplot as plt
from sympy import *

import json
np.seterr(divide='ignore',invalid='ignore')


def find_positive(a):  # 找多个解中的正数,此题中仅有一个正数
    for i in a:
        try:
            if i > 0:
                return i
        except:
            pass


# 【根据Bruggman公式计算孔隙率与等效折射率关系】
# 输入参数P为孔隙率，na,nb分别为纯TiO2和空气随波长折射率数组
# 输出为当前给定孔隙率P下的等效折射率随波长变化的数组
def calc_n(P, na, nb, N):  # 传递采样率N是为了分辨json文件名
    if len(na) != len(nb):
        print("Wrong input~")
    fb = P
    # 将原bruggman方程变形，关于n 只有n^2和n^4项，因此直接用二次方程解公式，只要正实解
    # x1=n^2
    a1 = 2
    b1 = (3 * fb - 2) * na * na + (1 - 3 * fb) * nb * nb
    c1 = -na * na * nb * nb
    x1 = (-b1 + np.sqrt(b1 * b1 - 4 * a1 * c1)) / (2 * a1)
    x = list(np.sqrt(x1))

    with open('ERI/'+("%.2f" % P)+'_'+str(N)+'.json', 'w') as file_obj:
        json.dump(x, file_obj)
    return x


def effective_n(porosity, na, nb):
    if len(na) != len(nb):
        print("Wrong input~")
    fb = porosity
    # x1=n^2
    a1 = 2
    b1 = (3 * fb - 2) * na * na + (1 - 3 * fb) * nb * nb
    c1 = -na * na * nb * nb
    x1 = (-b1 + np.sqrt(b1 * b1 - 4 * a1 * c1)) / (2 * a1)
    return np.sqrt(x1)


def reflectivity_to_reflected_light(reflectivity: list):
    """
    模拟一个入射光，通过反射率求反射光
    """
    x_range = np.arange(0.0, 500.1, 0.1)
    incident_light = np.sin(np.pi / 500 * x_range)
    return incident_light*reflectivity


# 对多层介质模型，利用菲涅尔公式进行计算
# theta是入射到棱镜直角边的入射角，需转换成 棱镜-玻璃的入射角
# 然后才是四层模型， 玻璃-金膜-多孔TiO2-介质层（空气）
# 返回计算所得共振波长
def draw_spectrum_3_layers(wavelength, n_prism, n_glass, n_metal, n_detection, angle_out, d_metal, draw_mode=True):
    """
    三层结构：1棱镜(玻璃)-2金属膜-3待测物质
    draw_mode: 默认为True, 此时是绘图模式; False时只返回共振波长.
    """
    # 棱镜到玻璃计入折射, 此处angle_out为入射光入射在棱镜直角边上的角度, 人为规定有正有负, 其定义如下:
    # 入射光偏向于棱镜直角, 为正; 否则为负.
    angle_in = np.arcsin(n_prism / n_glass * np.sin(np.pi / 4 +
                                                    np.arcsin(np.sin((angle_out * np.pi / 180)) / n_prism)))
    k0 = 2*np.pi / wavelength
    beta_square = (k0 * n_glass * np.sin(abs(angle_in)))**2
    k0_square = k0**2
    e_glass = n_glass**2
    e_metal = n_metal ** 2
    e_detection = n_detection**2
    # np.sqrt不能处理纯负数的情况, 因此可以手动全部加上0j
    alpha_glass = 0 - np.sqrt(beta_square - k0_square*e_glass+0j)   # 负数的平方根，取虚部为负的解
    alpha_metal = np.sqrt(beta_square - k0_square*e_metal+0j)
    alpha_detection = np.sqrt(beta_square - k0_square*e_detection+0j)
    r12 = (e_glass*alpha_metal - e_metal*alpha_glass) / (e_glass*alpha_metal + e_metal*alpha_glass)
    r23 = (e_metal*alpha_detection - e_detection*alpha_metal) / (e_metal*alpha_detection + e_detection*alpha_metal)
    r123 = (r12 + r23 * np.exp(-2 * alpha_metal * d_metal)) / (1 + r12 * r23 * np.exp(-2 * alpha_metal * d_metal))
    # r_tm = reflectivity_to_reflected_light(abs(r123) ** 2)
    r_tm = abs(r123)**2
    resonance_wavelength_temp = 0
    for i in range(len(wavelength)-10, 10, -1):  # 从后往前求解共振deep,不然当有两个deep的时候会出错
        if r_tm[i] < 0.6 and r_tm[i] < r_tm[i - 1] and r_tm[i] < r_tm[i + 1]:
            resonance_wavelength_temp = round(wavelength[i], 2)
            # print(angle_out, '° :', round(wavelength[i], 2), 'nm  ', round(r_tm[i], 2))
            break
    if draw_mode:
        plt.plot(wavelength, r_tm)
        plt.xlim(400, 900)
        plt.ylim(-0.1, 1.1)
        plt.text(resonance_wavelength_temp, 0, str(resonance_wavelength_temp))
        plt.show()
    else:
        return resonance_wavelength_temp


def draw_spectrum_4_layers(wavelength, n_prism, n_glass, n_metal, n_enhance,
                           n_detection, angle_out, d_metal, d_enhance, draw_mode=True):
    """
    四层结构：1棱镜(玻璃)-2金属膜-3修饰增强层-4待测物. 比三层模型多了两个参数: n_enhance,d_enhance
    draw_mode: 默认为True, 此时是绘图模式; False时只返回共振波长.
    """
    angle_in = np.arcsin(
        n_prism / n_glass * np.sin(np.pi / 4 + np.arcsin(np.sin((angle_out * np.pi / 180)) / n_prism)))
    k0 = 2*np.pi / wavelength
    k0_square = k0 ** 2
    beta_square = (k0 * n_glass * np.sin(abs(angle_in))) ** 2
    e_glass = n_glass**2
    e_metal = n_metal**2
    e_enhance = n_enhance**2
    e_detection = n_detection**2
    alpha_glass = 0 - np.sqrt(beta_square - k0_square*e_glass+0j)
    alpha_metal = np.sqrt(beta_square - k0_square*e_metal+0j)
    alpha_enhance = np.sqrt(beta_square - k0_square*e_enhance+0j)
    alpha_detection = np.sqrt(beta_square - k0_square*e_detection+0j)
    r12 = (e_glass*alpha_metal - e_metal*alpha_glass) / (e_glass*alpha_metal + e_metal*alpha_glass)
    r23 = (e_metal*alpha_enhance - e_enhance*alpha_metal) / (e_metal*alpha_enhance + e_enhance*alpha_metal)
    r34 = (e_enhance*alpha_detection - e_detection*alpha_enhance) / (e_enhance*alpha_detection + e_detection*alpha_enhance)
    r234 = (r23 + r34*np.exp(-2*alpha_enhance*d_enhance)) / (1+r23*r34*np.exp(-2*alpha_enhance*d_enhance))
    r1234 = (r12 + r234*np.exp(-2*alpha_metal*d_metal)) / (1+r12*r234*np.exp(-2*alpha_metal*d_metal))
    # r_tm = reflectivity_to_reflected_light(abs(r1234)**2)
    r_tm = abs(r1234)**2

    resonance_wavelength_temp = 0
    for i in range(len(wavelength) - 10, 10, -1):
        if r_tm[i] < 0.6 and r_tm[i] < r_tm[i - 1] and r_tm[i] < r_tm[i + 1]:
            resonance_wavelength_temp = round(wavelength[i], 2)
            # print(angle_out, '° :', round(wavelength[i], 2), 'nm  ', round(r_tm[i], 2))
            break
    if draw_mode:
        plt.plot(wavelength, r_tm)
        plt.xlim(400, 900)
        plt.ylim(-0.1, 1.1)
        plt.text(resonance_wavelength_temp, 0, str(resonance_wavelength_temp))
        plt.show()
    else:
        return resonance_wavelength_temp


def draw_spectrum(x, npr, n1, n2, n3, n4, d2, theta, d3):
    label = []
    A = np.arcsin(npr / n1 * np.sin(np.pi / 4 + np.arcsin(np.sin((theta * np.pi / 180)) / npr)))  # 棱镜到玻璃计入折射
    # A=np.pi/4+np.arcsin(np.sin((   (theta)*np.pi/180))/npr ) # 棱镜到玻璃不计入折射
    k1 = 2 * np.pi / x * (n1 ** 2 - n1 ** 2 * np.sin(A) ** 2) ** 0.5
    k2 = 2 * np.pi / x * (n2 ** 2 - n1 ** 2 * np.sin(A) ** 2) ** 0.5
    k3 = 2 * np.pi / x * (n3 ** 2 - n1 ** 2 * np.sin(A) ** 2) ** 0.5
    temps = (n4 ** 2 - n1 ** 2 * np.sin(A) ** 2)
    k4 = 2 * np.pi / x * np.array([(round(float(temp), 6)) ** 0.5 for temp in temps])

    r12 = ((n2 ** 2) * k1 - (n1 ** 2) * k2) / ((n2 ** 2) * k1 + (n1 ** 2) * k2)
    r23 = ((n3 ** 2) * k2 - (n2 ** 2) * k3) / ((n3 ** 2) * k2 + (n2 ** 2) * k3)
    r34 = ((n4 ** 2) * k3 - (n3 ** 2) * k4) / ((n4 ** 2) * k3 + (n3 ** 2) * k4)
    # r34 = np.zeros(5001)
    r234 = (r23 + r34 * np.exp(1j * 2 * k3 * d3)) / (1 + r23 * r34 * np.exp(1j * 2 * k3 * d3))
    # np.exp()可以对数组直接进行运算，但是要注意前面用sympy求解的结果需要转换成普通float
    r1234 = (r12 + r234 * np.exp(1j * 2 * k2 * d2)) / (1 + r12 * r234 * np.exp(1j * 2 * k2 * d2))

    RTM = abs(r1234) ** 2

    plt.plot(x, RTM)
    # plt.xlim(400, 900)
    # plt.ylim(-0.1,1.1)

    wavelength_temp = 0
    for i in range(len(x)-10, 10, -1):  # 从后往前求解共振deep,不然当有两个deep的时候会出错
        if RTM[i] < RTM[i - 1] and RTM[i] < RTM[i + 1]:
            wavelength_temp = round(x[i], 2)
            print(theta, '° :', round(x[i], 2), 'nm  ', round(RTM[i], 2))
            break

    label.append('TM ' + str(theta) + '°')
    plt.legend(label, loc=4, ncol=1)
    # plt.axvline(wavelength_temp)
    plt.text(wavelength_temp,0,str(wavelength_temp))

    # plt.show()
    return wavelength_temp


# 读取excel的数据，包括波长、各层随波长的折射率等
def read_excel(filepath, N):
    filename = filepath
    # data = xlrd.open_workbook('reference.xlsx')
    data = xlrd.open_workbook(filename)
    table = data.sheets()[0]
    begin = 30  # 400-900nm
    end = -1
    x = np.array(table.col_values(0)[begin:end])  # 波长
    d2 = 40  # 金膜厚度
    # d3 = 260  #多孔TiO2层厚度
    npr = np.array(table.col_values(1)[begin:end])  # 棱镜折射率
    n1 = np.array(table.col_values(2)[begin: end])  # 玻璃折射率
    n2_real = np.array(table.col_values(3)[begin:end])  # Au实部
    n2_imag = np.array(table.col_values(4)[begin:end])  # Au虚部
    n2 = n2_real + 1j * n2_imag  # Au折射率

    n_tio2 = np.array(table.col_values(6)[begin:end])  # TiO2折射率     na
    n4 = np.array(table.col_values(7)[begin:end])  # 空气折射率     nb
    # n3 = np.array( table.col_values(27)[begin:end])          #TiO2层等效折射率,由na和nb计算而来

    N = N  # 对数据进行每隔N点采一个点的下采样,N>1时才采样
    if N>1:
        x = np.array([x[i] for i in range(0, len(x), N)])
        npr = np.array([npr[i] for i in range(0, len(npr), N)])
        n1 = np.array([n1[i] for i in range(0, len(n1), N)])
        n2 = np.array([n2[i] for i in range(0, len(n2), N)])
        n_tio2 = np.array([n_tio2[i] for i in range(0, len(n_tio2), N)])
        # n3=np.array([n3[i] for i in range(0,len(n3),N)])
        n4 = np.array([n4[i] for i in range(0, len(n4), N)])
    print("Total length of datas:", len(x))
    return x,npr,n1,n2,n_tio2,n4,d2


# 对给定的入射角度和共振波长，遍历孔隙率列表，计算出一串P-T数据对，绘制曲线
def calc_thickness(x, npr, n1, n2, n_tio2, n4,d2,N,
                   P_list, d_start, accurary, theta, wavelength):
    # 给定入射角，给定所要拟合寻找的共振波长
    theta = theta  # 这个入射角度是指棱镜面上，需转换到玻璃
    wavelength0 = wavelength
    P_list = P_list
    d3_list = []

    temp = d_start
    for i in range(len(P_list)):
        # TiO2层等效折射率n3由calc_n(P,n_tio2,n4)计算而来
        P = round(P_list[i], 2)
        print('-------------------------------------------------------------  P= ', P)
        try:  # 对每一个孔隙率P，先尝试读取json文件，如果没有就重新计算等效折射率n数组
            filename = 'ERI/'+("%.2f" % P) + '_' + str(N) + '.json'
            print(filename)
            with open(filename, 'r') as file_obj:
                n3 = np.array(json.load(file_obj))
        except:
            n3 = np.array(calc_n(P, n_tio2, n4, N))
        print('------------------------')
        # d3_start = d_start[i]
        # d3 = d3_start + 5
        d3 = temp  #
        print('-------temp: ',temp)
        if_find_flag = 0
        while True:
            # 基于P-T曲线都是单增的
            # 对给定的起始d3，每次增5，往上扫描，
            # 计算当前d3对应的共振波长，与给定共振波长比较，进而求得一个大致的范围
            print('d3= ', d3)
            ans = draw_spectrum(x, npr, n1, n2, n3, n4, d2, theta, d3)
            print('resonance wavelength :', ans)
            if abs(ans - wavelength0) < accurary:  # 要更高的精确度
                print('The best thickness when P=' + str(P) + " is: ", d3)
                d3_list.append(round(d3,2))
                if_find_flag = 1
                temp = int(d3)#
                print('-------temp: ', temp)
                break
            if ans < wavelength0:
                print('smaller\n--------')
                d3_start = d3
                d3 = d3 + 5
            else:
                print('bigger\n--------')
                d3_min = d3_start
                d3_max = d3
                d3 = round((d3_min + d3_max) / 2, 4)
                while True:
                    # 当求得一个囊括给定共振波长范围时，利用二分法进一步获得准确的数值
                    print('d3= ', d3)
                    ans = draw_spectrum(x, npr, n1, n2, n3, n4, d2, theta, d3)
                    print('resonance wavelength :', ans)
                    if abs(ans - wavelength0) < accurary:  # 要更高的精确度
                        print('The best thickness when P=' + str(P) + " is: ", d3)
                        d3_list.append(round(d3,2))
                        if_find_flag = 1
                        temp=int(d3) #
                        print('-------temp: ',temp)
                        break
                    if ans > wavelength0:
                        print('bigger\n--------')
                        d3_max = d3
                        d3 = round((d3_min + d3) / 2, 4)
                    else:
                        print('smaller\n--------')
                        d3_min = d3
                        d3 = round((d3_max + d3) / 2, 4)
            if if_find_flag:
                break
    print(d3_list)  # 对给定的入射角度和共振波长，打印出一串P-T数据对，绘制曲线
    return d3_list
################################################


def my_plot(x, A):  # 两两相交求交点,A包含两个列表
    for a in A:
        plt.plot(x,a)
    abs_delta = (abs(A[0]-A[1]))
    temp = min(abs_delta)
    for i in range(len(abs_delta)):
        if abs_delta[i] == temp:
            print(i, x[i], A[0][i], A[1][i])
            temp_y = round((A[0][i]+A[1][i])/2, 2)
            temp_y = ("%.2f" % temp_y)
            plt.scatter(float(x[i]), float(temp_y), c='red', s=8)
            temp_x = ("%.2f" % x[i])
            plt.text(x[i], A[0][i]-20, '('+str(temp_x )+' , '+str(temp_y)+')')

            return temp_x, temp_y


def assess_data(A): #计算数组A的均值、标准差、相对标准差作为评估
    u = np.mean(A)
    sd = np.std(A, ddof=0)
    rsd = (sd / u) * 100
    print('---------------')
    print('average: ' + ('%.3f' % u))
    print('sd: '+('%.3f' % sd))
    print('rsd: '+('%.3f' % rsd)+'%')
    print('---------------')
    return u, sd, rsd


def calc_main(theta_list, wavelength_list, d_start, P_list, accuracy):
    N = 1
    datas = read_excel('reference.xlsx', N)  # 第二个参数为采样率
    angle = []
    t_list = []

    fitted_p_list = np.arange(P_list[0],P_list[-1], 0.001)
    fitted_t_list = []
    for i in range(len(theta_list)):    # 对每一个角度
        angle.append(str(theta_list[i]) + '°')

        t_temp = calc_thickness(datas[0],datas[1],datas[2],datas[3],datas[4],datas[5],datas[6],N,
                         P_list, d_start, accuracy, theta_list[i], wavelength_list[i])
        t_list.append(t_temp)   # 计算一些(孔隙率，最佳厚度)数据对
        z_temp = np.polyfit(P_list, t_temp, 6)
        p_temp = np.poly1d(z_temp)
        fitted_t_list.append(p_temp(fitted_p_list))  # 拟合成更加紧密的曲线

    print('=======================================')  # 显示
    for i in range(len(t_list)):
        print(angle[i], t_list[i])
    print('=======================================')

    fig_num = 0
    intersection_x = [] # 存储交点的x/y坐标
    intersection_y = []
    for i in range(len(fitted_t_list)-1):
        for j in range(i+1, len(fitted_t_list)):
            print(i, j)
            fig = plt.figure(fig_num)
            fig_num = fig_num+1
            A = [fitted_t_list[i], fitted_t_list[j]]
            label = [angle[i], angle[j]]
            result = my_plot(fitted_p_list, A)
            intersection_x.append(float(result[0]))
            intersection_y.append(float(result[1]))
            # plt.xlim(0.1, 0.75)
            # plt.ylim(100, 600)
            plt.xlabel('$P$')
            plt.ylabel('$d$ /nm')
            plt.legend(label)
            filename = angle[i]+'_'+angle[j]
            try:
                plt.savefig('C:/Users/yintao/Desktop/' + filename + '.png')
            except:
                plt.savefig(filename+'.png')
    print('---')
    # plt.show()
    print('+++')
    print(intersection_x)
    print(intersection_y)
    assess_data(intersection_x)
    assess_data(intersection_y)
    print('--finish--')
    return intersection_x, intersection_y

#                         计算每组数据并绘图
#                        【在这下面修改参数】
#
# theta_list =             [11,10,9
#                                 ]
# wavelength_list = [
#                                 733.34,744.38,755.41
#                                 ]
# accuracy=0.1 #搜索精度，若枚举出来的共振波长与给定波长相差低于这个数则认为此厚度最佳，搜索完成
# d_start=60 #给第一个搜索的孔隙率选取一个合适的搜索起始厚度，后面孔隙率的起始厚度从前面最佳厚度往上搜索(默认P-T曲线单增)
# P_list=[
#             # 0.10,0.15,0.20,0.25,0.30,0.35,0.40,0.45,0.46,0.47,0.48,0.49,
#          0.50,0.51, 0.52, 0.53, 0.54, 0.55, 0.56, 0.57, 0.58, 0.59, 0.60, 0.61, 0.62, 0.63,
#                  0.64, 0.65, 0.66, 0.67, 0.68, 0.69, 0.70, 0.71, 0.72]
# # calc_main(theta_list, wavelength_list, d_start, P_list, accuracy)
# datas=read_excel('reference.xlsx',1)


def calculate_porosity_thickness_curve_intersection(wavelength, n_prism, n_glass, n_metal, n_enhance,
                                                    angle_out, d_metal, d_start, p_start, p_end, n_detection_conditions,
                                                    target_resonance_wavelength_conditions: tuple) -> tuple:
    """
    计算孔隙率-厚度曲线, 求出不同条件下的曲线交点
    """
    porosity_range = np.arange(p_start, p_end, 0.01)
    accuracy = 0.1  # 仿真中由于波长分辨率为0.1nm, 因此accuracy≤0.1nm时效果都一样
    # plt.ion()
    # label = []
    results = []
    for i in range(len(n_detection_conditions)):
        target_resonance_wavelength_condition = target_resonance_wavelength_conditions[i]
        n_detection_condition = np.full(5001, n_detection_conditions[i])
        # label.append("%.2f" % n_detection_conditions[i])
        d_enhance = d_start
        d_enhance_result = []
        for porosity in porosity_range:
            find_flag = False
            effective_n3 = effective_n(porosity, n_enhance, n_detection_condition)
            while True:
                ans = draw_spectrum_4_layers(wavelength, n_prism, n_glass, n_metal, effective_n3,
                                             n_detection_condition, angle_out, d_metal, d_enhance, draw_mode=False)
                if abs(ans - target_resonance_wavelength_condition) <= accuracy:
                    d_enhance_result.append(round(d_enhance, 2))
                    break
                elif ans < target_resonance_wavelength_condition:
                    d_enhance += 10
                else:
                    d_max = d_enhance
                    d_min = d_enhance - 10
                    while True:
                        d_enhance = round((d_max + d_min) / 2, 4)
                        ans = draw_spectrum_4_layers(wavelength, n_prism, n_glass, n_metal, effective_n3,
                                                     n_detection_condition, angle_out, d_metal, d_enhance,
                                                     draw_mode=False)
                        if abs(ans - target_resonance_wavelength_condition) <= accuracy:
                            d_enhance_result.append(round(d_enhance, 2))
                            find_flag = True
                            break
                        elif ans < target_resonance_wavelength_condition:
                            d_min = d_enhance
                        else:
                            d_max = d_enhance
                if find_flag:
                    break
        results.append(d_enhance_result)
        # plt.plot(porosity_range, d_enhance_result)
        # plt.legend(label)
        # plt.pause(0.5)
    my_max = 9999
    my_min_index = 0
    for i in range(len(results[0])):
        if abs(results[0][i] - results[1][i]) < my_max:
            my_min_index = i
            my_max = abs(results[0][i] - results[1][i])
    best_porosity = porosity_range[my_min_index]
    best_thickness = round((results[0][my_min_index] + results[1][my_min_index])/2, 2)

    # plt.scatter(porosity_range[my_min_index], best_thickness, c='red')
    # plt.pause(0.5)
    # plt.plot(porosity_range, np.array(results[0]) - np.array(results[1]))
    # plt.axhline(0, xmin=0.1, xmax=0.9)
    # label.append("Delta")
    # plt.legend(label)
    # plt.ioff()
    # plt.show()

    return best_porosity, best_thickness
