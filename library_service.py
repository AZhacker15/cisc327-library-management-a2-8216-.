"""
Library Service Module - Business Logic Functions
Contains all the core business logic for the Library Management System
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any

from flask import current_app

from database import (
    get_book_by_id, get_book_by_isbn, get_patron_borrow_count,
    insert_book, insert_borrow_record, update_book_availability,
    update_borrow_record_return_date, get_all_books, get_patron_borrowed_books
)

# from routes.search_routes import search_books


def add_book_to_catalog(title: str, author: str, isbn: str, total_copies: int) -> Tuple[bool, str]:
    """
    Add a new book to the catalog.
    Implements R1: Book Catalog Management
    
    Args:
        title: Book title (max 200 chars)
        author: Book author (max 100 chars)
        isbn: 13-digit ISBN
        total_copies: Number of copies (positive integer)
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Input validation
    if not title or not title.strip():
        return False, "Title is required."

    if len(title.strip()) > 200:
        return False, "Title must be less than 200 characters."

    if not author or not author.strip():
        return False, "Author is required."

    if len(author.strip()) > 100:
        return False, "Author must be less than 100 characters."

    if len(isbn) != 13:
        return False, "ISBN must be exactly 13 digits."
    elif not isbn.isdigit():
        return False, "ISBN must contain numbers."

    if not isinstance(total_copies, int) or total_copies <= 0:
        return False, "Total copies must be a positive integer."

    # Check for duplicate ISBN
    existing = get_book_by_isbn(isbn)
    if existing:
        return False, "A book with this ISBN already exists."

    # Insert new book
    success = insert_book(title.strip(), author.strip(), isbn, total_copies, total_copies)
    if success:
        return True, f'Book "{title.strip()}" has been successfully added to the catalog.'
    else:
        return False, "Database error occurred while adding the book."


