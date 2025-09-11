"""
Admin Authentication Service

Handles admin login, password verification, and user management.
"""

import hashlib
import json
import logging
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime

from ..models.user_config_models import UserRole, UserConfig, WindowConfig, ThemeConfig
from config.app_config import USER_DATA_DIR


class AdminAuthService:
    """Service for handling admin authentication and user role management."""

    def __init__(self):
        """Initializes the AdminAuthService, setting up paths and ensuring config files exist."""
        self.data_dir = USER_DATA_DIR
        self.admin_config_file = USER_DATA_DIR / "admin_config.json"
        self.logger = logging.getLogger(__name__)

        # Default admin password hash (password: "admin123" - should be changed!)
        self.default_admin_hash = self._hash_password("admin123")

        self._ensure_admin_config()

    def _hash_password(self, password: str) -> str:
        """
        Hashes a password using a simple SHA-256 algorithm.

        Note:
            This is a basic implementation and is not cryptographically secure against
            modern attacks. See documentation for security hardening recommendations.

        Args:
            password: The plaintext password string.

        Returns:
            The hexadecimal representation of the SHA-256 hash.
        """
        return hashlib.sha256(password.encode()).hexdigest()

    def _ensure_admin_config(self):
        """Ensure admin config file exists with default admin password."""
        if not self.admin_config_file.exists():
            default_config = {
                "admin_password_hash": self.default_admin_hash,
                "created_date": datetime.now().isoformat(),
                "last_password_change": datetime.now().isoformat(),
            }

            self.admin_config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.admin_config_file, "w") as f:
                json.dump(default_config, f, indent=4)

            self.logger.info("Created default admin config")

    def authenticate_admin(self, password: str) -> bool:
        """
        Authenticates the admin by comparing the hash of the provided password
        with the stored hash.

        Args:
            password: The password to verify.

        Returns:
            True if authentication is successful, False otherwise.
        """
        try:
            with open(self.admin_config_file, "r") as f:
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
        Changes the admin password after verifying the current password.

        Args:
            current_password: The user's current admin password for verification.
            new_password: The new password to set.

        Returns:
            True if the password was changed successfully, False otherwise.
        """
        if not self.authenticate_admin(current_password):
            return False

        try:
            with open(self.admin_config_file, "r") as f:
                config = json.load(f)

            config["admin_password_hash"] = self._hash_password(new_password)
            config["last_password_change"] = datetime.now().isoformat()

            with open(self.admin_config_file, "w") as f:
                json.dump(config, f, indent=4)

            self.logger.info("Admin password changed successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error changing admin password: {e}")
            return False

    def get_all_users(self) -> List[Dict[str, Any]]:
        """
        Scans the user data directory for all user configuration files (`.json`)
        and returns a list of dictionaries representing each user.

        It intelligently determines the username from the filename and falls back
        to the username if a `display_name` is not set within the file.

        Returns:
            A list of dictionaries, where each dictionary is a user's profile data.
        """
        users = []
        for user_file in self.data_dir.glob("*.json"):
            # Ignore non-user config files
            if user_file.name in ["admin_config.json"]:
                continue

            try:
                with open(user_file, "r", encoding="utf-8") as f:
                    user_data = json.load(f)
                # The username is the filename without the extension
                username = user_file.stem
                # The display name is inside the file, but fall back to username
                display_name = user_data.get("display_name") or username

                # Basic validation to see if it's a user config
                if "role" in user_data:
                    user_data["username"] = username
                    user_data["display_name"] = display_name
                    users.append(user_data)
            except (json.JSONDecodeError, IOError) as e:
                self.logger.error(
                    f"Could not read or parse user file {user_file.name}: {e}"
                )
        return users

    def add_user(
        self, display_name: str, role: UserRole = UserRole.USER, is_active: bool = True
    ) -> bool:
        """
        Adds a new user by creating a default user configuration file.

        The username is derived from the display name (lowercased, spaces replaced
        with underscores).

        Args:
            display_name: The user's desired display name.
            role: The user's role, defaults to UserRole.USER.
            is_active: Whether the user account should be active, defaults to True.

        Returns:
            True if the user was added successfully, False if a user with that
            name already exists.
        """
        username = display_name.strip().lower().replace(" ", "_")
        user_config_path = self.data_dir / f"{username}.json"
        if user_config_path.exists():
            self.logger.warning(f"User '{display_name}' already exists.")
            return False

        try:
            # Create a default UserConfig for the new user
            from config.app_config import (
                DEFAULT_WINDOW_WIDTH,
                DEFAULT_WINDOW_HEIGHT,
                DEFAULT_THEME,
            )

            new_user_config = UserConfig(
                display_name=display_name,
                role=role,
                is_active=is_active,
                window=WindowConfig(
                    width=DEFAULT_WINDOW_WIDTH, height=DEFAULT_WINDOW_HEIGHT
                ),
                theme=ThemeConfig(mode=DEFAULT_THEME, color="blue"),
            )

            new_user_config.save_to_json(user_config_path)

            self.logger.info(f"Added user '{display_name}' with role '{role.value}'")
            return True

        except Exception as e:
            self.logger.error(f"Error adding user: {e}", exc_info=True)
            return False

    def update_user(self, original_name: str, updated_data: Dict[str, Any]) -> bool:
        """
        Updates an existing user's profile information.

        This can handle a name change, which involves renaming the user's
        configuration file.

        Args:
            original_name: The original username (filename stem) of the user to update.
            updated_data: A dictionary containing the new 'display_name', 'role',
                          and 'is_active' status.

        Returns:
            True if the update was successful, False otherwise.
        """
        # The user is identified by their username (original filename stem)
        original_path = self.data_dir / f"{original_name}.json"
        if not original_path.exists():
            self.logger.warning(
                f"User config for '{original_name}' not found for update."
            )
            return False

        new_name = updated_data.get("display_name")
        new_username = new_name.strip().lower().replace(" ", "_")
        new_path = self.data_dir / f"{new_username}.json"

        # If name is being changed, check for conflicts
        if new_username != original_name and new_path.exists():
            self.logger.error(
                f"Cannot rename user. A user with name '{new_name}' already exists."
            )
            return False

        try:
            user_config = UserConfig.load_from_json(original_path)
            if not user_config:
                self.logger.error(f"Failed to load user config for '{original_name}'.")
                return False

            # Update the user's data
            user_config.display_name = new_name
            user_config.role = UserRole(updated_data["role"])
            user_config.is_active = updated_data["is_active"]

            user_config.save_to_json(new_path)

            # If name changed, remove old file
            if new_username != original_name:
                original_path.unlink()

            return True
        except Exception as e:
            self.logger.error(
                f"Error updating user '{original_name}': {e}", exc_info=True
            )
            return False

    def remove_user(self, display_name: str) -> bool:
        """
        Removes a user by deleting their configuration file.

        Args:
            display_name: The username (filename stem) of the user to remove.

        Returns:
            True if the user was removed successfully, False otherwise.
        """
        # The user is identified by their username (filename stem)
        user_config_path = self.data_dir / f"{display_name}.json"
        if not user_config_path.exists():
            self.logger.warning(
                f"User config for '{display_name}' not found to remove."
            )
            return False

        try:
            user_config_path.unlink()
            self.logger.info(
                f"Removed user '{display_name}' by deleting their config file."
            )
            return True
        except OSError as e:
            self.logger.error(f"Error removing user file for '{display_name}': {e}")
            return False

    def get_user_by_name(self, display_name: str) -> Optional[Dict]:
        """
        Retrieves a single user's data by their display name.

        Args:
            display_name: The display name to search for.

        Returns:
            A dictionary of the user's data if found, otherwise None.
        """
        users = self.get_all_users()
        return next(
            (user for user in users if user["display_name"] == display_name), None
        )
