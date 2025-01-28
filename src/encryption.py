import hashlib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.asymmetric.utils import Prehashed
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
from binascii import hexlify, unhexlify
# from imaging.png import PngInteractor

def load_private_key(file_path: str) -> rsa.RSAPrivateKey:
    """Load an RSA private key from a PEM file."""
    try:
        with open(file_path, 'r') as key_file:
            pem_data = key_file.read()
            private_key_bytes = pem_data.encode("utf-8")
            private_key: rsa.RSAPrivateKey = load_pem_private_key(private_key_bytes, None)
            if not isinstance(private_key, rsa.RSAPrivateKey):
                raise ValueError("Not an RSA private key")
            return private_key
    except Exception as e:
        raise Exception(f"Error reading private key file: {str(e)}")

def load_public_key(file_path: str) -> rsa.RSAPublicKey:
    """Load an RSA public key from a PEM file."""
    try:
        with open(file_path, 'rb') as key_file:
            pem_data = key_file.read()
            public_key = load_pem_public_key(pem_data)
            if not isinstance(public_key, rsa.RSAPublicKey):
                raise ValueError("Not an RSA public key")
            return public_key
    except Exception as e:
        raise Exception(f"Error reading public key file: {str(e)}")

def sign_message(private_key: rsa.RSAPrivateKey, message: bytes, prehashed = True) -> bytes:
    """Sign a message using the private key."""
    try:
        signature = private_key.sign(
            message,
            padding.PKCS1v15(),
            Prehashed(hashes.SHA256()) if prehashed else hashes.SHA256()
        )
        return signature
    except Exception as e:
        raise Exception(f"Error signing message: {str(e)}")

def verify_signature(public_key: rsa.RSAPublicKey, message: bytes, signature: bytes, prehashed = True) -> bool:
    """Verify a signature using the public key."""
    try:
        public_key.verify(
            signature,
            message,
            padding.PKCS1v15(),
            Prehashed(hashes.SHA256()) if prehashed else hashes.SHA256()
        )
        return True
    except Exception as e:
        print(f"Verification error: {str(e)}")
        return False

def hash_image_sha256(data: bytes) -> bytes:
    """Create SHA256 hash of image data."""
    hasher = hashlib.sha256()
    hasher.update(data)
    return hasher.digest()