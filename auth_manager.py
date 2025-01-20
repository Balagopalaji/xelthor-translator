"""Authentication manager for the Xel'thor translator."""
import json
import hashlib
import os
import secrets
from datetime import datetime, timedelta

class AuthManager:
    def __init__(self, auth_file='xelthor_auth.json'):
        self.auth_file = auth_file
        self.sessions = {}  # Store active sessions
        self.initialize_auth_file()

    def initialize_auth_file(self):
        """Create auth file with default admin if it doesn't exist."""
        if not os.path.exists(self.auth_file):
            default_admin = {
                "username": "admin",
                "password": self._hash_password("admin123", self._generate_salt()),
                "salt": self._generate_salt(),
                "role": "admin",
                "created_at": datetime.now().isoformat()
            }
            with open(self.auth_file, 'w') as f:
                json.dump({"users": {"admin": default_admin}}, f, indent=4)

    def _generate_salt(self):
        """Generate a random salt for password hashing."""
        return secrets.token_hex(16)

    def _hash_password(self, password, salt):
        """Create a salted hash of the password."""
        return hashlib.sha256((password + salt).encode()).hexdigest()

    def _validate_password(self, password):
        """Validate password strength."""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one number"
        return True, "Password is valid"

    def verify_credentials(self, username, password):
        """Verify user credentials."""
        try:
            with open(self.auth_file, 'r') as f:
                auth_data = json.load(f)

            if username in auth_data["users"]:
                user = auth_data["users"][username]
                hashed = self._hash_password(password, user["salt"])
                if hashed == user["password"]:
                    # Create session
                    session_token = secrets.token_hex(32)
                    self.sessions[session_token] = {
                        "username": username,
                        "role": user["role"],
                        "expires": (datetime.now() + timedelta(hours=24)).isoformat()
                    }
                    return True, session_token
            return False, None
        except Exception as e:
            print(f"Authentication error: {str(e)}")
            return False, None

    def verify_session(self, session_token):
        """Verify if a session is valid."""
        if session_token in self.sessions:
            session = self.sessions[session_token]
            expires = datetime.fromisoformat(session["expires"])
            if datetime.now() < expires:
                return True, session
        return False, None

    def invalidate_session(self, session_token):
        """Invalidate a session."""
        if session_token in self.sessions:
            del self.sessions[session_token]
            return True
        return False

    def add_user(self, admin_session_token, new_username, new_password, role="user"):
        """Add a new user (requires admin session)."""
        valid, session = self.verify_session(admin_session_token)
        if not valid or session["role"] != "admin":
            return False, "Unauthorized access"

        try:
            # Validate password
            is_valid, msg = self._validate_password(new_password)
            if not is_valid:
                return False, msg

            with open(self.auth_file, 'r') as f:
                auth_data = json.load(f)

            if new_username in auth_data["users"]:
                return False, "Username already exists"

            salt = self._generate_salt()
            new_user = {
                "username": new_username,
                "password": self._hash_password(new_password, salt),
                "salt": salt,
                "role": role,
                "created_at": datetime.now().isoformat()
            }

            auth_data["users"][new_username] = new_user

            with open(self.auth_file, 'w') as f:
                json.dump(auth_data, f, indent=4)
            return True, "User added successfully"
        except Exception as e:
            return False, f"Error adding user: {str(e)}"

    def remove_user(self, admin_session_token, username):
        """Remove a user (requires admin session)."""
        valid, session = self.verify_session(admin_session_token)
        if not valid or session["role"] != "admin":
            return False, "Unauthorized access"

        if username == "admin":
            return False, "Cannot remove admin user"

        try:
            with open(self.auth_file, 'r') as f:
                auth_data = json.load(f)

            if username not in auth_data["users"]:
                return False, "User not found"

            del auth_data["users"][username]

            # Invalidate any active sessions for the removed user
            for token, session in list(self.sessions.items()):
                if session["username"] == username:
                    del self.sessions[token]

            with open(self.auth_file, 'w') as f:
                json.dump(auth_data, f, indent=4)
            return True, "User removed successfully"
        except Exception as e:
            return False, f"Error removing user: {str(e)}"

    def change_password(self, session_token, old_password, new_password):
        """Change user password."""
        valid, session = self.verify_session(session_token)
        if not valid:
            return False, "Invalid session"

        try:
            # Validate new password
            is_valid, msg = self._validate_password(new_password)
            if not is_valid:
                return False, msg

            with open(self.auth_file, 'r') as f:
                auth_data = json.load(f)

            username = session["username"]
            user = auth_data["users"][username]

            # Verify old password
            if self._hash_password(old_password, user["salt"]) != user["password"]:
                return False, "Invalid old password"

            # Update password
            salt = self._generate_salt()
            user["password"] = self._hash_password(new_password, salt)
            user["salt"] = salt

            with open(self.auth_file, 'w') as f:
                json.dump(auth_data, f, indent=4)
            return True, "Password changed successfully"
        except Exception as e:
            return False, f"Error changing password: {str(e)}"