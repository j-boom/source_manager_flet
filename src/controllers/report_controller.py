"""
Report Controller

Orchestrates the generation of reports by gathering necessary data
and calling the appropriate services.
"""
from typing import Tuple, Dict, Any

from .base_controller import BaseController


class ReportController(BaseController):
    """Controller for handling report generation."""

    def __init__(self, app_controller):
        super().__init__(app_controller)
        self.report_service = self.controller.report_service

    def export_word_report(self, output_path: str) -> Tuple[bool, str]:
        """
        Gathers project data and template info, then calls the ReportService
        to generate the Word document.
        """
        project = self.controller.project_controller.get_current_project()
        if not project:
            return False, "No project is currently open."

        project_type_config = self.controller.project_controller.get_project_type_config(
            project.project_type
        )
        template_path = project_type_config.get("word_template_path")

        # --- Prepare the data context for the template ---
        # 1. Start with the project's own metadata fields
        template_context: Dict[str, Any] = project.metadata.copy()

        # 2. Get the fully combined source data (master + link)
        combined_sources = self.controller.source_controller.get_combined_project_sources_data()

        # 3. Add the sources to the context under a 'sources' key
        template_context["sources"] = combined_sources

        return self.report_service.generate_word_report(
            template_context=template_context,
            template_path=template_path,
            output_path=output_path,
        )

    def export_powerpoint_report(self, output_path: str) -> Tuple[bool, str]:
        """
        Gathers project data and template info, then calls the ReportService
        to generate the PowerPoint document.
        """
        project = self.controller.project_controller.get_current_project()
        if not project:
            return False, "No project is currently open."

        project_type_config = self.controller.project_controller.get_project_type_config(
            project.project_type
        )
        template_path = project_type_config.get("powerpoint_template_path")

        # --- Prepare the data context for the template ---
        template_context: Dict[str, Any] = project.metadata.copy()
        combined_sources = self.controller.source_controller.get_combined_project_sources_data()
        template_context["sources"] = combined_sources

        return self.report_service.generate_powerpoint_report(
            template_context=template_context,
            template_path=template_path,
            output_path=output_path,
        )
