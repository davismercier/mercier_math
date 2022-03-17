import math


class Quadratic:

    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

    @classmethod
    def from_a_and_roots(cls, a, x_1, x_2):
        b = a * ((-1 * x_1) + (-1 * x_2))
        c = a * x_1 * x_2
        return cls(a, b, c)

    @classmethod
    def from_a_and_vertex(cls, a, x_coor, y_coor):
        b = a * -2 * x_coor
        c = a * x_coor**2 + y_coor
        return cls(a, b, c)

    def standard_form(self):
        return '{}x^2 + {}x + {}'.format(self.a, self.b, self.c)

    def get_vertex(self):
        x = (-1 * self.b) / (2 * self.a)
        y = (self.a * x * x) + (self.b * x) + self.c
        return x, y

    def get_roots(self):
        try:
            x_1 = (-1 * self.b + math.sqrt(self.b**2 - 4 * self.a * self.c)) / (2 * self.a)
        except Exception:
            x_1 = "imaginary root"
        try:
            x_2 = (-1 * self.b - math.sqrt(self.b**2 - 4 * self.a * self.c)) / (2 * self.a)
        except Exception:
            x_2 = "imaginary root"
        return x_1, x_2

    def eval_for_x(self, x):
        return self.a * x * x + self.b * x + self.c

    def get_y_int(self):
        return self.c


