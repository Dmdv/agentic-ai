import os
from tree_sitter import Language, Parser
import tree_sitter_python

# Initialize the parser with the Python language
PYTHON_LANGUAGE = Language(tree_sitter_python.language())
parser = Parser(PYTHON_LANGUAGE)

def get_file_skeleton(filepath):
    """
    Parses a Python file and returns a skeleton map containing only 
    class definitions, method signatures, and function signatures.
    """
    try:
        with open(filepath, 'rb') as f:
            source_code = f.read()
    except Exception as e:
        return f"Error reading {filepath}: {e}"

    tree = parser.parse(source_code)
    root_node = tree.root_node

    skeleton_lines = []

    def traverse(node, depth=0):
        indent = "    " * depth
        
        # Capture Classes
        if node.type == 'class_definition':
            name_node = node.child_by_field_name('name')
            if name_node:
                name = source_code[name_node.start_byte:name_node.end_byte].decode('utf8')
                skeleton_lines.append(f"{indent}class {name}:")
                
                # Recursively parse the body of the class for methods
                body_node = node.child_by_field_name('body')
                if body_node:
                    for child in body_node.children:
                        traverse(child, depth + 1)
                        
        # Capture Functions/Methods
        elif node.type == 'function_definition':
            name_node = node.child_by_field_name('name')
            params_node = node.child_by_field_name('parameters')
            
            if name_node and params_node:
                name = source_code[name_node.start_byte:name_node.end_byte].decode('utf8')
                params = source_code[params_node.start_byte:params_node.end_byte].decode('utf8')
                skeleton_lines.append(f"{indent}def {name}{params}: ...")
                
    # Start traversing from the top of the file
    for child in root_node.children:
        traverse(child)
        
    return "\n".join(skeleton_lines)

def generate_repo_map(directory="."):
    """Generates a skeleton map of the entire repository."""
    repo_map = []
    
    for root, dirs, files in os.walk(directory):
        # Exclude hidden directories (like .git, .venv), but allow the root "."
        if root != ".":
            parts = root.split(os.sep)
            if any(part.startswith('.') and part != '.' for part in parts) or 'venv' in root or '__pycache__' in root:
                continue
            
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, directory)
                
                repo_map.append(f"### {rel_path} ###")
                skeleton = get_file_skeleton(filepath)
                if skeleton:
                    repo_map.append(skeleton)
                else:
                    repo_map.append("  (No classes or functions defined)")
                repo_map.append("") # Empty line for spacing
                
    return "\n".join(repo_map)

if __name__ == "__main__":
    print("Generating Repository Skeleton Map...")
    full_map = generate_repo_map()
    
    with open(".repo_map", "w") as f:
        f.write(full_map)
        
    print("Successfully generated .repo_map")
    print("-" * 40)
    print(full_map)
