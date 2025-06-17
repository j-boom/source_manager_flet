"""Directory service for handling directory operations and navigation"""

import os
from typing import List, Dict, Any, Optional
import re


class DirectoryService:
    """Handles all directory-related operations for the project manager"""
    
    def __init__(self):
        self.directory_source_citations_path = self._find_directory_source_citations()
        self.primary_folders = self._get_primary_folders()
    
    def _find_directory_source_citations(self) -> Optional[str]:
        """Find the Directory_Source_Citations file/folder"""
        # Look for the file in current directory and common locations
        possible_paths = [
            "./Directory_Source_Citations",
            "../Directory_Source_Citations", 
            "../../Directory_Source_Citations",
            "./data/Directory_Source_Citations",
            "./sources/Directory_Source_Citations"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return os.path.abspath(path)
        
        return None
    
    def _get_primary_folders(self) -> List[str]:
        """Get list of primary folders in Directory_Source_Citations"""
        if not self.directory_source_citations_path or not os.path.exists(self.directory_source_citations_path):
            return []
        
        folders = []
        try:
            for item in os.listdir(self.directory_source_citations_path):
                item_path = os.path.join(self.directory_source_citations_path, item)
                if os.path.isdir(item_path):
                    folders.append(item)
        except PermissionError:
            pass
        
        return sorted(folders)
    
    def get_four_digit_folders(self, primary_folder: str) -> List[Dict[str, str]]:
        """Get all four-digit folders in the specified primary folder"""
        if not self.directory_source_citations_path:
            return []
        
        primary_path = os.path.join(self.directory_source_citations_path, primary_folder)
        if not os.path.exists(primary_path):
            return []
        
        folders = []
        try:
            for item in os.listdir(primary_path):
                item_path = os.path.join(primary_path, item)
                if os.path.isdir(item_path) and len(item) == 4 and item.isdigit():
                    folders.append({
                        'name': item,
                        'path': item_path,
                        'is_directory': True
                    })
        except PermissionError:
            pass
        
        return sorted(folders, key=lambda x: x['name'])
    
    def get_folder_contents(self, folder_path: str) -> List[Dict[str, Any]]:
        """Get contents of a specific folder"""
        if not os.path.exists(folder_path):
            return []
        
        contents = []
        try:
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)
                contents.append({
                    'name': item,
                    'path': item_path,
                    'is_directory': os.path.isdir(item_path)
                })
        except PermissionError:
            pass
        
        # Sort directories first, then files
        contents.sort(key=lambda x: (not x['is_directory'], x['name'].lower()))
        return contents
    
    def search_four_digit_folders(self, primary_folder: str, search_term: str) -> tuple:
        """Search for folders matching the search term"""
        if not self.directory_source_citations_path:
            return [], None, None
        
        primary_path = os.path.join(self.directory_source_citations_path, primary_folder)
        if not os.path.exists(primary_path):
            return [], None, None
        
        matching_folders = []
        exact_ten_digit_match = None
        four_digit_folder_for_ten_digit = None
        
        # Check if search term is a 10-digit number
        if len(search_term) == 10 and search_term.isdigit():
            four_digit_prefix = search_term[:4]
            four_digit_path = os.path.join(primary_path, four_digit_prefix)
            
            if os.path.exists(four_digit_path):
                # Look for the exact 10-digit folder
                contents = self.get_folder_contents(four_digit_path)
                for item in contents:
                    if item['is_directory'] and item['name'].startswith(search_term):
                        exact_ten_digit_match = item
                        break
                
                if not exact_ten_digit_match:
                    # 10-digit folder doesn't exist, but 4-digit does
                    four_digit_folder_for_ten_digit = {
                        'name': four_digit_prefix,
                        'path': four_digit_path,
                        'is_directory': True
                    }
        
        # Also search for 4-digit folders
        if len(search_term) == 4 and search_term.isdigit():
            four_digit_path = os.path.join(primary_path, search_term)
            if os.path.exists(four_digit_path):
                matching_folders.append({
                    'name': search_term,
                    'path': four_digit_path,
                    'is_directory': True
                })
        
        return matching_folders, exact_ten_digit_match, four_digit_folder_for_ten_digit
    
    def create_ten_digit_folder(self, parent_path: str, ten_digit_number: str, description: str = "") -> bool:
        """Create a new ten-digit folder"""
        full_folder_name = ten_digit_number
        if description:
            full_folder_name += f" {description}"
        
        new_folder_path = os.path.join(parent_path, full_folder_name)
        
        try:
            os.makedirs(new_folder_path, exist_ok=True)
            return True
        except OSError:
            return False
    
    def get_folder_path_from_breadcrumb(self, breadcrumb: List[str]) -> str:
        """Get the full folder path from breadcrumb"""
        if breadcrumb and self.directory_source_citations_path:
            path_parts = [self.directory_source_citations_path] + breadcrumb
            return os.path.join(*path_parts)
        return ""
    
    def is_four_digit_folder(self, breadcrumb: List[str]) -> bool:
        """Check if current location is a four-digit folder"""
        return (len(breadcrumb) == 2 and 
                len(breadcrumb[1]) == 4 and 
                breadcrumb[1].isdigit())
    
    def is_ten_digit_folder(self, breadcrumb: List[str]) -> bool:
        """Check if current location is a ten-digit folder"""
        if len(breadcrumb) >= 2:
            folder_name = breadcrumb[-1]
            # Check if folder name starts with 10 digits
            return bool(re.match(r'^\d{10}', folder_name))
        return False
    
    def extract_ten_digit_number(self, folder_name: str) -> Optional[str]:
        """Extract ten-digit number from folder name"""
        match = re.match(r'^(\d{10})', folder_name)
        return match.group(1) if match else None
