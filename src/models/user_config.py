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

from config import (
    USER_DATA_DIR, DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT, DEFAULT_THEME,
    UserConfig, WindowConfig, ThemeConfig, RecentSite, ProjectData
)


class UserConfigManager:
    """Manages user-specific configuration settings"""
    
    def __init__(self):
        self.username = getpass.getuser()
        self.config_dir = USER_DATA_DIR / "users"
        self.config_file = self.config_dir / f"{self.username}.json"
        
        # Default configuration using dataclasses
        self.default_config = UserConfig(
            window=WindowConfig(
                width=DEFAULT_WINDOW_WIDTH,
                height=DEFAULT_WINDOW_HEIGHT,
                x=None,
                y=None,
                maximized=False
            ),
            theme=ThemeConfig(
                mode=DEFAULT_THEME,
                color="blue"
            ),
            last_page="home",
            recent_sites=[],
            display_name=None,
            setup_completed=False
        )
        
        # Ensure user directory exists
        self._ensure_user_directory()
        
        # Load or create config
        self.config = self._load_config()
    
    def _ensure_user_directory(self):
        """Create user directory if it doesn't exist"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        print(f"User config directory: {self.config_dir.absolute()}")
    
    def _load_config(self) -> UserConfig:
        """Load configuration from file or return defaults"""
        if self.config_file.exists():
            try:
                # Try to load as dataclass
                config = UserConfig.load_from_json(self.config_file)
                if config:
                    print(f"Loaded config for user: {self.username}")
                    return config
                else:
                    # Fallback to manual loading for migration
                    with open(self.config_file, 'r') as f:
                        loaded_data = json.load(f)
                    config = UserConfig.from_dict(loaded_data)
                    print(f"Migrated config for user: {self.username}")
                    return config
                
            except Exception as e:
                print(f"Error loading config: {e}. Using defaults.")
                return self.default_config
        else:
            print(f"No config found for user: {self.username}. Creating new config.")
            return self.default_config
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            self.config.save_to_json(self.config_file)
            print(f"Config saved for user: {self.username}")
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get_window_config(self) -> Dict[str, Any]:
        """Get window configuration"""
        return self.config.window.to_dict()
    
    def save_window_config(self, width: int, height: int, x: Optional[int] = None, y: Optional[int] = None, maximized: bool = False):
        """Save window configuration"""
        self.config.window.width = width
        self.config.window.height = height
        self.config.window.x = x
        self.config.window.y = y
        self.config.window.maximized = maximized
        self.save_config()
    
    def get_theme_mode(self) -> str:
        """Get theme mode (light/dark)"""
        return self.config.theme.mode
    
    def save_theme_mode(self, mode: str):
        """Save theme mode"""
        if mode in ["light", "dark"]:
            self.config.theme.mode = mode
            self.save_config()
    
    def get_theme_color(self) -> str:
        """Get theme color"""
        return self.config.theme.color
    
    def save_theme_color(self, color: str):
        """Save theme color"""
        valid_colors = ["red", "blue", "orange", "green", "yellow", "purple", "indigo"]
        if color in valid_colors:
            self.config.theme.color = color
            self.save_config()
    
    def get_last_page(self) -> str:
        """Get last opened page"""
        return self.config.last_page
    
    def save_last_page(self, page: str):
        """Save last opened page"""
        self.config.last_page = page
        self.save_config()
    
    def get_username(self) -> str:
        """Get current username"""
        return self.username
    
    def get_display_name(self) -> Optional[str]:
        """Get user's display name"""
        return self.config.display_name
    
    def save_display_name(self, display_name: str):
        """Save user's display name"""
        self.config.display_name = display_name.strip() if display_name else None
        self.save_config()
    
    def is_setup_completed(self) -> bool:
        """Check if initial setup is completed"""
        return self.config.setup_completed
    
    def mark_setup_completed(self):
        """Mark initial setup as completed"""
        self.config.setup_completed = True
        self.save_config()
    
    def needs_setup(self) -> bool:
        """Check if user needs to complete initial setup"""
        return not self.config.setup_completed or not self.config.display_name
    
    def get_greeting(self) -> str:
        """Get personalized greeting for the user"""
        if self.config.display_name:
            return f"Hi, {self.config.display_name}!"
        return f"Hi, {self.username}!"

    def get_recent_sites(self) -> list:
        """Get list of recent sites, filtering out any with missing JSON files and syncing display names"""
        import os
        
        recent_sites = self.config.recent_sites
        
        # Filter out sites where the JSON file no longer exists and sync display names
        valid_sites = []
        sites_to_remove = []
        sites_updated = False
        
        for site in recent_sites:
            path = site.path
            if path and os.path.exists(path):
                # Get the current display name from the JSON file (source of truth)
                json_display_name = self._get_display_name_from_project_json(path)
                current_display_name = site.display_name
                
                # If the JSON file has a different display name, update it
                if json_display_name and json_display_name != current_display_name:
                    site.display_name = json_display_name
                    sites_updated = True
                    print(f"🔄 Synced display name from JSON: {json_display_name}")
                
                valid_sites.append(site)
            else:
                sites_to_remove.append(site)
                print(f"⚠️  Removing missing project from recent list: {site.display_name} ({path})")
        
        # If we found missing files or updated display names, save the config
        if sites_to_remove or sites_updated:
            self.config.recent_sites = valid_sites
            self.save_config()
            if sites_to_remove:
                print(f"✅ Cleaned up {len(sites_to_remove)} missing project(s) from recent list")
            if sites_updated:
                print(f"✅ Synced display names from project JSON files")
        
        return [site.to_dict() for site in valid_sites]
    
    def add_recent_site(self, display_name: str, path: str):
        """Add a site to recent sites list (max 10 items)"""
        current_sites = [site for site in self.config.recent_sites]
        
        # If no display_name provided, try to get it from the project JSON
        if not display_name.strip():
            display_name = self._get_display_name_from_project_json(path) or "Unknown Project"
        
        # Create new site entry
        new_site = RecentSite(display_name=display_name, path=path)
        
        # Remove if already exists (to move to top)
        current_sites = [site for site in current_sites if site.path != path]
        
        # Add to beginning of list
        current_sites.insert(0, new_site)
        
        # Keep only the 10 most recent
        current_sites = current_sites[:10]
        
        # Update config
        self.config.recent_sites = current_sites
        self.save_config()
    
    def _get_display_name_from_project_json(self, json_path: str) -> str:
        """Get the display name (document_title) from a project JSON file"""
        try:
            json_file = Path(json_path)
            if json_file.exists():
                # Try to load as ProjectData dataclass first
                project_data = ProjectData.load_from_json(json_file)
                if project_data:
                    # Try to get document_title, fall back to title, then project_id
                    display_name = (
                        project_data.document_title or 
                        project_data.title or 
                        project_data.project_id or
                        "Unknown Project"
                    )
                    return display_name if display_name else "Unknown Project"
                else:
                    # Fallback to manual JSON parsing for compatibility
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    display_name = (
                        data.get("document_title") or 
                        data.get("title") or
                        data.get("project_title") or 
                        data.get("project_id", "Unknown Project")
                    )
                    return display_name if display_name else "Unknown Project"
            
        except Exception as e:
            print(f"Error reading display name from project JSON: {e}")
        
        return "Unknown Project"
    
    def remove_recent_site(self, path: str):
        """Remove a site from recent sites list"""
        self.config.recent_sites = [site for site in self.config.recent_sites if site.path != path]
        self.save_config()
    
    def update_recent_site_display_name(self, path: str, new_display_name: str):
        """Update the display name for a specific recent site and sync with project JSON"""
        # First, update the document_title in the project JSON file (source of truth)
        self._sync_display_name_to_project_json(path, new_display_name)
        
        # Then update the recent sites display name to match
        for site in self.config.recent_sites:
            if site.path == path:
                site.display_name = new_display_name
                break
        self.save_config()
    
    def _sync_display_name_to_project_json(self, json_path: str, display_name: str):
        """Sync the display name to the document_title field in the project JSON file"""
        try:
            json_file = Path(json_path)
            if json_file.exists():
                # Try to load as ProjectData dataclass first
                project_data = ProjectData.load_from_json(json_file)
                if project_data:
                    # Update the document_title field
                    project_data.document_title = display_name
                    
                    # Save back as dataclass
                    project_data.save_to_json(json_file)
                    print(f"✅ Synced display name to project JSON: {display_name}")
                else:
                    # Fallback to manual JSON handling for compatibility
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Update the document_title field
                    data["document_title"] = display_name
                    
                    # Write back to the file
                    with open(json_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=4, ensure_ascii=False)
                    
                    print(f"✅ Synced display name to project JSON (fallback): {display_name}")
            else:
                print(f"⚠️  Project JSON file not found: {json_path}")
                
        except Exception as e:
            print(f"❌ Error syncing display name to project JSON: {e}")

    def clear_recent_sites(self):
        """Clear all recent sites"""
        self.config.recent_sites = []
        self.save_config()
