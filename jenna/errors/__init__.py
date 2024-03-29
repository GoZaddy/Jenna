class CodegenError(Exception):
    """
    This exception is raised when an error occurs or an invalid value is encountered in Jenna
    """

    def __init__(self, message):
        self.message = message
        super().__init__(message)
