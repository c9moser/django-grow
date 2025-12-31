

class NotFileError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)


class FileFormatError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)


class NotPermitted(Exception):
    """
    Raised when the user is not permitted to access certain content.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
