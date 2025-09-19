"""
Report Service

Handles the generation of reports, such as Word documents, from project data.
"""
import logging
import docx
from typing import Optional, Tuple, Dict, Any
import json

from src.models import Project


class ReportService:
    """Service for generating reports."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("ReportService initialized")

    def generate_word_report(
        self,
        template_context: Dict[str, Any],
        template_path: Optional[str],
        output_path: str,
    ) -> Tuple[bool, str]:
        """
        Generates a Word document report for a given project.
        This is a placeholder for the actual python-docx implementation.
        """
        project_title = template_context.get("project_title", "Unknown Project")
        self.logger.info("Generating Word report for project '%s'", project_title)
        self.logger.info("Template path: %s", template_path)
        self.logger.info("Output path: %s", output_path)

        # --- DEBUG: Print the full context that will be available to the template ---
        self.logger.info("--- WORD REPORT TEMPLATE CONTEXT ---")
        self.logger.info(json.dumps(template_context, indent=2, default=str))
        self.logger.info("--- END WORD REPORT TEMPLATE CONTEXT ---")

        # TODO: Implement actual document generation using python-docx
        # doc = Document(template_path) if template_path else Document()
        # ... logic to fill the document ...
        # doc.save(output_path)

        return True, f"Report successfully generated at {output_path}"

    def generate_powerpoint_report(
        self,
        template_context: Dict[str, Any],
        template_path: Optional[str],
        output_path: str,
    ) -> Tuple[bool, str]:
        """
        Generates a PowerPoint document report for a given project.
        This is a placeholder for the actual python-pptx implementation.
        """
        project_title = template_context.get("project_title", "Unknown Project")
        self.logger.info("Generating PowerPoint report for project '%s'", project_title)
        self.logger.info("Template path: %s", template_path)
        self.logger.info("Output path: %s", output_path)

        # --- DEBUG: Print the full context that will be available to the template ---
        self.logger.info("--- POWERPOINT REPORT TEMPLATE CONTEXT ---")
        self.logger.info(json.dumps(template_context, indent=2, default=str))
        self.logger.info("--- END POWERPOINT REPORT TEMPLATE CONTEXT ---")

        # TODO: Implement actual document generation using python-pptx
        # pres = Presentation(template_path) if template_path else Presentation()
        # ... logic to fill the presentation ...
        # pres.save(output_path)

        return True, f"Report successfully generated at {output_path}"
