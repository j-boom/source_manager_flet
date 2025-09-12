"""
Export Project as Text Files

This script walks the entire project directory and creates a mirrored
directory structure in an 'export' folder. It converts every file into a
.txt file, which is useful for transferring source code to systems with
strict file type restrictions.
"""

import os
from pathlib import Path
import shutil

# --- Configuration ---
# The name of the directory where the exported .txt files will be saved.
EXPORT_DIR_NAME = "project_export_txt"

# Directories to exclude from the export.
# This prevents copying virtual environments, git history, caches, etc.
EXCLUDE_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "env",
    "node_modules",
    "build",
    "dist",
    ".vscode",
    "logs",
    EXPORT_DIR_NAME,  # Exclude the export directory itself
}

# Specific files to exclude from the export.
EXCLUDE_FILES = {
    ".DS_Store",
    "migration.log",
}


def export_project(project_root: Path, target_dir: Path):
    """
    Walks the project directory, mirroring its structure and converting all
    files to .txt format in the target directory.

    Args:
        project_root: The root path of the project to export.
        target_dir: The destination directory for the exported .txt files.
    """
    exported_count = 0
    skipped_count = 0

    for source_path in project_root.rglob("*"):
        # Create a path relative to the project root to check for exclusions
        try:
            relative_path = source_path.relative_to(project_root)
        except ValueError:
            continue  # Should not happen with rglob

        # --- Exclusion Checks ---
        # 1. Check if any parent directory is in the exclusion list
        if any(part in EXCLUDE_DIRS for part in relative_path.parts):
            continue

        # 2. Check if the item is a file
        if not source_path.is_file():
            continue

        # 3. Check if the file itself is in the exclusion list
        if source_path.name in EXCLUDE_FILES:
            continue

        # --- File Processing ---
        # Construct the destination path, preserving the subdirectory structure
        # and appending .txt to the original filename.
        destination_path = target_dir / (str(relative_path) + ".txt")

        try:
            # Ensure the parent directory for the destination file exists
            destination_path.parent.mkdir(parents=True, exist_ok=True)

            # Read the source file and write its content to the destination
            # Using 'ignore' for errors to handle potential binary files gracefully
            content = source_path.read_text(encoding="utf-8", errors="ignore")
            destination_path.write_text(content, encoding="utf-8")

            print(f"  - Exported '{relative_path}'")
            exported_count += 1
        except Exception as e:
            print(f"  - SKIPPED '{relative_path}' due to error: {e}")
            skipped_count += 1

    print("\n" + "=" * 50)
    print("Export Complete")
    print(f"  - Successfully exported: {exported_count} file(s)")
    print(f"  - Skipped: {skipped_count} file(s)")
    print(f"  - Output directory: {target_dir.resolve()}")
    print("=" * 50)


def main():
    """Main function to run the script."""
    project_root = Path(__file__).parent.parent
    target_directory = project_root / EXPORT_DIR_NAME

    print(f"Starting export of project: {project_root.resolve()}")
    print(f"Target directory: {target_directory.resolve()}")

    if target_directory.exists():
        response = input(f"\nDirectory '{EXPORT_DIR_NAME}' already exists. Overwrite? (y/n): ").lower()
        if response != 'y':
            print("Export cancelled by user.")
            return
        print("Removing existing export directory...")
        shutil.rmtree(target_directory)

    target_directory.mkdir(exist_ok=True)
    print("\nProcessing files...")

    export_project(project_root, target_directory)


if __name__ == "__main__":
    main()

