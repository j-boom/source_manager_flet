"""
PowerPoint Service for the Source Manager Flet application.
Handles loading and extracting data from PowerPoint presentations.
"""

import os
from pptx import Presentation
from typing import List, Tuple, Optional


class PowerPointManager:
    """
    Service for handling PowerPoint operations in the Flet application.
    """
    
    def __init__(self):
        """Initialize the PowerPoint service."""
        self.powerpoint_file = None
        self.powerpoint_presentation = None
    
    def set_powerpoint_file(self, file_path: str):
        """
        Set the PowerPoint file path and load the presentation.
        
        Args:
            file_path: Path to the .pptx file
        """
        self.powerpoint_file = file_path

    def load_presentation(self, file_path: str) -> Optional[Presentation]:
        """
        Load a PowerPoint presentation from the given file path.
        
        Args:
            file_path: Path to the .pptx file
            
        Returns:
            Presentation object if successful, None if failed
        """
        if not self.is_valid_powerpoint_file(file_path):
            return None
            
        try:
            return Presentation(file_path)
        except Exception as e:
            print(f"Error loading PowerPoint file {file_path}: {e}")
            return None
    
    def get_slide_data(self, presentation: Presentation) -> List[Tuple[str, str]]:
        """
        Extract slide data from a presentation.
        
        Args:
            presentation: The loaded Presentation object
            
        Returns:
            List of tuples containing (slide_id, slide_title)
        """
        if not presentation:
            return []
        
        slide_data = []
        for i, slide in enumerate(presentation.slides):
            slide_id = str(slide.slide_id)
            slide_title = self._extract_slide_title(slide, i)
            slide_data.append((slide_id, slide_title))
            
        return slide_data
    
    def _extract_slide_title(self, slide, slide_index: int) -> str:
        """
        Extract the title from a slide using multiple strategies.
        
        Args:
            slide: The slide object
            slide_index: Index of the slide (0-based)
            
        Returns:
            The slide title or a default title
        """
        # Strategy 1: Check if slide has a title shape
        if hasattr(slide, 'shapes') and hasattr(slide.shapes, 'title') and slide.shapes.title:
            if hasattr(slide.shapes.title, 'text') and slide.shapes.title.text.strip():
                return slide.shapes.title.text.strip()
        
        # Strategy 2: Look for text at the top of the slide (title position)
        title_text = self._find_title_by_position(slide)
        if title_text:
            return title_text
        
        # Strategy 3: Find the largest text box
        title_text = self._find_title_by_size(slide)
        if title_text:
            return title_text
        
        # Fallback: Use default title
        return f"Slide {slide_index + 1}"
    
    def _find_title_by_position(self, slide) -> Optional[str]:
        """
        Find title by looking for text shapes in the top portion of the slide.
        """
        try:
            # Look for text shapes in the top 25% of the slide
            for shape in slide.shapes:
                if (hasattr(shape, 'has_text_frame') and shape.has_text_frame and 
                    hasattr(shape, 'top') and hasattr(shape, 'text')):
                    # Check if shape is in the top portion (top < 25% of slide height)
                    if shape.top < 914400 * 2:  # Roughly top 2 inches
                        text = shape.text.strip()
                        if text and len(text) < 100:  # Reasonable title length
                            return text
        except Exception:
            pass
        return None
    
    def _find_title_by_size(self, slide) -> Optional[str]:
        """
        Find title by looking for the largest text box.
        """
        try:
            largest_text = ""
            largest_area = 0
            
            for shape in slide.shapes:
                if (hasattr(shape, 'has_text_frame') and shape.has_text_frame and 
                    hasattr(shape, 'width') and hasattr(shape, 'height') and
                    hasattr(shape, 'text')):
                    area = shape.width * shape.height
                    text = shape.text.strip()
                    if area > largest_area and text and len(text) < 100:
                        largest_area = area
                        largest_text = text
            
            return largest_text if largest_text else None
        except Exception:
            pass
        return None
    
    def is_valid_powerpoint_file(self, file_path: str) -> bool:
        """
        Check if the given file path is a valid PowerPoint file.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if valid, False otherwise
        """
        if not file_path:
            return False
            
        if not os.path.isfile(file_path):
            return False
            
        if not file_path.lower().endswith('.pptx'):
            return False
            
        if not os.access(file_path, os.R_OK):
            return False
            
        return True