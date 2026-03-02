import os

def rename_content_in_files(directory):
    for root, dirs, files in os.walk(directory):
        if '.git' in root or 'pre-commit-venv' in root or '__pycache__' in root or '.pytest_cache' in root:
            continue
            
        for file in files:
            if not (file.endswith('.py') or file.endswith('.md') or file.endswith('.toml')):
                continue
                
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                new_content = content.replace('axios_python', 'axios_python') \
                                     .replace('axios_python', 'axios_python') \
                                     .replace('AxiosPython', 'AxiosPython') \
                                     .replace('AxiosPython', 'AxiosPython')
                
                if file == 'pyproject.toml':
                    new_content = new_content.replace('name = "axios_python"', 'name = "axios-python"')
                
                if new_content != content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Updated: {file_path}")
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

if __name__ == '__main__':
    project_root = '/home/avijit/Desktop/Projects/pyxios'
    
    print("Replacing contents...")
    rename_content_in_files(project_root)
    
    old_dir = os.path.join(project_root, 'axios_python')
    new_dir = os.path.join(project_root, 'axios_python')
    
    if os.path.exists(old_dir):
        print(f"Renaming directory {old_dir} to {new_dir}")
        os.rename(old_dir, new_dir)
        
    print("Renaming completed successfully.")
