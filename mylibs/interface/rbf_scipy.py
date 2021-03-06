__author__ = "Juri Bieler"
__version__ = "0.0.1"
__email__ = "juribieler@gmail.com"
__status__ = "Development"

# ==============================================================================
# description     :n-dimensional rbf interface to scipy RBF implementation
# date            :2018-07-23
# version         :0.01
# notes           :
# python_version  :3.6
# ==============================================================================

'''
'multiquadric': sqrt((r/self.epsilon)**2 + 1)
'inverse': 1.0/sqrt((r/self.epsilon)**2 + 1)
'gaussian': exp(-(r/self.epsilon)**2)
'linear': r
'cubic': r**3
'quintic': r**5
'thin_plate': r**2 * log(r)
'''

from scipy.interpolate import Rbf
import numpy as np


class RBFscipy:

    def __init__(self, known_in, known_val):
        """
        :param known_in: list of lists with input sample points
        :param known_val: list of results for the known_in
        """
        self._known_in = np.array(known_in.copy())
        self._known_val = np.array(known_val.copy())
        self._k = self._known_in.shape[1]
        self._n = self._known_in.shape[0]
        self._rbf = 'linear'
        self._rbf_const = 1.
        self._f = None
        self._offsets = np.zeros((self._k))
        self._scalers = np.zeros((self._k))

    def train(self):
        pass

    def update_param(self, rbf_const, rbf_name):
        self._rbf_const = rbf_const
        self._rbf = rbf_name
        self.calc_rbf()

    def calc_rbf(self):
        if self._k == 1:
            self._f = Rbf(self._known_in[:,0], self._known_val, function=self._rbf, epsilon=self._rbf_const)
        elif self._k == 2:
            self._f = Rbf(self._known_in[:,0], self._known_in[:,1], self._known_val, function=self._rbf, epsilon=self._rbf_const)
        elif self._k == 3:
            self._f = Rbf(self._known_in[:,0], self._known_in[:,1], self._known_in[:,2], self._known_val, function=self._rbf, epsilon=self._rbf_const)

    def predict(self, x_pred):
        if self._k == 1:
            return self._f(x_pred[0])
        elif self._k == 2:
            return self._f(x_pred[0], x_pred[1])
        elif self._k == 3:
            return self._f(x_pred[0], x_pred[1], x_pred[2])


if __name__ == '__main__':
    r = RBFscipy(np.array([[0,2,4,6,8],[1,2,3,4,5]]).T, [1,2,1,0,1])
    r.update_param(1., 'linear')
    print('done')