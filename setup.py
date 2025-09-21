#!/usr/bin/env python3
import os
import shutil

def create_project_structure():
    """Create the improved project structure."""
    directories = [
        'src',
        'src/config',
        'src/routes',
        'src/services',
        'src/models',
        'src/utils',
        'src/exceptions',
        'tests'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        # Create __init__.py in each directory
        init_file = os.path.join(directory, '__init__.py')
        with open(init_file, 'w') as f:
            f.write('')
    
    print("Project structure created successfully!")
    
    # Copy environment example if .env exists
    if os.path.exists('.env') and not os.path.exists('.env.example'):
        shutil.copy('.env', '.env.example')
        print("Created .env.example file")

if __name__ == "__main__":
    create_project_structure()