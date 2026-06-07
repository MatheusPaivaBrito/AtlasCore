from datetime import UTC

from core_api.modules.library.infrastructure.persistence.models import LibraryModel


def test_base_model_soft_delete_and_restore() -> None:
    library = LibraryModel(name="Central Library", code="central")

    library.soft_delete()

    assert library.deleted_at is not None
    assert library.deleted_at.tzinfo is UTC

    library.restore()

    assert library.deleted_at is None
