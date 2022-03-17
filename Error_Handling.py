from App_Exceptions import *


# accepts string describing error type
# returns corresponding error message
def process_error_type(error_type):
    if error_type == "user_type_not_selected":
        error_message = "Error: You must select a user type"
    elif error_type == "field_empty":
        error_message = "Error: All fields must be filled"
    elif error_type == "too_many_characters":
        error_message = "Error: All fields must contain less than 64 characters"
    elif error_type == "user_already_exists":
        error_message = "Error: A user with that email already exists"
    elif error_type == "username_password_incorrect":
        error_message = "Error: email and/or password incorrect - no account located"
    elif error_type == "course_id_does_not_exist":
        error_message = "Error: No course with specified Course ID exists"
    elif error_type == 'unknown_error':
        error_message = "Error: Unknown Error Occurred"
    return error_message


# accepts any number of user entries from a form
# raises error if any field is blank or more than 64 characters
def verify_user_entries(*user_entries):
    for user_entry in user_entries:
        if not user_entry:
            raise FieldEmptyError
        if len(user_entry) > 64:
            raise TooManyCharactersError

