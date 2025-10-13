import pytest
from unittest.mock import patch
from library_service import search_books_in_catalog


# 1️⃣ Empty Search Term
def test_search_books_empty_search_term():
    """Should fail when search term is empty or whitespace."""
    success, message, results = search_books_in_catalog("   ", "title")
    assert not success
    assert message == "Search input must not be empty"
    assert results == []


# 2️⃣ Invalid Search Type
def test_search_books_invalid_type():
    """Should fail when search_type is not one of the valid options."""
    success, message, results = search_books_in_catalog("harry potter", "genre")
    assert not success
    assert "Invalid search type" in message
    assert results == []


# 3️⃣ ISBN Search — Exact Match Success
@patch("library_service.get_book_by_isbn")
def test_search_books_isbn_found(mock_get_book_by_isbn):
    """Should find a book using exact ISBN match."""
    mock_get_book_by_isbn.return_value = {
        "id": 1,
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "isbn": "9780743273565",
        "available_copies": 3,
    }

    success, message, results = search_books_in_catalog("9780743273565", "isbn")
    assert success
    assert "List of books found" in message
    assert isinstance(results, list)
    assert len(results) == 1
    assert results[0]["isbn"] == "9780743273565"
    mock_get_book_by_isbn.assert_called_once_with("9780743273565")


# 4️⃣ Author Partial Match — Case Insensitive Search
@patch("library_service.get_all_books")
def test_search_books_author_partial_match(mock_get_all_books):
    """Should find books by partial author name regardless of case."""
    mock_get_all_books.return_value = [
        {"id": 1, "title": "Inferno", "author": "Dan Brown", "isbn": "111"},
        {"id": 2, "title": "Angels and Demons", "author": "dan brown", "isbn": "222"},
        {"id": 3, "title": "Dune", "author": "Frank Herbert", "isbn": "333"},
    ]

    success, message, results = search_books_in_catalog("dan brown", "author")
    assert success
    assert "List of books found" in message
    assert len(results) == 2
    for book in results:
        assert "dan brown" in book["author"].lower()
    mock_get_all_books.assert_called_once()


@patch("library_service.get_all_books", return_value=None)
def test_search_books_database_failure(mock_get_all_books):
    """Should handle None response from database gracefully instead of crashing."""
    success, message, results = search_books_in_catalog("harry", "title")

    assert not success
    assert "database error" in message.lower()
    assert results == []
    mock_get_all_books.assert_called_once()
