import pytest
import random
from playwright.sync_api import Page, expect

"""
This file will test an end-2-end user flow, simulating a patron adding and borrowing a book. 
Unlike in the previous tests, this file will not run any backend unit testing and it will mostly focus on user
interaction.
"""


def get_random_ISBN():
    # This helper function is used to get a randomised ISBM output.
    # The reason why this was created was to prevent test cases on using a repeated ISBM value.
    # Which would create an error, and should be exclusive in one testcase as not the others as it will cause an
    # assertion error.
    random_numbers = [random.randint(0, 9) for _ in range(13)]

    random_strings = [str(i) for i in random_numbers]  # Convert the value into a string value from a list.
    random_isbm = "".join(random_strings)  # Join the numbers together.
    return random_isbm


def test_user_add_book(page: Page):
    # This user flow will simulate the user adding a book into the catalog.

    page.goto("http://127.0.0.1:5000/add_book")
    isbn_value = get_random_ISBN()

    # Adds the information of the book based on the order in the webpage.
    page.get_by_label("Title").fill("E2E Example Book")
    page.get_by_label("Author").fill("Jeffery Katzenberg")
    page.get_by_label("ISBN").fill(isbn_value)
    page.get_by_label("Total Copies").fill("8")

    page.get_by_role("button", name="Add Book to Catalog").click()

    # The text appears on the homepage which is the reason why I have to go there.
    expect(
        page.get_by_text('Book "E2E Example Book" has been successfully added to the catalog.')
    ).to_be_visible()

    page.goto("http://127.0.0.1:5000/catalog")

    # Validates if the new book exists.
    book_title = page.locator("tr", has_text="E2E Example Book")
    book_author = page.locator("tr", has_text="Jeffery Katzenberg")
    book_ISBN = page.locator("tr", has_text=isbn_value)

    expect(book_title).to_be_visible()
    expect(book_author).to_be_visible()
    expect(book_ISBN).to_be_visible()


def test_user_borrow_book(page: Page):
    # This user flow will test the user on borrowing the book.
    page.goto("http://127.0.0.1:5000/catalog")

    patron_id = "646818"

    book_gatsby = page.locator("tr", has_text="The Great Gatsby")
    book_gatsby.get_by_placeholder("Patron ID (6 digits)").fill(patron_id)

    book_gatsby.get_by_role("button", name="Borrow").click()

    # Validates if the user successfully borrow a book
    expect(
        page.get_by_text('Successfully borrowed')
    ).to_be_visible()
