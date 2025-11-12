import random
from database import (
    get_all_books, get_book_by_id, get_book_by_isbn,
)
import random


# The test script for the interface, unlike the other scripts this one checks the database.
# With the book, the ids, isbn, and the books patron borrowed.
# Noted. This script should not work test alongside other test scripts.

def get_random_ISBN_value():
    # Gets the random ISBM value
    random_numbers = [random.randint(0, 9) for _ in range(13)]
    random_strings = [str(i) for i in random_numbers]
    random_isbm = "".join(random_strings)
    return random_isbm


def test_get_all_books():
    # This function tests the amount of books it has.
    result = get_all_books()
    assert isinstance(result, list)


def test_get_book_by_id():
    # For this function I'm using the book "To Kill a Mockingbird" as an example, since it has been
    # in the catalog.
    result = get_book_by_id(2)

    # Goes through each display requirements for R2.
    book_title = "To Kill a Mockingbird"
    book_author = "Harper Lee"
    book_ISBN = "9780061120084"
    book_copies = 2
    book_available_copies = 2

    if result:  # If the book is able to display the information
        assert book_title in result["title"]
        assert book_author in result["author"]
        assert book_ISBN in result["isbn"]
        assert result["total_copies"] == book_copies
        assert result["available_copies"] == book_available_copies
    else:  # Else, the book system will display and return nothing
        assert result is None


def test_get_book_by_isbn():
    # Similar to the previous example, except that Get the book, not by using the ID but using
    # The ISBN tag.

    isbn_tag = "9780743273565"
    result = get_book_by_isbn(isbn_tag)
    book_title = "The Great Gatsby"
    book_author = "F. Scott Fitzgerald"
    book_copies = 3
    book_available_copies = 3

    if result:
        assert book_title in result["title"]
        assert book_author in result["author"]
        assert result["total_copies"] == book_copies
        assert result["available_copies"] == book_available_copies
    else:
        assert result is None


def test_return_nothing():
    # This test case will demonstrate what happens if you give an invalid input.
    nothing_1 = get_book_by_isbn("1234567891234")
    nothing_2 = get_book_by_id(50)  # Changed the ID to 50

    # As mentioned before, the system will return nothing if both the ID and ISBN of a book doesn't exist.
    assert nothing_1 is None
    assert nothing_2 is None
