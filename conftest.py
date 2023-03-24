import pytest


@pytest.fixture
def book_valid_data() -> dict:
    return {
        "title": "Test Book",
        "author": "Test Author",
        "description": "Test Description",
        "rating": 40
    }


@pytest.fixture
def book_invalid_data() -> dict:
    return {
        "title": "a",
        "author": "b" * 101,
        "description": "c" * 101,
        "rating": 101
    }


@pytest.fixture
def new_book_data() -> dict:
    return {
        "title": "Updated Book",
        "author": "Updated Author",
        "description": "Updated description",
        "rating": 70
    }