import sys
sys.path.insert(0, "src")

try:
    print("Trying to import from views.pages.new_project_view")
    import views.pages.new_project_view
    print("Module imported successfully")
    print(f"Module __all__: {views.pages.new_project_view.__all__ if hasattr(views.pages.new_project_view, '__all__') else 'No __all__ defined'}")
    print(f"Module dir: {dir(views.pages.new_project_view)}")

    if 'NewProjectView' in dir(views.pages.new_project_view):
        npv = views.pages.new_project_view.NewProjectView
        print(f"NPV type: {type(npv)}")
    else:
        print("NewProjectView not in module dir")
except Exception as e:
    import traceback
    print(f"Import error: {e}")
    traceback.print_exc()

try:
    print("\nTrying to import from views.pages.new_project_view.new_project_view")
    from views.pages.new_project_view.new_project_view import NewProjectView
    print("Class imported successfully")
    print(f"Class: {NewProjectView}")
except Exception as e:
    import traceback
    print(f"Import error: {e}")
    traceback.print_exc()
