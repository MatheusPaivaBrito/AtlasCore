class LibraryError(Exception):
    pass


class BookAlreadyRentedError(LibraryError):
    pass


class BookNotAvailableError(LibraryError):
    pass
