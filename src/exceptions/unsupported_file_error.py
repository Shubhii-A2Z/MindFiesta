class UnsupportedFileError(Exception):
    """
    Raised when file type is not supported
    """
    
    def __init__(self, message: str):
        self.message=message
        super().__init__(self.message)