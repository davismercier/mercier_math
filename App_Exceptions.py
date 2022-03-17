class SQLError(Exception):
    pass


class FieldEmptyError(Exception):
    pass


class TooManyCharactersError(Exception):
    pass


class UserAlreadyExistsError(Exception):
    pass


class UsernamePasswordError(Exception):
    pass


class CourseIdError(Exception):
    pass