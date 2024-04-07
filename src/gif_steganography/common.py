from enum import Enum, auto


class SteganographyMethod(Enum):
    LSB = auto()
    CSHIFT = auto()


class CustomError(Exception):
    """Base class for other exceptions"""

    def __init__(self, message="An unspecified error occurred."):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}"


class DataError(CustomError):
    """Raised when a data-related error occurs"""

    def __init__(self, message="An unspecified data-related error occurred."):
        super().__init__(message)


class CorruptDataError(DataError):
    """Raised when the data is corrupt"""

    def __init__(self, message="The data is corrupt."):
        super().__init__(message)


class CapacityError(DataError):
    """Raised when the capacity of the image is exceeded"""

    def __init__(self, message="The capacity of the image has been exceeded."):
        super().__init__(message)


class CryptoError(CustomError):
    """Raised when an encryption-related error occurs"""

    def __init__(self, message="An unspecified encryption-related error occurred."):
        super().__init__(message)


class InvalidPassphraseError(CryptoError):
    """Raised when an invalid passphrase is provided"""

    def __init__(self, message="The passphrase is invalid."):
        super().__init__(message)


class InternalError(CustomError):
    """Raised when an internal error occurs"""

    def __init__(self, message="An unspecified internal error occurred."):
        super().__init__(message)
