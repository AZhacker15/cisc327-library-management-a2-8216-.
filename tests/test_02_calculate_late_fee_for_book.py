import pytest
import random
from datetime import datetime, timedelta

from database import get_db_connection
from library_service import (
    calculate_late_fee_for_book, borrow_book_by_patron, return_book_by_patron
)


# This file showcases the test cases for calculating any late fees form overdue books.
# IMPORTANT This test suite only works if conftest.py has already been initialized and used as a parameter,
# as it contains books from those tests.
# In addition, this function calls the borrow and return book functions for these tests cases to work.
# et_db_connection is used to edit the database in order to run tests for an overdue book.

def test_on_day_return(library_setup):
    # A test case in a patron returns a non-overdue book

    patron_id = "549923"
    book_id = 9
    s1, m1 = borrow_book_by_patron(patron_id, book_id)  # Calls the borrow function
    assert s1 == True
    assert "Successfully borrowed" in m1  # Validate if the code is working.

    success, message, cost = calculate_late_fee_for_book(patron_id, book_id)
    assert success == True
    assert "Book is not overdue, no outstanding fees" in message
    assert cost == 0.00
    print(success, message, cost)  # Prints for testing, you could remove it.

    s2, m2 = return_book_by_patron(patron_id, book_id)
    assert s2 == True
    assert "Successfully returned" in m2  # Validate if the code is working.
    # This type of structure is used when testing overdue books.


def test_on_day_return_random(library_setup):
    # A positive test case by borrowing a random book

    patron_id = "985482"
    book_id = random.randint(1, 18)  # Getting Random book
    s1, m1 = borrow_book_by_patron(patron_id, book_id)
    if s1:  # An if condition to see of the book is available or not.
        success, message, cost = calculate_late_fee_for_book(patron_id, book_id)
        assert success == True
        assert "Book is not overdue, no outstanding fees" in message
        assert cost == 0.00
        # print(success, message, cost)

        s2, m2 = return_book_by_patron(patron_id, book_id)
        print(s2, m2)
    else:  # Skips the sequence if the there are no books that are available.
        assert s1 == False
        assert "This book is currently not available." in m1


def test_invalid_id1(library_setup):
    # A negative test case by using an invalid ID, with the length being short

    invalid_patron_id = "33742"
    book_id = 3

    success, message, cost = calculate_late_fee_for_book(invalid_patron_id, book_id)
    assert success == False
    assert "Invalid patron ID. Must be exactly 6 digits." in message
    assert cost == 0.00


def test_invalid_id2(library_setup):
    # A negative test case by using an Invalid ID, with the length being too long.

    invalid_patron_id = "12420934"
    book_id = 6

    success, message, cost = calculate_late_fee_for_book(invalid_patron_id, book_id)
    assert success == False
    assert "Invalid patron ID. Must be exactly 6 digits." in message
    assert cost == 0.00


def test_book_not_found(library_setup):
    # A negative test case in which the book is not found.

    patron_id = "673292"
    invalid_book_id = 50

    success, message, cost = calculate_late_fee_for_book(patron_id, invalid_book_id)

    assert success == False
    assert "Book not found."
    assert cost == 0.00


def test_book_not_borrowed(library_setup):
    # A negative test case in which the book hasn't been borrowed and is not recorded in the records.

    patron_id = "283049"
    book_id = 1

    success, message, cost = calculate_late_fee_for_book(patron_id, book_id)
    assert success == False
    assert "Database error:" in message
    assert cost == 0.00


def test_book_overdue_1_day(library_setup):
    # A test case in which the book is returned but is overdue by 1 day.

    patron_id = "648239"
    book_id = 7

    s1, m1 = borrow_book_by_patron(patron_id, book_id)
    assert s1 == True
    assert "Successfully borrowed" in m1

    # The only way I can edit is by calling get_db_connection and edit the file directly.
    # The same applies for the next 2 test cases below.
    conn = get_db_connection()
    current_date = datetime.now()
    overdue_date = datetime.now() - timedelta(days=1)
    conn.execute('''
           UPDATE borrow_records 
           SET due_date = ? 
           WHERE patron_id = ? AND book_id = ? AND return_date IS NULL
       ''', (overdue_date.isoformat(), patron_id, book_id))
    conn.commit()
    conn.close()

    success, message, cost = calculate_late_fee_for_book(patron_id, book_id)

    assert success == True
    assert f'Book is overdue by: 1 day(s)' in message
    assert cost == 1.00  # Checks the cost to see if it's 1 dollar

    s2, m2 = return_book_by_patron(patron_id, book_id)
    # print(s2, m2)
    assert s2 == True
    assert "Successfully returned" in m2


def test_book_overdue_15_day(library_setup):
    # A test case in which the book is returned but is overdue by 15 days.
    # Since it's the limit the overdue days for a book.

    patron_id = "118363"
    book_id = 2

    s1, m1 = borrow_book_by_patron(patron_id, book_id)
    assert s1 == True
    assert "Successfully borrowed" in m1

    conn = get_db_connection()
    current_date = datetime.now()
    overdue_date = datetime.now() - timedelta(days=15)
    conn.execute('''
               UPDATE borrow_records 
               SET due_date = ? 
               WHERE patron_id = ? AND book_id = ? AND return_date IS NULL
           ''', (overdue_date.isoformat(), patron_id, book_id))
    conn.commit()
    conn.close()

    success, message, cost = calculate_late_fee_for_book(patron_id, book_id)

    assert success == True
    assert f'Book is overdue by: 15 day(s)' in message
    assert cost == 15.00

    s2, m2 = return_book_by_patron(patron_id, book_id)
    # print(s2, m2)
    assert s2 == True
    assert "Successfully returned" in m2


def test_book_return_on_same_day(library_setup):
    # A test case but the patron returning the book on the same day

    patron_id = "932313"
    book_id = 4

    s1, m1 = borrow_book_by_patron(patron_id, book_id)
    assert s1 == True
    assert "Successfully borrowed" in m1

    conn = get_db_connection()
    current_date = datetime.now()
    # The number of days is zero to simulate returning the bok on the same day it's due.
    overdue_date = datetime.now() - timedelta(days=0)
    conn.execute('''
                   UPDATE borrow_records 
                   SET due_date = ? 
                   WHERE patron_id = ? AND book_id = ? AND return_date IS NULL
               ''', (overdue_date.isoformat(), patron_id, book_id))
    conn.commit()
    conn.close()

    success, message, cost = calculate_late_fee_for_book(patron_id, book_id)

    assert success == True
    assert f'Book is not overdue, no outstanding fees' in message
    assert cost == 0.00

    s2, m2 = return_book_by_patron(patron_id, book_id)
    # print(s2, m2)
    assert s2 == True
    assert "Successfully returned" in m2


