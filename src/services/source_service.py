"""
Source Service

Manages all operations related to master source records, including
CRUD operations and caching.
"""

import json
import uuid
import logging
from pathlib import Path
from filelock import FileLock, Timeout
from typing import List, Dict, Optional, Tuple, Any
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
        self._dirty_countries: set[str] = set()
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

        try:
            new_source = SourceRecord.from_dict(form_data)
            new_source.country = country
        except Exception as e:
            self.logger.error(f"Failed to create source model: {e}", exc_info=True)
            return False, f"Failed to create source model: {e}", None

        source_file_path = self.master_sources_dir / get_source_file_for_country(country)
        lock_path = source_file_path.with_suffix('.lock')

        try:
            with FileLock(lock_path, timeout=5):
                self.logger.debug(f"Acquired lock for {source_file_path}")
                # --- CRITICAL SECTION: Read, Modify, Write ---
                sources_list = []
                master_data = {"sources": sources_list}
                if source_file_path.exists():
                    with open(source_file_path, "r", encoding="utf-8") as f:
                        master_data = json.load(f)
                        sources_list = master_data.get("sources", [])

                sources_list.append(new_source.to_dict())
                master_data["sources"] = sources_list

                with open(source_file_path, "w", encoding="utf-8") as f:
                    json.dump(master_data, f, indent=4)
                # --- END CRITICAL SECTION ---

            # Invalidate the cache for the country where the source was added
            if country in self._master_source_cache:
                del self._master_source_cache[country]

            return True, "Source created successfully.", new_source
        except Timeout:
            self.logger.warning(f"Could not acquire lock for {source_file_path}. File may be in use.")
            return False, "The source file is currently in use. Please try again.", None
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

        # Mark the country as dirty to be saved later
        if source.country:
            self._dirty_countries.add(source.country)
            self.logger.debug(f"Marked country '{source.country}' as dirty after updating source {source_id}.")
        
        return True, "Source updated in memory."

    def save_all_dirty_sources(self):
        """Writes all cached sources for 'dirty' countries back to disk."""
        if not self._dirty_countries:
            self.logger.info("No dirty sources to save. Shutdown clean.")
            return

        self.logger.info(f"Saving dirty sources for countries: {self._dirty_countries}")
        for country in list(self._dirty_countries): # Iterate over a copy
            source_file_path = self.master_sources_dir / get_source_file_for_country(country)
            lock_path = source_file_path.with_suffix('.lock')

            # Get all sources for the country from the cache
            country_cache = self._master_source_cache.get(country, {})
            if not country_cache:
                self.logger.warning(f"No cache found for dirty country '{country}'. Skipping save.")
                continue

            sources_list = [source.to_dict() for source in country_cache.values()]
            master_data = {"sources": sources_list}

            try:
                # Acquire a lock on the file, with a timeout.
                with FileLock(lock_path, timeout=10): # Longer timeout for shutdown
                    self.logger.debug(f"Acquired lock for {source_file_path} during shutdown save.")
                    with open(source_file_path, "w", encoding="utf-8") as f:
                        json.dump(master_data, f, indent=4)
                    
                    # If save is successful, remove from dirty set
                    self._dirty_countries.remove(country)
                    self.logger.info(f"Successfully saved sources for '{country}'.")

            except Timeout:
                self.logger.error(f"Could not acquire lock for {source_file_path} during shutdown. Changes for '{country}' may be lost.")
            except Exception as e:
                self.logger.error(f"Failed to save sources for '{country}' during shutdown: {e}", exc_info=True)

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
