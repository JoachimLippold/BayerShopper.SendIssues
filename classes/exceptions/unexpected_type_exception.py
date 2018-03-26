class UnexpectedTypeException(object):

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


if __name__ == '__main__':
    print("This module is not for execution...")
