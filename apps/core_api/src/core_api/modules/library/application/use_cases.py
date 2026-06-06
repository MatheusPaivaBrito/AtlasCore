from core_api.modules.library.application.dtos import (
    LibraryModelDescription,
    RelationshipExample,
)


def describe_library_model() -> LibraryModelDescription:
    return LibraryModelDescription(
        examples=[
            RelationshipExample(
                name="simple",
                description="Library is a simple aggregate root for the bounded context.",
            ),
            RelationshipExample(
                name="one-to-many",
                description="A Library has many Shelves, and a Shelf has many Books.",
            ),
            RelationshipExample(
                name="many-to-many",
                description="A Reader rents many Books and a Book can be rented by many Readers over time through BookRental.",
            ),
        ]
    )
