from linear_class import Linear
from quadratic_class import Quadratic
import random


# receives string parameter specifying type of equation object to be instantiated
# returns equation object
def make_equation_of_type(equation_type):

    if equation_type == "Linear":
        m = random.randint(-9, 9)
        b = random.randint(-9, 9)
        equation = Linear(m, b)
    elif equation_type == "Quadratic":
        a = random.randint(-9, 9)
        b = random.randint(-9, 9)
        c = random.randint(-9, 9)
        equation = Quadratic(a, b, c)
    return equation


# accepts any number of arguments that represent variables
# returns a dictionary of these variables, each assigned a random value
def make_random_values_dict(*variables):
    random_values_dict = {}

    for variable in variables:
        random_values_dict[variable] = random.randint(-9, 9)
        while random_values_dict[variable] == 0:
            random_values_dict[variable] = random.randint(-9, 9)
    return random_values_dict


class Question:
    all_questions = {}
    categories = []
    question_templates = {}

    def __init__(self, id, category, title, instructions):
        self.id = id
        self.category = category
        self.title = title
        self.instructions = instructions
        # add every question created to a class level dictionary
        Question.all_questions[self.id] = self
        # if the question is of a new category/type, add this to the class level dictionary of categories
        if self.category not in Question.categories:
            Question.categories.append(self.category)

    def regenerate(self):
        Question.all_questions[self.id] = Question.question_templates[self.id]()


class EquationSingleValueAnswer(Question):
    def __init__(self, id, category, title, instructions, equation_to_display, answer, margin_of_error):
        super().__init__(id, category, title, instructions)
        self.equation_to_display = equation_to_display
        self.answer = answer
        self.margin_of_error = margin_of_error

    # accepts answer from user and checks if it falls within the margin of error from the question answer
    def grade(self, user_answer):
        if (user_answer >= self.answer - self.margin_of_error) and (user_answer <= self.answer + self.margin_of_error):
            return True
        else:
            return False


# This type of question is still in development
class GraphEquation(Question):
    def __init__(self, id, category, title, instructions, equation, answer):
        super().__init__(id, category, title, instructions)
        self.equation = equation
        self.answer = answer


def question_1():
    m = random.randint(-9, 9)
    b = random.randint(-9, 9)
    equation = Linear(m, b)

    x = random.randint(-9, 9)

    q1 = EquationSingleValueAnswer(
        1,
        'Linear Equations',
        'Evaluate Linear Equation',
        'Evaluate the equation below for the value x = {}'.format(x),
        equation.get_display(),
        equation.eval_for_x(x),
        0
    )
    return q1


def question_2():
    m = random.randint(-9, 9)
    b = random.randint(-9, 9)
    equation = Linear(m, b)

    q2 = EquationSingleValueAnswer(
        2,
        'Linear Equations',
        'Find Slope of Linear Equation',
        'Find the slope of the following equation',
        equation.get_display(),
        equation.get_slope(),
        0
    )
    return q2


def question_3():
    m = random.randint(-9, 9)
    b = random.randint(-9, 9)
    equation = Linear(m, b)

    q3 = EquationSingleValueAnswer(
        3,
        'Linear Equations',
        'Find Y-Int of Linear Equation',
        'Find the y-intercept of the following equation',
        equation.get_display(),
        equation.get_y_int(),
        0
    )
    return q3


def question_4():
    a = random.randint(-9, 9)
    b = random.randint(-9, 9)
    c = random.randint(-9, 9)
    equation = Quadratic(a, b, c)

    x = random.randint(-9, 9)

    q4 = EquationSingleValueAnswer(
        4,
        'Quadratic Equations',
        'Evaluate Quadratic Equation',
        'Evaluate the equation below for the value x = {}'.format(x),
        equation.standard_form(),
        equation.eval_for_x(x),
        0
    )
    return q4


def question_5():
    a = random.randint(-9, 9)
    b = random.randint(-9, 9)
    c = random.randint(-9, 9)
    equation = Quadratic(a, b, c)

    q5 = EquationSingleValueAnswer(
        5,
        'Quadratic Equations',
        'Find Y-Int of Quadratic Equation',
        'Find the y-intercept of the following equation',
        equation.standard_form(),
        equation.get_y_int(),
        0
    )
    return q5


Question.question_templates[1] = question_1
Question.question_templates[2] = question_2
Question.question_templates[3] = question_3
Question.question_templates[4] = question_4
Question.question_templates[5] = question_5

question_1()
question_2()
question_3()
question_4()
question_5()

print('Questions.py executed in full')


# Below are questions of quadratic type that are not ready for deployment

# a = random.randint(-10, 10)
# b = random.randint(-10, 10)
# c = random.randint(-10, 10)
#
# equation = QuadraticEquation(a, b, c)
#
# EquationSingleValueAnswer(
#     1,
#     'Quadratics',
#     'Solve Quadratic by Factoring',
#     'Solve the following quadratic equation',
#     equation.standard_form() + ' = 0',
#     '({},{})'.format(equation.get_roots()[0], equation.get_roots()[1]),
#     .01
# )
#
# a = random.randint(-10, 10)
# b = random.randint(-10, 10)
# c = random.randint(-10, 10)
#
# equation = QuadraticEquation(a, b, c)
#
# EquationSingleValueAnswer(
#     2,
#     'Quadratics',
#     'Find Vertex of Standard Form Parabola',
#     'Identify the vertex of the following equation',
#     'y = ' + equation.standard_form(),
#     '({},{})'.format(equation.get_vertex()[0], equation.get_vertex()[1]),
#     .01
# )
#
# a = random.randint(-10, 10)
# b = random.randint(-10, 10)
# c = random.randint(-10, 10)
#
# equation = QuadraticEquation(a, b, c)
#
# GraphEquation(
#     3,
#     'Quadratics',
#     'Graph Standard Form Parabola',
#     'Graph the quadratic equation shown below',
#     'y = ' + equation.standard_form(),
#     'y = ' + equation.standard_form()
# )




