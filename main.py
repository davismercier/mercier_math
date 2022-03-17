from flask import Flask, render_template, request, url_for, redirect
from Controller import *
from Database import *
from Questions import *
from fractions import Fraction
from App_Exceptions import *
from Error_Handling import *

app = Flask(__name__)

# create a database object
# this object already knows how to connect to the mysql database specific to this app
database = Database('SIE_508_FP')

# create a controller object
# this has exclusive access to the database object and can ask the database to process and return data
# this also contains a user object (currently = None) that holds all info for the current user
controller = Controller(database)

# access the dictionary of all pre-made questions from Questions.py
all_questions = Question.all_questions

# extract all categories of questions
# this will be used to sort questions when displayed during assignment creation
categories = Question.categories


# Displays sign_up_login.html which allows new users to enter data to sign-up or
# existing users to login to an existing account
@app.route('/sign_up+login')
def sign_up_login():
    return render_template('sign_up_login.html')


# This receives any error type caught during the sign_up or login process
# Then reloads the page with the proper error message displayed
@app.route('/sign_up_login_error/<error_type>')
def sign_up_login_error(error_type):
    error_message = process_error_type(error_type)
    return render_template('sign_up_login.html', error_message=error_message)


@app.route('/register_user', methods=['POST'])
def register_user():
    if request.method == 'POST':
        try:
            user_type = request.form['user_type']
        except KeyError:
            return redirect('/sign_up_login_error/user_type_not_selected')

        # receive data entered in sign-in form
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']

        form_error = controller.check_form_fields(first_name, last_name, email, password)

        if form_error:
            return redirect('/sign_up_login_error/{}'.format(form_error))
        else:
            try:
                # pass user data to controller
                controller.create_user(user_type, first_name, last_name, email, password)
            except UserAlreadyExistsError:
                # route back to sign_up page if email already exists in database
                return redirect('/sign_up_login_error/user_already_exists')
            else:
                try:
                    # add user object as attribute to controller
                    # this user object does not currently contain any courses
                    controller.load_user(email, password)
                except UsernamePasswordError:
                    # route back to login page if username and password don't match an account
                    return redirect('/sign_up_login_error/username_password_incorrect')

        if controller.user_type == 'Teachers':
            # receive data from sign in form
            course = request.form["course"]
            period = request.form["teacher's_period"]

            form_error = controller.check_form_fields(course, period)
            if form_error:
                return redirect('/sign_up_login_error/{}'.format(form_error))
            else:
                # combine entries to form course_name and pass to controller to create teacher course
                course_name = '{} ({})'.format(course, period)
                controller.create_course_with_name(course_name)
                # routes to teacher home
                return redirect('http://localhost:5000/teacher_home')

        if controller.user_type == "Students":
            # receive data from sign in form
            course_id = request.form["course_id"]

            form_error = controller.check_form_fields(course_id)
            if form_error:
                return redirect('/sign_up_login_error/{}'.format(form_error))

            try:
                # add student to database for given course
                # if no course with matching id exists, controller will throw an error
                controller.add_student_to_course(course_id)
            except CourseIdError:
                # route back to sign-up page if no course with ID exists
                return redirect('/sign_up_login_error/course_id_does_not_exist')
            else:
                # select all assignments associated with course an assign them to student
                controller.create_student_assignment_relationship(course_id, controller.user.student_id)

            return redirect('http://localhost:5000/student_home')


@app.route('/login_user', methods=['POST'])
def login_user():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        error = controller.check_form_fields(email, password)
        if error:
            return redirect('/sign_up_login_error/{}'.format(error))

        try:
            # add user object as attribute to controller
            # this user object does not currently contain any courses
            controller.load_user(email, password)
        except UsernamePasswordError:
            # route back to login page if username and password don't match an account
            return redirect('/sign_up_login_error/username_password_incorrect')

        if controller.user_type == "Teachers":
            return redirect('http://localhost:5000/teacher_home')

        if controller.user_type == "Students":
            return redirect('http://localhost:5000/student_home')


# Removes current user from controller object
# Routes user back to login page
@app.route('/log_out', methods=['POST'])
def log_out():
    if request.method == "POST":
        controller.user_type = None
        controller.user = None

        return redirect('http://localhost:5000/sign_up+login')


# If user selects "Main Menu" they are routed back to the correct home page
# This depends on the type of user currently logged in / assigned to the controller
@app.route('/Home')
def home():
    if controller.user_type == "Students":
        return redirect('/student_home')
    else:
        return redirect('/teacher_home')


@app.route('/student_home')
def student_home():
    # reload all courses and assignments when routed to home screen
    controller.load_student_courses_and_assignments()
    return render_template("student_home.html", student_user=controller.user)


