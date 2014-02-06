
class LogDebug:

    def __init__(self, func):
        self.calls = 0
        self.func = func

    def __call__(self, *args, **kwargs):
        self.calls += 1
        print '='*10
        print "call %s to %s" % (self.calls, self.func.__name__)
        print '='*10
        print dir(self.func)
        self.func(*args, **kwargs)
