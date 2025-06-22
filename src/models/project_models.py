"""
Project-related data models for Source Manager Application
Contains dataclasses and models for projects and related entities
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Project:
    """Project data model representing a facility project"""
    uuid: str
    facility_number: Optional[str] = None  # 10-digit facility number
    facility_suffix: Optional[str] = None  # facility suffix
    engineer: Optional[str] = None
    drafter: Optional[str] = None
    reviewer: Optional[str] = None
    architect: Optional[str] = None
    geologist: Optional[str] = None
    project_code: Optional[str] = None
    project_type: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    status: str = 'active'
    id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class SlideAssignment:
    """Model for assigning sources to PowerPoint slides"""
    project_id: int
    source_id: int
    slide_number: int
    slide_title: Optional[str] = None
    notes: Optional[str] = None
    id: Optional[int] = None
