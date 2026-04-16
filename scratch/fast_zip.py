import zipfile
import os

def fast_zip():
    zip_name = "project_clean.zip"
    # Files and directories to include
    include = [
        "backend",
        "deploy",
        "docker-compose.yml"
    ]
    # Directories/Extensions to exclude
    exclude_dirs = {"venv", "__pycache__", ".git", ".pytest_cache", "findix_app", "scratch"}
    exclude_exts = {".pyc", ".log", ".db"}

    print(f"Creating {zip_name}...")
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for item in include:
            if os.path.isfile(item):
                zipf.write(item)
                print(f"  Added: {item}")
            elif os.path.isdir(item):
                for root, dirs, files in os.walk(item):
                    # Filter directories
                    dirs[:] = [d for d in dirs if d not in exclude_dirs]
                    
                    for file in files:
                        if any(file.endswith(ext) for ext in exclude_exts):
                            continue
                        
                        file_path = os.path.join(root, file)
                        # Relative path for zip
                        arcname = os.path.relpath(file_path, os.getcwd())
                        zipf.write(file_path, arcname)
                print(f"  Added directory: {item}")

    print("ZIP READY!")

if __name__ == "__main__":
    fast_zip()
