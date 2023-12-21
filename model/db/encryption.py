import scrypt
import jwt
from datetime import datetime, timedelta
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import base64

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

def decrypt_aes(ciphertext: str, key: str) -> str:
    """
    Decrypt a string encrypted with AES

    Parameters:
    ----------
    ciphertext: str
        The ciphertext to decrypt
    key: str
        The key to use for decryption
    
    Returns:
    -------
    str
        The decrypted plaintext
    """
    # Convert the key to bytes
    key_bytes = key.encode('utf-8')

    # Decode the ciphertext from base64
    ciphertext_bytes = base64.b64decode(ciphertext)

    # Create a cipher object with AES algorithm and CBC mode
    cipher = Cipher(algorithms.AES(key_bytes), modes.CBC(b'\x00' * 16), backend=default_backend())

    # Create a decryptor object
    decryptor = cipher.decryptor()

    # Decrypt the ciphertext
    plaintext_bytes = decryptor.update(ciphertext_bytes) + decryptor.finalize()

    # Remove padding
    unpadder = padding.PKCS7(128).unpadder()
    plaintext_unpadded = unpadder.update(plaintext_bytes) + unpadder.finalize()

    # Convert the plaintext to string
    return plaintext_unpadded.decode('utf-8')
