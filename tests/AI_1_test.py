import pytest
from unittest.mock import patch
from library_service import return_book_by_patron


# 1️⃣ Invalid Patron ID Format
def test_return_book_invalid_patron_id():
    """Should fail when patron ID is not a 6-digit number."""
    success, message = return_book_by_patron("abc123", 1)
    assert not success
    assert message == "Invalid patron ID. Must be exactly 6 digits."


# 2️⃣ Book Not Found in Database
@patch("library_service.get_book_by_id", return_value=None)
def test_return_book_not_found(mock_get_book):
    """Should fail when the book ID does not exist in the database."""
    success, message = return_book_by_patron("123456", 999)
    assert not success
    assert message == "Book not found."
    mock_get_book.assert_called_once_with(999)


# 3️⃣ Patron Has No Books Borrowed
@patch("library_service.get_book_by_id", return_value={"id": 1, "title": "Book A"})
@patch("library_service.get_patron_borrow_count", return_value=0)
def test_return_book_no_books_borrowed(mock_borrow_count, mock_get_book):
    """Should fail when patron has no books currently borrowed."""
    success, message = return_book_by_patron("123456", 1)
    assert not success
    assert message == "There are no books to return."
    mock_get_book.assert_called_once()
    mock_borrow_count.assert_called_once_with("123456")


# 4️⃣ Database Error: Return Date Update Fails
@patch("library_service.get_book_by_id", return_value={"id": 1, "title": "Book A"})
@patch("library_service.get_patron_borrow_count", return_value=1)
@patch("library_service.calculate_late_fee_for_book", return_value=(True, "Late fee calculated", 0.0))
@patch("library_service.update_borrow_record_return_date", return_value=False)
def test_return_book_update_date_failure(
        mock_update_date, mock_calc_fee, mock_borrow_count, mock_get_book
):
    """Should fail when the database fails to update the return date."""
    success, message = return_book_by_patron("123456", 1)
    assert not success
    assert "Database error" in message
    mock_update_date.assert_called_once()


# 5️⃣ Successful Book Return
@patch("library_service.get_book_by_id", return_value={"id": 1, "title": "Book A"})
@patch("library_service.get_patron_borrow_count", return_value=1)
@patch("library_service.calculate_late_fee_for_book", return_value=(True, "Late fee calculated", 0.0))
@patch("library_service.update_borrow_record_return_date", return_value=True)
@patch("library_service.update_book_availability", return_value=True)
def test_return_book_success(
        mock_update_availability,
        mock_update_date,
        mock_calc_fee,
        mock_borrow_count,
        mock_get_book,
):
    """Should succeed when all operations complete successfully."""
    success, message = return_book_by_patron("123456", 1)
    assert success
    assert "Successfully returned" in message
    mock_get_book.assert_called_once_with(1)
    mock_borrow_count.assert_called_once_with("123456")
    mock_calc_fee.assert_called_once_with("123456", 1)
    mock_update_date.assert_called_once()
    mock_update_availability.assert_called_once_with(1, +1)


# 6️⃣ Database Error: Book Availability Update Fails
@patch("library_service.get_book_by_id", return_value={"id": 1, "title": "Book A"})
@patch("library_service.get_patron_borrow_count", return_value=1)
@patch("library_service.calculate_late_fee_for_book", return_value=(True, "Late fee calculated", 0.0))
@patch("library_service.update_borrow_record_return_date", return_value=True)
@patch("library_service.update_book_availability", return_value=False)
def test_return_book_update_availability_failure(
        mock_update_availability,
        mock_update_date,
        mock_calc_fee,
        mock_borrow_count,
        mock_get_book,
):
    """Should fail when updating the book’s availability in the database fails."""
    success, message = return_book_by_patron("123456", 1)
    assert not success
    assert "Database error" in message
    mock_update_availability.assert_called_once_with(1, +1)
