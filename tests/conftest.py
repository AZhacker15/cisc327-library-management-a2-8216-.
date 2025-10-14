from array import array
from zoneinfo import available_timezones

import pytest
from library_service import (
    add_book_to_catalog
)

from database import add_sample_data
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
Below is a sequence of adding books to setup library, note I have to utilize the
@pytest.fixture command so when running the test.yml it won't create an errors as
it depends on if the book is already in the library. 
"""


@pytest.fixture(scope="session")  # Only adds once per module not per test.
# This file is completely redone to accommodate running tests.yml
def library_setup():
    book_selection = [
        ("Percy Jackson", "Rick Riordan"),
        ("IT", "Stephen King"),
        ("Dune", "Frank Herbert"),
        ("The Expanse", "James S. A. Corey"),
        ("Lord Of The Rings", "J.R.R. Tolkien"),
        ("Do Robots Dream Of Electric Sheep", "Philip K. Dick."),
        ("Narnia", "C.S Lewis"),  # This book is for borrowing a book.
        ("The Two Towers", "J.R.R. Tolkien"),
        ("The Return of the King", "J.R.R. Tolkien"),
        ("Percy Jackson: The Sea of Monsters", "Rick Riordan"),
        ("Puttering About in a Small Land", "Philip K. Dick."),
        ("The Stand", "Stephen King"),
        ("Firestarter", "Stephen King"),
        ("Misery", "Stephen King"),
        ("The Expanse: Nemesis Games", "James S. A. Corey")
    ]

    # Reset the database completely for repetitive testing.
    from database import get_db_connection
    conn = get_db_connection()
    try:
        # Directly removes the book from the database.
        conn.execute("DELETE FROM BOOKS")
        conn.execute("DELETE FROM sqlite_sequence WHERE name='books'")
        conn.commit()
    finally:
        conn.close()

    # Retrieves the sample data first.
    add_sample_data()

    # Add each book into the database
    for title, author in book_selection:
        isbn_value = get_random_ISBN()
        if title != 'Narnia':
            available_copies = get_random_copy()
        else:
            available_copies = 8
        success, message = add_book_to_catalog(title, author, isbn_value, available_copies)

        assert success == True
        assert "Book" in message
