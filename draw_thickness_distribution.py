# !usr/bin/env python
# -*- coding:utf-8 -*-
# # @Author: Yin Tao
# @File: draw_thickness_distribution.py
# @Time: 2019/09/16
# 


import numpy as np
import matplotlib.pyplot as plt
from Thickness_P import calculate_porosity_thickness_curve_intersection


if __name__ == '__main__':
    x = np.load("RI\\wavelength.npy")
    npr = np.load("RI\\prism.npy")
    n1 = np.load("RI\\glass.npy")
    n2 = np.load("RI\\Au_n.npy") + 1j*np.load("RI\\Au_k.npy")
    n3 = np.load("RI\\tio2.npy")
    d2 = 50
    theta = 10
    d3_start = 100
    p_start = 0.00
    p_end = 0.61
    n4_conditions = [1.33, 1.36]
    rand = np.random.uniform(-1, 1)
    target_resonance_conditions = [616.8+rand, 645.1+rand]  # [599.1, 645.1]

    N = 5
    resonance_wavelength_condition1 = [[0.0 for _ in range(N)] for _ in range(N)]
    resonance_wavelength_condition2 = [[0.0 for _ in range(N)] for _ in range(N)]

    thickness = [[0.0 for _ in range(N)] for _ in range(N)]
    original_thickness_matrix = [[0.0 for _ in range(N)] for _ in range(N)]
    porosity = [[0.0 for _ in range(N)] for _ in range(N)]
    original_thickness = [140, 142, 144, 146, 148, 150, 152, 154, 156, 158]
    targets = [(589.3, 613.6), (594.7, 619.8), (600.1, 626.1), (605.6, 632.4), (611.2, 638.8),
               (616.8, 645.1), (622.5, 651.5), (628.2, 657.8), (634.0, 664.2), (639.7, 670.6)]
    import time
    t1 = time.time()
    for i in range(N):
        for j in range(N):
            rand_index = np.random.randint(0, 10)
            rand = np.random.uniform(-1, 1)
            resonance_wavelength_condition1[i][j] = targets[rand_index][0] + rand
            resonance_wavelength_condition2[i][j] = targets[rand_index][1] + rand
            original_thickness_matrix[i][j] = original_thickness[rand_index]
            target_resonance_conditions = [resonance_wavelength_condition1[i][j], resonance_wavelength_condition2[i][j]]
            res = calculate_porosity_thickness_curve_intersection(x, npr, n1, n2, n3, theta, d2, d3_start, p_start,
                                                                  p_end, n4_conditions, target_resonance_conditions)
            porosity[i][j] = res[0]
            thickness[i][j] = res[1]
            print("original_thickness:", original_thickness[rand_index])
            print("({i}, {j})=".format(i=i, j=j), res)
    np.save('condition1.npy', resonance_wavelength_condition1)
    np.save('condition2.npy', resonance_wavelength_condition2)
    plt.figure("condition1")
    plt.imshow(resonance_wavelength_condition1)
    plt.colorbar()
    plt.figure("condition2")
    plt.imshow(resonance_wavelength_condition2)
    plt.colorbar()
    plt.figure("original-thickness")
    plt.imshow(original_thickness_matrix, cmap=plt.get_cmap('rainbow'), vmin=130, vmax=170)
    plt.colorbar()
    plt.figure("calculated-thickness")
    plt.imshow(thickness, cmap=plt.get_cmap('rainbow'), vmin=130, vmax=170)
    plt.colorbar()
    plt.figure("Delta")
    plt.imshow(np.array(thickness)-np.array(original_thickness_matrix), cmap=plt.get_cmap('rainbow'), vmin=-10, vmax=10)
    plt.colorbar()
    plt.figure("calculated-porosity")
    plt.imshow(porosity, cmap=plt.get_cmap('rainbow'), vmin=0.1, vmax=0.6)
    plt.colorbar()
    t2 = time.time()
    print("Time Used: ", t2-t1)
    plt.show()
