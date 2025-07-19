"""
Source Service

Manages all operations related to master source records, including
CRUD operations and caching.
"""

import json
import uuid
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime

from config import MASTER_SOURCES_DIR, get_source_file_for_country
from src.models.source_models import SourceRecord, SourceRecordFactory
from .directory_service import DirectoryService


class SourceService:
    """Manages loading, saving, and querying master source records."""

    def __init__(self, directory_service: DirectoryService):
        self.logger = logging.getLogger(__name__)
        self.master_sources_dir = Path(MASTER_SOURCES_DIR)
        self.master_sources_dir.mkdir(parents=True, exist_ok=True)
        self._master_source_cache: Dict[str, Dict[str, SourceRecord]] = {}
        self.directory_service = directory_service
        self.logger.info("SourceService initialized")

    def get_sources_by_country(self, country: str) -> List[SourceRecord]:
        """Retrieves all master source records for a specific country."""
        source_map = self._load_master_sources_for_country(country)
        return list(source_map.values())

    def get_all_master_sources(self) -> List[SourceRecord]:
        """Retrieves all master source records from all available countries."""
        all_sources = []
        for f in self.master_sources_dir.glob("*_sources.json"):
            country = f.name.replace("_sources.json", "")
            all_sources.extend(self.get_sources_by_country(country))
        return all_sources

    def get_source_by_id(self, source_id: str) -> Optional[SourceRecord]:
        """Finds a master source by its unique ID across all countries."""
        for country_cache in self._master_source_cache.values():
            if source_id in country_cache:
                return country_cache[source_id]
        
        all_sources = self.get_all_master_sources()
        return next((s for s in all_sources if s.id == source_id), None)

    def get_available_countries(self) -> List[str]:
        return self.directory_service.get_country_folders()

    def create_new_source(
        self, country: str, form_data: Dict[str, Any]
    ) -> Tuple[bool, str, Optional[SourceRecord]]:
        """Create a new master source for a specific country using the factory."""
        source_type_str = form_data.get("source_type")
        if not source_type_str:
            return False, "Source type not specified.", None

        try:
            # Use the factory to correctly build the object with its defined fields
            new_source = SourceRecordFactory.create_source_record(
                source_type=source_type_str, initial_values=form_data
            )
            # Set the remaining metadata attributes
            new_source.country = country
            new_source.id = str(uuid.uuid4()) # Override the default UUID if needed
        except Exception as e:
            self.logger.error(f"Failed to create source model: {e}", exc_info=True)
            return False, f"Failed to create source model: {e}", None

        source_file_path = self.master_sources_dir / get_source_file_for_country(country)
        
        sources_list = []
        master_data = {"sources": sources_list}
        if source_file_path.exists():
            with open(source_file_path, "r", encoding="utf-8") as f:
                master_data = json.load(f)
                sources_list = master_data.get("sources", [])

        sources_list.append(new_source.to_dict())
        master_data["sources"] = sources_list

        try:
            with open(source_file_path, "w", encoding="utf-8") as f:
                json.dump(master_data, f, indent=4)

            # Invalidate the cache for the country where the source was added
            if country in self._master_source_cache:
                del self._master_source_cache[country]

            return True, "Source created successfully.", new_source
        except Exception as e:
            self.logger.error(f"Failed to save master source file: {e}", exc_info=True)
            return False, f"Failed to save master source file: {e}", None

    def update_master_source(
        self, source_id: str, updated_data: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """Finds a master source, updates it, and saves the corresponding country file."""
        source = self.get_source_by_id(source_id)
        if not source:
            return False, f"Source with ID '{source_id}' not found."

        # Update the source object's dynamic fields and metadata
        for key, value in updated_data.items():
            if key in ["display_name", "country", "used_in"]:
                if getattr(source, key) != value:
                    setattr(source, key, value)
                    source.last_modified = datetime.now()
            else:
                # Use the dedicated method for updating dynamic fields
                source.set_field_value(key, value)

        country_to_save = source.country
        if not country_to_save:
            return False, f"Source {source_id} has no country; cannot determine where to save."

        source_file_path = self.master_sources_dir / get_source_file_for_country(country_to_save)

        if not source_file_path.exists():
            return False, f"Master source file for country '{country_to_save}' does not exist."

        try:
            with open(source_file_path, "r", encoding="utf-8") as f:
                master_data = json.load(f)
            
            sources_list = master_data.get("sources", [])
            found_and_updated = False
            for i, record_data in enumerate(sources_list):
                if record_data.get("id") == source_id:
                    sources_list[i] = source.to_dict()
                    found_and_updated = True
                    break

            if not found_and_updated:
                return False, f"Could not find source ID '{source_id}' in file '{source_file_path.name}'."

            with open(source_file_path, "w", encoding="utf-8") as f:
                json.dump(master_data, f, indent=4)

            if source.country in self._master_source_cache:
                del self._master_source_cache[source.country]

            return True, "Source updated successfully."
        except Exception as e:
            self.logger.error(f"Failed to save updated source: {e}", exc_info=True)
            return False, f"Failed to save updated source: {e}"

    def _load_master_sources_for_country(self, country: str) -> Dict[str, SourceRecord]:
        """Loads master sources for a specific country, with caching."""
        if country in self._master_source_cache:
            return self._master_source_cache[country]

        source_file_path = self.master_sources_dir / get_source_file_for_country(country)
        if not source_file_path.exists():
            self._master_source_cache[country] = {}
            return {}
        
        try:
            with open(source_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            sources_list = data.get("sources", [])
            source_map = {
                record_data["id"]: SourceRecord.from_dict(record_data)
                for record_data in sources_list
            }
            self._master_source_cache[country] = source_map
            return source_map
        except (json.JSONDecodeError, TypeError) as e:
            self.logger.error(f"Error loading master sources for '{country}': {e}", exc_info=True)
            return {}
            
    def get_master_sources_for_country(self, country: str) -> List[SourceRecord]:
        """Get all master sources for a specific country. Note: This is a duplicate of get_sources_by_country."""
        source_map = self._load_master_sources_for_country(country)
        return list(source_map.values())
