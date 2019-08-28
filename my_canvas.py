# !usr/bin/env python
# -*- coding:utf-8 -*-
# # @Author: Yin Tao
# @File: my_canvas.py
# @Time: 2019/08/20
# 
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtCore import *
import matplotlib
matplotlib.use("Qt5Agg")


class MyCanvas(FigureCanvas):
    """
    Overload FigureCanvas class, for doing something else about it.
    """
    my_signal = pyqtSignal()

    def __init__(self):
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        FigureCanvas.__init__(self, self.fig)

        # parameters about selection.
        # (x1, y1) coordinate of left upper corner
        # (x2, y2) coordinate of right bottom corner
        self.press_flag = False
        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0

        # signals and slots
        self.fig.canvas.mpl_connect("button_press_event", self.call_back)

    def call_back(self, event):
        if event.button == 2:  # mid button of mouse
            self.ax.scatter(event.xdata, event.ydata, color='red', s=10)
            self.fig.canvas.draw_idle()

    def my_plot(self, x_data, y_data):
        self.ax.plot(x_data, y_data)

    def my_draw(self, data, color_map="gray", title='', extent=None):
        """
        Display gray image from 2-D array.
        """
        self.ax.clear()
        self.ax.imshow(data, cmap=color_map, extent=extent)
        self.fig.suptitle(title)
        self.draw()

    def my_draw_rectangle(self, x1, y1, x2, y2):
        """
        Draw selection area over the gray image.
        """
        self.ax.plot([x1, x2], [y1, y1], c='red', alpha=0.5)
        self.ax.plot([x1, x2], [y2, y2], c='red', alpha=0.5)
        self.ax.plot([x2, x2], [y1, y2], c='red', alpha=0.5)
        self.ax.plot([x1, x1], [y1, y2], c='red', alpha=0.5)
        self.fig.canvas.draw_idle()

    def my_clear_lines(self):
        """
        clear all matplotlib.lines.Line2D objects
        """
        if self.ax.lines:
            self.ax.lines.clear()
            self.draw()
