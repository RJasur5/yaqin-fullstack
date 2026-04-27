from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
password = "789789"
hash_val = "$pbkdf2-sha256$29000$tdb6n9Na6z0H4JyT0hrj/A$iwMzF0XTFINJYXqVtATk8wbVfY/llzhEemQSOnY9zRk"

if pwd_context.verify(password, hash_val):
    print("Password matches")
else:
    print("Password does NOT match")
