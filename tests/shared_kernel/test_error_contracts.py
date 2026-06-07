from shared_kernel.errors import ApplicationError, ErrorTarget


def test_application_error_keeps_structured_context() -> None:
    error = ApplicationError(
        "Invalid payload.",
        code="test.invalid_payload",
        status_code=422,
        target=ErrorTarget(
            location="body",
            entity="books",
            field="isbn",
            payload={"isbn": "bad"},
        ),
        details={"reason": "format"},
    )

    assert error.message == "Invalid payload."
    assert error.code == "test.invalid_payload"
    assert error.status_code == 422
    assert error.target.as_dict() == {
        "location": "body",
        "entity": "books",
        "field": "isbn",
        "payload": {"isbn": "bad"},
    }
    assert error.details == {"reason": "format"}
