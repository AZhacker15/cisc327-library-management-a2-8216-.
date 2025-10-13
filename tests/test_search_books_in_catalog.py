import pytest
import random
from library_service import (
    search_books_in_catalog
)
from database import get_book_by_id

# This file showcases the test cases for searching for a book in the online catalog.
# IMPORTANT This test suite only works if R2_alt_test has already been initialized,
# as it contains books from those tests.


def test_search_book_ISBN():
    # Positive test case for searching a book using an ISBN type.

    targeted_book = get_book_by_id(14)
    targeted_isbn = targeted_book['isbn']  # Retrieves the ISBN since it's randomized, but the ID isn't

    success, message, book_list = search_books_in_catalog(targeted_isbn, 'isbn')

    assert success == True
    assert 'List of books found:' in message

    assert book_list != []


def test_search_book_full_title():
    # Positive test case for searching a book using a title type.

    targeted_book_title = "It"  # Works due to partial matching
    success, message, book_list = search_books_in_catalog(targeted_book_title, 'title')

    assert success == True
    assert 'List of books found:' in message

    assert book_list != []


def test_search_book_partial_title():
    # Positive test case for searching a book using a partial title type.
    # Displays teh results that include the name 'percy' in it

    targeted_book_title = "Percy"
    success, message, book_list = search_books_in_catalog(targeted_book_title, 'title')
    print(success, message, book_list)

    assert success == True
    assert 'List of books found:' in message

    assert book_list != []


def test_search_book_title_all_caps():
    # Positive test case to test case insensitivity for the assignment.
    # Note because in the code converts both the target and teh search term into lowercase it doesn't matter.

    targeted_book_title = "LORD OF THE RINGS"
    success, message, book_list = search_books_in_catalog(targeted_book_title, 'title')
    # print(success, message, book_list)

    assert success == True
    assert 'List of books found:' in message

    assert book_list != []


def test_search_book_title_lowercase_partial():
    # Positive test case to test case insensitivity for the assignment.

    targeted_book_title = "gatsby"  # Testing a lower case input
    success, message, book_list = search_books_in_catalog(targeted_book_title, 'title')
    # print(success, message, book_list)

    assert success == True
    assert 'List of books found:' in message

    assert book_list != []


def test_search_book_author():
    # A positive test case that searches the author of the book

    targeted_book_title = "Stephen King"  # The author of the book
    success, message, book_list = search_books_in_catalog(targeted_book_title, 'author')
    print(success, message, book_list)

    assert success == True
    assert 'List of books found:' in message

    assert book_list != []


def test_search_book_author_uppercase():
    # A positive test case that searches the author of the book
    # This time the search query is all caps.
    # Along with partial matching, which displays the results that have the author Herbert.

    targeted_book_title = "HERBERT"
    success, message, book_list = search_books_in_catalog(targeted_book_title, 'author')
    # print(success, message, book_list)

    assert success == True
    assert 'List of books found:' in message

    assert book_list != []


def test_search_book_author_lowercase():
    # Similar to the previous test case but in lower case.

    targeted_book_title = "rick riordan"
    success, message, book_list = search_books_in_catalog(targeted_book_title, 'author')
    # print(success, message, book_list)

    assert success == True
    assert 'List of books found:' in message

    assert book_list != []


def test_search_book_author_partial():
    # A test case that uses partial matching to search for the author

    targeted_book_title = "j.r.r"
    success, message, book_list = search_books_in_catalog(targeted_book_title, 'author')
    # print(success, message, book_list)

    assert success == True
    assert 'List of books found:' in message

    assert book_list != []


def test_invalid_search_type():
    # Invalid search type.

    targeted_isbn = "1234567891234"

    # Banana is not a valid search type for the function and thus will return false.
    success, message, book_list = search_books_in_catalog(targeted_isbn, 'banana')

    assert success == False
    assert 'Invalid search type:' in message

    assert book_list == []


def test_invalid_search_type_nothing():
    # Invalid test case if the search term is empty.

    targeted_isbn = ""
    success, message, book_list = search_books_in_catalog(targeted_isbn, 'isbn')

    assert success == False
    assert 'Search input must not be empty' in message

    assert book_list == []


def test_no_books_ISBN():
    # Invalid test case if the book doesn't exist

    targeted_isbn = "1234567890123"
    success, message, book_list = search_books_in_catalog(targeted_isbn, 'isbn')

    assert success == False
    assert 'Book not found.' in message

    assert book_list == []


def invalid_isbn():
    # Invalid test case by using an invalid ISBN value.
    # Again when searching for a book using an ISBN value the term needs to be precise.

    targeted_isbn = "12390123"
    success, message, book_list = search_books_in_catalog(targeted_isbn, 'isbn')

    assert success == False
    assert 'Invalid ISBN.' in message

    assert book_list == []


def test_no_books_author():
    # Invalid test case where searching a book using an author doesn't exist

    targeted_author = "Markus"
    success, message, book_list = search_books_in_catalog(targeted_author, 'author')

    assert success == False
    assert 'No matching books are found.' in message

    assert book_list == []


def test_no_books_title():
    # A negative test case by searching a nonexistent book title

    targeted_title = "Test_title"
    success, message, book_list = search_books_in_catalog(targeted_title, 'title')

    assert success == False
    assert 'No matching books are found.' in message

    assert book_list == []


def new_words_title():
    # A negative test case by searching a title with additional wording
    # NOTE: The function uses partial matching, but doesn't recognize terms with new lettering
    # Or misspelling mistakes.

    targeted_title = "THE LORD OF THE RINGS"
    success, message, book_list = search_books_in_catalog(targeted_title, 'title')

    assert success == False
    assert 'No matching books are found.' in message

    assert book_list == []


def search_miss_spelling_title():
    # A negative test case of misspelling a title

    targeted_title = "The gret gatbsy"
    success, message, book_list = search_books_in_catalog(targeted_title, 'title')

    assert success == False
    assert 'No matching books are found.' in message

    assert book_list == []


def search_miss_spelling_author():
    # A negative test case of misspelling an author's name.

    targeted_title = "steven king"
    success, message, book_list = search_books_in_catalog(targeted_title, 'author')

    assert success == False
    assert 'No matching books are found.' in message

    assert book_list == []
