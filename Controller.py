from Courses_Assignments import *
from Users import *
from App_Exceptions import *
from Error_Handling import *
import json


class Controller:
    def __init__(self, database, user_type=None, user=None):
        # holds database object passed as parameter
        # controller has exclusive access to the database (Model)
        self.database = database
        # holds type of user, which can be used to inform controller how to use the user object
        self.user_type = user_type
        # holds the user object (Student or Teacher)
        self.user = user

    @staticmethod
    def check_form_fields(*user_entries):
        try:
            # check that all fields are filled and less than 64 characters
            verify_user_entries(*user_entries)
        except FieldEmptyError:
            # route back to sign_up page if field empty
            return 'field_empty'
        except TooManyCharactersError:
            # route back to sign_up page if field contains > 64 characters
            return 'too_many_characters'
        except Exception:
            return 'unknown_error'
        else:
            return False

    def create_user(self, user_type, first_name, last_name, email, password):
        # pass email to database
        if self.database.get_user_type(email):
            # if database finds an entry with a matching email raise an error
            raise UserAlreadyExistsError
        else:
            self.database.create_user_account(user_type, first_name, last_name, email, password)
        return "User of type {} successfully created".format(user_type)

    def load_user(self, email, password):
        # ask database to determine the type of user
        user_type = self.database.get_user_type(email)
        # ask database for tuple of data for given user
        user_tuple = self.database.load_user(user_type, email, password)

        # create user object (based on type) if tuple returned
        # store object as attribute of controller
        if user_tuple:
            if user_type == "Teachers":
                self.user_type = "Teachers"
                teacher_user = Teacher(*user_tuple)
                self.user = teacher_user
            elif user_type == "Students":
                self.user_type = "Students"
                student_user = Student(*user_tuple)
                self.user = student_user
        # if no tuple is returned, raise an error
        else:
            raise UsernamePasswordError

    def create_course_with_name(self, course_name):
        # ask database to create a course for logged in user
        self.database.create_course_with_name(self.user, course_name)

    def add_student_to_course(self, course_id):
        # select all currently existing course ids
        all_course_ids = self.database.select_all_course_ids()

        course_exists = False

        # if course id entered by user matches an existing course id...
        for course in all_course_ids:
            if str(course_id) == str(course[0]):
                course_exists = True

        if course_exists:
            # ask database to create a student course relationship
            self.database.add_student_to_course(self.user, course_id)
        else:
            # raise error to pass to view
            raise CourseIdError

    def create_student_assignment_relationship(self, course_id, student_id):
        # Ask database to select data for all assignments associated with the specified course_id
        assignment_tuples = self.database.select_assignments_with_given_course_id(course_id)
        # Ask database to take data for each selected assignment and create a student-assignment-relationship
        # i.e. assign each assignment for a course to the logged in student
        for assignment_tuple in assignment_tuples:
            self.database.create_student_assignment_relationship(student_id, *assignment_tuple)

    def load_student_courses_and_assignments(self):
        # ask database to select all rows that match the student's id
        # returns tuples of data necessary to make course object
        course_tuples = self.database.select_courses_with_given_student(self.user)
        # pass tuples to function that creates course objects and adds them to user attribute
        self.user.load_courses(course_tuples)

        for course in self.user.courses.values():
            # select all assignments in a given course
            assignment_ids = self.database.select_all_assignment_ids_for_a_course(course.course_id)

            course.assignments = {}

            # load each assignment and add it to the course
            for assignment_id in assignment_ids:
                assignment_tuple = self.database.load_student_assignment_with_id(self.user, assignment_id[0])
                course.load_assignment_from_tuple(assignment_tuple)

    def load_teacher_courses_and_assignments_and_students(self):
        # ask database to select all rows that match the teacher's id
        # returns tuples of data necessary to make course object
        course_tuples = self.database.select_courses_with_given_teacher(self.user)
        # pass tuples to function that creates course objects and adds them to user attribute
        self.user.load_courses(course_tuples)

        # cycle through every course assigned to the teacher
        for course in self.user.courses.values():
            # select all assignments in a given course
            assignment_tuples = self.database.select_all_assignments_for_a_course(course.course_id)

            course.assignments = {}

            for assignment_tuple in assignment_tuples:
                assignment = Assignment(*assignment_tuple)
                course.add_assignment(assignment)

            # ask database to select all rows (students) that match the course id
            # returns tuples of data necessary to make student object
            student_tuples = self.database.select_students_with_given_course_id(course.course_id)

            # empty the list of students in the course
            course.students = []
            for student_tuple in student_tuples:
                # turn each data tuple from database into Student object and add to course
                student = Student(*student_tuple)
                course.students.append(student)

                course_tuples = self.database.select_courses_with_given_student(student)
                # pass tuples to function that creates course objects and adds them to user attribute
                student.load_courses(course_tuples)

                for student_course in student.courses.values():
                    # select all assignments in a given course
                    assignment_ids = self.database.select_all_assignment_ids_for_a_course(student_course.course_id)

                    student_course.assignments = {}

                    # load each assignment and add it to the course
                    for assignment_id in assignment_ids:
                        assignment_tuple = self.database.load_student_assignment_with_id(student, assignment_id[0])
                        student_course.load_assignment_from_tuple(assignment_tuple)

    # pass name of course to database to update based on course id
    def rename_course(self, course_name, course_id):
        self.database.rename_course_with_given_id(course_name, course_id)

    # pass course id to database for deletion
    def delete_course(self, course_id):
        self.database.delete_course_with_given_id(course_id)

    # questions parameter is a list of comma separated question data
    # remaining parameters are strings
    def create_assignment(self, course_id_list, assignment_name, due_date, questions):
        # list to hold question objects created from questions parameter
        questions_list = []
        # convert questions parameter into python objects and add to above list
        for question in questions:
            question = question.split(",")
            question_id, title, status = question
            question_object = {
                "id": question_id,
                "title": title,
                "status": status
            }
            questions_list.append(question_object)

        # convert list of python objects into JSON
        # necessary to store on database
        questions_json = json.dumps(questions_list)

        # create an assignment with the given course_id
        self.database.create_assignment(self.user.teacher_id, assignment_name, due_date, questions_json)

        # select assignment id of assignment just created
        assignment_id = self.database.get_assignment_id_of_assignment(self.user.teacher_id, assignment_name)

        # cycle through the course_id for each course selected by teacher
        for course_id in course_id_list:

            # create an assignment_course_relationship
            self.database.create_assignment_course_relationship(assignment_id, course_id)

            # select all students with the course id
            student_tuples = (self.database.select_students_with_given_course_id(course_id))
            students = []
            # create student object and append to above list
            for student_tuple in student_tuples:
                students.append(Student(*student_tuple))

            # create student assignment relationship between the assignment and each student
            for student in students:
                self.database.create_student_assignment_relationship(student.student_id, assignment_id, due_date, questions_json)

    # asks database for data tuple of student with given student id
    # converts data tuple into Student object and returns object
    def select_student_with_student_id(self, student_id):
        student_tuple = self.database.select_student_with_given_student_id(student_id)
        student = Student(*student_tuple)
        return student

    # passes updated student info (from teacher user) to database for update
    def update_student_with_student_id(self, student_id, first_name, last_name, email, password):
        self.database.update_student_with_given_student_id(student_id, first_name, last_name, email, password)

    # pass list of student ids and course id to database
    # request each student with matching student id will be removed from course
    def delete_students_from_course(self, student_ids, course_id):
        for student_id in student_ids:
            self.database.delete_student_from_given_course(student_id, course_id)

    def select_course_ids_with_given_assignment_id(self, assignment_id):
        course_ids = self.database.select_course_ids_with_given_assignment_id(assignment_id)
        return course_ids

    def select_teacher_assignment_with_assignment_id(self, assignment_id):
        assignment_tuple = self.database.select_teacher_assignment_with_assignment_id(assignment_id)
        assignment = (Assignment(*assignment_tuple[0]))
        assignment.questions = json.loads(assignment.questions)
        return assignment

    def new_update_assignment(self, updated_assignment_course_ids, assignment_id, teacher_id, assignment_name, due_date, assignment_questions):
        # An empty list to hold question objects after being parsed into a python object
        questions_list = []

        # loop through each question parameter (comma separated list)
        for question in assignment_questions:
            # parse into a python list
            question = question.split(",")
            # unpack list and create a python object
            question_id, title, status = question
            question_object = {
                "id": question_id,
                "title": title,
                "status": status
            }
            # add question object to above list
            questions_list.append(question_object)

        # turn python list of objects into JSON
        # this is necessary to store in mysql as JSON data
        questions_json = json.dumps(questions_list)

        # update generic assignment (not associated with any student)
        self.database.update_assignment(assignment_id, teacher_id, assignment_name, due_date, questions_json)

        # select all course ids of courses taught by the teacher (select by teacher id from Courses)
        teacher_course_data_tuples = self.database.select_courses_with_given_teacher(self.user)
        course_ids_for_teacher = []
        for tc_data_tuple in teacher_course_data_tuples:
            course_ids_for_teacher.append(str(tc_data_tuple[0]))

        # select all course ids of courses that currently contain the assignment (select by assignment_id from ACR)
        assignment_course_data_tuples = self.database.select_course_ids_with_given_assignment_id(assignment_id)
        course_ids_of_courses_that_currently_have_the_assignment = []
        for ac_data_tuple in assignment_course_data_tuples:
            course_ids_of_courses_that_currently_have_the_assignment.append(str(ac_data_tuple[0]))

        # determine which courses fall into the following categories
        courses_with_assignment_that_should_stay = []
        courses_with_assignment_that_should_be_deleted = []
        courses_that_need_assignment_created = []

        # assign course ids to above lists
        for teacher_course_id in course_ids_for_teacher:
            if teacher_course_id in course_ids_of_courses_that_currently_have_the_assignment and teacher_course_id in updated_assignment_course_ids:
                courses_with_assignment_that_should_stay.append(teacher_course_id)
            elif teacher_course_id in course_ids_of_courses_that_currently_have_the_assignment and teacher_course_id not in updated_assignment_course_ids:
                courses_with_assignment_that_should_be_deleted.append(teacher_course_id)
            elif teacher_course_id not in course_ids_of_courses_that_currently_have_the_assignment and teacher_course_id in updated_assignment_course_ids:
                courses_that_need_assignment_created.append(teacher_course_id)

        # for courses that need assignment added
        for course_id_that_needs_assignment in courses_that_need_assignment_created:
            # create assignment_course_relation
            self.database.create_assignment_course_relationship(assignment_id, course_id_that_needs_assignment)
            # select students in these courses
            student_tuples = self.database.select_students_with_given_course_id(course_id_that_needs_assignment)
            for student_tuple in student_tuples:
                student_id = student_tuple[0]
                # create sar for these students
                self.database.create_student_assignment_relationship(student_id, assignment_id, due_date, questions_json)

        # for courses that need assignment deleted
        for course_id_with_assignment_to_remove in courses_with_assignment_that_should_be_deleted:
            self.database.delete_assignment_course_relation(course_id_with_assignment_to_remove, assignment_id)

        for course_id_keeping_assignment in course_ids_of_courses_that_currently_have_the_assignment:
            # select all students in these courses and make object
            student_data_tuples = self.database.select_students_with_given_course_id(course_id_keeping_assignment)
            for tuple in student_data_tuples:
                student_id = tuple[0]

                # select student assignment with student_id and assignment_id
                assignment_tuple = self.database.select_assignment_with_student_id_and_assignment_id(student_id, assignment_id)
                assignment = Assignment(*assignment_tuple[0])
                assignment.questions = json.loads(assignment.questions)

                new_question_list = []
                # for every question selected by user
                for new_question in questions_list:
                    new_question_not_in_list = True
                    for original_question in assignment.questions:
                        # if the question already existed
                        if new_question['id'] == original_question['id']:
                            # keep the original question (including the grade)
                            new_question_list.append(original_question)
                            new_question_not_in_list = False
                            break
                    # if the question did not exist
                    if new_question_not_in_list:
                        # add it to the list of questions
                        new_question_list.append(new_question)

                # recalculate grade based on new question list
                assignment.questions = new_question_list
                updated_student_grade = assignment.calculate_grade()

                # convert question list to json
                new_question_list = json.dumps(new_question_list)
                # update assignment on database with new questions
                self.database.update_student_assignment_relationship(student_id,
                                                                     assignment_id,
                                                                     due_date,
                                                                     new_question_list,
                                                                     updated_student_grade)

    def delete_assignment(self, assignment_id):
        self.database.delete_assignment(assignment_id)

    def mark_question_complete_and_update_assignment_grade(self):
        # select the current course and assignment (stored in controller when question is clicked)
        current_course = self.user.courses[self.user.current_course_id]
        current_assignment = current_course.assignments[self.user.current_assignment_id]

        # search for the question id that matches the question id stored when question was clicked
        for question in current_assignment.questions:
            # change status of question to complete
            if int(self.user.current_question.id) == int(question['id']):
                question['status'] = 'complete'

        # regrade assignment with question marked complete
        grade = current_assignment.calculate_grade()

        # request database update question status and assignment grade
        self.database.update_student_questions_status_and_assignment_grade(grade, current_course.course_id, current_assignment.assignment_id, self.user)









