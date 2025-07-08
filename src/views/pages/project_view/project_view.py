import flet as ft
from views import BaseView
from config.project_types_config import get_project_type_config

# Import tab and component classes
from .tabs.project_metadata import ProjectMetadataTab
from .tabs.project_sources import ProjectSourcesTab
from .tabs.cite_sources import CiteSourcesTab
from views.components.app_fab import AppFab

class ProjectView(BaseView):
    """Project view with a tabbed interface for different project aspects."""
    
    def __init__(self, page: ft.Page, controller):
        super().__init__(page, controller)
        self.project_state_manager = self.controller.project_state_manager
        
        # Initialize tab views
        self.metadata_tab = ProjectMetadataTab(controller=self.controller)
        self.sources_tab = ProjectSourcesTab(controller=self.controller)
        self.cite_sources_tab = CiteSourcesTab(controller=self.controller)
        
        # This will hold the ft.Tabs instance once it's built
        self.tabs_control: ft.Tabs | None = None

    def build(self) -> ft.Control:
        """Builds the entire project view UI."""
        project = self.project_state_manager.current_project
        if not project:
            return self.show_error("No project is currently loaded.")

        # 1. Create the tabs control and store it as an instance attribute.
        self.tabs_control = self._build_tabs()
        
        # 2. Call the tab change handler to set the initial FAB state.
        self._on_tab_change()

        project_info = f"Project: {project.title}"
        project_type_config = get_project_type_config(project.project_type.value)
        project_type_display = f"({project_type_config.display_name})" if project_type_config else ""

        return ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.Row([
                        ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda e: self.controller.navigate_to("new_project"), tooltip="Back to Project Browser"),
                        ft.Text(project_info, size=20, weight=ft.FontWeight.BOLD),
                    ]),
                    ft.Container(expand=True),
                    ft.Text(project_type_display, size=20, color=ft.colors.ON_SURFACE_VARIANT),
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.all(20),
                border=ft.border.only(bottom=ft.BorderSide(1, ft.colors.OUTLINE))
            ),
            ft.Container(
                # 3. Use the stored tabs_control instance in the layout.
                content=self.tabs_control,
                expand=True,
                padding=ft.padding.symmetric(horizontal=20, vertical=10)
            )
        ], expand=True, spacing=0)

    def _build_tabs(self) -> ft.Tabs:
        """Constructs the Flet Tabs control and assigns an on_change handler."""
        project = self.project_state_manager.current_project
        if project:
            self.metadata_tab.update_project_data(project.metadata, str(project.file_path))
            self.sources_tab.update_project_data(project.metadata, str(project.file_path))
            self.cite_sources_tab.update_project_data(project.metadata, str(project.file_path))

        return ft.Tabs(
            selected_index=0,
            animation_duration=300,
            on_change=lambda e: self._on_tab_change(),
            tabs=[
                ft.Tab(text="Project Metadata", icon=ft.icons.INFO_OUTLINE, content=self.metadata_tab.build()),
                ft.Tab(text="Manage Sources", icon=ft.icons.SOURCE, content=self.sources_tab.build()),
                ft.Tab(text="Cite Slides", icon=ft.icons.COMPARE_ARROWS, content=self.cite_sources_tab.build()),
            ],
            expand=True
        )

    def _on_tab_change(self):
        """Shows, hides, or changes the FAB based on the selected tab."""
        if self.tabs_control is None:
            return

        # "Manage Sources" tab is at index 1
        if self.tabs_control.selected_index == 1:
            self.page.floating_action_button = AppFab(
                icon=ft.icons.ADD_ROUNDED,
                text="New Source",
                tooltip="Create and add a new source to this project",
                on_click=lambda e: self.controller.show_create_source_dialog(add_to_project_on_create=True)
            )
        else:
            self.page.floating_action_button = None
        
        self.page.update()

    def update_view(self):
        """This method is called by the controller's refresh_current_view."""
        project = self.project_state_manager.current_project
        if project:
            self.sources_tab.update_project_data(project.metadata, str(project.file_path))
            self.metadata_tab.update_project_data(project.metadata, str(project.file_path))
            self.cite_sources_tab.update_project_data(project.metadata, str(project.file_path))
