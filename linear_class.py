import random
from fractions import Fraction


class Linear:
    def __init__(self, m, b):
        self.m = Fraction(m)
        self.b = Fraction(b)

    @classmethod
    def from_2_points(cls, x1, y1, x2, y2):
        m = (y2 - y1) / (x2 - x1)
        m = Fraction(m).limit_denominator(100)
        b = (y1 - (m * x1))
        b = Fraction(b).limit_denominator(100)
        return cls(m, b)

    def randomize(self):
        self.m = random.randint(-10, 10)
        self.b = random.randint(-10, 10)

    def get_slope(self):
        return self.m

    def get_x_int(self):
        return -1*self.b / self.m

    def get_y_int(self):
        return self.b

    def get_display(self):
        return 'y = {}x + {}'.format(self.m, self.b)

    def eval_for_x(self, x):
        return self.m * x + self.b

    def solve_given_y(self, y):
        return (y - self.b) / self.m
