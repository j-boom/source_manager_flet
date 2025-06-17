"""
Project creation helper methods for NewProjectView
"""
import flet as ft
import os


def show_simple_project_dialog(self, ten_digit_number: str):
    """Show a simple project creation dialog"""
    import datetime
    import json
    import re
    
    # Form fields
    project_type_dropdown = ft.Dropdown(
        label="Project Type *",
        options=[
            ft.dropdown.Option("CCR"),
            ft.dropdown.Option("GSC"), 
            ft.dropdown.Option("STD"),
            ft.dropdown.Option("FCR"),
            ft.dropdown.Option("COM"),
            ft.dropdown.Option("CRS"),
            ft.dropdown.Option("OTH")
        ],
        width=200
    )
    
    suffix_field = ft.TextField(
        label="Suffix",
        hint_text="ABC123 format",
        width=150,
        max_length=6
    )
    
    current_year = datetime.datetime.now().year
    year_dropdown = ft.Dropdown(
        label="Request Year *",
        options=[ft.dropdown.Option(str(year)) for year in range(current_year, current_year + 5)],
        value=str(current_year),
        width=150
    )
    
    document_title_field = ft.TextField(
        label="Document Title",
        hint_text="Required for OTH projects",
        width=300,
        visible=False
    )
    
    def on_type_change(e):
        project_type = e.control.value
        document_title_field.visible = (project_type == "OTH")
        if project_type == "GSC":
            suffix_field.label = "Suffix (Optional)"
        else:
            suffix_field.label = "Suffix *"
        self.page.update()
    
    project_type_dropdown.on_change = on_type_change
    
    def create_project(e):
        project_type = project_type_dropdown.value
        suffix = suffix_field.value.strip().upper() if suffix_field.value else ""
        year = year_dropdown.value
        doc_title = document_title_field.value.strip() if document_title_field.value else ""
        
        # Validation
        errors = []
        if not project_type:
            errors.append("Project type required")
        if not year:
            errors.append("Year required")
        if project_type != "GSC" and not suffix:
            errors.append("Suffix required")
        if project_type == "OTH" and not doc_title:
            errors.append("Document title required for OTH")
        if suffix and not re.match(r'^[A-Z]{3}\d{3}$', suffix):
            errors.append("Suffix format: ABC123")
        
        if errors:
            error_dialog = ft.AlertDialog(
                title=ft.Text("Validation Error"),
                content=ft.Text("\n".join(errors)),
                actions=[ft.TextButton("OK", on_click=lambda e: self._close_dialog(error_dialog))]
            )
            self.page.dialog = error_dialog
            error_dialog.open = True
            self.page.update()
            return
        
        # Build filename
        parts = [ten_digit_number]
        if suffix:
            parts.append(suffix)
        parts.append(project_type)
        if project_type == "OTH" and doc_title:
            parts.append(doc_title)
        parts.append(year)
        
        filename = " - ".join(parts) + ".json"
        folder_path = self._form_fields['folder_path']
        file_path = os.path.join(folder_path, filename)
        
        # Create project data
        project_data = {
            "project_id": ten_digit_number,
            "project_type": project_type,
            "suffix": suffix if suffix else None,
            "document_title": doc_title if doc_title else None,
            "request_year": int(year),
            "created_date": datetime.datetime.now().isoformat(),
            "status": "active"
        }
        
        try:
            with open(file_path, 'w') as f:
                json.dump(project_data, f, indent=4)
            
            # Add to recent projects
            if self.user_config:
                display_name = " - ".join(parts)
                self.user_config.add_recent_site(display_name, folder_path)
            
            self._close_dialog(dialog)
            
            # Refresh view
            contents = self._get_folder_contents(folder_path)
            self._update_folder_view(contents, "folder_contents")
            
        except Exception as ex:
            error_dialog = ft.AlertDialog(
                title=ft.Text("Error"),
                content=ft.Text(f"Failed to create project: {ex}"),
                actions=[ft.TextButton("OK", on_click=lambda e: self._close_dialog(error_dialog))]
            )
            self.page.dialog = error_dialog
            error_dialog.open = True
            self.page.update()
    
    # Create dialog
    dialog_content = ft.Column([
        ft.Text(f"Create Project: {ten_digit_number}", size=16, weight=ft.FontWeight.BOLD),
        ft.Container(height=15),
        ft.Row([project_type_dropdown, suffix_field, year_dropdown], spacing=15),
        document_title_field,
    ], spacing=10)
    
    dialog = ft.AlertDialog(
        title=ft.Text("Add New Project"),
        content=dialog_content,
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: self._close_dialog(dialog)),
            ft.ElevatedButton("Create", on_click=create_project,
                style=ft.ButtonStyle(color=ft.colors.WHITE, bgcolor=ft.colors.GREEN_700))
        ]
    )
    
    self.page.dialog = dialog
    dialog.open = True
    self.page.update()
