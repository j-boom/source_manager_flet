import sys
sys.path.insert(0, str(sys.path[0] + '/src'))
print("Python path:", sys.path)

try:
    from views.pages.new_project_view.new_project_view import NewProjectView
    print("Direct import from file works")
except Exception as e:
    print(f"Direct import error: {e}")

