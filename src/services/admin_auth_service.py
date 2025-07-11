"""
Admin Authentication Service

Handles admin login, password verification, and role management.
"""
import hashlib
import json
import logging
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime

from ..models.user_config_models import UserRole, UserProfile


class AdminAuthService:
    """Service for handling admin authentication and user role management."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.admin_config_file = data_dir / "admin_config.json"
        self.users_file = data_dir / "users.json"
        self.logger = logging.getLogger(__name__)
        
        # Default admin password hash (password: "admin123" - should be changed!)
        self.default_admin_hash = self._hash_password("admin123")
        
        self._ensure_admin_config()
        self._ensure_users_file()
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _ensure_admin_config(self):
        """Ensure admin config file exists with default admin password."""
        if not self.admin_config_file.exists():
            default_config = {
                "admin_password_hash": self.default_admin_hash,
                "created_date": datetime.now().isoformat(),
                "last_password_change": datetime.now().isoformat()
            }
            
            self.admin_config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.admin_config_file, 'w') as f:
                json.dump(default_config, f, indent=4)
            
            self.logger.info("Created default admin config")
    
    def _ensure_users_file(self):
        """Ensure users file exists."""
        if not self.users_file.exists():
            default_users = {
                "users": [],
                "created_date": datetime.now().isoformat()
            }
            
            self.users_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.users_file, 'w') as f:
                json.dump(default_users, f, indent=4)
            
            self.logger.info("Created default users file")
    
    def authenticate_admin(self, password: str) -> bool:
        """
        Authenticate admin with password.
        
        Args:
            password: The password to verify
            
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            with open(self.admin_config_file, 'r') as f:
                config = json.load(f)
            
            password_hash = self._hash_password(password)
            stored_hash = config.get("admin_password_hash")
            
            if password_hash == stored_hash:
                self.logger.info("Admin authentication successful")
                return True
            else:
                self.logger.warning("Admin authentication failed - incorrect password")
                return False
                
        except Exception as e:
            self.logger.error(f"Error during admin authentication: {e}")
            return False
    
    def change_admin_password(self, current_password: str, new_password: str) -> bool:
        """
        Change the admin password.
        
        Args:
            current_password: Current admin password
            new_password: New password to set
            
        Returns:
            True if password changed successfully, False otherwise
        """
        if not self.authenticate_admin(current_password):
            return False
        
        try:
            with open(self.admin_config_file, 'r') as f:
                config = json.load(f)
            
            config["admin_password_hash"] = self._hash_password(new_password)
            config["last_password_change"] = datetime.now().isoformat()
            
            with open(self.admin_config_file, 'w') as f:
                json.dump(config, f, indent=4)
            
            self.logger.info("Admin password changed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error changing admin password: {e}")
            return False
    
    def get_all_users(self) -> List[Dict]:
        """Get all users from the users file."""
        try:
            with open(self.users_file, 'r') as f:
                data = json.load(f)
            return data.get("users", [])
        except Exception as e:
            self.logger.error(f"Error loading users: {e}")
            return []
    
    def add_user(self, display_name: str, role: UserRole = UserRole.USER) -> bool:
        """
        Add a new user.
        
        Args:
            display_name: User's display name
            role: User's role (default: USER)
            
        Returns:
            True if user added successfully, False otherwise
        """
        try:
            users_data = {"users": self.get_all_users()}
            
            # Check if user already exists
            existing_user = next(
                (user for user in users_data["users"] if user["display_name"] == display_name),
                None
            )
            
            if existing_user:
                self.logger.warning(f"User '{display_name}' already exists")
                return False
            
            new_user = {
                "display_name": display_name,
                "role": role.value,
                "created_date": datetime.now().isoformat(),
                "last_login": None,
                "is_active": True
            }
            
            users_data["users"].append(new_user)
            
            with open(self.users_file, 'w') as f:
                json.dump(users_data, f, indent=4)
            
            self.logger.info(f"Added user '{display_name}' with role '{role.value}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding user: {e}")
            return False
    
    def update_user_role(self, display_name: str, new_role: UserRole) -> bool:
        """
        Update a user's role.
        
        Args:
            display_name: User's display name
            new_role: New role to assign
            
        Returns:
            True if role updated successfully, False otherwise
        """
        try:
            users_data = {"users": self.get_all_users()}
            
            user = next(
                (user for user in users_data["users"] if user["display_name"] == display_name),
                None
            )
            
            if not user:
                self.logger.warning(f"User '{display_name}' not found")
                return False
            
            user["role"] = new_role.value
            user["role_updated"] = datetime.now().isoformat()
            
            with open(self.users_file, 'w') as f:
                json.dump(users_data, f, indent=4)
            
            self.logger.info(f"Updated user '{display_name}' role to '{new_role.value}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating user role: {e}")
            return False
    
    def remove_user(self, display_name: str) -> bool:
        """
        Remove a user.
        
        Args:
            display_name: User's display name
            
        Returns:
            True if user removed successfully, False otherwise
        """
        try:
            users_data = {"users": self.get_all_users()}
            
            original_count = len(users_data["users"])
            users_data["users"] = [
                user for user in users_data["users"] 
                if user["display_name"] != display_name
            ]
            
            if len(users_data["users"]) == original_count:
                self.logger.warning(f"User '{display_name}' not found")
                return False
            
            with open(self.users_file, 'w') as f:
                json.dump(users_data, f, indent=4)
            
            self.logger.info(f"Removed user '{display_name}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Error removing user: {e}")
            return False
    
    def get_user_by_name(self, display_name: str) -> Optional[Dict]:
        """Get a user by display name."""
        users = self.get_all_users()
        return next(
            (user for user in users if user["display_name"] == display_name),
            None
        )
