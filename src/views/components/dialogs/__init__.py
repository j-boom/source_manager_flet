"""Dialog components for the project manager"""

from .base_dialog import BaseDialog
from .project_creation_dialog import ProjectCreationDialog
from .folder_creation_dialog import FolderCreationDialog
from .first_time_setup_dialog import FirstTimeSetupDialog
from .source_creation_dialog import SourceCreationDialog
from .source_editor_dialog import SourceEditorDialog
from .add_source_to_project_dialog import AddSourceToProjectDialog
from .admin_login_dialog import AdminLoginDialog
from .add_config_type_dialog import AddConfigTypeDialog
from .user_editor_dialog import UserEditorDialog
from .delete_confirmation_dialog import DeleteConfirmationDialog
from .source_citation_dialog import SourceCitationDialog
from .add_boilerplate_sources_dialog import AddBoilerplateSourcesDialog
from .import_sources_dialog import ImportSourcesDialog


__all__ = [
    "BaseDialog",
    "AddSourceToProjectDialog",
    "ProjectCreationDialog",
    "FolderCreationDialog",
    "FirstTimeSetupDialog",
    "SourceCreationDialog",
    "SourceEditorDialog",
    "AdminLoginDialog",
    "AddConfigTypeDialog",
    "UserEditorDialog",
    "DeleteConfirmationDialog",
    "SourceCitationDialog",
    "AddBoilerplateSourcesDialog",
    "ImportSourcesDialog",
]
