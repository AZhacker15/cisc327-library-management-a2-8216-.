import pytest
from library_service import (
    add_book_to_catalog
)
import random


# This function showcases R2, which is the function that displays the catalog.
# However since it technically correlates with function 1, I might was well repeat some of the test functions.
# In addition, I'll also be using this as a helper function for R3.

def get_random_ISBN():
    # Gets the random ISBM value
    random_numbers = [random.randint(0, 9) for _ in range(13)]
    random_strings = [str(i) for i in random_numbers]
    random_isbm = "".join(random_strings)
    return random_isbm


def get_random_copy():
    # Provides a random number of copies for the books that I might add.
    random_copies = random.randint(4, 9)
    return random_copies


"""
Below is a sequence of me adding 7 additional books to the library catalog 
The first 6 uses the same test function layout.
"""


def test_valid_display1():
    # Test shows a valid display of these books, with unique numbering and such.
    isbm_value = get_random_ISBN()
    copies = get_random_copy()
    success, message = add_book_to_catalog("Percy Jackson", "Rick Riordan", isbm_value, copies)

    assert success == True
    assert 'Book "Percy Jackson" has been successfully added to the catalog.' in message


def test_valid_display_2():
    isbm_value = get_random_ISBN()
    copies = get_random_copy()
    success, message = add_book_to_catalog("IT", "Stephen King", isbm_value, copies)

    assert success == True
    assert 'Book "IT" has been successfully added to the catalog.' in message


def test_valid_display_3():
    isbm_value = get_random_ISBN()
    copies = get_random_copy()
    success, message = add_book_to_catalog("Dune", "Frank Herbert", isbm_value, copies)

    assert success == True
    assert 'Book "Dune" has been successfully added to the catalog.' in message


def test_valid_display_4():
    isbm_value = get_random_ISBN()
    copies = get_random_copy()
    success, message = add_book_to_catalog("The Expanse", "James S. A. Corey", isbm_value, copies)

    assert success == True
    assert 'Book "The Expanse" has been successfully added to the catalog.' in message


def test_valid_display_5():
    isbm_value = get_random_ISBN()
    copies = get_random_copy()
    success, message = add_book_to_catalog("Lord Of The Rings", "J.R.R. Tolkien", isbm_value, copies)

    assert success == True
    assert 'Book "Lord Of The Rings" has been successfully added to the catalog.' in message


def test_valid_display_6():
    isbm_value = get_random_ISBN()
    copies = get_random_copy()
    success, message = add_book_to_catalog("Do Robots Dream Of Electric Sheep", "Philip K. Dick.",
                                           isbm_value, copies)

    assert success == True
    assert 'Book "Do Robots Dream Of Electric Sheep" has been successfully added to the catalog.' in message


def test_five_copies_test_for_R3():
    # This test case will be used for R3, for when user attempts to borrow more than 5 books.
    isbm_value = get_random_ISBN()
    success, message = add_book_to_catalog("Narnia", "C.S Lewis", isbm_value, 8)

    assert success == True
    assert 'Book "Narnia" has been successfully added to the catalog.' in message


def test_series_1():
    isbm_value = get_random_ISBN()
    copies = get_random_copy()
    success, message = add_book_to_catalog("The Two Towers", "J.R.R. Tolkien", isbm_value, copies)

    assert success == True
    assert 'Book "The Two Towers" has been successfully added to the catalog.' in message


def test_series_2():
    isbm_value = get_random_ISBN()
    copies = get_random_copy()
    success, message = add_book_to_catalog("The Return of the King", "J.R.R. Tolkien", isbm_value, copies)

    assert success == True
    assert 'Book "The Return of the King" has been successfully added to the catalog.' in message


def test_series_3():
    isbm_value = get_random_ISBN()
    copies = get_random_copy()
    success, message = add_book_to_catalog("Percy Jackson: The Sea of Monsters", "Rick Riordan", isbm_value, copies)

    assert success == True
    assert 'Book "Percy Jackson: The Sea of Monsters" has been successfully added to the catalog.' in message


def test_series_4():
    isbm_value = get_random_ISBN()
    copies = get_random_copy()
    success, message = add_book_to_catalog("Puttering About in a Small Land", "Philip K. Dick.", isbm_value, copies)

    assert success == True
    assert 'Book "Puttering About in a Small Land" has been successfully added to the catalog.' in message


def test_series_5():
    isbm_value = get_random_ISBN()
    copies = get_random_copy()
    success, message = add_book_to_catalog("The Stand", "Stephen King", isbm_value, copies)

    assert success == True
    assert 'Book "The Stand" has been successfully added to the catalog.' in message


def test_series_6():
    isbm_value = get_random_ISBN()
    copies = get_random_copy()
    success, message = add_book_to_catalog("Firestarter", "Stephen King", isbm_value, copies)

    assert success == True
    assert 'Book "Firestarter" has been successfully added to the catalog.' in message


def test_series_7():
    isbm_value = get_random_ISBN()
    copies = get_random_copy()
    success, message = add_book_to_catalog("Misery", "Stephen King", isbm_value, copies)

    assert success == True
    assert 'Book "Misery" has been successfully added to the catalog.' in message


def test_series_8():
    isbm_value = get_random_ISBN()
    copies = get_random_copy()
    success, message = add_book_to_catalog("The Expanse: Nemesis Games", "James S. A. Corey", isbm_value, copies)

    assert success == True
    assert 'Book "The Expanse: Nemesis Games" has been successfully added to the catalog.' in message
