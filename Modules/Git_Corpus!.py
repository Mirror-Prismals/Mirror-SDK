import os
import subprocess
import shutil
import tempfile

def clone_repository(repo_url):
    """Clone the GitHub repository into a temporary directory."""
    try:
        temp_dir = tempfile.mkdtemp(prefix="Mirror-SDK-")
        subprocess.run(['git', 'clone', repo_url, temp_dir], check=True)
        print(f"Repository cloned to {temp_dir}")
        return temp_dir
    except subprocess.CalledProcessError as e:
        print(f"Error cloning repository: {e}")
        return None

def save_python_files_to_text(directory, output_file):
    """Extract all .py files from the directory and save their contents to a .txt file."""
    with open(output_file, 'w', encoding='utf-8') as out_file:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):  # Only process .py files
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as py_file:
                            content = py_file.read()
                            out_file.write(f"# START OF FILE: {file}\n")
                            out_file.write(content)
                            out_file.write("\n# END OF FILE\n\n")
                    except Exception as e:
                        print(f"Error reading file {file_path}: {e}")

if __name__ == "__main__":
    repo_url = "https://github.com/Mirror-Prismals/Mirror-SDK"
    output_file = "repository_python_files.txt"

    # Clone the repository into a temporary directory
    clone_dir = clone_repository(repo_url)
    if clone_dir:
        try:
            # Extract .py files and save to the output file
            save_python_files_to_text(clone_dir, output_file)
            print(f"Python files from the repository saved to {output_file}")
        finally:
            # Clean up the temporary directory
            try:
                shutil.rmtree(clone_dir)
                print(f"Removed temporary directory at {clone_dir}")
            except Exception as e:
                print(f"Error removing temporary directory {clone_dir}: {e}")
