from scipy.interpolate import RegularGridInterpolator
import numpy
from decimal import Decimal


class Interpolator2d:
    def __init__(self, x_grid: list, y_grid: list, values: numpy.array):
        self.regular_grid_interpolator = RegularGridInterpolator((x_grid, y_grid), values)

    def __call__(self, x_y_tuples: list):
        return [self.__interpolate(xy[0], xy[1]) for xy in x_y_tuples]

    def __interpolate(self, x: float, y: float):
        x_grid, y_grid = self.regular_grid_interpolator.grid
        if x < x_grid[0]:
            x = float(x_grid[0])
        elif x > x_grid[-1]:
            x = float(x_grid[-1])
        if y < y_grid[0]:
            y = float(y_grid[0])
        elif y > y_grid[-1]:
            y = float(y_grid[-1])

        return self.regular_grid_interpolator([[x, y]])[0]
