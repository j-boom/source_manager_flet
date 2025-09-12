import unittest
from unittest.mock import MagicMock

from src.controllers.admin_controller import AdminController


class TestAdminController(unittest.TestCase):

    def setUp(self):
        """Set up a mock AppController and AdminController for each test."""
        self.mock_app_controller = MagicMock()
        self.admin_controller = AdminController(self.mock_app_controller)
        # Alias for easier access to the main controller mock
        self.controller = self.mock_app_controller

    def test_add_new_source_type_success(self):
        """Test successfully adding a new source type."""
        # Arrange: No existing source types
        self.controller.admin_service.get_source_types.return_value = {}
        
        # Act
        self.admin_controller.add_new_source_type("IC Source", "ic_source")
        
        # Assert
        # Check that the save method was called
        self.controller.admin_service.save_source_types.assert_called_once()
        
        # Check the content that was saved
        saved_data = self.controller.admin_service.save_source_types.call_args[0][0]
        self.assertIn("ic_source", saved_data)
        self.assertEqual(saved_data["ic_source"]["display_name"], "IC Source")
        self.assertIn("fields", saved_data["ic_source"])
        
        # Check UI feedback
        self.controller.show_success_message.assert_called_once_with("Source type 'IC Source' created.")
        self.controller.update_view.assert_called_once_with("admin")
        self.controller.show_error_message.assert_not_called()

    def test_add_new_source_type_already_exists(self):
        """Test adding a source type that already exists."""
        # Arrange: Source type already exists
        self.controller.admin_service.get_source_types.return_value = {"ic_source": {}}
        
        # Act
        self.admin_controller.add_new_source_type("IC Source", "ic_source")
        
        # Assert
        # Check that save was NOT called
        self.controller.admin_service.save_source_types.assert_not_called()
        
        # Check UI feedback
        self.controller.show_error_message.assert_called_once_with("Source type 'ic_source' already exists.")
        self.controller.show_success_message.assert_not_called()
        self.controller.update_view.assert_not_called()

    def test_add_new_project_type_success(self):
        """Test successfully adding a new project type."""
        # Arrange: No existing project types
        self.controller.admin_service.get_project_types.return_value = {}
        
        # Act
        self.admin_controller.add_new_project_type("Sample Report", "sample_report")
        
        # Assert
        # Check that the save method was called
        self.controller.admin_service.save_project_types.assert_called_once()
        
        # Check the content that was saved
        saved_data = self.controller.admin_service.save_project_types.call_args[0][0]
        self.assertIn("sample_report", saved_data)
        self.assertEqual(saved_data["sample_report"]["display_name"], "Sample Report")
        self.assertIn("fields", saved_data["sample_report"])
        
        # Check UI feedback
        self.controller.show_success_message.assert_called_once_with("Project type 'Sample Report' created.")
        self.controller.update_view.assert_called_once_with("admin")
        self.controller.show_error_message.assert_not_called()