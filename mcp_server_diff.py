import sys
import json
import os
import difflib

def apply_diff(content: str, search_block: str, replace_block: str) -> str:
    # A simple strict find-and-replace first. If it fails, fallback to line-by-line fuzzy matching.
    if search_block in content:
        return content.replace(search_block, replace_block, 1)
        
    # Normalize line endings
    content_lines = content.splitlines(keepends=True)
    search_lines = search_block.splitlines(keepends=True)
    replace_lines = replace_block.splitlines(keepends=True)
    
    # Try to find the exact block of lines ignoring leading/trailing empty lines in search_block
    # Remove empty lines at the start and end of search_lines
    start_idx = 0
    while start_idx < len(search_lines) and not search_lines[start_idx].strip():
        start_idx += 1
    end_idx = len(search_lines)
    while end_idx > start_idx and not search_lines[end_idx-1].strip():
        end_idx -= 1
        
    search_lines_core = search_lines[start_idx:end_idx]
    
    if not search_lines_core:
        raise ValueError("Search block is effectively empty.")

    # Simple sliding window search
    found_idx = -1
    for i in range(len(content_lines) - len(search_lines_core) + 1):
        match = True
        for j in range(len(search_lines_core)):
            if content_lines[i+j].strip() != search_lines_core[j].strip():
                match = False
                break
        if match:
            found_idx = i
            break
            
    if found_idx != -1:
        # We found the block! Replace it.
        # But we want to preserve the original indentation if possible.
        # For a simple implementation, we just replace the exact matched lines.
        new_content_lines = content_lines[:found_idx] + replace_lines + content_lines[found_idx + len(search_lines_core):]
        return "".join(new_content_lines)

    raise ValueError("Could not find the search block in the file. Ensure the search block exactly matches the existing code.")

def handle_list_tools():
    return {
        "tools": [
            {
                "name": "edit_file_diff",
                "description": "Surgically edit a file by providing a block of existing code to search for, and the new code to replace it with. This is heavily preferred over rewriting entire files.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Path to the file to edit."},
                        "search_block": {"type": "string", "description": "The exact block of code currently in the file that you want to replace. Provide enough context lines to uniquely identify the block."},
                        "replace_block": {"type": "string", "description": "The new block of code that will replace the search_block."}
                    },
                    "required": ["path", "search_block", "replace_block"]
                }
            }
        ]
    }

def handle_call_tool(tool_name, arguments):
    if tool_name != "edit_file_diff":
        raise ValueError(f"Unknown tool: {tool_name}")
        
    path = arguments.get("path")
    search_block = arguments.get("search_block")
    replace_block = arguments.get("replace_block")
    
    if not os.path.exists(path):
        return [{"type": "text", "text": f"Error: File '{path}' does not exist."}]
        
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        new_content = apply_diff(content, search_block, replace_block)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
        return [{"type": "text", "text": f"Successfully applied diff to {path}."}]
    except Exception as e:
        return [{"type": "text", "text": f"Error applying diff: {str(e)}"}]

def main():
    while True:
        line = sys.stdin.readline()
        if not line:
            break
            
        try:
            req = json.loads(line)
            
            if req.get("method") == "initialize":
                resp = {
                    "jsonrpc": "2.0",
                    "id": req.get("id"),
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "serverInfo": {"name": "custom-diff-server", "version": "1.0.0"}
                    }
                }
            elif req.get("method") == "tools/list":
                resp = {
                    "jsonrpc": "2.0",
                    "id": req.get("id"),
                    "result": handle_list_tools()
                }
            elif req.get("method") == "tools/call":
                params = req.get("params", {})
                tool_name = params.get("name")
                args = params.get("arguments", {})
                try:
                    content = handle_call_tool(tool_name, args)
                    resp = {
                        "jsonrpc": "2.0",
                        "id": req.get("id"),
                        "result": {"content": content}
                    }
                except Exception as e:
                    resp = {
                        "jsonrpc": "2.0",
                        "id": req.get("id"),
                        "error": {"code": -32000, "message": str(e)}
                    }
            else:
                continue
                
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
            
        except json.JSONDecodeError:
            continue

if __name__ == "__main__":
    main()
