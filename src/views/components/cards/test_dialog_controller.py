import unittest
from unittest.mock import MagicMock, patch

from src.controllers.dialog_controller import DialogController


class TestDialogController(unittest.TestCase):

    def setUp(self):
        """Set up a mock AppController and DialogController for each test."""
        self.mock_app_controller = MagicMock()
        self.dialog_controller = DialogController(self.mock_app_controller)
        # Alias for easier access to the main controller mock
        self.controller = self.mock_app_controller

    @patch('src.controllers.dialog_controller.FirstTimeSetupDialog')
    def test_show_first_time_setup_flow_success(self, MockFirstTimeSetupDialog):
        """Test the complete flow of the first-time user setup on success."""
        # Arrange: The mock dialog instance that will be created
        mock_dialog_instance = MockFirstTimeSetupDialog.return_value
        
        # Act: Call the method that starts the flow
        self.dialog_controller.show_first_time_setup()

        # Assert: Check that the dialog was created and shown
        MockFirstTimeSetupDialog.assert_called_once()
        mock_dialog_instance.show.assert_called_once()

        # Arrange: Capture the on_setup_complete callback and define a test name
        on_complete_callback = MockFirstTimeSetupDialog.call_args.args[1]
        test_display_name = "Test User"

        # Act: Simulate the user completing the dialog by invoking the callback
        on_complete_callback(test_display_name)

        # Assert: Check that all the correct actions were taken upon completion
        self.controller.settings_manager.save_display_name.assert_called_once_with(test_display_name)
        self.controller.user_config_manager.mark_setup_completed.assert_called_once()
        self.controller.main_view.update_greeting.assert_called_once()
        self.controller.navigate_to.assert_called_once_with("home")

    @patch('src.controllers.dialog_controller.FirstTimeSetupDialog')
    def test_show_first_time_setup_flow_skipped(self, MockFirstTimeSetupDialog):
        """Test the first-time user setup flow when the user skips."""
        # Act
        self.dialog_controller.show_first_time_setup()

        # Arrange: Capture the callback and simulate skipping
        on_complete_callback = MockFirstTimeSetupDialog.call_args.args[1]
        
        # Act: Simulate skipping by calling the callback with an empty string
        on_complete_callback("")

        # Assert: Check that an empty name is saved and the rest of the flow completes
        self.controller.settings_manager.save_display_name.assert_called_once_with("")
        self.controller.user_config_manager.mark_setup_completed.assert_called_once()