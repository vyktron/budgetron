import scrypt
import jwt
from datetime import datetime, timedelta

jwt_instance = jwt.PyJWT()

def encrypt_password(password : str, salt : str) -> str:
    """
    Encrypt a password using Scrypt

    Parameters:
    ----------
    password: str
        The password to encrypt
    salt: str
        The salt to use for the encryption (email)
    
    Returns:
    -------
    str
        The authentication hash
    """
    # Derive a key from the password using Scrypt and convert to string
    return scrypt.hash(password, salt, N=16384, r=8, p=1).hex()

def generate_token(expiration : int, data : dict, secret_key : str) -> str:
    """
    Generate a JWT token for authentication (access or refresh)

    Parameters:
    ----------
    expiration: int
        The expiration time of the token in seconds
    data: dict
        The data to encrypt in the token
    secret_key: str
        The secret key to use for the encryption
    
    Returns:
    -------
    str
        The encrypted token
    """

    # Expiration date needs to be a NumericDate
    expiration_date = datetime.now() + timedelta(seconds=expiration)

    # Generate the token
    return jwt_instance.encode({'exp': expiration_date, **data}, secret_key, algorithm='HS256')

def decrypt_token(token : str, secret_key : str) -> dict:
    """
    Decrypt a JWT token

    Parameters:
    ----------
    token: str
        The token to decrypt
    secret_key: str
        The secret key to use for the decryption
    
    Returns:
    -------
    dict
        The decrypted token
    
    Raises:
    ------
    Exception
        If the token is invalid or has expired
    """
    # Decode the token
    try :
        return jwt_instance.decode(token, secret_key, algorithms=['HS256'])
    except jwt.exceptions.ExpiredSignatureError:
        raise Exception("Token has expired")
    except:
        raise Exception("Invalid token")

