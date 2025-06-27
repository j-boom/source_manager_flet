import json
import os
import sys
import getpass
from pathlib import Path
from typing import Dict, Any, Optional
import flet as ft

# Add project root to path for config imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from config import USER_DATA_DIR, DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT, DEFAULT_THEME


class UserConfigManager:
    """Manages user-specific configuration settings"""
    
    def __init__(self):
        self.username = getpass.getuser()
        self.config_dir = USER_DATA_DIR / "users" / self.username
        self.config_file = self.config_dir / "config.json"
        
        # Default configuration
        self.default_config = {
            "window": {
                "width": DEFAULT_WINDOW_WIDTH,
                "height": DEFAULT_WINDOW_HEIGHT,
                "x": None,  # Will center if None
                "y": None,  # Will center if None
                "maximized": False
            },
            "theme": {
                "mode": DEFAULT_THEME,  # "light" or "dark"
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
        """Get list of recent sites, filtering out any with missing JSON files and syncing display names"""
        import os
        
        recent_sites = self.config.get("recent_sites", [])
        
        # Filter out sites where the JSON file no longer exists and sync display names
        valid_sites = []
        sites_to_remove = []
        sites_updated = False
        
        for site in recent_sites:
            path = site.get("path", "")
            if path and os.path.exists(path):
                # Get the current display name from the JSON file (source of truth)
                json_display_name = self._get_display_name_from_project_json(path)
                current_display_name = site.get("display_name", "")
                
                # If the JSON file has a different display name, update it
                if json_display_name and json_display_name != current_display_name:
                    site["display_name"] = json_display_name
                    sites_updated = True
                    print(f"🔄 Synced display name from JSON: {json_display_name}")
                
                valid_sites.append(site)
            else:
                sites_to_remove.append(site)
                print(f"⚠️  Removing missing project from recent list: {site.get('display_name', 'Unknown')} ({path})")
        
        # If we found missing files or updated display names, save the config
        if sites_to_remove or sites_updated:
            self.config["recent_sites"] = valid_sites
            self.save_config()
            if sites_to_remove:
                print(f"✅ Cleaned up {len(sites_to_remove)} missing project(s) from recent list")
            if sites_updated:
                print(f"✅ Synced display names from project JSON files")
        
        return valid_sites
    
    def add_recent_site(self, display_name: str, path: str):
        """Add a site to recent sites list (max 10 items)"""
        recent_sites = self.get_recent_sites()
        
        # If no display_name provided, try to get it from the project JSON
        if not display_name.strip():
            display_name = self._get_display_name_from_project_json(path) or "Unknown Project"
        
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
    
    def _get_display_name_from_project_json(self, json_path: str) -> str:
        """Get the display name (document_title) from a project JSON file"""
        try:
            import json
            from pathlib import Path
            
            json_file = Path(json_path)
            if json_file.exists():
                with open(json_file, 'r', encoding='utf-8') as f:
                    project_data = json.load(f)
                
                # Try to get document_title, fall back to project_title, then project_id
                display_name = (
                    project_data.get("document_title") or 
                    project_data.get("project_title") or 
                    project_data.get("project_id", "Unknown Project")
                )
                
                return display_name if display_name else "Unknown Project"
            
        except Exception as e:
            print(f"Error reading display name from project JSON: {e}")
        
        return "Unknown Project"
    
    def remove_recent_site(self, path: str):
        """Remove a site from recent sites list"""
        recent_sites = self.get_recent_sites()
        recent_sites = [site for site in recent_sites if site["path"] != path]
        self.config["recent_sites"] = recent_sites
        self.save_config()
    
    def update_recent_site_display_name(self, path: str, new_display_name: str):
        """Update the display name for a specific recent site and sync with project JSON"""
        # First, update the document_title in the project JSON file (source of truth)
        self._sync_display_name_to_project_json(path, new_display_name)
        
        # Then update the recent sites display name to match
        recent_sites = self.get_recent_sites()
        for site in recent_sites:
            if site["path"] == path:
                site["display_name"] = new_display_name
                break
        self.config["recent_sites"] = recent_sites
        self.save_config()
    
    def _sync_display_name_to_project_json(self, json_path: str, display_name: str):
        """Sync the display name to the document_title field in the project JSON file"""
        try:
            import json
            from pathlib import Path
            
            json_file = Path(json_path)
            if json_file.exists():
                # Read the current JSON data
                with open(json_file, 'r', encoding='utf-8') as f:
                    project_data = json.load(f)
                
                # Update the document_title field
                project_data["document_title"] = display_name
                
                # Write back to the file
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(project_data, f, indent=4, ensure_ascii=False)
                
                print(f"✅ Synced display name to project JSON: {display_name}")
            else:
                print(f"⚠️  Project JSON file not found: {json_path}")
                
        except Exception as e:
            print(f"❌ Error syncing display name to project JSON: {e}")

    def clear_recent_sites(self):
        """Clear all recent sites"""
        self.config["recent_sites"] = []
        self.save_config()