# This receives any error type
# Then reloads the page with the proper error message displayed
@app.route('/student_home/<error_type>')
def student_home_error(error_type):
    error_message = process_error_type(error_type)
    return render_template("student_home.html", student_user=controller.user, error_message=error_message)


@app.route('/teacher_home')
def teacher_home():
    # reload all courses, assignments, and students when routed to home screen
    # this is often done after a new course or assignment is created to update screen
    controller.load_teacher_courses_and_assignments_and_students()
    return render_template("teacher_home.html", teacher_user=controller.user, all_questions=all_questions,
                           categories=categories)


# This receives any error type
# Then reloads the page with the proper error message displayed
@app.route('/teacher_home/<error_type>')
def teacher_home_error(error_type):
    error_message = process_error_type(error_type)
    return render_template("teacher_home.html", teacher_user=controller.user, all_questions=all_questions,
                           categories=categories, error_message=error_message)


# A button on the teacher home page allows them to create a course by inputting the name and period
# This route handles the form submission
@app.route('/create_course', methods=['POST'])
def create_course():
    if request.method == "POST":
        # accept course name and period from user
        course = request.form["course"]
        period = request.form["teacher's_period"]

        form_error = controller.check_form_fields(course, period)

        if form_error:
            return redirect('/teacher_home/{}'.format(form_error))
        else:
            # create single string "course_name" to pass to controller
            course_name = '{} ({})'.format(course, period)
            controller.create_course_with_name(course_name)
            # route user to home page after course created
            # teacher courses reloaded automatically through this route
            return redirect('/teacher_home')


# From teacher home, teacher can click button to create assignment
# This displays a form to fill with necessary data
# This route handles form submission
@app.route('/create_assignment', methods=['POST'])
def create_assignment():

    if request.method == "POST":
        # receive assignment data from user
        assignment_name = request.form["assignment_name"]
        due_date = request.form["due_date"]
        course_ids = request.form.getlist('course_ids')
        assignment_questions = request.form.getlist("questions")

        form_error = controller.check_form_fields(assignment_name, due_date, course_ids)

        if form_error:
            return redirect('/teacher_home/{}'.format(form_error))
        else:
            # create assignment by passing data to controller
            controller.create_assignment(course_ids, assignment_name, due_date, assignment_questions)

            # route user to teacher home page
            # automatically reloads courses, assignments, and students for teacher
            return redirect('/teacher_home')


# Every course taught by a teacher displays as a link
# This route handles when a specific course is clicked and routes user to a page that displays course information
@app.route('/course/<course_name>/<course_id>')
def course(course_name, course_id):
    # Loads course page
    return render_template('teacher_course_page.html', course_name=course_name, course_id=course_id, teacher_user=controller.user)


# On course page, teacher can click button to edit the name of or delete the given course
# This route handles either button being clicked
@app.route('/edit_delete_course', methods=['POST'])
def edit_delete_course():
    if request.method == "POST":
        # define if user wishes to edit or delete the course
        action_type = request.form["action_type"]
        # receive info submitted by user
        course_name = request.form["course_name"]
        course_id = request.form["course_id"]

        # call appropriate controller function based on action type
        if action_type == "Edit":
            controller.rename_course(course_name, course_id)
        else:
            controller.delete_course(course_id)
        # route user back to teacher home
        # teacher courses reloaded automatically through this route
        return redirect('/teacher_home')


# Teacher course page displays a link for each assignment in course
# This route responds to teacher clicking on this link
@app.route('/edit_assignment', methods=['POST'])
def edit_assignment():
    if request.method == "POST":
        # receives assignment id of assignment clicked by user
        assignment_id = request.form['assignment_id']

        # select all course_ids from assignment_course_relationship with given assignment_id
        course_ids_tuples = controller.select_course_ids_with_given_assignment_id(assignment_id)
        course_ids = []
        for course_id_tuple in course_ids_tuples:
            course_ids.append(course_id_tuple[0])

        # select assignment from Assignments with given assignment_id
        assignment = controller.select_teacher_assignment_with_assignment_id(assignment_id)

        # create a list to hold the ids of all questions currently in the assignment
        question_ids = []
        # cycle through each question in the assignment
        for question in assignment.questions:
            # add question ids not already in list to list
            if question['id'] not in question_ids:
                question_ids.append(int(question['id']))

        # pass necessary info to a page that allows user to see current state of assignment and make changes
        return render_template('edit_assignment.html',
                               teacher_user=controller.user,
                               course_ids=course_ids,
                               question_ids=question_ids,
                               assignment=assignment,
                               categories=categories,
                               all_questions=all_questions)