def borrow_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Allow a patron to borrow a book.
    Implements R3 as per requirements  
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to borrow
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."

    # Check if book exists and is available
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."

    if book['available_copies'] <= 0:
        return False, "This book is currently not available."

    # Check patron's current borrowed books count
    current_borrowed = get_patron_borrow_count(patron_id)

    if current_borrowed > 5:
        return False, "You have reached the maximum borrowing limit of 5 books."

    # Create borrow record
    borrow_date = datetime.now()
    due_date = borrow_date + timedelta(days=14)

    # Insert borrow record and update availability
    borrow_success = insert_borrow_record(patron_id, book_id, borrow_date, due_date)
    if not borrow_success:
        return False, "Database error occurred while creating borrow record."

    availability_success = update_book_availability(book_id, -1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."

    return True, f'Successfully borrowed "{book["title"]}". Due date: {due_date.strftime("%Y-%m-%d")}.'


def return_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Allows a patron to return a book.

    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to borrow

    Returns:
        tuple: (success: bool, message: str)
    
    TODO: Implement R4 as per requirements
    """

    # Validate the id
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."

    # Checks if book that patron is returning actually exists.
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."

    # Checks the number of books that the person borrowed
    current_borrowed = get_patron_borrow_count(patron_id)
    if current_borrowed <= 0:
        return False, "There are no books to return."

    current_date = datetime.now()  # Gets the current date.

    success, message, late_fee = calculate_late_fee_for_book(patron_id, book_id)  # Gets the late fee

    # Update the date records.
    update_date = update_borrow_record_return_date(patron_id, book_id, current_date)
    if not update_date:
        return False, "Database error occurred while updating the return date."

    # Update the book availability.
    return_success = update_book_availability(book_id, +1)  # Increment the amount of copies.
    if not return_success:
        return False, "Database error occurred while returning book."

    return True, (f'Successfully returned "{book["title"]}" on {current_date.strftime("%Y-%m-%d")}. '
                  f'Status {message}, Late fee: ${late_fee:.2f}.')


def calculate_late_fee_for_book(patron_id: str, book_id: int) -> tuple[bool, str, float]:
    """
    Calculates the late fee of the books
    borrowed by a patron.

    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to borrow

    Returns:
        tuple: (success: bool, message: str, cost: float)
    """
    total_cost = 0.00

    # Validate the id.
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits.", total_cost

    # Validate if the book exists in the catalog.
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found.", total_cost

    patron_info = get_patron_borrowed_books(patron_id)

    # Recommended by ChatGbt for AI-Assisted Test Generation in task 3 to test out database errors.
    if not patron_info or not isinstance(patron_info, list):
        return False, "Database error: could not retrieve borrowed books.", total_cost

    # Checks if the user borrowed any books
    id_list = {books['book_id'] for books in patron_info}
    if book_id not in id_list:
        return False, "The book not borrowed", total_cost

    current_date = datetime.now()  # Gets the current time

    # Retrieves the due date.
    due_date = next((book['due_date'] for book in patron_info if book['book_id'] == book_id),
                    None)
    days_overdue = (current_date - due_date).days

    # If the due date is below zero there are no fees.
    if days_overdue > 0:
        for i in range(days_overdue):
            total_cost += 1.00  # Increment the cost by 1 dollar per day.
        return True, f"Book is overdue by: {days_overdue} day(s)", total_cost
    else:
        return True, "Book is not overdue, no outstanding fees", 0.00


def search_books_in_catalog(search_term: str, search_type: str) -> tuple[bool, str, list[Any]]:
    """
    The search engine to look at the books available in the catalog
    Implements R4 as per requirements

    Args:
       search_term: str: A string that contains what the patron is searching
       search_type: str: Contains what the type of search value the patron is looking for

    Returns:
       tuple: (success: bool, message: str, book_results: list[any])
    """

    book_results = []
    # Turns the input into lowercase to remove case sensitivity
    search_type = search_type.lower()  
    search_term = search_term.lower()
    # Gets all the books
    complete_catalog = get_all_books()  

    # Recommended by ChatGbt for AI-Assisted Test Generation in task 3 to test out database errors.
    if not complete_catalog or not isinstance(complete_catalog, list):
        return False, "Database error: could not retrieve catalog.", []

    # Checks if the search term is empty
    if not search_term or not search_term.strip():
        return False, "Search input must not be empty", []

    # Validate the right search type.
    if search_type not in ('title', 'author', 'isbn'):
        return False, "Invalid search type: Valid ones are ('title', 'author', 'isbn')", []

    # Below are the 3 scenarios that might commence depending on which search type the patron is using
    if search_type == 'isbn':  # If it's ISBN it uses partial matching
        if len(search_term) != 13 or not search_term.isdigit():
            return False, "Invalid ISBN", [] 
        
        # Uses the get book by isbn to look for the book
        book_result = get_book_by_isbn(search_term)  
        if not book_result:
            return False, "Book not found.", []
        book_results.append(book_result)
    
    # If it's either 'author' or 'title', use partial matching.
    if search_type == 'author':  
        for books in complete_catalog:
            # Removes case sensitivity by turing the target into lowercase
            if search_term in books['author'].lower():
                book_results.append(books)
    if search_type == 'title':
        for books in complete_catalog:
            if search_term in books['title'].lower():
                book_results.append(books)

    if not book_results:  # Returns false if no books are found.
        return False, "No matching books are found.", []

    return True, f"List of books found: {len(book_results)} Results:", book_results


def get_patron_status_report(patron_id: str) -> Tuple[bool, str, Dict]:
    """
    Displays the current status report of the patron
    which includes a list of all of their borrowed books.

    Args:
        patron_id: 6-digit library card ID

    Returns:
        tuple: (success: bool, message: str, patron status: Dict)
    """

    book_list = []  # List of books the patron has
    due_dates = []  # List of due_dates and borrow dates the patron has
    total_late_fee_sum = []  # The list to calculate the total sum.

    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits.", {}

    patron_info = get_patron_borrowed_books(patron_id)
    if patron_info is None:  # Checks if the user does exist
        return False, "Patron not existent", {}
    elif len(patron_info) == 0:  # Checks if there are any books that the patron has borrowed
        return False, "Patron does not have any borrowed books", {}
    else:
        for books in patron_info:
            title = books['title']  # Retrieves the title

            patron_book_id = books['book_id']  # Gets the book id.

            # Below calculate gets the late fee, due date, book borrowing date, and due date
            success, message, late_fee = calculate_late_fee_for_book(patron_id, patron_book_id)
            book_barrow_date = books['borrow_date'].strftime("%Y-%m-%d")
            book_due_date = books['due_date'].strftime("%Y-%m-%d")

            # Checks if the book is overdue.
            check_overdue = f"Is Overdue" if books['is_overdue'] else f"Is not Overdue."

            # Organized both the books and due dates into tuples. I even added string labels for better clarification.
            book_group = ("Title-", title, "ID-", patron_book_id)
            date_group = ("Title-", title, "Borrowed date-", book_barrow_date, "Due date-", book_due_date,
                          check_overdue)
            book_list.append(book_group)  # Append both of them into their respected lists.
            due_dates.append(date_group)

            total_late_fee_sum.append(late_fee)

    total_fee_sum = sum(total_late_fee_sum)  # Calculate the sum of the late fee

    # Creates the dict to store the patron's status report.
    patron_status = {'Borrowed books': book_list, 'Due dates': due_dates, 'Total fee': total_fee_sum}

    return True, (f"List of books currently borrowed: {patron_status['Borrowed books']}"
                  f"\nBorrow dates and Due dates for the borrowed books: {patron_status['Due dates']}"
                  f"\nCurrent standing late fee $ {patron_status['Total fee']}"), patron_status


