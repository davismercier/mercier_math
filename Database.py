import pymysql
import json
from App_Exceptions import *


class Database:
    # create database with name specifying the specific database to connect with
    def __init__(self, name):
        self.name = name

    # create ane return a mysql connection object
    def create_db_connection(self):
        try:
            conn = pymysql.connect(host="localhost", user="DB_user", password="", database=self.name)
            return conn
        except Exception as error:
            print('connection failed!', error)
            exit()

    # takes email string parameter
    # if an email is found in sql table Students or Teachers, user type is returned
    # if no email is found, false is returned
    def get_user_type(self, email):
        conn = self.create_db_connection()

        try:
            with conn.cursor() as cursor:
                sql_1 = "SELECT email FROM Students"
                cursor.execute(sql_1)
                students = cursor.fetchall()

                sql_2 = "SELECT email FROM Teachers"
                cursor.execute(sql_2)
                teachers = cursor.fetchall()

                for student in students:
                    if email in student:
                        return "Students"

                for teacher in teachers:
                    if email in teacher:
                        return "Teachers"
                return False

        except Exception as error:
            print(error)
            raise SQLError
        finally:
            conn.close()

    # The first parameter, user_type, allows you to specify if you wish to add a user to the Student or Teachers table
    # Remaining parameters represent values to be passed into table (all strings)
    def create_user_account(self, user_type, first_name, last_name, email, password):

        conn = self.create_db_connection()

        try:
            with conn.cursor() as cursor:
                sql = "INSERT INTO {} (first_name, last_name, email, password) VALUES (%s, %s, %s, %s)".format(user_type)
                cursor.execute(sql, (first_name, last_name, email, password))
                conn.commit()
        except Exception as error:
            print(error)
            raise SQLError

        finally:
            conn.close()

    def load_user(self, user_type, email, password):

        conn = self.create_db_connection()

        try:
            with conn.cursor() as cursor:
                # user_type parameter specifies which table should be searched (Students or Teachers)
                # email and password must both match for a user to be selected
                sql = "SELECT * FROM {} WHERE email = %s AND password = %s".format(user_type)
                cursor.execute(sql, (email, password))
                user_tuple = cursor.fetchone()

                if user_tuple:
                    # if a matching user located, return tuple of data
                    return user_tuple
                else:
                    # if no matching user located, return False
                    return False

        except Exception as error:
            print("something went wrong", error)

        finally:
            conn.close()

    # parameter teacher represents a teacher_object
    # parameter course_name is a string
    # function creates an entry in table Courses
    def create_course_with_name(self, teacher, course_name):
        conn = self.create_db_connection()

        try:
            with conn.cursor() as cursor:
                sql_add_course = "INSERT INTO Courses (teacher_id, name) VALUES (%s, %s)"
                cursor.execute(sql_add_course, (teacher.teacher_id, course_name))
                conn.commit()
        except Exception as error:
            print(error)
        finally:
            conn.close()

    # select all existing course ids from table Courses
    def select_all_course_ids(self):
        conn = self.create_db_connection()

        try:
            with conn.cursor() as cursor:
                sql_select_all_course_ids = "SELECT course_id FROM Courses"
                cursor.execute(sql_select_all_course_ids)
                course_ids = cursor.fetchall()
                return course_ids
        except Exception as error:
            print(error)
        finally:
            conn.close()

    # parameter student represents a student object
    # parameter course_id is a string
    # function adds entry to Table student_course_relationship
    def add_student_to_course(self, student, course_id):

        conn = self.create_db_connection()

        try:
            with conn.cursor() as cursor:
                sql_add_to_course = "INSERT INTO student_course_relationship (student_id, course_id) VALUES (%s, %s)"
                cursor.execute(sql_add_to_course, (student.student_id, course_id))
                conn.commit()
        except Exception as error:
            print(error)
        finally:
            conn.close()

    # selects and returns all assignments associated with specified course id
    def select_assignments_with_given_course_id(self, course_id):

        conn = self.create_db_connection()

        try:
            with conn.cursor() as cursor:
                sql_select_assignment = "SELECT a.assignment_id, a.due_date, a.questions " \
                                        "FROM Assignments a, assignment_course_relationship acr, Courses c " \
                                        "WHERE a.assignment_id = acr.assignment_id " \
                                        "AND acr.course_id = c.course_id " \
                                        "AND c.course_id = %s"
                cursor.execute(sql_select_assignment, course_id)
                assignments = cursor.fetchall()
                return assignments
        except Exception as error:
            print(error)
        finally:
            conn.close()

    # adds entry into Table student_assignment_relationship
    def create_student_assignment_relationship(self, student_id, assignment_id, due_date, questions):

        conn = self.create_db_connection()

        try:
            with conn.cursor() as cursor:
                sql_create_student_relation = "INSERT INTO student_assignment_relationship " \
                                      "(student_id, assignment_id, due_date, questions, grade) " \
                                      "VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(sql_create_student_relation, (student_id, assignment_id, due_date, questions, '0%'))
                conn.commit()
        except Exception as error:
            print(error)
        finally:
            conn.close()

    # parameter student represents a Student object
    # selects all rows that match the student id
    # returns tuples necessary to create course object
    def select_courses_with_given_student(self, student):
        conn = self.create_db_connection()

        try:
            with conn.cursor() as cursor:
                sql_select_courses = "SELECT c.course_id, c.teacher_id, c.name " \
                                     "FROM Students s, Courses c, student_course_relationship scr " \
                                     "WHERE s.student_id = scr.student_id AND scr.course_id = c.course_id " \
                                     "AND %s = s.student_id"
                cursor.execute(sql_select_courses, student.student_id)
                courses = cursor.fetchall()
                return courses
        except Exception as error:
            print(error)
        finally:
            conn.close()

    # parameter course id is a string
    # select all assignment_ids with matching course_id
    # return assignment_ids
    def select_all_assignment_ids_for_a_course(self, course_id):
        conn = self.create_db_connection()

        try:
            with conn.cursor() as cursor:
                sql_select_assignment_ids = "SELECT a.assignment_id " \
                                     "FROM Assignments a, Courses c, assignment_course_relationship acr " \
                                     "WHERE a.assignment_id = acr.assignment_id AND acr.course_id = c.course_id " \
                                     "AND %s = c.course_id"
                cursor.execute(sql_select_assignment_ids, course_id)
                assignment_ids = cursor.fetchall()
                return assignment_ids
        except Exception as error:
            print(error)
        finally:
            conn.close()

    # accepts a string representing course id
    # returns a tuple of assignment ids
    def select_all_assignments_for_a_course(self, course_id):
        conn = self.create_db_connection()

        try:
            with conn.cursor() as cursor:
                sql_select_assignment_ids = "SELECT a.assignment_id, a.name, a.due_date, a.questions " \
                                     "FROM Assignments a, Courses c, assignment_course_relationship acr " \
                                     "WHERE a.assignment_id = acr.assignment_id AND acr.course_id = c.course_id " \
                                     "AND %s = c.course_id"
                cursor.execute(sql_select_assignment_ids, course_id)
                assignment_ids = cursor.fetchall()
                return assignment_ids
        except Exception as error:
            print(error)
        finally:
            conn.close()

    # student represent a Student object
    # assignment id is a string
    # returns a list of assignment tuple data
    def load_student_assignment_with_id(self, student, assignment_id):
        conn = self.create_db_connection()

        try:
            with conn.cursor() as cursor:
                sql = "SELECT a.assignment_id, a.name, sar.due_date, sar.questions, sar.grade " \
                      "FROM Assignments a, Students s, student_assignment_relationship sar " \
                      "WHERE a.assignment_id = sar.assignment_id AND sar.student_id = s.student_id " \
                      "AND s.student_id=%s AND a.assignment_id = %s"
                cursor.execute(sql, (student.student_id, assignment_id))
                assignments = cursor.fetchall()
                return assignments
        except Exception as error:
            print(error)
        finally:
            conn.close()

    # parameter student represents a Teacher object
    # selects all rows that match the teacher id
    # returns tuples necessary to create course object
    def select_courses_with_given_teacher(self, teacher):

        conn = self.create_db_connection()

        try:
            with conn.cursor() as cursor:
                sql_select_courses = "SELECT course_id, teacher_id, name FROM Courses WHERE teacher_id = %s"
                cursor.execute(sql_select_courses, teacher.teacher_id)
                courses = cursor.fetchall()
                return courses
        except Exception as error:
            print(error)
        finally:
            conn.close()

    # parameter course_id is a string
    # selects all rows that match this id
    # return tuples necessary to make Student object
    def select_students_with_given_course_id(self, course_id):

        conn = self.create_db_connection()

        try:
            with conn.cursor() as cursor:
                sql_select_students = "SELECT s.student_id, s.first_name, s.last_name, s.email, s.password " \
                                      "FROM Students s, Courses c, student_course_relationship scr " \
                                      "WHERE s.student_id = scr.student_id AND scr.course_id = c.course_id AND c.Course_id = {}".format(course_id)
                cursor.execute(sql_select_students)
                students = cursor.fetchall()
                return students
        except Exception as error:
            print(error)
        finally:
            conn.close()

    # accepts strings as arguments
    # selects and returns all assignment ids that match a teacher and assignment name
    # This identifies the assignment_id that is created by the database when an assignment is created by a teacher
    def get_assignment_id_of_assignment(self, teacher_id, assignment_name):
        conn = self.create_db_connection()

        try:
            with conn.cursor() as cursor:
                sql_select_assignment_id = "SELECT assignment_id " \
                                      "FROM Assignments " \
                                      "WHERE teacher_id = %s AND name = %s"
                cursor.execute(sql_select_assignment_id, (teacher_id, assignment_name))
                assignment_id = cursor.fetchall()
                return assignment_id
        except Exception as error:
            print(error)
        finally:
            conn.close()

    # assignment id and course id are strings
    # creates a relationship between the given assignment and course
    def create_assignment_course_relationship(self, assignment_id, course_id):
        conn = self.create_db_connection()

        try:
            with conn.cursor() as cursor:
                sql_create_acr = "INSERT INTO assignment_course_relationship " \
                                              "(assignment_id, course_id) " \
                                              "VALUES (%s, %s)"
                cursor.execute(sql_create_acr, (assignment_id, course_id))
                conn.commit()
        except Exception as error:
            print(error)
        finally:
            conn.close()

    # parameters both represent strings
    # selects course by id and updates name to name passed as parameter
    def rename_course_with_given_id(self, course_name, course_id):
        conn = self.create_db_connection()

        try:
            with conn.cursor() as cursor:
                sql_update_course_name = "UPDATE Courses SET name = %s WHERE course_id = %s"
                cursor.execute(sql_update_course_name, (course_name, course_id))
                conn.commit()
        except Exception as error:
            print(error)
        finally:
            conn.close()

    # parameter represents a string
    # selects course by id and deletes row / entry
    def delete_course_with_given_id(self, course_id):
        conn = self.create_db_connection()

        try:
            with conn.cursor() as cursor:
                sql_delete_course = "DELETE FROM Courses WHERE course_id = %s"
                cursor.execute(sql_delete_course, course_id)
                conn.commit()
        except Exception as error:
            print(error)
        finally:
            conn.close()

    # student_id parameter is a string
    # database selects and returns data tuple of student with given id
    def select_student_with_given_student_id(self, student_id):
        conn = self.create_db_connection()

        try:
            with conn.cursor() as cursor:
                sql = "SELECT * FROM Students WHERE student_id = %s"
                cursor.execute(sql, student_id)
                student_tuple = cursor.fetchone()
                return student_tuple

        except Exception as error:
            print("something went wrong", error)

        finally:
            conn.close()

    # all parameters are strings with updated student account info (entered by teacher)
    # this function selects student with matching student id and updates data
    def update_student_with_given_student_id(self, student_id, first_name, last_name, email, password):
        conn = self.create_db_connection()

        try:
            with conn.cursor() as cursor:
                sql = "UPDATE Students SET " \
                      "first_name=%s, last_name=%s, email=%s, password=%s " \
                      "WHERE student_id = %s"
                cursor.execute(sql, (first_name, last_name, email, password, student_id))
                conn.commit()

        except Exception as error:
            print("something went wrong", error)

        finally:
            conn.close()

    # student_id and course_id are strings
    # removes student (with matching id) from course by eliminating student_course_relationship
    # student and course will both still exist (connection is only thing deleted)
    def delete_student_from_given_course(self, student_id, course_id):
        conn = self.create_db_connection()

        try:
            with conn.cursor() as cursor:
                sql = "DELETE FROM student_course_relationship " \
                      "WHERE student_id = %s AND course_id = %s"
                cursor.execute(sql, (student_id, course_id))
                conn.commit()

        except Exception as error:
            print("something went wrong", error)

        finally:
            conn.close()

    # questions represents a list of questions
    # remaining parameters are strings
    def create_assignment(self, teacher_id, assignment_name, due_date, questions):
        conn = self.create_db_connection()

        try:
            with conn.cursor() as cursor:
                sql_insert_assignment = "INSERT INTO assignments (teacher_id, name, due_date, questions) " \
                                        "VALUES (%s, %s, %s, %s)"
                cursor.execute(sql_insert_assignment, (teacher_id, assignment_name, due_date, questions))
                conn.commit()
        except Exception as error:
            print(error)
        finally:
            conn.close()

    # questions represents a list of questions
    # remaining parameters are strings
    def update_assignment(self, assignment_id, teacher_id, assignment_name, due_date, questions):
        conn = self.create_db_connection()

        try:
            with conn.cursor() as cursor:
                sql_update_assignment = "UPDATE Assignments " \
                                        "SET name = %s, " \
                                        "due_date = %s, " \
                                        "questions = %s " \
                                        "WHERE assignment_id = %s AND " \
                                        "teacher_id = %s"
                cursor.execute(sql_update_assignment, (assignment_name, due_date,  questions, assignment_id, teacher_id))
                conn.commit()
        except Exception as error:
            print('update assignment failed')
            print(error)
        finally:
            conn.close()

    def delete_assignment(self, assignment_id):
        conn = self.create_db_connection()

        try:
            with conn.cursor() as cursor:
                sql_delete_assignment = "DELETE FROM Assignments WHERE assignment_id = %s"
                cursor.execute(sql_delete_assignment, assignment_id)
                conn.commit()
        except Exception as error:
            print('update assignment failed')
            print(error)
        finally:
            conn.close()

    # assignment_id is a string
    # selects all course ids associated with this assignment id and returns tuple
    def select_course_ids_with_given_assignment_id(self, assignment_id):
        conn = self.create_db_connection()

        try:
            with conn.cursor() as cursor:
                sql_select_assignment = "SELECT course_id FROM assignment_course_relationship WHERE assignment_id = %s"
                cursor.execute(sql_select_assignment, assignment_id)
                course_ids = cursor.fetchall()
                return course_ids
        except Exception as error:
            print(error)
        finally:
            conn.close()

    # assignment id is a string
    # returns a list of assignment data tuples
    def select_teacher_assignment_with_assignment_id(self, assignment_id):
        conn = self.create_db_connection()
        try:
            with conn.cursor() as cursor:
                sql_select_assignment = "SELECT assignment_id, name, due_date, questions " \
                                        "FROM Assignments " \
                                        "WHERE assignment_id = %s"
                cursor.execute(sql_select_assignment, assignment_id)
                assignments = cursor.fetchall()
                return assignments
        except Exception as error:
            print(error)
        finally:
            conn.close()

    # questions represents a list of questions
    # remaining parameters are strings
    def update_student_assignment_relationship(self, student_id, assignment_id, due_date, questions, grade):
        conn = self.create_db_connection()

        try:
            with conn.cursor() as cursor:
                sql_update_student_relation = "UPDATE student_assignment_relationship " \
                                      "SET due_date = %s, questions = %s, grade = %s " \
                                      "WHERE student_id = %s AND assignment_id = %s"
                cursor.execute(sql_update_student_relation, (due_date, questions, grade, student_id, assignment_id))
                conn.commit()
        except Exception as error:
            print('update sar failed')
            print(error)
        finally:
            conn.close()

    # student represents student object which contains updated questions
    # remaining parameters are strings
    def update_student_questions_status_and_assignment_grade(self, grade, course_id, assignment_id, student):

        # select list of question object for the specified course and assignment (identified by id parameters)
        questions = student.courses[str(course_id)].assignments[str(assignment_id)].questions
        # convert to json
        questions_json = json.dumps(questions)

        # update questions list (including updated question status)
        # update assignment grade
        conn = self.create_db_connection()
        try:
            with conn.cursor() as cursor:
                sql_update = "UPDATE student_assignment_relationship " \
                             "SET questions = %s, grade = %s " \
                             "WHERE student_id = %s AND assignment_id = %s"
                cursor.execute(sql_update, (questions_json, grade, student.student_id, assignment_id))
                conn.commit()
                print(cursor.rowcount)
        except Exception as error:
            print(error)
        finally:
            conn.close()

    def delete_assignment_course_relation(self, course_id, assignment_id):
        conn = self.create_db_connection()

        try:
            with conn.cursor() as cursor:
                sql_delete_acr = "DELETE FROM assignment_course_relationship WHERE course_id = %s AND assignment_id= %s"
                cursor.execute(sql_delete_acr, (course_id, assignment_id))
                conn.commit()
        except Exception as error:
            print(error)
        finally:
            conn.close()

    # student id and assignment id are strings
    # returns list of student data tuples
    def select_assignment_with_student_id_and_assignment_id(self, student_id, assignment_id):
        conn = self.create_db_connection()

        try:
            with conn.cursor() as cursor:
                sql_select_assignment = "SELECT a.assignment_id, a.name, sar.due_date, sar.questions, sar.grade " \
                                        "FROM Assignments a, student_assignment_relationship sar " \
                                        "WHERE sar.assignment_id = a.assignment_id AND " \
                                        "sar.student_id = %s AND sar.assignment_id = %s"
                cursor.execute(sql_select_assignment, (student_id, assignment_id))
                students = cursor.fetchall()
                return students
        except Exception as error:
            print('select students failed')
            print(error)
        finally:
            conn.close()





