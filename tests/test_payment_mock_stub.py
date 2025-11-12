import pytest
from unittest.mock import Mock


from services.library_service import pay_late_fees, refund_late_fee_payment
from services.payment_service import PaymentGateway

# This file is used to run the mocks and stubs for this file.


def test_invalid_patron_id():
    # Validates and reject an invalid ID.
    success, message, transaction_id = pay_late_fees("abc123", 7, None)

    assert success == False
    assert "Invalid patron ID. Must be exactly 6 digits." in message
    assert transaction_id is None


def test_no_fee_info(mocker):
    # The test case that checks it's unable to calculate fees due a database error

    # The mocker patch creates a stub where it provides fake results from the functions called within
    # the "pay_late_fees" function. Without actually effecting the database.

    # Without it, the terminal will return an Operational error.
    mocker.patch("services.library_service.calculate_late_fee_for_book",
                 return_value=(False, "Database error: could not retrieve borrowed books.", None))

    mocker.patch("services.library_service.get_book_by_id",
                 return_value={"title": "Lord Of The Rings"})

    mock_gateway = Mock(spec=PaymentGateway)

    # Returns a mock return value from the PaymentGateway class without actually interacting the function.
    mock_gateway.process_payment.return_value = (True, "txn_543", "Success")

    success, message, transaction_id = pay_late_fees("563239", 8, mock_gateway)
    assert success == False
    assert "Unable to calculate late fees." in message  # Get a false output because there is a database error.
    assert transaction_id is None

    # Because the function stops prior to calling the PaymentGateway class, the mock_gateway has not been asserted.
    mock_gateway.process_payment.assert_not_called()


def test_no_late_fees(mocker):
    # Tests a case where the fee is 0, in which it will be rejected.
    mocker.patch("services.library_service.get_book_by_id",
                 return_value={"title": "Dune"})

    # Provides a fake result where no late fees have been returned
    mocker.patch("services.library_service.calculate_late_fee_for_book",
                 return_value=(True, "Book is not overdue, no outstanding fees", 0.0)
                 )
    mock_gateway = Mock(spec=PaymentGateway)

    success, message, transaction_id = pay_late_fees("563239", 6, mock_gateway)
    assert success == False
    assert "No late fees to pay for this book." in message
    assert transaction_id is None

    mock_gateway.process_payment.assert_not_called()


def test_no_book_found(mocker):
    # A test case where no books are found or returned.
    mocker.patch("services.library_service.calculate_late_fee_for_book",
                 return_value=(True, "Book is overdue by 4 days", 4.0))

    # A stub that simulates finding a missing book.
    mocker.patch("services.library_service.get_book_by_id", return_value=None)

    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (True, "txn_223", "Success")

    success, message, transaction_id = pay_late_fees("542123", 999, mock_gateway)

    assert success is False
    assert "Book not found" in message
    assert transaction_id is None
    mock_gateway.process_payment.assert_not_called()


def test_pay_late_fee_success(mocker):
    # A successful test_case where all conditions are met.

    mocker.patch("services.library_service.get_book_by_id",
                 return_value={"title": "IT"})
    mocker.patch("services.library_service.calculate_late_fee_for_book",
                 return_value=(True, "Book is overdue by 6 days:", 6.0)
                 )
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (True, "txn_123", "Success")

    success, message, transaction_id = pay_late_fees("731945", 5, mock_gateway)
    assert success == True
    assert "Payment successful!" in message
    assert transaction_id == "txn_123"

    # Because that the test case is a success, it reaches the stage where the PaymentGateway mock is asserted.
    # The assert_called_with command will validate if these fake parameters actually came from the studs.
    # This verifcation also checks if the mock was called once, in which it should
    mock_gateway.process_payment.assert_called_with(
        patron_id="731945",
        amount=6.0,
        description="Late fees for 'IT'"
    )
    # This verifcation also checks if the mock was called once, in which it should
    mock_gateway.process_payment.assert_called_once()


def test_pay_late_fee_failure1(mocker):
    # This test case will go through a scenario where despite having the right conditions in the stub,
    # the process_payment function produce a negative result. Which will
    # cause a Payment failure.

    mocker.patch("services.library_service.get_book_by_id",
                 return_value={"title": "Misery"})
    mocker.patch("services.library_service.calculate_late_fee_for_book",
                 return_value=(True, "Book is overdue by 9 days:", 9.0))

    mock_gateway = Mock(spec=PaymentGateway)

    # Unlike before, the outcome from process_payment is negative.
    # For this case, if the amount is over 1000.
    mock_gateway.process_payment.return_value = (False, None, "Payment declined: amount exceeds limit.")

    success, message, transaction_id = pay_late_fees("886213", 17, mock_gateway)
    assert success == False
    assert "Payment failed" in message
    assert "Payment declined: amount exceeds limit." in message
    assert transaction_id is None

    # Despite having an error these values are still valid
    mock_gateway.process_payment.assert_called_with(
        patron_id="886213",
        amount=9.0,
        description="Late fees for 'Misery'"
    )

    # Validates if the assertion still happened.
    mock_gateway.process_payment.assert_called_once()


def test_pay_late_fee_failure2(mocker):
    # Another tests that focuses on another payment error.

    mocker.patch("services.library_service.get_book_by_id",
                 return_value={"title": "Narnia"})
    mocker.patch("services.library_service.calculate_late_fee_for_book",
                 return_value=(True, "Book is overdue by 4 days:", 4.0))

    mock_gateway = Mock(spec=PaymentGateway)

    # Provides a negative outcome if the value is less than 0.
    mock_gateway.process_payment.return_value = (False, None, "Invalid amount: must be greater than 0.")

    success, message, transaction_id = pay_late_fees("637213", 10, mock_gateway)
    assert success == False
    assert "Payment failed" in message
    assert "Invalid amount: must be greater than 0." in message
    assert transaction_id is None

    mock_gateway.process_payment.assert_called_with(
        patron_id="637213",
        amount=4.0,
        description="Late fees for 'Narnia'"
    )
    mock_gateway.process_payment.assert_called_once()


