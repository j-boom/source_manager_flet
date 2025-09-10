import subprocess
import os
from pathlib import Path

# --- Configuration ---
# The name of the directory where the exported .txt files will be saved.
EXPORT_DIRECTORY = "changed_files_export"


def get_changed_files_since_last_commit() -> list[str]:
    """
    Uses Git to get a list of all files that have changed since the last commit (HEAD).
    This includes both staged and unstaged changes.

    Returns:
        A list of file paths relative to the repository root.
        Returns an empty list if the git command fails or there are no changes.
    """
    try:
        # The `git diff` command compares the working directory against the last commit.
        # `--name-only` ensures we only get the file paths.
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            capture_output=True,
            text=True,
            check=True,  # This will raise an exception if git returns a non-zero exit code
            encoding="utf-8",
        )
        changed_files = result.stdout.strip().split("\n")
        # Filter out any empty strings that might result from the split
        return [file for file in changed_files if file]
    except FileNotFoundError:
        print("Error: 'git' command not found. Is Git installed and in your PATH?")
        return []
    except subprocess.CalledProcessError as e:
        print(f"Error executing git command: {e.stderr}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []


def export_files_to_txt(file_list: list[str], target_dir: Path):
    """
    Reads each file from the list and writes its content to a new .txt file
    in the target directory, preserving the original directory structure.

    Args:
        file_list: A list of file paths to export.
        target_dir: The Path object for the directory to save files into.
    """
    if not file_list:
        return

    exported_count = 0
    for relative_path_str in file_list:
        source_path = Path(relative_path_str)

        # Skip files that don't exist (e.g., they were deleted in the git changes)
        if not source_path.is_file():
            print(f"Skipping '{source_path}' (file not found, likely deleted).")
            continue

        # Construct the destination path, preserving the subdirectory structure
        # and appending .txt to the original filename.
        destination_path = target_dir / (relative_path_str + ".txt")

        try:
            # Ensure the parent directory for the destination file exists
            destination_path.parent.mkdir(parents=True, exist_ok=True)

            # Read the source file and write its content to the destination
            content = source_path.read_text(encoding="utf-8", errors="ignore")
            destination_path.write_text(content, encoding="utf-8")

            print(f"  - Exported '{source_path}' to '{destination_path}'")
            exported_count += 1
        except Exception as e:
            print(f"Error processing file '{source_path}': {e}")
    
    print(f"\nSuccessfully exported {exported_count} file(s).")


def main():
    """Main function to run the script."""
    print("Evaluating changed files since last commit...")
    changed_files = get_changed_files_since_last_commit()

    if not changed_files:
        print("No changed files found.")
        return

    print(f"Found {len(changed_files)} changed file(s):")
    for file in changed_files:
        print(f"  - {file}")

    target_directory = Path(EXPORT_DIRECTORY)
    target_directory.mkdir(exist_ok=True)
    print(f"\nExporting contents to '{target_directory.resolve()}'...")

    export_files_to_txt(changed_files, target_directory)


if __name__ == "__main__":
    main()
