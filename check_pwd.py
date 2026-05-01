from passlib.context import CryptContext
pwd_context = CryptContext(schemes=['pbkdf2_sha256'], deprecated='auto')
print(pwd_context.verify('123456', '$pbkdf2-sha256$29000$pPSek7KWUkpJKUUo5RwD4A$4wsSEQl61CAAgOD9G7aDLa8zpLhzDiigAZjaXxYOAdo'))
