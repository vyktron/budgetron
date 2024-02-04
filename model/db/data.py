# File that describes the data model for the application using pydantic
from pydantic import BaseModel, Field
from datetime import date


#### User ####

class User(BaseModel):
    
    """
    Base class for the User model

    Attributes:
    ----------
    id: str
        The id of the user (primary key in the database)
    email: str
        The email of the user
    authentication_hash: str
        The authentication hash of the user
    encrypted_vault_key: str
        The encrypted vault key of the user (will be used to decrypt all other data keys)
    banks: list[str]
        The list of banks ids (foreign keys in the database)
    active : bool
        The activation status of the user (default: False)
    active_token: str
        The jwt token used to activate the user
    """

    id: str = Field(alias="_id", default=None)
    email: str
    authentication_hash : str
    encrypted_vault_key: str = None
    banks: list = []
    active: bool = False 
    active_token: str = None

#### Bank ####

class Bank(BaseModel):

    """
    Base class for the Bank model

    Attributes:
    ----------
    id : str
        The id of the bank (primary key in the database)
    name : str
        The name of the bank
    client_number : str
        The client number of the user in the bank
    website : str
        The website of the bank
    accounts : list[str]
        The list of accounts ids (foreign keys in the database)
    enc_aes_key : str
        The encrypted AES key used to encrypt the data of the bank
    random_iv : str
        The random iv used to encrypt the data of the bank
    last_update : str
        The last update of the bank data
    """
    id: str = Field(alias="_id", default=None)
    name: str
    website: str = None
    client_number: str = None
    accounts: list = []
    last_update: str = None
    enc_aes_key: str = None
    random_iv: str = None

#### Account ####

class Account(BaseModel):

    """
    Base class for the Account model

    Attributes:
    ----------
    id: str
        The id of the account (primary key in the database)
    number: str
        The account number
    name: str
        The account name
    balance: list
        The list of balances of the account [balance1, balance2, ...]
    dates: list
        The list of dates of the balances [date1, date2, ...]
    currency: str
        The account currency
    transactions: list[str]
        The list of transactions ids (foreign keys in the database)
    enc_aes_key: str
        The encrypted AES key used to encrypt the data of the account
    random_iv: str
        The random iv used to encrypt the data of the account
    """

    id: str = Field(alias="_id", default=None)
    number: str
    name: str
    balances: list = []
    dates: list = []
    currency: str = "EUR"
    transactions: list = []
    enc_aes_key: str = None
    random_iv: str = None


#### Transaction ####

class Transaction(BaseModel):


    """
    Base class for the Transaction model
    
    Transactions are encrypted using the random_iv and the enc_aes_key of the account

    Attributes:
    ----------
    id: str
        The id of the transaction (primary key in the database)
    date: str
        The date of the transaction in the format YYYY-MM-DD
    amount: float
        The amount of the transaction
    currency: str
        The currency of the transaction
    description: str
        The description of the transaction
    category: str
        The category of the transaction
    """

    id: str = Field(alias="_id", default=None)
    date: str = date.today().strftime("%Y-%m-%d")
    amount: float
    currency: str = "EUR"
    description: str
    category: str = "None"