@app.route('/update_delete_assignment', methods=["POST"])
def update_assignment():
    if request.method == "POST":
        action_type = request.form['action_type']
        assignment_name = request.form["assignment_name"]
        assignment_id = request.form['assignment_id']
        due_date = request.form["due_date"]
        course_ids = request.form.getlist('course_ids')
        assignment_questions = request.form.getlist("questions")

        if action_type == "Edit":
            controller.new_update_assignment(course_ids, assignment_id, controller.user.teacher_id, assignment_name, due_date, assignment_questions)
        else:
            controller.delete_assignment(assignment_id)
        return redirect('/teacher_home')


# Teacher course page displays links to edit each student
# This route responds to the link click
@app.route('/edit_student', methods=['POST'])
def edit_student():
    if request.method == "POST":
        # the id of the student selected by user click is passed
        student_id = request.form['student_id']
        # request student object with matching student id
        student = controller.select_student_with_student_id(student_id)
        # pass student object to webpage that allows student profile to be edited
        return render_template('edit_student.html', student=student)


# This route processes the information for an updated student profile
@app.route('/update_student', methods=['POST'])
def update_student():
    if request.method == 'POST':
        # updated student information received by form submission from teacher user
        student_id = request.form['student_id']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']

    # pass information to database to perform an update of student with given id
    controller.update_student_with_student_id(student_id, first_name, last_name, email, password)
    # route user back to teacher home
    # this route automatically updates all student objects associated with this teacher
    return redirect('/teacher_home')


# Teacher course page allows student select (by checkbox) any number of student to be removed from course
# This route responds to button click that submits a list of students to remove from a given course
@app.route('/remove_students', methods=['POST'])
def remove_students():
    if request.method == 'POST':
        # receive list of students (ids) to remove from a given course (id)
        course_id = request.form['course_id']
        students_to_remove = request.form['students_to_remove'].split(",")
        # request list of students be removed from given course
        controller.delete_students_from_course(students_to_remove, course_id)
        # route user back to teacher home
        # all student lists for each course automatically updated by this route
        return redirect('/teacher_home')


# Students have the option to enroll themselves in additional courses from their home page
# This route responds to user submitting the id of a course
@app.route('/add_course', methods=['POST'])
def add_course():
    if request.method == 'POST':
        # receive id of course students wishes to join
        course_id = request.form['course_to_add']
        # assigns student to course (creates a relation between student and course)
        try:
            controller.add_student_to_course(course_id)
        except CourseIdError:
            return redirect('/student_home/course_id_does_not_exist')
        # create relation between students and all current course assignments
        # (i.e. select and assign all existing assignments to student)
        controller.create_student_assignment_relationship(course_id, controller.user.student_id)
        return redirect('/student_home')


# Each question is displayed to student as link
# each link contains info that allows the correct question to be selected from the dictionary "all_questions"
# this question object is then passed to a webpage that extracts and displays the question
@app.route('/ask_question/<course_id>/<assignment_id>/<question_title>/<question_id>')
def ask_question(course_id, assignment_id, question_title, question_id):
    # receive question info from link "click" and assign to controller attributes
    controller.user.current_course_id = course_id
    controller.user.current_assignment_id = assignment_id

    # select current course
    current_course = controller.user.courses[course_id]
    # select current assignment
    current_assignment = current_course.assignments[assignment_id]

    # select question object from question dictionary and assign to controller
    controller.user.current_question = all_questions[int(question_id)]
    # select question object and pass to web page
    current_question = all_questions[int(question_id)]

    javascript_file = url_for('static', filename='ask_question.js')
    return render_template('ask_question.html', question=current_question,
                                                assignment=current_assignment,
                                                course = current_course,
                                                javascript_file=javascript_file)


# This route receives user answer for current question and compares it to the question answer
@app.route('/grader', methods=['POST'])
def grader():
    # receive user answer
    user_answer = Fraction(request.form['user_answer'])
    # select the current question object (stored in controller)
    current_question = controller.user.current_question
    # grade answer by using the built in grade function for the question object
    is_correct = controller.user.current_question.grade(user_answer)

    if is_correct:
        feedback = 'Correct'
        # select question and change status to complete
        # recalculate grade for the related assignment
        controller.mark_question_complete_and_update_assignment_grade()
    else:
        feedback = 'Incorrect'

    current_question.regenerate()
    course_id = controller.user.current_course_id
    assignment_id = controller.user.current_assignment_id

    return render_template('Feedback.html',
                           user_answer=user_answer,
                           course_id=course_id,
                           assignment_id=assignment_id,
                           question=current_question,
                           feedback=feedback)


if __name__ == '__main__':
    app.run(debug=True)
