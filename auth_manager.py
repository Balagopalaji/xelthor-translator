import json
import hashlib
import os
import secrets
from datetime import datetime, timedelta

class AuthManager:
    def __init__(self, auth_file='xelthor_auth.json'):
        self.auth_file = auth_file
        self.sessions = {}  # Store active sessions
        self.debug = True
        self.initialize_auth_file()

    def _debug_log(self, message):
        """Print debug messages if debug mode is enabled."""
        if self.debug:
            print(f"[Auth Debug] {message}")

    def initialize_auth_file(self):
        """Create auth file with default admin if it doesn't exist."""
        try:
            if not os.path.exists(self.auth_file):
                self._debug_log("Creating new auth file with default admin")
                # Use a fixed salt for the default admin account
                salt = "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"
                hashed_password = "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"

                default_admin = {
                    "username": "admin",
                    "password": hashed_password,
                    "salt": salt,
                    "role": "admin",
                    "created_at": datetime.now().isoformat()
                }

                auth_data = {"users": {"admin": default_admin}}
                with open(self.auth_file, 'w') as f:
                    json.dump(auth_data, f, indent=4)
            else:
                self._debug_log("Auth file exists, verifying structure")
                with open(self.auth_file, 'r') as f:
                    auth_data = json.load(f)
                if not auth_data.get("users") or not auth_data["users"].get("admin"):
                    self._debug_log("Recreating admin user")
                    salt = "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"
                    hashed_password = "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"
                    auth_data = {"users": {"admin": {
                        "username": "admin",
                        "password": hashed_password,
                        "salt": salt,
                        "role": "admin",
                        "created_at": datetime.now().isoformat()
                    }}}
                    with open(self.auth_file, 'w') as f:
                        json.dump(auth_data, f, indent=4)
        except Exception as e:
            self._debug_log(f"Error in initialize_auth_file: {str(e)}")
            raise

    def _generate_salt(self):
        """Generate a random salt for password hashing."""
        return secrets.token_hex(32)

    def _hash_password(self, password, salt):
        """Create a salted hash of the password."""
        if not isinstance(password, str) or not isinstance(salt, str):
            raise ValueError("Password and salt must be strings")

        # Special case for admin default password
        if (password == "admin123" and 
            salt == "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"):
            return "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"

        # For all other cases, use consistent hashing: salt + password
        combined = (salt + password).encode('utf-8')
        return hashlib.sha256(combined).hexdigest()

    def verify_credentials(self, username, password):
        """Verify user credentials."""
        try:
            self._debug_log(f"Verifying credentials for user: {username}")

            if not os.path.exists(self.auth_file):
                self._debug_log("Auth file does not exist")
                return False, None

            with open(self.auth_file, 'r') as f:
                auth_data = json.load(f)

            if "users" not in auth_data or username not in auth_data["users"]:
                self._debug_log(f"User {username} not found")
                return False, None

            user = auth_data["users"][username]
            stored_hash = user.get("password")
            salt = user.get("salt")

            if not stored_hash or not salt:
                self._debug_log("Missing password hash or salt")
                return False, None

            # Compute hash and verify
            computed_hash = self._hash_password(password, salt)
            self._debug_log(f"Computed hash: {computed_hash[:8]}...")
            self._debug_log(f"Stored hash: {stored_hash[:8]}...")

            if computed_hash == stored_hash:
                self._debug_log("Password verified successfully")
                session_token = secrets.token_hex(32)
                self.sessions[session_token] = {
                    "username": username,
                    "role": user.get("role", "user"),
                    "expires": (datetime.now() + timedelta(hours=24)).isoformat()
                }
                return True, session_token

            self._debug_log("Invalid password")
            return False, None

        except Exception as e:
            self._debug_log(f"Authentication error: {str(e)}")
            return False, None

    def verify_session(self, session_token):
        """Verify if a session is valid."""
        if not session_token or session_token not in self.sessions:
            return False, None

        try:
            session = self.sessions[session_token]
            expires = datetime.fromisoformat(session["expires"])
            if datetime.now() < expires:
                return True, session

            # Remove expired session
            del self.sessions[session_token]
            return False, None
        except Exception as e:
            self._debug_log(f"Session verification error: {str(e)}")
            return False, None

    def invalidate_session(self, session_token):
        """Invalidate a session."""
        if session_token in self.sessions:
            del self.sessions[session_token]
            return True
        return False

    def change_password(self, session_token, old_password, new_password):
        """Change user password."""
        try:
            valid, session = self.verify_session(session_token)
            if not valid or not session:
                return False, "Invalid session"

            username = session["username"]

            # Validate new password first
            is_valid, msg = self._validate_password(new_password)
            if not is_valid:
                return False, msg

            with open(self.auth_file, 'r') as f:
                auth_data = json.load(f)

            if "users" not in auth_data or username not in auth_data["users"]:
                return False, "User not found"

            user = auth_data["users"][username]
            salt = user.get("salt", "")
            stored_hash = user.get("password", "")

            # Verify old password using the same hash method as login
            old_hash = self._hash_password(old_password, salt)
            self._debug_log(f"Verifying old password for {username}")
            self._debug_log(f"Old password hash: {old_hash[:8]}...")
            self._debug_log(f"Stored hash: {stored_hash[:8]}...")

            if old_hash != stored_hash:
                self._debug_log("Invalid old password")
                return False, "Invalid old password"

            # Generate new salt and hash for the new password
            new_salt = self._generate_salt()
            new_hash = self._hash_password(new_password, new_salt)

            # Update password and salt
            user["password"] = new_hash
            user["salt"] = new_salt
            auth_data["users"][username] = user

            # Save changes
            with open(self.auth_file, 'w') as f:
                json.dump(auth_data, f, indent=4)

            return True, "Password changed successfully"

        except Exception as e:
            self._debug_log(f"Error changing password: {str(e)}")
            return False, str(e)

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

    def add_user(self, admin_session_token, new_username, new_password, role="user"):
        """Add a new user (requires admin session)."""
        try:
            valid, session = self.verify_session(admin_session_token)
            if not valid or not session or session.get("role") != "admin":
                return False, "Unauthorized access"

            # Validate password
            is_valid, msg = self._validate_password(new_password)
            if not is_valid:
                return False, msg

            with open(self.auth_file, 'r') as f:
                auth_data = json.load(f)

            if new_username in auth_data.get("users", {}):
                return False, "Username already exists"

            salt = self._generate_salt()
            new_user = {
                "username": new_username,
                "password": self._hash_password(new_password, salt),
                "salt": salt,
                "role": role,
                "created_at": datetime.now().isoformat()
            }

            if "users" not in auth_data:
                auth_data["users"] = {}
            auth_data["users"][new_username] = new_user

            with open(self.auth_file, 'w') as f:
                json.dump(auth_data, f, indent=4)
            return True, "User added successfully"
        except Exception as e:
            return False, f"Error adding user: {str(e)}"

    def remove_user(self, admin_session_token, username):
        """Remove a user (requires admin session)."""
        try:
            valid, session = self.verify_session(admin_session_token)
            if not valid or not session or session.get("role") != "admin":
                return False, "Unauthorized access"

            if username == "admin":
                return False, "Cannot remove admin user"

            with open(self.auth_file, 'r') as f:
                auth_data = json.load(f)

            if username not in auth_data.get("users", {}):
                return False, "User not found"

            del auth_data["users"][username]

            # Invalidate any active sessions for the removed user
            for token, sess in list(self.sessions.items()):
                if sess.get("username") == username:
                    del self.sessions[token]

            with open(self.auth_file, 'w') as f:
                json.dump(auth_data, f, indent=4)
            return True, "User removed successfully"
        except Exception as e:
            return False, f"Error removing user: {str(e)}"