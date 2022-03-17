from Courses_Assignments import *


class User:
    def __init__(self, first_name, last_name, email, password, courses={}):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.courses = courses

    # accepts list of tuples of data
    # each tuple of data can be used to instantiate a course object
    def load_courses(self, course_tuples):
        # empty the current user attribute courses
        self.courses = {}
        for course_tuple in course_tuples:
            # make a course object from each tuple of data
            course_object = (Course(*course_tuple))
            # assign course object to the attribute/dictionary "courses" for the user
            self.courses[str(course_object.course_id)] = course_object


class Teacher(User):
    def __init__(self, teacher_id, first_name, last_name, email, password, courses={}):
        self.teacher_id = teacher_id
        super().__init__(first_name, last_name, email, password, courses)


class Student(User):
    def __init__(self, student_id, first_name, last_name, email, password, courses={}, current_course_id=None, current_assignment_id=None, current_question_id=None):
        self.student_id = student_id
        super().__init__(first_name, last_name, email, password, courses)
        self.current_course_id = current_course_id
        self.current_assignment_id = current_assignment_id
        self.current_question = current_question_id


