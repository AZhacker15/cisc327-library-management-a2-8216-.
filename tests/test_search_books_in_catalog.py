import pytest
import random
from library_service import (
    search_books_in_catalog
)
from database import get_book_by_id


def test_search_book_ISBN():
    targeted_book = get_book_by_id(14)
    targeted_isbn = targeted_book['isbn']  # Retrieves the ISBN since it's randomized, but the ID isn't

    success, message, book_list = search_books_in_catalog(targeted_isbn, 'isbn')

    assert success == True
    assert 'List of books found:' in message

    assert book_list != []


def test_search_book_full_title():
    targeted_book_title = "It"
    success, message, book_list = search_books_in_catalog(targeted_book_title, 'title')

    assert success == True
    assert 'List of books found:' in message

    assert book_list != []


def test_search_book_partial_title():
    targeted_book_title = "Percy"
    success, message, book_list = search_books_in_catalog(targeted_book_title, 'title')
    print(success, message, book_list)

    assert success == True
    assert 'List of books found:' in message

    assert book_list != []


def test_search_book_title_all_caps():
    targeted_book_title = "LORD OF THE RINGS"
    success, message, book_list = search_books_in_catalog(targeted_book_title, 'title')
    # print(success, message, book_list)

    assert success == True
    assert 'List of books found:' in message

    assert book_list != []


def test_search_book_title_lowercase_partial():
    targeted_book_title = "gatsby"
    success, message, book_list = search_books_in_catalog(targeted_book_title, 'title')
    # print(success, message, book_list)

    assert success == True
    assert 'List of books found:' in message

    assert book_list != []


def test_search_book_author():
    targeted_book_title = "Stephen King"
    success, message, book_list = search_books_in_catalog(targeted_book_title, 'author')
    print(success, message, book_list)

    assert success == True
    assert 'List of books found:' in message

    assert book_list != []


def test_search_book_author_uppercase():
    targeted_book_title = "HERBERT"
    success, message, book_list = search_books_in_catalog(targeted_book_title, 'author')
    # print(success, message, book_list)

    assert success == True
    assert 'List of books found:' in message

    assert book_list != []


def test_search_book_author_lowercase():
    targeted_book_title = "rick riordan"
    success, message, book_list = search_books_in_catalog(targeted_book_title, 'author')
    # print(success, message, book_list)

    assert success == True
    assert 'List of books found:' in message

    assert book_list != []


def test_search_book_author_partial():
    targeted_book_title = "j.r.r"
    success, message, book_list = search_books_in_catalog(targeted_book_title, 'author')
    # print(success, message, book_list)

    assert success == True
    assert 'List of books found:' in message

    assert book_list != []


def test_invalid_search_type():
    targeted_isbn = "1234567891234"
    success, message, book_list = search_books_in_catalog(targeted_isbn, 'banana')

    assert success == False
    assert 'Invalid search type:' in message

    assert book_list == []


def test_invalid_search_type_nothing():
    targeted_isbn = ""
    success, message, book_list = search_books_in_catalog(targeted_isbn, 'isbn')

    assert success == False
    assert 'Search input must not be empty' in message

    assert book_list == []


def test_no_books_ISBN():
    targeted_isbn = "1234567890123"
    success, message, book_list = search_books_in_catalog(targeted_isbn, 'isbn')

    assert success == False
    assert 'Book not found.' in message

    assert book_list == []


def invalid_isbn():
    targeted_isbn = "12390123"
    success, message, book_list = search_books_in_catalog(targeted_isbn, 'isbn')

    assert success == False
    assert 'Book not found.' in message

    assert book_list == []


def test_no_books_author():
    targeted_author = "Markus"
    success, message, book_list = search_books_in_catalog(targeted_author, 'author')

    assert success == False
    assert 'No matching books are found.' in message

    assert book_list == []


def test_no_books_title():
    targeted_title = "Test_title"
    success, message, book_list = search_books_in_catalog(targeted_title, 'title')

    assert success == False
    assert 'No matching books are found.' in message

    assert book_list == []


def new_words_title():
    targeted_title = "THE LORD OF THE RINGS"
    success, message, book_list = search_books_in_catalog(targeted_title, 'title')

    assert success == False
    assert 'No matching books are found.' in message

    assert book_list == []


def search_miss_spelling_title():
    targeted_title = "The gret gatbsy"
    success, message, book_list = search_books_in_catalog(targeted_title, 'title')

    assert success == False
    assert 'No matching books are found.' in message

    assert book_list == []


def search_miss_spelling_author():
    targeted_title = "steven king"
    success, message, book_list = search_books_in_catalog(targeted_title, 'author')

    assert success == False
    assert 'No matching books are found.' in message

    assert book_list == []
