import pytest

from datetime import datetime, timedelta

from database import get_db_connection
from library_service import (
    get_patron_status_report, borrow_book_by_patron, return_book_by_patron
)


def test_invalid_patron_id():
    invalid_patron_id = "5362"
    success, message, report = get_patron_status_report(invalid_patron_id)

    assert success == False
    assert 'Invalid patron ID. Must be exactly 6 digits.' in message
    assert report == {}


def test_no_books_in_report():
    patron_id = "132162"
    success, message, report = get_patron_status_report(patron_id)

    assert success == False
    assert 'Patron does not' in message
    assert report == {}


def test_returned_book_in_report():
    patron_id = "652813"
    book_id = 15
    s1, m1 = borrow_book_by_patron(patron_id, book_id)
    assert s1 == True
    assert "Successfully borrowed" in m1

    success, message, report = get_patron_status_report(patron_id)

    assert success == True
    assert 'List of books currently borrowed' in message
    assert report != {}

    s2, m2 = return_book_by_patron(patron_id, book_id)

    assert s2 == True
    assert "Successfully returned" in m2


def test_borrowed_book_in_report():
    patron_id = "528372"
    book_id1 = 4
    book_id2 = 17
    book_id3 = 8

    s1, m1 = borrow_book_by_patron(patron_id, book_id1)
    s2, m2 = borrow_book_by_patron(patron_id, book_id2)
    s3, m3 = borrow_book_by_patron(patron_id, book_id3)

    success, message, report = get_patron_status_report(patron_id)

    # print(message)

    assert success == True
    assert 'List of books currently borrowed' in message
    assert report != {}

    s1, m1 = return_book_by_patron(patron_id, book_id1)
    s2, m2 = return_book_by_patron(patron_id, book_id2)
    s3, m3 = return_book_by_patron(patron_id, book_id3)


def test_return_book():
    patron_id = "222733"
    book_id = 12
    s1, m1 = borrow_book_by_patron(patron_id, book_id)
    assert s1 == True
    assert "Successfully borrowed" in m1

    s2, m2 = return_book_by_patron(patron_id, book_id)
    assert s2 == True
    assert "Successfully returned" in m2

    success, message, report = get_patron_status_report(patron_id)

    assert success == False
    assert 'Patron does not' in message
    assert report == {}


def test_return_1_book():
    patron_id = "528372"
    book_id1 = 6
    book_id2 = 9
    book_id3 = 14

    s1, m1 = borrow_book_by_patron(patron_id, book_id1)
    s2, m2 = borrow_book_by_patron(patron_id, book_id2)
    s3, m3 = borrow_book_by_patron(patron_id, book_id3)

    s1, m1 = return_book_by_patron(patron_id, book_id1)

    success, message, report = get_patron_status_report(patron_id)
    print(message)

    assert success == True
    assert 'List of books currently borrowed' in message
    assert report != {}

    s2, m2 = return_book_by_patron(patron_id, book_id2)
    s3, m3 = return_book_by_patron(patron_id, book_id3)


def test_overdue_book_in_report():
    patron_id = "345127"
    book_id = 4

    s1, m1 = borrow_book_by_patron(patron_id, book_id)
    assert s1 == True
    assert "Successfully borrowed" in m1

    conn = get_db_connection()
    current_date = datetime.now()
    overdue_date = datetime.now() - timedelta(days=8)
    conn.execute('''
            UPDATE borrow_records 
            SET due_date = ? 
            WHERE patron_id = ? AND book_id = ? AND return_date IS NULL
        ''', (overdue_date.isoformat(), patron_id, book_id))
    conn.commit()
    conn.close()
    success, message, report = get_patron_status_report(patron_id)

    # print(message)

    assert success == True
    assert 'List of books currently borrowed' in message
    assert report != {}

    s1, m1 = return_book_by_patron(patron_id, book_id)


def test_overdue_books_in_report():
    patron_id = "528372"
    book_id1 = 2
    book_id2 = 16
    book_id3 = 11

    s1, m1 = borrow_book_by_patron(patron_id, book_id1)
    s2, m2 = borrow_book_by_patron(patron_id, book_id2)
    s3, m3 = borrow_book_by_patron(patron_id, book_id3)

    # Alter the amount of late days for the first book
    conn = get_db_connection()
    current_date = datetime.now()
    overdue_date = datetime.now() - timedelta(days=2)
    conn.execute('''
                UPDATE borrow_records 
                SET due_date = ? 
                WHERE patron_id = ? AND book_id = ? AND return_date IS NULL
            ''', (overdue_date.isoformat(), patron_id, book_id1))
    conn.commit()
    conn.close()

    # For the second book
    conn = get_db_connection()
    current_date = datetime.now()
    overdue_date = datetime.now() - timedelta(days=6)
    conn.execute('''
                UPDATE borrow_records 
                SET due_date = ? 
                WHERE patron_id = ? AND book_id = ? AND return_date IS NULL
            ''', (overdue_date.isoformat(), patron_id, book_id2))
    conn.commit()
    conn.close()

    # For the third book
    conn = get_db_connection()
    current_date = datetime.now()
    overdue_date = datetime.now() - timedelta(days=4)
    conn.execute('''
                UPDATE borrow_records 
                SET due_date = ? 
                WHERE patron_id = ? AND book_id = ? AND return_date IS NULL
            ''', (overdue_date.isoformat(), patron_id, book_id3))
    conn.commit()
    conn.close()

    # The total late fee of the overdue books should be 12 dollars.

    success, message, report = get_patron_status_report(patron_id)
    print(message)

    assert success == True
    assert 'List of books currently borrowed' in message
    assert '12' in message
    assert report != {}

    s1, m1 = return_book_by_patron(patron_id, book_id1)
    s2, m2 = return_book_by_patron(patron_id, book_id2)
    s3, m3 = return_book_by_patron(patron_id, book_id3)
