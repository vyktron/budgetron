from pymongo import MongoClient
from model.db.data import Account, Transaction, User, Bank
from bson.objectid import ObjectId
import json

class DBClient:
    def __init__(self, host : str, port : int, username : str, password : str):
        """
        Constructor for the MongoDBClient class

        Parameters:
        ----------
        host: str
            The host of the database
        port: int
            The port of the database
        username: str
            The username of the database
        password: str
            The password of the database
        """

        self.client = MongoClient(host, port, username=username, password=password)
        self.db = self.client['budgetron']
        self.users_collection = self.db['users']
        self.banks_collection = self.db['banks']
        self.accounts_collection = self.db['accounts']
        self.transactions_collection = self.db['transactions']
    
    def save_account(self, account : Account, bank_id : str) -> str:
        """
        Save an account in the database
        
        Parameters:
        ----------
        account: Account
            The account to save
        bank_id: str
            The id of the bank to save the account in
        
        Returns:
        -------
        str
            The id of the saved account
        
        Raises:
        ------
        Exception
            If the account insertion failed
        Exception
            If the account number already exists
        """

        # Remove the id field from the account
        account_dict = account.model_dump()
        del account_dict['id']
        account_dict['transactions'] = [ObjectId(t) for t in account_dict['transactions']]
        # Verify that the account number does not already exist
        account_in_db = self.accounts_collection.find_one({'number': account.number})
        if account_in_db is not None:
            raise Exception("Account number already exists")

        # Handle failed insertion
        saved_account = self.accounts_collection.insert_one(account_dict)
        if saved_account is None:
            raise Exception("Failed to save account")
        
        # Add the account id to the bank
        self.banks_collection.update_one({'_id': ObjectId(bank_id)}, {'$push': {'accounts': str(saved_account.inserted_id)}})
        
        return str(saved_account.inserted_id)
    
    def save_transactions(self, transactions : list[Transaction], account_id : str) -> list[str]:

        """
        Save a transaction in the database
        
        Parameters:
        ----------
        transactions: list[Transaction]
            The transactions to save
        account_id: str
            The id of the account to save the transaction in
        
        Returns:
        -------
        list[str]
            The list of ids of the saved transactions
        
        Raises:
        ------
        Exception
            If the transaction insertion failed
        """

        transactions_dict = []
        for transaction in transactions:
            # Remove the id field from the transaction
            transaction_dict = transaction.model_dump()
            # Remove the id field from the transaction (the id is generated by the database)
            del transaction_dict['id']
            transactions_dict.append(transaction_dict)

        # Insert the transactions in the database
        saved_transactions = self.transactions_collection.insert_many(transactions_dict)
        # Handle failed insertion
        if saved_transactions is None:
            raise Exception("Failed to save transactions")
        
        # Convert the ids from ObjectId to str
        inserted_ids_str = [str(t) for t in saved_transactions.inserted_ids]

        # Add the transactions ids to the account
        self.accounts_collection.update_one({'_id': ObjectId(account_id)}, {'$push': {'transactions': {'$each': inserted_ids_str}}})

        return inserted_ids_str
    
    def save_transaction(self, transaction : Transaction, account_id : str) -> str:
        try :
            return self.save_transactions([transaction], account_id)[0]
        except Exception as e:
            raise Exception("Failed to save transaction")

    def get_account(self, account_id : str) -> Account:
        """
        Get an account from the database
        
        Parameters:
        ----------
        account_id: str
            The id of the account to get
        
        Returns:
        -------
        Account
            The account retrieved from the database
        """
        account = self.accounts_collection.find_one({'_id': ObjectId(account_id)})
        
        if account is None:
            return None
        
        # Convert the id from ObjectId to str
        account['_id'] = str(account['_id'])
        account['transactions'] = [str(t) for t in account['transactions']]

        return Account(**account)
    
    def get_account_by_number(self, account_number : str) -> Account:
        """
        Get an account from the database
        
        Parameters:
        ----------
        account_number: str
            The number of the account to get
        
        Returns:
        -------
        Account
            The account retrieved from the database
        """
        account = self.accounts_collection.find_one({'number': account_number})
        account['_id'] = str(account['_id'])
        if account is None:
            return None
        return Account(**account)
    
    def get_accounts(self, bank : Bank) -> list[Account] :
        """
        Get all the accounts from a bank account
        
        Parameters:
        ----------
        bank: Bank
            The bank account to get the accounts from
        
        Returns:
        -------
        list[Account]
            The list of accounts retrieved from the database
        """
        
        accounts = self.accounts_collection.find({'_id': {'$in': [ObjectId(a) for a in bank.accounts]}})
        
        res = []
        if accounts is not None:
            for a in accounts:
                a['_id'] = str(a['_id'])
                a['transactions'] = [str(t) for t in a['transactions']]
                res.append(Account(**a))
        return res

    def get_transaction(self, transaction_id : str) -> Transaction:
        """
        Get a transaction from the database
        
        Parameters:
        ----------
        transaction_id: str
            The id of the transaction to get
        
        Returns:
        -------
        Transaction
            The transaction retrieved from the database
        """
        transaction = self.transactions_collection.find_one({'_id': ObjectId(transaction_id)})
        transaction['_id'] = str(transaction['_id'])
        if transaction is None:
            return None
        return Transaction(**transaction)
    
    def get_transactions(self, account : Account) -> list[Transaction]:
        """
        Get all the transactions from an account
        
        Parameters:
        ----------
        account: Account
            The id of the account to get the transactions from
        
        Returns:
        -------
        list[Transaction]
            The list of transactions retrieved from the database
        """

        transactions = self.transactions_collection.find({'_id': {'$in': [ObjectId(t) for t in account.transactions]}})
        
        if transactions is None:
            return None
        
        res = []
        for t in transactions:
            t['_id'] = str(t['_id'])
            res.append(Transaction(**t))
        return res
    
    def verify_user(self, authentication_hash : str) -> User:
        """
        Verify that a user exists in the database
        
        Parameters:
        ----------
        authentication_hash: str
            The authentication hash of the user to verify
        
        Returns:
        -------
        User
            The user retrieved from the database (None if the user does not exist)
        """
        user = self.users_collection.find_one({'authentication_hash': authentication_hash})
        if user is None:
            return None
        # Convert the id from ObjectId to str
        user['_id'] = str(user['_id'])
        # Delete None fields
        user = {k: v for k, v in user.items() if v is not None}
        return User(**user)
    
    def update_user(self, user_id : str, **kwargs) -> None:
        """
        Update a user in the database
        
        Parameters:
        ----------
        user_id: str
            The id of the user to update
        **kwargs
            The fields to update
        """
        self.users_collection.update_one({'_id': ObjectId(user_id)}, {'$set': kwargs})
    
    def user_by_email(self, email : str) -> User:
        """
        Verify that an email is unique in the database and get the user if it exists
        
        Parameters:
        ----------
        email: str
            The email to verify
        
        Returns:
        -------
        User
            The user retrieved from the database (None if the user does not exist)
        """
        user = self.users_collection.find_one({'email': email})
        if user is None:
            return None
        # Convert the id from ObjectId to str
        user['_id'] = str(user['_id'])
        # Delete None fields
        user = {k: v for k, v in user.items() if v is not None}
        return User(**user)
        

    def save_user(self, user : User) -> str:
        """
        Save a user in the database
        
        Parameters:
        ----------
        user: User
            The user to save
        
        Returns:
        -------
        str
            The id of the saved user
        
        Raises:
        ------
        DatabaseError
            If the user insertion failed
        """

        # Remove the id field from the user
        user_dict = user.model_dump()
        del user_dict['id']

        # Handle failed insertion
        saved_user = self.users_collection.insert_one(user_dict)
        if saved_user is None:
            raise DatabaseError("Failed to save user")
        return str(saved_user.inserted_id)
    
    def save_bank(self, bank : Bank, user_id : str) -> str:
        """
        Save a bank in the database
        
        Parameters:
        ----------
        bank: Bank
            The bank to save
        user_id: str
            The id of the user to save the bank in
        
        Returns:
        -------
        str
            The id of the saved bank
        
        Raises:
        ------
        DatabaseError
            If the bank insertion failed
        """

        # Remove the id field from the bank
        bank_dict = bank.model_dump()
        del bank_dict['id']
        # Handle failed insertion
        saved_bank = self.banks_collection.insert_one(bank_dict)
        if saved_bank is None:
            raise DatabaseError("Failed to save bank")
        
        # Add the bank id to the user
        self.users_collection.update_one({'_id': ObjectId(user_id)}, {'$push': {'banks': str(saved_bank.inserted_id)}})
        return str(saved_bank.inserted_id)

    def delete_bank(self, bank : Bank, user_id : str) -> None:
        #TODO : ADD A CHECK FOR THE USER TO NOT DELETE A BANK MISLEADINGLY (DO ON THE FRONTEND)
        """
        Delete a bank from the database and all its accounts and transactions linked to it
        
        Parameters:
        ----------
        bank: Bank
            The bank to delete
        user_id: str
            The id of the user to delete the bank from
        
        Raises:
        ------
        DatabaseError
            If the bank deletion failed (from user or in the banks collection)
        """
        # Remove the bank from the user
        result = self.users_collection.update_one({'_id': ObjectId(user_id)}, {'$pull': {'banks': str(bank.id)}})
        if result.modified_count == 0:
            raise DatabaseError("Failed to delete bank from user")
        # Get the accounts from the bank
        accounts = self.get_accounts(bank)
        # Delete all the accounts linked to the bank
        for account in accounts:
            self.delete_account(account)
        # Delete the bank
        result = self.banks_collection.delete_one({'_id': ObjectId(bank.id)})
        if result.deleted_count == 0:
            raise DatabaseError("Failed to delete bank")
    
    def delete_account(self, account : Account) -> None:
        """
        Delete an account from the database and all its transactions linked to it
        
        Parameters:
        ----------
        account: Account
            The account to delete
        
        Raises:
        ------
        DatabaseError
            If the account deletion failed
        """
        # Delete all the transactions linked to the account
        result = self.transactions_collection.delete_many({'_id': {'$in': [ObjectId(t) for t in account.transactions]}})
        # Delete the account
        result = self.accounts_collection.delete_one({'_id': ObjectId(account.id)})
        if result.deleted_count == 0:
            raise DatabaseError("Failed to delete account")
    
    def delete_transactions(self, transaction_ids : list, account_id : str) -> None:
        """
        Delete transactions from the database
        
        Parameters:
        ----------
        transactions: list
            The transaction ids to delete
        account_id: str
            The id of the account to delete the transactions from
        
        Raises:
        ------
        Exception
            If the transactions deletion failed
        """
        result = self.transactions_collection.delete_many({'_id': {'$in': [ObjectId(id) for id in transaction_ids]}})
        if result.deleted_count == 0 and len(transaction_ids) > 0:
            raise DatabaseError("Failed to delete transactions")
        # Delete all the ids from the account
        result = self.accounts_collection.update_one({'_id': ObjectId(account_id)}, {'$pull': {'transactions': {'$in': [id for id in transaction_ids]}}})
        if result.modified_count == 0 and len(transaction_ids) > 0:
            raise DatabaseError("Failed to delete transactions from account")
        
    
    def update_balance(self, account : Account, balance : float, date : str) -> None:
        """
        Update the balance of an account
        
        Parameters:
        ----------
        account: Account
            The account to update
        balance: float
            The new balance
        date: str
        """
        self.accounts_collection.update_one({'_id': ObjectId(account.id)}, {'$push': {'balances': balance, 'dates': date}})
    
    def update_bank_last_update(self, bank_id : str, date : str) -> None:
        """
        Update the last update of a bank
        
        Parameters:
        ----------
        bank_id: str
            The id of the bank to update
        date: str
            The new last update
        """
        self.banks_collection.update_one({'_id': ObjectId(bank_id)}, {'$set': {'last_update': date}})
    
    def update_account_balance(self, account : Account, balance : float, date : str) -> None:
        """
        Update the balance of an account
        
        Parameters:
        ----------
        account: Account
            The account to update
        balance: float
            The new balance
        date: str
        """
        # Verify that the date is more recent than the last date 
        if len(account.dates) > 0 and account.dates[-1] > date:
            self.accounts_collection.update_one({'_id': ObjectId(account.id)}, {'$push': {'balances': balance, 'dates': date}})
    
    def get_banks(self, user : User) -> list[Bank]:
        """
        Get all the banks from a user
        
        Parameters:
        ----------
        user: User
            The user to get the banks from
        
        Returns:
        -------
        list[Bank]
            The list of banks retrieved from the database
        """
        
        banks = self.banks_collection.find({'_id': {'$in': [ObjectId(b) for b in user.banks]}})
        
        if banks is None:
            return None
        
        res = []
        for b in banks:
            b['_id'] = str(b['_id'])
            b['accounts'] = [str(a) for a in b['accounts']]
            res.append(Bank(**b))
        return res

    def clear(self):
        """
        Drop the database (for testing purposes)
        """
        self.client.drop_database("budgetron")
    
    def backup(self):
        """
        Backup the database into a json file
        """

        collections = ['accounts', 'transactions', 'banks', 'users']

        for collection_name in collections:

            collection = self.db[collection_name]
            # Query all documents in the collection
            cursor = collection.find()

            # Convert documents to a list
            documents = list(cursor)

            # Convert ObjectId to str
            for document in documents:
                # Convert all fields that are ObjectId to str
                for key in document:
                    if isinstance(document[key], ObjectId):
                        document[key] = str(document[key])

            output_file = "model/db/backup/" + collection_name + ".json"

            # Write documents to a JSON file
            with open(output_file, 'w+') as json_file:
                json.dump(documents, json_file)


class DatabaseError(Exception):
    """
    Base class for the DatabaseError exception
    """
    pass

