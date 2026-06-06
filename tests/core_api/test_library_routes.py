from core_api.main import app


def test_library_crud_and_restore_routes_are_registered() -> None:
    paths = {route.path for route in app.routes if route.path.startswith("/library")}

    assert "/library/libraries" in paths
    assert "/library/libraries/{resource_id}/restore" in paths
    assert "/library/shelves" in paths
    assert "/library/shelves/{resource_id}/restore" in paths
    assert "/library/sections" in paths
    assert "/library/sections/{resource_id}/restore" in paths
    assert "/library/books" in paths
    assert "/library/books/{resource_id}/restore" in paths
    assert "/library/readers" in paths
    assert "/library/readers/{resource_id}/restore" in paths
    assert "/library/rentals" in paths
    assert "/library/rentals/{resource_id}/restore" in paths
