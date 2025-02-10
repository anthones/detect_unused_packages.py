#!/usr/bin/env python3
import os
import json
import sys

def get_project_root():
    project_root = os.path.abspath(os.path.dirname(__file__))
    return project_root

def load_package_json(project_root):
    package_json_path = os.path.join(project_root, 'package.json')
    try:
        with open(package_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading {package_json_path}: {e}", file=sys.stderr)
        sys.exit(1)
    return data

def collect_dependencies(package_json):
    deps = package_json.get('dependencies', {})
    dev_deps = package_json.get('devDependencies', {})
    # Return a set of package names
    return set(list(deps.keys()) + list(dev_deps.keys()))

def search_for_package_in_file(package, file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            if package in content:
                return True
    except Exception:
        pass
    return False

def main():
    project_root = get_project_root()
    package_json = load_package_json(project_root)
    packages = collect_dependencies(package_json)
    
    found = {pkg: False for pkg in packages}

    for root, dirs, files in os.walk(project_root):
        # Exclude directories we don't want to search
        if 'node_modules' in dirs:
            dirs.remove('node_modules')
        if 'bin' in dirs:
            dirs.remove('bin')
        for filename in files:
            file_path = os.path.join(root, filename)
            # For each file, check every package that hasn't been found yet.
            for pkg in list(found.keys()):
                if not found[pkg] and search_for_package_in_file(pkg, file_path):
                    found[pkg] = True
    
    unused = [pkg for pkg, was_found in found.items() if not was_found]
    for pkg in unused:
        print(pkg)

if __name__ == '__main__':
    main()
