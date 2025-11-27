import hashlib
import datetime
import time
from infosec_banking.storage.storage_manager import StorageManager
from infosec_banking.utils.colors import print_processing, print_success, print_error
from infosec_banking.config import USERS_FILE, DEFAULT_BALANCE, RESERVED_USERNAMES

class UserManager:
    """Manages user registration, authentication, and balances"""
    
    def __init__(self):
        self.users = {}
        self.logged_in_user_id = None
        self.load()

    def _hash_password(self, password):
        """Hashes password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, user_id, password):
        """Registers a new user"""
        print_processing("Validating registration...")
        time.sleep(0.2)
        
        if user_id.upper() in RESERVED_USERNAMES:
            print_error(f"Username '{user_id}' is reserved")
            return False, f"User ID '{user_id}' is reserved. Choose another."
        
        if user_id in self.users:
            print_error(f"User ID '{user_id}' already exists")
            return False, "User ID already exists."
        
        print_processing("Hashing password...")
        time.sleep(0.1)
        hashed_password = self._hash_password(password)
        
        self.users[user_id] = {
            "password_hash": hashed_password,
            "balance": DEFAULT_BALANCE,
            "active_session": False,
            "created_at": datetime.datetime.now().isoformat()
        }
        self.save()
        print_success(f"User '{user_id}' registered with balance ${DEFAULT_BALANCE:.2f}")
        StorageManager.log_operation(user_id, "Registration successful")
        return True, f"Welcome! Your initial balance: ${DEFAULT_BALANCE:.2f}"

    def verify_password(self, user_id, password):
        """Verifies password WITHOUT changing session state"""
        user_data = self.users.get(user_id)
        if not user_data:
            return False
        return user_data['password_hash'] == self._hash_password(password)

    def authenticate(self, user_id, password):
        """Authenticates user credentials"""
        print_processing("Authenticating user...")
        time.sleep(0.2)
        
        user_data = self.users.get(user_id)
        
        if not user_data:
            print_error("Invalid credentials")
            StorageManager.log_operation(user_id, "Auth failed (not found)", "FAIL")
            return False, "Invalid User ID or password."

        if user_data['password_hash'] != self._hash_password(password):
            print_error("Invalid credentials")
            StorageManager.log_operation(user_id, "Auth failed (wrong password)", "FAIL")
            return False, "Invalid User ID or password."

        if user_data['active_session'] and self.logged_in_user_id != user_id:
            print_error(f"User already logged in")
            StorageManager.log_operation(user_id, "Concurrent login denied", "FAIL")
            return False, "User already logged in elsewhere."
        
        print_processing("Starting session...")
        time.sleep(0.1)
        user_data['active_session'] = True
        self.logged_in_user_id = user_id
        self.save()
        print_success(f"Welcome, {user_id}!")
        StorageManager.log_operation(user_id, "Login successful")
        return True, f"Welcome, {user_id}. Balance: ${self.get_balance(user_id):.2f}"

    def logout(self, user_id):
        """Logs out a user"""
        print_processing("Ending session...")
        time.sleep(0.1)
        
        if user_id in self.users:
            self.users[user_id]['active_session'] = False
            if self.logged_in_user_id == user_id:
                self.logged_in_user_id = None
            self.save()
            print_success("Logged out successfully")
            StorageManager.log_operation(user_id, "Logout successful")
            return True, "Session ended."
        return False, "User not found."

    def force_logout_all(self):
        """Force logout all sessions (recovery)"""
        print_processing("Forcing logout of all sessions...")
        time.sleep(0.1)
        for user_id in self.users:
            self.users[user_id]['active_session'] = False
        self.logged_in_user_id = None
        self.save()
        print_success("All sessions terminated")

    def get_balance(self, user_id):
        """Gets user balance"""
        return self.users.get(user_id, {}).get('balance', 0.0)
    
    def update_balance(self, user_id, amount):
        """Updates user balance"""
        if user_id not in self.users:
            return False
        
        new_balance = self.users[user_id]['balance'] + amount
        if new_balance < 0:
            return False
        
        self.users[user_id]['balance'] = round(new_balance, 2)
        return True

    def load(self):
        """Loads users from file"""
        data = StorageManager.load_json(USERS_FILE, default_data={})
        self.users = data

    def save(self):
        """Saves users to file"""
        StorageManager.atomic_write_json(USERS_FILE, self.users)
