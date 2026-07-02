import bcrypt

def hash_password(password: str) -> str:
    """
    Securely hashes a password using bcrypt with a salt.
    """
    if not password:
        raise ValueError("Password cannot be empty")
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def check_password(password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against its bcrypt hash.
    """
    if not password or not hashed_password:
        return False
    try:
        # Check if the password matches the hash
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        # Return False if checkpw fails due to invalid hash format
        return False

def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Checks if a password meets minimum complexity guidelines:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter."
    if not any(char.islower() for char in password):
        return False, "Password must contain at least one lowercase letter."
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one number."
    
    special_characters = "!@#$%^&*()-_=+[]{}|;:',.<>?/`~\"\\"
    if not any(char in special_characters for char in password):
        return False, "Password must contain at least one special character (e.g., @, #, $, !, etc.)."
        
    return True, "Password is strong."

