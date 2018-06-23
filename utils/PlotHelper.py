
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import rc
import matplotlib
import numpy as np


class PlotHelper:

    def __init__(self, axis_labels, fancy=False):
        self.FONT_SIZE = 14
        self.font = {'family': 'sans-serif', 'size': self.FONT_SIZE}
        if len(axis_labels) == 2:
            self.fig, self.ax = plt.subplots()
            self.ax.set_xlabel(axis_labels[0], fontdict=self.font)
            self.ax.set_ylabel(axis_labels[1], fontdict=self.font)
            rc('xtick', labelsize=self.FONT_SIZE)
            rc('ytick', labelsize=self.FONT_SIZE)
        elif len(axis_labels) == 3:
            self.fig = plt.figure()
            self.ax = self.fig.gca(projection='3d')
            self.ax.set_xlabel(axis_labels[0], fontdict=self.font)
            self.ax.set_ylabel(axis_labels[1], fontdict=self.font)
            self.ax.set_zlabel(axis_labels[2], fontdict=self.font)
            rc('xtick', labelsize=self.FONT_SIZE)
            rc('ytick', labelsize=self.FONT_SIZE)
            #rc('ztick', labelsize=self.FONT_SIZE)
            #self.ax.xaxis._axinfo['label']['space_factor'] = 4
        else:
            raise ValueError('length of axis_labels should be 2(D) or 3(D)')
        self.ax.tick_params(labelsize=self.FONT_SIZE, length=6, width=2)
        if fancy:
            rc('text', usetex=True)
        rc('font', **self.font)

    def finalize(self, width=8, height=5):
        self.ax.legend()
        self.fig.set_size_inches(width, height)
        self.ax.autoscale_view(tight=True)

    def save(self, file_path):
        plt.savefig(file_path)

    def show(self):
        plt.show()

    def animate(self):
        for angle in np.linspace(0, 360, 1000):
            self.ax.view_init(30, angle)
            plt.draw()
            #print(str(angle))
            plt.pause(.001)