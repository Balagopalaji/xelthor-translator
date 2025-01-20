"""Authentication manager for the Xel'thor translator."""
import json
import hashlib
import os
from datetime import datetime

class AuthManager:
    def __init__(self, auth_file='xelthor_auth.json'):
        self.auth_file = auth_file
        self.initialize_auth_file()
    
    def initialize_auth_file(self):
        """Create auth file with default admin if it doesn't exist."""
        if not os.path.exists(self.auth_file):
            default_admin = {
                "admin": self.hash_password("admin123")  # Default admin credentials
            }
            with open(self.auth_file, 'w') as f:
                json.dump({"users": default_admin}, f, indent=4)
    
    def hash_password(self, password):
        """Create a hash of the password."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_credentials(self, username, password):
        """Verify user credentials."""
        try:
            with open(self.auth_file, 'r') as f:
                auth_data = json.load(f)
            
            if username in auth_data["users"]:
                return auth_data["users"][username] == self.hash_password(password)
        except Exception as e:
            print(f"Authentication error: {str(e)}")
        return False
    
    def add_user(self, admin_username, admin_password, new_username, new_password):
        """Add a new user (requires admin credentials)."""
        if self.verify_credentials(admin_username, admin_password):
            try:
                with open(self.auth_file, 'r') as f:
                    auth_data = json.load(f)
                
                auth_data["users"][new_username] = self.hash_password(new_password)
                
                with open(self.auth_file, 'w') as f:
                    json.dump(auth_data, f, indent=4)
                return True
            except Exception as e:
                print(f"Error adding user: {str(e)}")
        return False
