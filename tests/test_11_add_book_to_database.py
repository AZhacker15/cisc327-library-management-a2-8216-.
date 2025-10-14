import pytest
import random
from library_service import (
    add_book_to_catalog
)


# This file showcases the test cases for R1, adding a book to the online catalog.

def get_random_ISBN():
    # This helper function is used to get a randomised ISBM output.
    # The reason why this was created was to prevent test cases on using a repeated ISBM value.
    # Which would create an error, and should be exclusive in one testcase as not the others as it will cause an
    # assertion error.
    random_numbers = [random.randint(0, 9) for _ in range(13)]

    random_strings = [str(i) for i in random_numbers]  # Convert the value into a string value from a list.
    random_isbm = "".join(random_strings)  # Join the numbers together.
    return random_isbm


def test_valid_book_submission(library_setup):
    # The first testcase.
    # Since all the requirements are met and satisfied, it should return a positive statement
    isbm_value = get_random_ISBN()  # Retrieve the randomized isbm value.

    random_copies = random.randint(4, 9)
    # Success is a bool to see if the return statement is true. While Message is the message itself.
    success, message = add_book_to_catalog("Random Book", "Random Author", isbm_value, random_copies)

    assert success == True  # Asserts if these 2 statement are true.
    assert 'Book "Random Book" has been successfully added to the catalog.' in message

    # Later removes the book


def test_book_title_too_long():
    # For the second test case, the return statement will show False.
    # The reason is that one of the requirements is not met.

    long_title = "a" * 201  # The title should be less than 200 characters if is, it will return False.
    isbm_value = get_random_ISBN()
    success, message = add_book_to_catalog(long_title, "Max", isbm_value, 4)

    assert success == False
    assert "Title must be less than 200 characters." in message


def test_book_a_name_too_long():
    # The third test will demonstrate a false return statement if the Author has
    # over 100 characters.
    a_name = "g" * 102  # Gave the author's name over 100 words long.
    isbm_value = get_random_ISBN()
    success, message = add_book_to_catalog("The slug", a_name, isbm_value, 4)

    assert success == False
    assert "Author must be less than 100 characters." in message


def test_isbm_is_too_short():
    """Test adding a book with ISBN too short."""
    # This example is taken from the sample test, considering that I still have to test it.
    success, message = add_book_to_catalog("Last of Us", "James", "123456789", 3)

    assert success == False
    assert "13 digits" in message


def test_negative_total_copies():
    # The fourth test will demonstrate having a negative amount of book copies
    isbm_value = get_random_ISBN()
    success, message = add_book_to_catalog("Subzero", "susan", isbm_value, -5)

    assert success == False
    assert "Total copies must be a positive integer." in message


def test_repeated_ISBN(library_setup):
    # The fifth Test will show what happens if the ISBM is repeated.
    # Since I would need to use this command twice for this test to
    # run properly I would need to implement and if an else statement
    # Note I'm adding a different book as an example
    
    success, message = add_book_to_catalog("The Truman Novel", "Kristoff", "1862489149691", 4)
    success, message = add_book_to_catalog("The Truman Novel", "Kristoff", "1862489149691", 4)

    # The test will return False if the ISBN is repeated. Called the function twice.
    assert success == False
    assert "ISBN already exists." in message


def test_no_author_is_located():
    # The Test to see what happens if no author is added.
    # Note Author needs to be in between "" for the function to register.
    isbn_value = get_random_ISBN()
    success, message = add_book_to_catalog("Noman's land", "", isbn_value, 4)
    assert success == False
    assert "Author is required." in message


def test_multiple_errors():
    # This test checks if the library can detect multiple errors, and return False if first detected.
    long_title = "a" * 201
    isbm_value = get_random_ISBN()
    success, message = add_book_to_catalog(long_title, "", isbm_value, -2)

    assert success == False
    # Since the function checks the title first, it should return false when there's something wrong.
    assert "Title must be less than 200 characters." in message


def test_bug_isbm_no_lettering():
    # Fixed bug.
    isbm_numbers = get_random_ISBN()
    sub_isbm = isbm_numbers[0: 9]
    isbm_value = sub_isbm + "abcd"

    success, message = add_book_to_catalog("King Kong", "Delos Wheeler Lovelace", isbm_value, 5)

    assert success == False  # This should give me assertion error.
    assert 'ISBN must contain numbers.' in message
