from datetime import datetime, timedelta

import pytest

from database import get_book_by_id, get_patron_borrow_count
from library_service import (
    borrow_book_by_patron, return_book_by_patron
)

import random


# This test shows demonstrates the functional requirements of R3. Borrowing a book from the database.
# Along with all the testcases that will demonstrate the positive and negative return statements.


def get_random_ID():
    # This function gets a randomized id when borrowing his book.
    random_numbers = [random.randint(0, 9) for _ in range(6)]
    id_strings = [str(i) for i in random_numbers]
    id_value = "".join(id_strings)
    return id_value


def test_accept_borrowing(library_setup):
    # This function borrow a books.
    current_time = datetime.now()
    patron_id = get_random_ID()
    random_book_id = random.randint(1, 18)  # Gets a random book so the books won't lose copies as fast
    random_book_name = get_book_by_id(random_book_id)
    due_date = current_time + timedelta(days=14)
    success, message = borrow_book_by_patron(patron_id, random_book_id)

    if success:
        assert success == True
        assert (f'Successfully borrowed "{random_book_name["title"]}". Due date: {due_date.strftime("%Y-%m-%d")}'
                in message)
    else:  # This statement will happen if the patron gets a book with no copies left especially if the book has
        # The id of 3!
        assert success == False
        assert "This book is currently not available." in message

    success2, message2 = return_book_by_patron(patron_id, random_book_id)
    assert success2 == True
    assert "Successfully returned " in message2

    # Update: Added a return statement


def test_exceed_book_limit(library_setup):
    # This functions tests wait will happen if a patron borrowed more than 5 books.
    current_time = datetime.now()
    patron_id = "123456"
    due_date = current_time + timedelta(days=14)

    # Calling the same function again instead of calling the file itself again.
    success, message = borrow_book_by_patron(patron_id, 10)
    success, message = borrow_book_by_patron(patron_id, 10)
    success, message = borrow_book_by_patron(patron_id, 10)
    success, message = borrow_book_by_patron(patron_id, 10)
    success, message = borrow_book_by_patron(patron_id, 10)
    success, message = borrow_book_by_patron(patron_id, 10)

    # I chose the 10th book since I would be able to see the remaining copies of said book, as well as
    # checking if my test case works.
    assert success == False
    if "You have reached the maximum borrowing limit of 5 books." in message:
        assert "You have reached the maximum borrowing limit of 5 books." in message
    else:  # This assertion will run if someone took the last narnia book.
        assert "This book is currently not available." in message


def test_invalid_patron_id_numbers(library_setup):
    # The Test case that checks for an invalid password.
    current_time = datetime.now()
    wrong_id = "126573829"
    success, message = borrow_book_by_patron(wrong_id, 2)

    assert success == False
    assert "Invalid patron ID. Must be exactly 6 digits." in message


def test_invalid_patron_id_letters(library_setup):
    # The test case that checks for letters in the patron id
    current_time = datetime.now()
    wrong_id = "126abc"
    success, message = borrow_book_by_patron(wrong_id, 2)

    assert success == False
    assert "Invalid patron ID. Must be exactly 6 digits." in message


def test_no_book_is_available(library_setup):
    # The test case that checks if the book is available in the catalog
    current_time = datetime.now()
    id_value = get_random_ID()
    success, message = borrow_book_by_patron(id_value, 50)

    assert success == False
    assert "Book not found." in message


def test_no_copies_found(library_setup):
    # The test case checks if there are no copies.
    current_time = datetime.now()
    id_value = get_random_ID()
    success, message = borrow_book_by_patron(id_value, 3)

    assert success == False
    assert "This book is currently not available." in message

# Removed the second randomized function as it seems redundant
