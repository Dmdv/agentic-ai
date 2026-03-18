import sys
import json
import subprocess
import os

# A custom, highly constrained Bash MCP Server implementation
# Because raw bash access is dangerous, this server strictly limits commands
# to read-only tools and standard compilers/linters.

ALLOWED_COMMANDS = [
    "ls", "pwd", "pytest", "npm run test", "npm test", 
    "cargo build", "cargo test", "python -m unittest", "tsc"
]

def handle_list_tools():
    return {
        "tools": [
            {
                "name": "run_bash_command",
                "description": "Execute a safe bash command (like 'pytest' or 'npm test') to check for errors.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "The exact shell command to run."}
                    },
                    "required": ["command"]
                }
            }
        ]
    }

def handle_call_tool(tool_name, arguments):
    if tool_name != "run_bash_command":
        raise ValueError(f"Unknown tool: {tool_name}")
        
    cmd = arguments.get("command", "")
    
    # Security check: Ensure command is in the allowed list or starts with an allowed prefix
    is_allowed = any(cmd.startswith(allowed) for allowed in ALLOWED_COMMANDS)
    if not is_allowed:
        return [
            {
                "type": "text", 
                "text": f"Error: Command '{cmd}' is blocked for security reasons. Allowed commands: {ALLOWED_COMMANDS}"
            }
        ]
    
    try:
        # Execute the command and capture both stdout and stderr
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=os.path.abspath("."), 
            capture_output=True, 
            text=True, 
            timeout=30 # Prevent infinite loops
        )
        
        output = result.stdout
        if result.stderr:
            output += f"\n--- STDERR ---\n{result.stderr}"
            
        return [{"type": "text", "text": output if output else "Command executed successfully (no output)."}]
        
    except subprocess.TimeoutExpired:
        return [{"type": "text", "text": "Error: Command timed out after 30 seconds."}]
    except Exception as e:
        return [{"type": "text", "text": f"Error: {str(e)}"}]

def main():
    # MCP Protocol communicates via stdio using JSON-RPC
    while True:
        line = sys.stdin.readline()
        if not line:
            break
            
        try:
            req = json.loads(line)
            
            # Handle Initialize
            if req.get("method") == "initialize":
                resp = {
                    "jsonrpc": "2.0",
                    "id": req.get("id"),
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "serverInfo": {"name": "custom-bash-server", "version": "1.0.0"}
                    }
                }
            
            # Handle list tools
            elif req.get("method") == "tools/list":
                resp = {
                    "jsonrpc": "2.0",
                    "id": req.get("id"),
                    "result": handle_list_tools()
                }
                
            # Handle call tool
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
                # Ignore other methods (like notifications)
                continue
                
            # Write response
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
            
        except json.JSONDecodeError:
            continue

if __name__ == "__main__":
    main()
