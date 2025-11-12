from datetime import datetime, timedelta

import pytest
import random

from database import get_book_by_id, get_patron_borrowed_books, get_patron_borrow_count, get_db_connection
from services.library_service import (
    return_book_by_patron, borrow_book_by_patron
)


# This file showcases the test cases for returning a book to the online catalog.
# IMPORTANT This test suite only works if conftest.py has already been initialized,
# as it contains books from those tests.
# et_db_connection is used to edit the database in order to run tests for an overdue book.


def test_return_random_book(library_setup):
    # This function test a patron that borrows a random book (Taken from R3)

    current_time = datetime.now()
    patron_id = "526910"
    random_book_id = random.randint(1, 18)
    random_book_name = get_book_by_id(random_book_id)
    due_date = current_time + timedelta(days=14)
    success, message = borrow_book_by_patron(patron_id, random_book_id)
    # print(success, message) (Used for testing to see the results)
    # print(get_patron_borrow_count(patron_id)) (Used for testing to see the results)

    if success:
        assert success == True
        assert (f'Successfully borrowed "{random_book_name["title"]}". Due date: {due_date.strftime("%Y-%m-%d")}.'
                in message)
    else:
        assert success == False
        if "You have reached the maximum borrowing limit of 5 books." in message:
            assert "You have reached the maximum borrowing limit of 5 books." in message
        else:  # This assertion will run if the patron gets a book that is not available
            assert "This book is currently not available." in message


def test_valid_return(library_setup):
    # A positive test case that validates the return using a helper function to borrow the book.

    valid_id = "543218"
    success1, message2 = borrow_book_by_patron(valid_id, 10)

    assert success1 == True
    assert 'Successfully borrowed "Narnia". Due date:' in message2

    book_id = 10
    success, message = return_book_by_patron(valid_id, book_id)
    current_date = datetime.now()

    assert success == True
    assert (f'Successfully returned "Narnia" on {current_date.strftime("%Y-%m-%d")}. '
            f'Status: Book is not overdue, no outstanding fees, Late fee: $0.00.') in message


def test_valid_return2(library_setup):
    # A positive test case that returns a random book.

    valid_id = "526910"  # The patron that borrows a random book.
    patron_info = get_patron_borrowed_books(valid_id)
    if not patron_info:
        # Added this since it will give me an index error. If the book borrowed is not available
        print("No books has been borrowed yet")
        pass
    else:
        # Runs if the book is available
        first_book_id = patron_info[0]['book_id']
        success, message = return_book_by_patron(valid_id, first_book_id)
        first_title = get_book_by_id(first_book_id)
        current_date = datetime.now()

        assert success == True
        assert (f'Successfully returned "{first_title["title"]}" on {current_date.strftime("%Y-%m-%d")}. '
                f'Status: Book is not overdue, no outstanding fees, Late fee: $0.00.') in message


def test_valid_return3(library_setup):
    # A positive test case where the user directly borrows a book and then returns it

    patron_id = "241966"
    book_id = 4

    s1, m1 = borrow_book_by_patron(patron_id, book_id)
    assert s1 == True
    assert "Successfully borrowed" in m1

    success, message = return_book_by_patron(patron_id, book_id)
    current_date = datetime.now()

    assert success == True
    assert (f'Successfully returned "Percy Jackson" on {current_date.strftime("%Y-%m-%d")}. '
            f'Status: Book is not overdue, no outstanding fees, Late fee: $0.00.') in message


def test_invalid_id(library_setup):
    # An invalid test case if the id doesn't meet the required length

    invalid_id = "3461"
    book_id = 7

    success, message = return_book_by_patron(invalid_id, book_id)

    assert success == False
    assert f'Invalid patron ID. Must be exactly 6 digits.'


def test_invalid_id_words(library_setup):
    # An invalid test case if it contains words.

    invalid_id = "123abc"
    book_id = 7

    success, message = return_book_by_patron(invalid_id, book_id)

    assert success == False
    assert f'Invalid patron ID. Must be exactly 6 digits.'


def test_no_books_found(library_setup):
    # An invalid test case if there are no books found.

    patron_id = "768839"
    invalid_book_id = 34

    success, message = return_book_by_patron(patron_id, invalid_book_id)

    assert success == False
    assert f'Book not found.'


def test_book_to_return(library_setup):
    # An invalid test case if the user haven't borrowed any books

    patron_id = "848839"
    no_book_id = 9

    success, message = return_book_by_patron(patron_id, no_book_id)

    assert success == False
    assert f'There are no books to return.'


def test_book_already_returned(library_setup):
    # An invalid test case if the user haven't already returned the same book

    patron_id = "576349"
    book_id = 6

    # The user first borrows the book
    s1, m1 = borrow_book_by_patron(patron_id, book_id)
    assert s1 == True
    assert "Successfully borrowed" in m1

    # The user then returns the book
    s2, m2 = return_book_by_patron(patron_id, book_id)

    assert s2 == True
    assert "Successfully returned" in m2

    # If the user returns the book once again, th function will return false.
    success, message = return_book_by_patron(patron_id, book_id)
    print(success, message)

    assert success == False
    assert f'There are no books to return.' in message


def test_book_late_fee1(library_setup):
    # A valid test case if the book returns was overdue

    patron_id = "468102"
    book_id = 2
    s1, m1 = borrow_book_by_patron(patron_id, book_id)
    assert s1 == True
    assert "Successfully borrowed" in m1

    # In order to create a scenario for an overdue book I Had to manually edit the database by altering the due date
    conn = get_db_connection()
    current_date = datetime.now()
    overdue_date = datetime.now() - timedelta(days=3)  # Make the dae overdue by 3 days.
    conn.execute('''
        UPDATE borrow_records 
        SET due_date = ? 
        WHERE patron_id = ? AND book_id = ? AND return_date IS NULL
    ''', (overdue_date.isoformat(), patron_id, book_id))  # Update the format
    conn.commit()
    conn.close()

    success, message = return_book_by_patron(patron_id, book_id)
    print(success, message)

    assert success == True
    assert (f'Successfully returned "To Kill a Mockingbird" on {current_date.strftime("%Y-%m-%d")}. '
            f'Status: Book is overdue by: 3 day(s), Late fee: $3.00.') in message


def test_book_late_fee2(library_setup):
    # A valid test case that returns a random overdue book

    patron_id = "768902"
    random_book_id = random.randint(1, 18, )  # Chooses a random book.
    random_book_name = get_book_by_id(random_book_id)

    s1, m1 = borrow_book_by_patron(patron_id, random_book_id)
    if s1:  # Checks if the book is that the patron borrowed is actually is available
        assert s1 == True
    else:
        assert s1 == False  # Exits the function if no books are available.
        if "This book is currently not available." in m1:
            assert "This book is currently not available." in m1
            pass

    current_date = datetime.now()  # Gets the current date.
    overdue_days = random.randint(1, 15)  # Randomizes the days overdue
    overdue_date = datetime.now() - timedelta(days=overdue_days)

    conn = get_db_connection()
    conn.execute('''
            UPDATE borrow_records 
            SET due_date = ? 
            WHERE patron_id = ? AND book_id = ? AND return_date IS NULL
        ''', (overdue_date.isoformat(), patron_id, random_book_id))
    conn.commit()
    conn.close()

    success, message = return_book_by_patron(patron_id, random_book_id)
    print(success, message)

    assert success == True
    assert (f'Successfully returned "{random_book_name["title"]}" on {current_date.strftime("%Y-%m-%d")}. '
            f'Status: Book is overdue by: {overdue_days} day(s), Late fee: ${overdue_days}.00.') in message




