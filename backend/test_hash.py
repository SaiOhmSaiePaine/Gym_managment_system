import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

test_password = "123456789"
hashed = hash_password(test_password)
print(f"Password: {test_password}")
print(f"Hash: {hashed}") 