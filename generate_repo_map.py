import os
import re
from tree_sitter import Language, Parser
import tree_sitter_python
import tree_sitter_javascript
import tree_sitter_typescript
import tree_sitter_rust
import tree_sitter_go
import tree_sitter_dockerfile
import tree_sitter_yaml
import tree_sitter_toml
import tree_sitter_bash
import tree_sitter_make

# Initialize parsers for multiple languages
LANGUAGES = {
    ".py": Language(tree_sitter_python.language()),
    ".js": Language(tree_sitter_javascript.language()),
    ".ts": Language(tree_sitter_typescript.language_typescript()),
    ".tsx": Language(tree_sitter_typescript.language_tsx()),
    ".rs": Language(tree_sitter_rust.language()),
    ".go": Language(tree_sitter_go.language()),
    ".sh": Language(tree_sitter_bash.language()),
    "Dockerfile": Language(tree_sitter_dockerfile.language()),
    "Makefile": Language(tree_sitter_make.language()),
    ".yaml": Language(tree_sitter_yaml.language()),
    ".yml": Language(tree_sitter_yaml.language()),
    ".toml": Language(tree_sitter_toml.language()),
}

def get_fallback_skeleton(filepath, ext, source_code):
    """Fallback Regex parsing for languages without easy Tree-Sitter pip packages (e.g., Terraform)."""
    skeleton_lines = []
    lines = source_code.decode('utf-8', errors='ignore').split('\n')
    
    if ext == ".tf":
        for line in lines:
            if re.match(r'^(resource|data|module|variable|output|provider)\s+', line):
                skeleton_lines.append(f"{line.strip().replace('{', '').strip()}")
                
    return "\n".join(skeleton_lines)

def get_file_skeleton(filepath, file_name, ext):
    """
    Parses a file and returns a skeleton map.
    """
    try:
        with open(filepath, 'rb') as f:
            source_code = f.read()
    except Exception as e:
        return f"Error reading {filepath}: {e}"

    # Handle Terraform fallback
    if ext == ".tf":
        return get_fallback_skeleton(filepath, ext, source_code)

    # Determine Tree-Sitter language (match by extension or exact filename)
    lang = LANGUAGES.get(ext) or LANGUAGES.get(file_name)
    if not lang:
        return None

    parser = Parser(lang)
    tree = parser.parse(source_code)
    root_node = tree.root_node

    skeleton_lines = []

    def traverse(node, depth=0):
        indent = "    " * depth
        
        # --- Programming Languages ---
        if node.type in ['class_definition', 'class_declaration', 'struct_item', 'type_spec']:
            name_node = node.child_by_field_name('name') or node.child_by_field_name('type')
            if name_node:
                name = source_code[name_node.start_byte:name_node.end_byte].decode('utf8')
                type_label = "class" if "class" in node.type else "struct/type"
                skeleton_lines.append(f"{indent}{type_label} {name}:")
                
                body_node = node.child_by_field_name('body') or node.child_by_field_name('declaration_list')
                if body_node:
                    for child in body_node.children:
                        traverse(child, depth + 1)
                        
        elif node.type in ['function_definition', 'function_declaration', 'method_definition', 'function_item']:
            name_node = node.child_by_field_name('name')
            params_node = node.child_by_field_name('parameters')
            if name_node:
                name = source_code[name_node.start_byte:name_node.end_byte].decode('utf8')
                params = ""
                if params_node:
                    params = source_code[params_node.start_byte:params_node.end_byte].decode('utf8')
                skeleton_lines.append(f"{indent}def {name}{params}: ...")
                
        # --- DevOps & Config Languages ---
        # Dockerfile (Extract Stages/FROM)
        elif node.type == 'from_instruction':
            image = source_code[node.start_byte:node.end_byte].decode('utf8').replace("FROM ", "").strip()
            skeleton_lines.append(f"FROM {image}")
            
        # Makefile (Extract Targets)
        elif node.type == 'rule':
            target_node = node.child_by_field_name('target')
            if target_node:
                target = source_code[target_node.start_byte:target_node.end_byte].decode('utf8')
                skeleton_lines.append(f"Target: {target}")

        # YAML (Extract Root Keys)
        elif node.type == 'block_mapping_pair' and depth == 0:
            key_node = node.child_by_field_name('key')
            if key_node:
                key = source_code[key_node.start_byte:key_node.end_byte].decode('utf8')
                skeleton_lines.append(f"Key: {key}: ...")
                
        # TOML (Extract Tables)
        elif node.type == 'table':
            skeleton_lines.append(source_code[node.start_byte:node.end_byte].decode('utf8'))

        # Continue traversing if not a matched block
        if node.type not in ['block_mapping_pair']: # Stop deep YAML parsing
            for child in node.children:
                traverse(child, depth)

    for child in root_node.children:
        traverse(child)
        
    return "\n".join(skeleton_lines)

def generate_repo_map(directory="."):
    """Generates a skeleton map of the entire repository."""
    repo_map = []
    
    for root, dirs, files in os.walk(directory):
        if root != ".":
            parts = root.split(os.sep)
            if any(part.startswith('.') and part != '.' for part in parts) or 'venv' in root or '__pycache__' in root or 'node_modules' in root:
                continue
            
        for file in files:
            ext = os.path.splitext(file)[1]
            # Process if it matches an extension or an exact filename (like Dockerfile)
            if ext in LANGUAGES or file in LANGUAGES or ext == ".tf":
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, directory)
                
                repo_map.append(f"### {rel_path} ###")
                skeleton = get_file_skeleton(filepath, file, ext)
                if skeleton:
                    repo_map.append(skeleton)
                else:
                    repo_map.append("  (No relevant structure defined)")
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
