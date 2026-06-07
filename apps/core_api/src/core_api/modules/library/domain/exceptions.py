from starlette import status

from shared_kernel.errors import ApplicationError, ErrorTarget


class LibraryError(ApplicationError):
    code = "library.error"
    message = "A library domain error occurred."


class BookAlreadyRentedError(LibraryError):
    status_code = status.HTTP_409_CONFLICT
    code = "library.book_already_rented"

    def __init__(self, *, book_id: str, reader_id: str | None = None) -> None:
        payload = {"book_id": book_id}
        if reader_id:
            payload["reader_id"] = reader_id

        super().__init__(
            "Book is already rented.",
            target=ErrorTarget(location="body", entity="book_rentals", field="book_id", payload=payload),
        )


class BookNotAvailableError(LibraryError):
    status_code = status.HTTP_409_CONFLICT
    code = "library.book_not_available"

    def __init__(self, *, book_id: str) -> None:
        super().__init__(
            "Book is not available for rental.",
            target=ErrorTarget(
                location="body",
                entity="book_rentals",
                field="book_id",
                payload={"book_id": book_id},
            ),
        )
