DEBUG = True


def log(self, *args, sep=' ', end='\n', file=None):
    if DEBUG:
        print(self.__class__.__name__, args, sep=sep, end=end, file=file)
