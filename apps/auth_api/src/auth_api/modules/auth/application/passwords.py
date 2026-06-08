from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher

from auth_api.infrastructure.settings import settings


password_hash = PasswordHash((BcryptHasher(rounds=settings.BCRYPT_ROUNDS),))


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, password_hash_value: str) -> bool:
    return password_hash.verify(password, password_hash_value)
