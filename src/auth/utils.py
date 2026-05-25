from passlib.context import CryptContext

password_cotext = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def generate_password_hash(password:str) -> str:
    hashed_pw = password_cotext.hash(password)
    return hashed_pw

def verify_password(password: str, hashed_pw:str) -> bool:
    return password_cotext.verify(password, hashed_pw)