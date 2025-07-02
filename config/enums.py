from enum import Enum

class ProjectType(Enum):
    OTHER = "oth"
    STANDARD = "std"
    GEOTECHNICAL_REPORT = "gsc"
    
    def get_human_readable(self):
        """Return human-readable string for display purposes"""
        mapping = {
            "oth": "Other",
            "std": "Standard",
            "gsc": "Geotechnical Report"
        }
        return mapping.get(self.value, str(self.value))
    
    @classmethod
    def get_dropdown_options(cls):
        """Return list of tuples (value, display_text) for dropdown population"""
        return [(item.value, item.get_human_readable()) for item in cls]
    
    @classmethod
    def from_value(cls, value):
        """Get enum instance from string value"""
        for item in cls:
            if item.value == value:
                return item
        raise ValueError(f"No ProjectType with value: {value}")
    
    class SourceType(Enum):
        JOURNAL = "jnl"
        WEBSITE = "web"
        BOOK = "bk"
        ARTICLE = "art"
        
        def get_human_readable(self):
            """Return human-readable string for display purposes"""
            mapping = {
                "jnl": "Journal",
                "web": "Website", 
                "bk": "Book",
                "art": "Article"
            }
            return mapping.get(self.value, str(self.value))
        
        @classmethod
        def get_dropdown_options(cls):
            """Return list of tuples (value, display_text) for dropdown population"""
            return [(item.value, item.get_human_readable()) for item in cls]
        
        @classmethod
        def from_value(cls, value):
            """Get enum instance from string value"""
            for item in cls:
                if item.value == value:
                    return item
            raise ValueError(f"No SourceType with value: {value}")