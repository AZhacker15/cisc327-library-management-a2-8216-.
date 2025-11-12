import pytest
from unittest.mock import patch
from datetime import datetime, timedelta
from services.library_service import calculate_late_fee_for_book


# 1️⃣ Invalid Patron ID Format
def test_calculate_late_fee_invalid_patron_id():
    """Should fail when patron ID is not a valid 6-digit number."""
    success, message, fee = calculate_late_fee_for_book("12A45", 1)
    assert not success
    assert message == "Invalid patron ID. Must be exactly 6 digits."
    assert fee == 0.00


# 2️⃣ Book Not Found in Database
@patch("services.library_service.get_book_by_id", return_value=None)
def test_calculate_late_fee_book_not_found(mock_get_book):
    """Should fail when the book ID does not exist."""
    success, message, fee = calculate_late_fee_for_book("123456", 99)
    assert not success
    assert message == "Book not found."
    assert fee == 0.00
    mock_get_book.assert_called_once_with(99)


# 3️⃣ Patron Has Not Borrowed This Book
@patch("services.library_service.get_book_by_id", return_value={"id": 1, "title": "Book A"})
@patch("services.library_service.get_patron_borrowed_books", return_value=[
    {"book_id": 2, "title": "Other Book", "author": "Author B",
     "borrow_date": datetime.now() - timedelta(days=10),
     "due_date": datetime.now() - timedelta(days=2),
     "is_overdue": True}
])
def test_calculate_late_fee_not_borrowed(mock_borrowed_books, mock_get_book):
    """Should fail when patron never borrowed this book."""
    success, message, fee = calculate_late_fee_for_book("123456", 1)
    assert not success
    assert message == "The book not borrowed."
    assert fee == 0.00
    mock_get_book.assert_called_once()
    mock_borrowed_books.assert_called_once_with("123456")


# 4️⃣ Overdue Book (Positive Late Fee)
@patch("services.library_service.get_book_by_id", return_value={"id": 1, "title": "Book A"})
@patch("services.library_service.get_patron_borrowed_books")
def test_calculate_late_fee_overdue(mock_borrowed_books, mock_get_book):
    """Should correctly calculate late fee for overdue books."""
    overdue_days = 5
    mock_borrowed_books.return_value = [
        {
            "book_id": 1,
            "title": "Book A",
            "author": "Author A",
            "borrow_date": datetime.now() - timedelta(days=15),
            "due_date": datetime.now() - timedelta(days=overdue_days),
            "is_overdue": True,
        }
    ]
    success, message, fee = calculate_late_fee_for_book("123456", 1)
    assert success
    assert "Book is overdue" in message
    assert fee > 0.00  # Should increment for overdue
    mock_get_book.assert_called_once()
    mock_borrowed_books.assert_called_once_with("123456")


@patch("services.library_service.get_book_by_id", return_value={"id": 1, "title": "Book A"})
@patch("services.library_service.get_patron_borrowed_books", return_value=None)
def test_calculate_late_fee_database_failure(mock_borrowed_books, mock_get_book):
    """Should handle unexpected database failure gracefully instead of raising TypeError."""
    success, message, fee = calculate_late_fee_for_book("123456", 1)
    assert not success
    assert "database error" in message.lower()
    assert fee == 0.00
    mock_get_book.assert_called_once()
    mock_borrowed_books.assert_called_once_with("123456")
