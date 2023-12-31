import pytest

import sys
import os
# Set the path so we can import from the parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.db.data import Account, Transaction
from model.db.mongo import DBClient
from datetime import date


# Connect to the MongoDB database
client = DBClient(host="localhost", port=27017, username="root", password="admin")

# Test data for insertion
test_account = {
    "number": "123456789",
    "name": "Test Account",
    "balance": 1000.0,
}

test_transaction = {
    "amount": 100.0,
    "description": "Test Transaction",
}

test_transaction2 = {
    "amount": 200.0,
    "description": "Test Transaction 2",
}

test_account_base = Account(**test_account)

# Test the insertion of an account
def test_save_account():
    # Save the account
    saved_account_id = client.save_account(test_account_base)
    # Check that the id is not None
    assert saved_account_id is not None
    # Check that the id is a string
    assert isinstance(saved_account_id, str)

    # Try to get the account from the database
    account = client.get_account(saved_account_id)
    # Check that the account is equal to the test account (except for the id)
    test_account_base.id = saved_account_id
    assert account == test_account_base

# Test the insertion of a transaction
def test_save_transaction():

    # Get the account from the database with the number 123456789
    account = client.get_account_by_number("123456789")
    test_transaction_base = Transaction(**test_transaction)
    # Save the transaction
    saved_transaction_id = client.save_transaction(test_transaction_base, account.id)
    # Check that the id is not None
    assert saved_transaction_id is not None
    # Check that the id is a string
    assert isinstance(saved_transaction_id, str)

    # Try to get the transaction from the database
    transaction = client.get_transaction(saved_transaction_id)
    # Check that the transaction is equal to the test transaction (except for the id and the date)
    test_transaction_base.id = saved_transaction_id
    assert transaction == test_transaction_base

# Test the retrieval of transactions from an account
def test_get_transactions():

    # Find the account with the number 123456789
    account = client.get_account_by_number("123456789")
    # Save the second transaction
    test_transaction_base2 = Transaction(**test_transaction2)
    saved_transaction_id = client.save_transactions([test_transaction_base2, test_transaction_base2], account.id)
    
    # Get the transactions from the database
    transactions = client.get_transactions(account.id)
    print(transactions)
    # Check that the transactions are equal to the test transactions (except for the id and the date)
    test_transaction_base2.id = saved_transaction_id[0]
    test_transaction_base3 = Transaction(**test_transaction2)
    test_transaction_base3.id = saved_transaction_id[1]
    assert test_transaction_base2 in transactions and test_transaction_base3 in transactions and len(transactions) == 3

def clean():
    # Backup the database
    client.backup()
    # Drop the database
    client.clear()

# Clean the database
clean()

# Run the tests
if __name__ == '__main__':
    pytest.main()