def test_pay_late_fee_failure3(mocker):
    # Another test that focuses on payment failure.
    mocker.patch("services.library_service.get_book_by_id",
                 return_value={"title": "Dune"})
    mocker.patch("services.library_service.calculate_late_fee_for_book",
                 return_value=(True, "Book is overdue by 2 days:", 2.0))

    mock_gateway = Mock(spec=PaymentGateway)

    # The Payment Gateway response now states that there is an invalid patron id.
    mock_gateway.process_payment.return_value = (False, None, "Invalid patron ID")

    success, message, transaction_id = pay_late_fees("677793", 6, mock_gateway)
    assert success == False
    assert "Payment failed" in message
    assert "Invalid patron ID" in message
    assert transaction_id is None

    mock_gateway.process_payment.assert_called_once()

    mock_gateway.process_payment.assert_called_with(
        patron_id="677793",
        amount=2.0,
        description="Late fees for 'Dune'"
    )


def test_payment_processing_error(mocker):
    # This test case focuses on handling an error that came from the PaymentGateway mock.
    mocker.patch("services.library_service.get_book_by_id",
                 return_value={"title": "Firestarter"})
    mocker.patch("services.library_service.calculate_late_fee_for_book",
                 return_value=(True, "Book is overdue by 2 days:", 3.0))

    mock_gateway = Mock(spec=PaymentGateway)

    # Returns a fake error message.
    mock_gateway.process_payment.side_effect = Exception("Gateway Timeout")

    success, message, transaction_id = pay_late_fees("343245", 16, mock_gateway)
    assert success == False
    assert "Payment processing error: Gateway Timeout" in message
    assert transaction_id is None

    # Didn't include asserting the fake parameters due to an error.
    mock_gateway.process_payment.assert_called_once()


# These test cases will be checking the functionalities of both the "refund_late_fee_payment" function in the
# library service file and "refund_payment" function in Payment gateway.

def test_invalid_transaction_id():
    # Tests a case where an invalid id is used.

    # Doesn't include or needs a mocker.patch because there are no functions other than PaymentGateway that this
    # function is dependent on.

    # Also doesn't include a patch for said function because the function will no each the stage where it calls
    # the mock info.
    mock_gateway = Mock(spec=PaymentGateway)

    # Calls the function with an invalid transaction ID value.
    success, message = refund_late_fee_payment("123", 3.0, mock_gateway)

    assert success == False
    assert "Invalid transaction ID." in message

    mock_gateway.refund_payment.assert_not_called()


def test_low_refund_amount():
    # Tests a case where the refund amount is low.

    mock_gateway = Mock(spec=PaymentGateway)

    # Sets the parameter of teh refund value to 0.
    success, message = refund_late_fee_payment("txn_555", 0.0, mock_gateway)

    assert success == False
    assert "Refund amount must be greater than 0." in message

    mock_gateway.refund_payment.assert_not_called()


def test_high_refund_amount():
    # Tests a case where the refund amount is over 15 dollars.

    mock_gateway = Mock(spec=PaymentGateway)

    success, message = refund_late_fee_payment("txn_412", 20.0, mock_gateway)

    assert success == False
    assert "Refund amount exceeds maximum late fee." in message

    mock_gateway.refund_payment.assert_not_called()


def test_refund_success():
    # Tests a case where a patron successfully creates a refund.

    mock_gateway = Mock(spec=PaymentGateway)

    # Patches a fake response where the refund payment was successful.
    mock_gateway.refund_payment.return_value = (True, "Refund of 12.00 Processed successfully")

    success, message = refund_late_fee_payment("txn_472", 12.0, mock_gateway)

    assert success == True
    assert "Refund of 12.00 Processed successfully" in message

    mock_gateway.refund_payment.assert_called_once()
    mock_gateway.refund_payment.assert_called_once_with("txn_472", 12.0)


def test_refund_failed1():
    # A test case where the payment gateway returns a false statement, due to an invalid transaction id.

    mock_gateway = Mock(spec=PaymentGateway)

    mock_gateway.refund_payment.return_value = (False, "Invalid transaction ID")

    success, message = refund_late_fee_payment("txn_874", 6.0, mock_gateway)

    assert success == False
    assert "Refund failed: Invalid transaction ID" in message

    mock_gateway.refund_payment.assert_called_once()
    mock_gateway.refund_payment.assert_called_once_with("txn_874", 6.0)


def test_refund_failed2():
    # A test case where the payment gateway returns a false statement, due to an invalid amount.
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.return_value = (False, "Invalid refund amount")

    success, message = refund_late_fee_payment("txn_339", 12.0, mock_gateway)

    assert success == False
    assert "Refund failed: Invalid refund amount" in message

    mock_gateway.refund_payment.assert_called_once()
    mock_gateway.refund_payment.assert_called_once_with("txn_339", 12.0)


def test_refund_exception_error():
    # A test case that handles an exception error from the payment gateway file.
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.side_effect = Exception("Gateway Timeout")

    success, message = refund_late_fee_payment("txn_119", 2.0, mock_gateway)

    assert success == False
    assert "Refund processing error: Gateway Timeout" in message

    mock_gateway.refund_payment.assert_called_once()
