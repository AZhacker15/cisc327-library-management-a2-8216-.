import pytest
import random
from datetime import datetime, timedelta

from unittest.mock import patch

from database import get_db_connection
from library_service import (
    calculate_late_fee_for_book, borrow_book_by_patron, return_book_by_patron
)


def test_on_day_return():
    patron_id = "549923"
    book_id = 9
    s1, m1 = borrow_book_by_patron(patron_id, book_id)

    success, message, cost = calculate_late_fee_for_book(patron_id, book_id)
    assert success == True
    assert "Book is not overdue, no outstanding fees" in message
    assert cost == 0.00
    print(success, message, cost)

    s2, m2 = return_book_by_patron(patron_id, book_id)
    print(s2, m2)


def test_on_day_return_random():
    patron_id = "985482"
    book_id = random.randint(1, 18)
    s1, m1 = borrow_book_by_patron(patron_id, book_id)
    if s1:
        success, message, cost = calculate_late_fee_for_book(patron_id, book_id)
        assert success == True
        assert "Book is not overdue, no outstanding fees" in message
        assert cost == 0.00
        # print(success, message, cost)

        s2, m2 = return_book_by_patron(patron_id, book_id)
        print(s2, m2)
    else:
        assert s1 == False
        assert "This book is currently not available." in m1


def test_invalid_id1():
    invalid_patron_id = "33742"
    book_id = 3

    success, message, cost = calculate_late_fee_for_book(invalid_patron_id, book_id)
    assert success == False
    assert "Invalid patron ID. Must be exactly 6 digits." in message
    assert cost == 0.00


def test_invalid_id2():
    invalid_patron_id = "12420934"
    book_id = 6

    success, message, cost = calculate_late_fee_for_book(invalid_patron_id, book_id)
    assert success == False
    assert "Invalid patron ID. Must be exactly 6 digits." in message
    assert cost == 0.00


def test_book_not_found():
    patron_id = "673292"
    invalid_book_id = 50

    success, message, cost = calculate_late_fee_for_book(patron_id, invalid_book_id)

    assert success == False
    assert "Book not found."
    assert cost == 0.00


def test_book_not_borrowed():
    patron_id = "283049"
    book_id = 1

    success, message, cost = calculate_late_fee_for_book(patron_id, book_id)
    assert success == False
    assert "The book not borrowed" in message
    assert cost == 0.00


def test_book_overdue_1_day():
    patron_id = "648239"
    book_id = 7

    s1, m1 = borrow_book_by_patron(patron_id, book_id)
    assert s1 == True
    assert "Successfully borrowed" in m1

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
    assert cost == 1.00

    s2, m2 = return_book_by_patron(patron_id, book_id)
    # print(s2, m2)
    assert s2 == True
    assert "Successfully returned" in m2


def test_book_overdue_20_day():
    patron_id = "118363"
    book_id = 2

    s1, m1 = borrow_book_by_patron(patron_id, book_id)
    assert s1 == True
    assert "Successfully borrowed" in m1

    conn = get_db_connection()
    current_date = datetime.now()
    overdue_date = datetime.now() - timedelta(days=20)
    conn.execute('''
               UPDATE borrow_records 
               SET due_date = ? 
               WHERE patron_id = ? AND book_id = ? AND return_date IS NULL
           ''', (overdue_date.isoformat(), patron_id, book_id))
    conn.commit()
    conn.close()

    success, message, cost = calculate_late_fee_for_book(patron_id, book_id)

    assert success == True
    assert f'Book is overdue by: 20 day(s)' in message
    assert cost == 20.00

    s2, m2 = return_book_by_patron(patron_id, book_id)
    # print(s2, m2)
    assert s2 == True
    assert "Successfully returned" in m2


def test_book_return_on_same_day():
    patron_id = "932313"
    book_id = 4

    s1, m1 = borrow_book_by_patron(patron_id, book_id)
    assert s1 == True
    assert "Successfully borrowed" in m1

    conn = get_db_connection()
    current_date = datetime.now()
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

