

# Following, http://flask.pocoo.org/docs/patterns/apierrors/, let's add custom exceptions
# to our views:


class AppError(Exception):
    pass


