import json


class Course:
    def __init__(self, course_id, teacher_id, name, students=[], assignments={}):
        self.course_id = course_id
        self.teacher_id = teacher_id
        self.name = name
        self.students = students
        self.assignments = assignments

    # accepts tuple of data passed from sql
    # this unpacks the tuple, creates an assignment object, and adds it to the dict of assignments
    def load_assignment_from_tuple(self, assignment_tuple):
        assignment = Assignment(*assignment_tuple[0])
        assignment.questions = json.loads(assignment.questions)
        self.add_assignment(assignment)

    def add_assignment(self, assignment):
        self.assignments[str(assignment.assignment_id)] = assignment


class Assignment:
    def __init__(self, assignment_id, name, due_date, questions=[], grade=None):
        self.assignment_id = assignment_id
        self.name = name
        self.due_date = due_date
        self.questions = questions
        self.grade = grade

    # this looks at every question in question list
    # determines if the question is complete
    # calculates and then returns the percent of questions complete
    def calculate_grade(self):

        total_number_of_questions = len(self.questions)
        total_number_correct = 0

        for question in self.questions:
            if question['status'] == "complete":
                total_number_correct += 1

        self.grade = "{:.0f}%".format(total_number_correct / total_number_of_questions * 100)
        return self.grade
