import json
import os
import getpass
from pathlib import Path
from typing import Dict, Any, Optional
import flet as ft


class UserConfigManager:
    """Manages user-specific configuration settings"""
    
    def __init__(self):
        self.username = getpass.getuser()
        self.config_dir = Path("users") / self.username
        self.config_file = self.config_dir / "config.json"
        
        # Default configuration
        self.default_config = {
            "window": {
                "width": 1600,
                "height": 900,
                "x": None,  # Will center if None
                "y": None,  # Will center if None
                "maximized": False
            },
            "theme": {
                "mode": "light",  # "light" or "dark"
                "color": "blue"   # "red", "blue", "orange", "green", "yellow", "purple", "indigo"
            },
            "last_page": "home",
            "recent_sites": []  # List of up to 10 recent sites
        }
        
        # Ensure user directory exists
        self._ensure_user_directory()
        
        # Load or create config
        self.config = self._load_config()
    
    def _ensure_user_directory(self):
        """Create user directory if it doesn't exist"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        print(f"User config directory: {self.config_dir.absolute()}")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or return defaults"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                
                # Merge with defaults to ensure all keys exist
                config = self.default_config.copy()
                self._deep_update(config, loaded_config)
                
                print(f"Loaded config for user: {self.username}")
                return config
                
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Error loading config: {e}. Using defaults.")
                return self.default_config.copy()
        else:
            print(f"No config found for user: {self.username}. Creating new config.")
            return self.default_config.copy()
    
    def _deep_update(self, base_dict: Dict[str, Any], update_dict: Dict[str, Any]):
        """Recursively update nested dictionaries"""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            print(f"Config saved for user: {self.username}")
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get_window_config(self) -> Dict[str, Any]:
        """Get window configuration"""
        return self.config["window"].copy()
    
    def save_window_config(self, width: int, height: int, x: Optional[int] = None, y: Optional[int] = None, maximized: bool = False):
        """Save window configuration"""
        self.config["window"].update({
            "width": width,
            "height": height,
            "x": x,
            "y": y,
            "maximized": maximized
        })
        self.save_config()
    
    def get_theme_mode(self) -> str:
        """Get theme mode (light/dark)"""
        return self.config["theme"]["mode"]
    
    def save_theme_mode(self, mode: str):
        """Save theme mode"""
        if mode in ["light", "dark"]:
            self.config["theme"]["mode"] = mode
            self.save_config()
    
    def get_theme_color(self) -> str:
        """Get theme color"""
        return self.config["theme"]["color"]
    
    def save_theme_color(self, color: str):
        """Save theme color"""
        valid_colors = ["red", "blue", "orange", "green", "yellow", "purple", "indigo"]
        if color in valid_colors:
            self.config["theme"]["color"] = color
            self.save_config()
    
    def get_last_page(self) -> str:
        """Get last opened page"""
        return self.config.get("last_page", "home")
    
    def save_last_page(self, page: str):
        """Save last opened page"""
        self.config["last_page"] = page
        self.save_config()
    
    def get_username(self) -> str:
        """Get current username"""
        return self.username
    
    def get_recent_sites(self) -> list:
        """Get list of recent sites"""
        return self.config.get("recent_sites", [])
    
    def add_recent_site(self, display_name: str, path: str):
        """Add a site to recent sites list (max 10 items)"""
        recent_sites = self.get_recent_sites()
        
        # Create new site entry
        new_site = {
            "display_name": display_name,
            "path": path
        }
        
        # Remove if already exists (to move to top)
        recent_sites = [site for site in recent_sites if site["path"] != path]
        
        # Add to beginning of list
        recent_sites.insert(0, new_site)
        
        # Keep only the 10 most recent
        recent_sites = recent_sites[:10]
        
        # Update config
        self.config["recent_sites"] = recent_sites
        self.save_config()
    
    def remove_recent_site(self, path: str):
        """Remove a site from recent sites list"""
        recent_sites = self.get_recent_sites()
        recent_sites = [site for site in recent_sites if site["path"] != path]
        self.config["recent_sites"] = recent_sites
        self.save_config()
    
    def update_recent_site_display_name(self, path: str, new_display_name: str):
        """Update the display name for a specific recent site"""
        recent_sites = self.get_recent_sites()
        for site in recent_sites:
            if site["path"] == path:
                site["display_name"] = new_display_name
                break
        self.config["recent_sites"] = recent_sites
        self.save_config()

    def clear_recent_sites(self):
        """Clear all recent sites"""
        self.config["recent_sites"] = []
        self.save_config()
