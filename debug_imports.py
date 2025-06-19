import sys
sys.path.insert(0, 'src')

try:
    from src.views.pages.new_project_view.new_project_view import NewProjectView
    print("Direct import from file works")
except Exception as e:
    print(f"Direct import error: {e}")

try:
    from src.views.pages.new_project_view import NewProjectView
    print("Import from package works")
except Exception as e:
    print(f"Package import error: {e}")

try:
    import src.views.pages.new_project_view
    print("Module contents:", dir(src.views.pages.new_project_view))
    print("NewProjectView in module:", hasattr(src.views.pages.new_project_view, "NewProjectView"))
except Exception as e:
    print(f"Module import error: {e}")
