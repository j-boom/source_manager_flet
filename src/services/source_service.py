"""
Source Service

Manages all operations related to master source records, including
CRUD operations and caching.
"""

import json
import uuid
import re
import logging
from pathlib import Path
from filelock import FileLock, Timeout
from typing import List, Dict, Optional, Tuple, Any, TYPE_CHECKING
from datetime import datetime

from config import MASTER_SOURCES_DIR, get_source_file_for_country
from src.models.source_models import SourceRecord
from .directory_service import DirectoryService
if TYPE_CHECKING:
    from .admin_service import AdminService


class SourceService:
    """Manages loading, saving, and querying master source records."""

    def __init__(self, directory_service: DirectoryService, admin_service: "AdminService"):
        self.logger = logging.getLogger(__name__)
        self.master_sources_dir = Path(MASTER_SOURCES_DIR)
        self.master_sources_dir.mkdir(parents=True, exist_ok=True)
        self._master_source_cache: Dict[str, Dict[str, SourceRecord]] = {}
        self.directory_service = directory_service
        self.admin_service = admin_service
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
        # First, check all cached sources for a quick lookup.
        for country_cache in self._master_source_cache.values():
            if source_id in country_cache:
                return country_cache[source_id]
        
        # If not in cache, load all uncached source files and check again.
        self.logger.debug(f"Source ID {source_id} not in cache. Scanning all source files.")
        for f in self.master_sources_dir.glob("*_sources.json"):
            country = f.name.replace("_sources.json", "")
            if country not in self._master_source_cache:
                self._load_master_sources_for_country(country)

        # After loading, check the cache again. This is the crucial second check.
        for country_cache in self._master_source_cache.values():
            if source_id in country_cache:
                source_record = country_cache[source_id]
                self.logger.debug(f"Found source ID {source_id} after loading from disk.")
                # After loading, check if it needs migration and perform it.
                self._migrate_source_if_needed(source_record)
                return source_record

        self.logger.warning(f"Source with ID '{source_id}' could not be found in any source file.")
        return None

    def _migrate_source_if_needed(self, source: SourceRecord):
        """Compares a loaded source's fields against its type config and migrates if necessary."""
        source_configs = self.admin_service.get_source_types()
        current_config = source_configs.get(source.source_type)
        if not current_config:
            return

        config_fields = {f['name'] for f in current_config.get('fields', [])}
        source_fields = {f.name for f in source.fields}

        added_fields = config_fields - source_fields

        if not added_fields:
            return

        self.logger.info(f"Migrating source '{source.id}' by adding new fields.")
        modified = False
        for field_name in added_fields:
            source.set_field_value(field_name, "")
            modified = True
        
        if modified:
            self.update_master_source(source.id, source.to_dict())
            self.logger.info(f"Source '{source.id}' migration complete.")

    def get_available_countries(self) -> List[str]:
        return [c['name'] for c in self.directory_service.get_country_folders()]

    def create_new_source(
        self, country: str, form_data: Dict[str, Any]
    ) -> Tuple[bool, str, Optional[SourceRecord]]:
        """Create a new master source for a specific country using the factory."""
        source_type_str = form_data.get("source_type")
        if not source_type_str:
            return False, "Source type not specified.", None

        # --- Configurable Duplicate Check ---
        source_configs = self.admin_service.get_source_types()
        source_type_config = source_configs.get(source_type_str, {})

        # Identify fields that are part of the title based on the 'is_title_part' flag
        title_part_fields_config = [
            f for f in source_type_config.get("fields", []) if f.get("is_title_part")
        ]
        # Sort them by their defined display order
        title_part_fields_config.sort(key=lambda f: f.get("display_order", 0))
        unique_key_fields = [f["name"] for f in title_part_fields_config]

        # Generate the display_name from the form data
        title_parts = [
            str(form_data.get(key, "")).strip() for key in unique_key_fields
        ]
        # Filter out any empty parts before joining
        display_name = " - ".join(filter(None, title_parts))

        # Add the generated display name to the form data so it gets saved
        form_data["display_name"] = display_name

        if unique_key_fields:
            self.logger.info(f"Performing duplicate check for source type '{source_type_str}' using title parts: {unique_key_fields}")
            
            # Get values from the new source data, normalized for comparison
            new_source_values = {
                key: str(form_data.get(key, "")).strip().lower() for key in unique_key_fields
            }

            # Check against existing sources
            existing_sources = self.get_sources_by_country(country)
            for existing_source in existing_sources:
                if existing_source.source_type != source_type_str:
                    continue
                # Check if all key fields in the existing source match the new source's values
                if all(str(existing_source.get_field_value(key, "")).strip().lower() == new_source_values[key] for key in unique_key_fields):
                    message = f"A source with the same title parts already exists for {country} (Title: '{display_name}')."
                    self.logger.warning(f"Duplicate source creation blocked for country '{country}'. New data: {form_data}")
                    return False, message, None
        else:
            self.logger.warning(f"No title parts defined for source type '{source_type_str}'. Skipping duplicate check and automatic title generation.")
        # --- End Configurable Duplicate Check ---

        try:
            new_source = SourceRecord.from_dict(form_data)
            new_source.country = country
        except Exception as e:
            self.logger.error(f"Failed to create source model: {e}", exc_info=True)
            return False, f"Failed to create source model: {e}", None

        source_file_path = self.master_sources_dir / get_source_file_for_country(country)

        # Load the country into cache if it's not already there.
        # This ensures we're adding to the existing set of sources in memory.
        self._load_master_sources_for_country(country)
        
        # Add the new source to the in-memory cache.
        self._master_source_cache[country][new_source.id] = new_source

        # Now, save the entire updated cache for that country to disk.
        success, message = self._save_sources_for_country(country)

        if success:
            return True, "Source created successfully.", new_source
        else:
            # If saving failed, roll back the in-memory change to maintain consistency.
            del self._master_source_cache[country][new_source.id]
            return False, message, None

    def create_boilerplate_source(
        self, form_data: Dict[str, Any]
    ) -> Tuple[bool, str, Optional[SourceRecord]]:
        """Create a new boilerplate source."""
        # ... (This method's logic remains the same as it doesn't use the main cache)
        source_type_str = form_data.get("source_type")
        if not source_type_str:
            return False, "Source type not specified.", None

        # --- Duplicate Check for Boilerplate ---
        source_configs = self.admin_service.get_source_types()
        source_type_config = source_configs.get(source_type_str, {})

        title_part_fields_config = [
            f for f in source_type_config.get("fields", []) if f.get("is_title_part")
        ]
        title_part_fields_config.sort(key=lambda f: f.get("display_order", 0))
        unique_key_fields = [f["name"] for f in title_part_fields_config]

        title_parts = [str(form_data.get(key, "")).strip() for key in unique_key_fields]
        display_name = " - ".join(filter(None, title_parts))
        form_data["display_name"] = display_name

        if unique_key_fields:
            self.logger.info(f"Performing duplicate check for boilerplate source using title parts: {unique_key_fields}")
            new_source_values = {key: str(form_data.get(key, "")).strip().lower() for key in unique_key_fields}
            existing_sources = self.get_boilerplate_sources()
            for existing_source in existing_sources:
                if existing_source.source_type != source_type_str:
                    continue
                if all(str(existing_source.get_field_value(key, "")).strip().lower() == new_source_values[key] for key in unique_key_fields):
                    message = f"A boilerplate source with the same title parts already exists (Title: '{display_name}')."
                    self.logger.warning(f"Duplicate boilerplate source creation blocked. New data: {form_data}")
                    return False, message, None
        else:
            self.logger.warning(f"No title parts defined for source type '{source_type_str}'. Skipping duplicate check.")
        
        try:
            form_data["country"] = "boilerplate"
            new_source = SourceRecord.from_dict(form_data)
        except Exception as e:
            self.logger.error(f"Failed to create boilerplate source model: {e}", exc_info=True)
            return False, f"Failed to create source model: {e}", None

        from config.app_config import BOILERPLATE_SOURCES_PATH
        lock_path = BOILERPLATE_SOURCES_PATH.with_suffix('.lock')

        try:
            with FileLock(lock_path, timeout=5):
                master_data = {"sources": [s.to_dict() for s in self.get_boilerplate_sources()]}
                master_data["sources"].append(new_source.to_dict())
                BOILERPLATE_SOURCES_PATH.write_text(json.dumps(master_data, indent=4), encoding="utf-8")
            return True, "Boilerplate source created successfully.", new_source
        except Timeout:
            return False, "The boilerplate source file is currently in use. Please try again.", None
        except Exception as e:
            return False, f"Failed to save boilerplate source file: {e}", None

    def _save_sources_for_country(self, country: str) -> Tuple[bool, str]:
        """
        Writes all cached sources for a given country back to its JSON file.
        This is the single, authoritative method for saving country-specific source data.
        """
        source_file_path = self.master_sources_dir / get_source_file_for_country(country)
        lock_path = source_file_path.with_suffix('.lock')

        country_cache = self._master_source_cache.get(country)
        if country_cache is None:
            self.logger.warning(f"No cache found for country '{country}'. Assuming new country and creating file.")
            country_cache = {}

        sources_list = [source.to_dict() for source in country_cache.values()]
        master_data = {"sources": sources_list}

        try:
            with FileLock(lock_path, timeout=5):
                self.logger.debug(f"Acquired lock for {source_file_path} to save.")
                source_file_path.write_text(json.dumps(master_data, indent=4), encoding="utf-8")
                self.logger.info(f"Successfully saved sources for '{country}'.")
                return True, "Saved successfully."
        except Timeout:
            msg = f"Could not acquire lock for {source_file_path}. The file may be in use."
            self.logger.error(msg)
            return False, msg
        except Exception as e:
            msg = f"An unexpected error occurred while saving sources for '{country}': {e}"
            self.logger.error(msg, exc_info=True)
            return False, msg

    def update_master_source(
        self, source_id: str, updated_data: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """Finds a master source, updates it, and saves the corresponding country file."""
        source = self.get_source_by_id(source_id)
        if not source:
            return False, f"Source with ID '{source_id}' not found."

        # Update the source object's dynamic fields and metadata
        for key, value in updated_data.items():
            if key in ["id", "source_type", "date_created", "last_modified"]:
                # These are read-only or managed internally, so we skip them.
                continue
            elif key in ["display_name", "country", "used_in"]:
                if getattr(source, key) != value:
                    setattr(source, key, value)
                    source.last_modified = datetime.now()
            else:
                # Use the dedicated method for updating dynamic fields
                source.set_field_value(key, value)

        if source.country:
            success, message = self._save_sources_for_country(source.country)
            if not success:
                return False, message # Propagate the error message
        
        return True, "Source updated successfully."

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

    def get_boilerplate_sources(self) -> List["SourceRecord"]:
        """
        Loads and returns all source records from the boilerplate JSON file.
        If the file does not exist, it will be created with a default structure.
        """
        from config.app_config import BOILERPLATE_SOURCES_PATH

        if not BOILERPLATE_SOURCES_PATH.exists():
            self.logger.warning(f"Boilerplate sources file not found at: {BOILERPLATE_SOURCES_PATH}. Creating a new one.")
            try:
                default_data = {"sources": []}
                BOILERPLATE_SOURCES_PATH.write_text(json.dumps(default_data, indent=4), encoding="utf-8")
                self.logger.info(f"Successfully created boilerplate sources file at {BOILERPLATE_SOURCES_PATH}.")
                return []
            except Exception as e:
                self.logger.error(f"Failed to create boilerplate sources file: {e}", exc_info=True)
                return []

        try:
            data = json.loads(BOILERPLATE_SOURCES_PATH.read_text(encoding="utf-8"))
            sources_data = data.get("sources", [])

            source_records = [SourceRecord.from_dict(s_data) for s_data in sources_data]
            self.logger.info(f"Loaded {len(source_records)} boilerplate sources.")
            return source_records
        except Exception as e:
            self.logger.error(f"Failed to load or parse boilerplate sources: {e}", exc_info=True)
            return []
