
import time
import logging
# from config import logging_parameters


def log_output(f):

    def wrap_function(*args, **kwargs):

        def test_function():
            print "test function active"

        start = time.time()
        spacer = (' '*20) + '}} '

        print spacer, '(entering function ', f.__name__, 'with args: ', args, 'kwargs: ', kwargs,')'
        result = f(*args, **kwargs)
        end = time.time() - start
        print spacer, '(function complete.  total time: ', round(end, 3), ')'
        return result

    return wrap_function



