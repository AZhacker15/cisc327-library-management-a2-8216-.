import pytest
from unittest.mock import patch
from datetime import datetime, timedelta


# --- 1. Invalid Patron ID (format or length) ---
def test_invalid_patron_id_format():
    """Should reject invalid patron IDs (non-digit or incorrect length)."""
    from services.library_service import get_patron_status_report

    success, message, report = get_patron_status_report("abc123")
    assert not success
    assert "Invalid patron ID" in message
    assert report == {}


# --- 2. Patron Not Found in Database ---
@patch("services.library_service.get_patron_borrowed_books", return_value=None)
def test_patron_not_found(mock_borrowed_books):
    """Should handle nonexistent patron gracefully."""
    from services.library_service import get_patron_status_report

    success, message, report = get_patron_status_report("123456")
    assert not success
    assert "Patron not existent" in message
    assert report == {}


# --- 3. Patron Exists but Has No Borrowed Books ---
@patch("services.library_service.get_patron_borrowed_books", return_value=[])
def test_patron_no_borrowed_books(mock_borrowed_books):
    """Should handle valid patron who has not borrowed any books."""
    from services.library_service import get_patron_status_report

    success, message, report = get_patron_status_report("123456")
    assert not success
    assert "does not have any borrowed books" in message
    assert report == {}


# --- 4. Patron Has Borrowed Books, All On Time ---
@patch("services.library_service.get_patron_borrowed_books")
@patch("services.library_service.calculate_late_fee_for_book")
def test_patron_with_borrowed_books_on_time(mock_calc_fee, mock_borrowed_books):
    """Should return a valid report when patron has borrowed books (no overdue fees)."""
    from services.library_service import get_patron_status_report

    # Mock borrowed book data
    today = datetime.now()
    mock_borrowed_books.return_value = [
        {
            "title": "Python 101",
            "book_id": "B001",
            "borrow_date": today - timedelta(days=3),
            "due_date": today + timedelta(days=4),
            "is_overdue": False,
        }
    ]

    mock_calc_fee.return_value = (True, "No late fee", 0.0)

    success, message, report = get_patron_status_report("123456")

    assert success
    assert "List of books currently borrowed" in message
    assert "Borrowed books" in report
    assert len(report["Borrowed books"]) == 1
    assert report["Total fee"] == 0.0


# --- 5. Patron Has Overdue Book(s) + Database Defensive Guard ---
@patch("services.library_service.get_patron_borrowed_books")
@patch("services.library_service.calculate_late_fee_for_book")
def test_patron_overdue_books_and_database_error(mock_calc_fee, mock_borrowed_books):
    """Should handle overdue books correctly and sum late fees."""
    from services.library_service import get_patron_status_report

    today = datetime.now()
    mock_borrowed_books.return_value = [
        {
            "title": "Advanced Python",
            "book_id": "B777",
            "borrow_date": today - timedelta(days=15),
            "due_date": today - timedelta(days=5),
            "is_overdue": True,
        },
        {
            "title": "Data Science with Pandas",
            "book_id": "B778",
            "borrow_date": today - timedelta(days=20),
            "due_date": today - timedelta(days=10),
            "is_overdue": True,
        },
    ]

    # Return two different late fees for each book
    mock_calc_fee.side_effect = [
        (True, "Late by 5 days", 2.5),
        (True, "Late by 10 days", 5.0),
    ]

    success, message, report = get_patron_status_report("123456")

    assert success
    assert "List of books currently borrowed" in message
    assert isinstance(report, dict)
    assert "Total fee" in report
    assert report["Total fee"] == 7.5  # 2.5 + 5.0
    assert len(report["Borrowed books"]) == 2


# ✅ Defensive Guard - If Database returns None
@patch("services.library_service.get_patron_borrowed_books", return_value=None)
def test_database_returns_none(mock_borrowed_books):
    """Should handle None response gracefully instead of crashing."""
    from services.library_service import get_patron_status_report
    try:
        success, message, report = get_patron_status_report("654321")
    except TypeError:
        pytest.fail("Function crashed with TypeError when database returned None")
