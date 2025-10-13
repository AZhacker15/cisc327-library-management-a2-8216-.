import pytest

from datetime import datetime, timedelta

from database import get_db_connection
from library_service import (
    get_patron_status_report, borrow_book_by_patron, return_book_by_patron
)

# This file demonstrates the test cases for showing patron's status report
# IMPORTANT This test suite only works if R2_alt_test has already been initialized,
# as it contains books from those tests.
# In addition, this function calls the borrow and return book functions for these tests cases to work.
# et_db_connection is used to edit the database in order to run tests for an overdue book.


def test_invalid_patron_id():
    # A negative test case if the patron used an invalid id.

    invalid_patron_id = "5362"
    success, message, report = get_patron_status_report(invalid_patron_id)

    assert success == False
    assert 'Invalid patron ID. Must be exactly 6 digits.' in message
    assert report == {}  # The dict is empty if false


def test_no_books_in_report():
    # A negative test case if there are no books borrowed

    patron_id = "132162"
    success, message, report = get_patron_status_report(patron_id)

    assert success == False
    assert 'Patron does not' in message
    assert report == {}


def test_borrowed_book_in_report():
    # A test case where a patron borrowed a book

    patron_id = "652813"
    book_id = 15
    s1, m1 = borrow_book_by_patron(patron_id, book_id)
    assert s1 == True
    assert "Successfully borrowed" in m1

    # Tests to see if the book is in the records.
    success, message, report = get_patron_status_report(patron_id)

    assert success == True
    assert 'List of books currently borrowed' in message
    assert report != {} # The dict is not empty if true.

    s2, m2 = return_book_by_patron(patron_id, book_id)  # Return the books

    assert s2 == True
    assert "Successfully returned" in m2


def test_borrowed_books_in_report():
    # A test case in which a patron borrowed 3 books at the same time.

    patron_id = "528372"
    book_id1 = 4  # Each book is categorized the number at the end.
    book_id2 = 17
    book_id3 = 8

    # Borrowing the 3 books, would be a bit too redundant to assert them.
    s1, m1 = borrow_book_by_patron(patron_id, book_id1)
    s2, m2 = borrow_book_by_patron(patron_id, book_id2)
    s3, m3 = borrow_book_by_patron(patron_id, book_id3)

    success, message, report = get_patron_status_report(patron_id)

    # print(message)

    # Tests if the books are located in the status report.
    assert success == True
    assert 'List of books currently borrowed' in message
    assert report != {}

    # Return the 3 books
    s1, m1 = return_book_by_patron(patron_id, book_id1)
    s2, m2 = return_book_by_patron(patron_id, book_id2)
    s3, m3 = return_book_by_patron(patron_id, book_id3)


def test_return_book():
    # A test case when viewing a patron record after they returned the book.

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
    # A test case in which the patron returns 1 book out of the 3 that were borrowed.

    patron_id = "528372"
    book_id1 = 6
    book_id2 = 9
    book_id3 = 14

    s1, m1 = borrow_book_by_patron(patron_id, book_id1)
    s2, m2 = borrow_book_by_patron(patron_id, book_id2)
    s3, m3 = borrow_book_by_patron(patron_id, book_id3)

    # Returns the first book only.
    s1, m1 = return_book_by_patron(patron_id, book_id1)

    # The function will return positive put only display 2 books out of 3.
    success, message, report = get_patron_status_report(patron_id)
    print(message)

    assert success == True
    assert 'List of books currently borrowed' in message
    assert report != {}

    s2, m2 = return_book_by_patron(patron_id, book_id2)
    s3, m3 = return_book_by_patron(patron_id, book_id3)


def test_overdue_book_in_report():
    # A test case in which the patron contains an overdue borrowed book

    patron_id = "345127"
    book_id = 4

    # Borrow the book.
    s1, m1 = borrow_book_by_patron(patron_id, book_id)
    assert s1 == True
    assert "Successfully borrowed" in m1

    # Directly edit the database for this scenario to work.
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
    # A test case in which the user has 3 overdue books.

    patron_id = "528372"
    book_id1 = 2
    book_id2 = 16
    book_id3 = 11

    s1, m1 = borrow_book_by_patron(patron_id, book_id1)
    s2, m2 = borrow_book_by_patron(patron_id, book_id2)
    s3, m3 = borrow_book_by_patron(patron_id, book_id3)

    # Alter the amount of late days for the first book by directly editing the database.
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
