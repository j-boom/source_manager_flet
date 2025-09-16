import unittest
from unittest.mock import MagicMock, PropertyMock
import sys
import os

# Add the project root to the Python path to allow imports from `src`
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

import flet as ft
from src.views.pages.sources_view import SourcesView
from src.models.source_models import SourceRecord


class TestSourcesViewFiltering(unittest.TestCase):

    def setUp(self):
        """Set up a mock environment for each test."""

        # --- Mock Data ---
        self.source1_usa = MagicMock(spec=SourceRecord)
        self.source1_usa.id = "usa-1"
        self.source1_usa.country = "USA"
        self.source1_usa.source_type = "book"
        self.source1_usa.display_name = "The Art of Software"
        self.source1_usa.get_field_value.side_effect = lambda key, default="": {
            "title": "The Art of Software", "authors": "John Doe"
        }.get(key, default)

        self.source2_usa = MagicMock(spec=SourceRecord)
        self.source2_usa.id = "usa-2"
        self.source2_usa.country = "USA"
        self.source2_usa.source_type = "report"
        self.source2_usa.display_name = "Annual Security Report"
        self.source2_usa.get_field_value.side_effect = lambda key, default="": {
            "title": "Annual Security Report", "authors": "Jane Smith"
        }.get(key, default)

        self.source3_can = MagicMock(spec=SourceRecord)
        self.source3_can.id = "can-1"
        self.source3_can.country = "Canada"
        self.source3_can.source_type = "book"
        self.source3_can.display_name = "Canadian Software History"
        self.source3_can.get_field_value.side_effect = lambda key, default="": {
            "title": "Canadian Software History", "authors": "John Doe"
        }.get(key, default)

        self.usa_sources = [self.source1_usa, self.source2_usa]
        self.canada_sources = [self.source3_can]

        # --- Mock Controller and its dependencies ---
        self.mock_controller = MagicMock()
        self.mock_page = MagicMock(spec=ft.Page)
        self.mock_controller.page = self.mock_page

        # Mock project state (no project loaded)
        mock_project_state_manager = MagicMock()
        type(mock_project_state_manager).current_project = PropertyMock(return_value=None)
        self.mock_controller.project_state_manager = mock_project_state_manager

        # Mock source controller methods
        self.mock_controller.source_controller.get_available_countries.return_value = ["USA", "Canada"]
        def get_sources_by_country_side_effect(country):
            if country == "USA":
                return self.usa_sources
            if country == "Canada":
                return self.canada_sources
            return []
        self.mock_controller.source_controller.get_sources_by_country.side_effect = get_sources_by_country_side_effect

        # Mock admin controller methods
        self.mock_controller.admin_controller.get_all_source_types.return_value = [
            ("book", {"fields": [{"name": "title", "label": "Title", "storage_scope": "core"}, {"name": "authors", "label": "Authors", "storage_scope": "core"}]}),
            ("report", {"fields": [{"name": "title", "label": "Title", "storage_scope": "core"}]})
        ]

        # --- Instantiate the View ---
        # We manually call build() to simulate Flet's behavior
        self.view = SourcesView(self.mock_page, self.mock_controller)
        self.view.build()

    def get_result_ids(self):
        """Helper to get the source IDs from the current results list."""
        return [
            card.source.id
            for card in self.view.results_list.controls
            if isinstance(card, ft.Control) and hasattr(card, 'source')
        ]

    def test_initial_load(self):
        """Test that sources for the default country (USA) are loaded initially."""
        self.assertEqual(self.view.selected_country, "USA")
        self.assertEqual(len(self.view.results_list.controls), 2)
        result_ids = self.get_result_ids()
        self.assertIn("usa-1", result_ids)
        self.assertIn("usa-2", result_ids)

    def test_filter_by_single_field_title(self):
        """Test filtering by a single field (title)."""
        # Simulate user typing "art" into the "Title" filter field
        self.view.filter_controls["title"].value = "art"
        self.view._apply_all_filters()

        self.assertEqual(len(self.view.results_list.controls), 1)
        self.assertEqual(self.get_result_ids()[0], "usa-1")

    def test_filter_by_single_field_case_insensitive(self):
        """Test that filtering is case-insensitive."""
        # Simulate user typing "ART" (uppercase)
        self.view.filter_controls["title"].value = "ART"
        self.view._apply_all_filters()

        self.assertEqual(len(self.view.results_list.controls), 1)
        self.assertEqual(self.get_result_ids()[0], "usa-1")

    def test_filter_by_multiple_fields(self):
        """Test filtering by multiple fields (author and title)."""
        # This should find nothing, as John Doe didn't write the security report
        self.view.filter_controls["authors"].value = "john doe"
        self.view.filter_controls["title"].value = "security"
        self.view._apply_all_filters()

        self.assertEqual(len(self.view.results_list.controls), 1)
        # The result list should contain a Text control saying no results
        self.assertIsInstance(self.view.results_list.controls[0], ft.Text)

        # This should find the "Art of Software" book
        self.view.filter_controls["title"].value = "software"
        self.view._apply_all_filters()

        self.assertEqual(len(self.view.results_list.controls), 1)
        self.assertEqual(self.get_result_ids()[0], "usa-1")

    def test_filter_no_results(self):
        """Test a filter that yields no results."""
        self.view.filter_controls["title"].value = "nonexistent"
        self.view._apply_all_filters()

        self.assertEqual(len(self.view.results_list.controls), 1)
        self.assertIsInstance(self.view.results_list.controls[0], ft.Text)
        self.assertIn("No sources match", self.view.results_list.controls[0].value)

    def test_clear_filters(self):
        """Test the 'Clear' button functionality."""
        # Apply a filter first
        self.view.filter_controls["title"].value = "art"
        self.view._apply_all_filters()
        self.assertEqual(len(self.view.results_list.controls), 1)

        # Now clear it
        self.view._clear_all_filters()

        # Should be back to the full list for the country
        self.assertEqual(len(self.view.results_list.controls), 2)
        result_ids = self.get_result_ids()
        self.assertIn("usa-1", result_ids)
        self.assertIn("usa-2", result_ids)
        self.assertEqual(self.view.filter_controls["title"].value, "")

    def test_remove_filter_chip(self):
        """Test removing a filter by clicking its chip."""
        self.view.filter_controls["title"].value = "art"
        self.view._apply_all_filters()
        self.assertEqual(len(self.view.results_list.controls), 1)
        self.assertEqual(len(self.view.active_filter_chips.controls), 1)

        # Simulate clicking the delete icon on the chip
        chip_to_delete = self.view.active_filter_chips.controls[0]
        mock_event = MagicMock()
        mock_event.control = chip_to_delete
        self.view._remove_filter_chip(mock_event)

        # The list should be reset to the full country list
        self.assertEqual(len(self.view.results_list.controls), 2)
        self.assertEqual(len(self.view.active_filter_chips.controls), 0)
        self.assertEqual(self.view.filter_controls["title"].value, "")

    def test_change_country(self):
        """Test changing the country dropdown."""
        # Initial state is USA
        self.assertEqual(self.view.selected_country, "USA")
        self.assertEqual(len(self.get_result_ids()), 2)

        # Apply a filter
        self.view.filter_controls["title"].value = "art"
        self.view._apply_all_filters()
        self.assertEqual(len(self.get_result_ids()), 1)

        # Simulate changing the country to Canada
        mock_event = MagicMock()
        mock_event.control.value = "Canada"
        self.view._on_country_changed(mock_event)

        # Assert that the country changed
        self.assertEqual(self.view.selected_country, "Canada")

        # Assert that the filters were cleared
        self.assertEqual(self.view.filter_controls["title"].value, "")
        self.assertEqual(len(self.view.active_filter_chips.controls), 0)

        # Assert that the results list now shows sources for Canada
        self.assertEqual(len(self.view.results_list.controls), 1)
        self.assertEqual(self.get_result_ids()[0], "can-1")


if __name__ == '__main__':
    unittest.main()