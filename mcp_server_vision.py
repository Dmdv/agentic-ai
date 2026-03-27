import sys
import json
import asyncio
from mlx_vlm import load, generate

# A custom Vision MCP Server using Apple MLX and a VLM (Vision Language Model)
# This enables Multimodal Validation (e.g. comparing UI screenshots to specs)

class VisionServer:
    def __init__(self, model_name="mlx-community/Qwen2.5-VL-7B-Instruct-4bit"):
        self.model_name = model_name
        self.model = None
        self.processor = None
        
    def _load(self):
        if self.model is None:
            self.model, self.processor = load(self.model_name)
            
    def analyze_image(self, image_path: str, prompt: str) -> str:
        self._load()
        
        # Format specifically for Qwen2.5-VL via mlx_vlm
        # mlx_vlm handles the image preprocessing
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "url": image_path},
                    {"type": "text", "text": prompt}
                ]
            }
        ]
        
        try:
            prompt_text = self.processor.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            
            output = generate(
                self.model,
                self.processor,
                prompt_text,
                max_tokens=1000,
                verbose=False
            )
            
            return output
        except Exception as e:
            raise Exception(f'Error processing image: {str(e)}')

vision_server = VisionServer()

def handle_list_tools():
    return {
        "tools": [
            {
                "name": "vision_analyze",
                "description": "Analyze an image (like a UI screenshot) using a Vision Language Model. Useful for visual QA, UI validation against Figma specs, or debugging rendering issues.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "image_path": {"type": "string", "description": "Local path or URL to the image."},
                        "prompt": {"type": "string", "description": "What to look for or validate in the image. e.g. 'Does this UI match a login screen with a blue button?"}
                    },
                    "required": ["image_path", "prompt"]
                }
            }
        ]
    }

def handle_call_tool(tool_name, arguments):
    if tool_name != "vision_analyze":
        raise ValueError(f"Unknown tool: {tool_name}")
        
    image_path = arguments.get("image_path")
    prompt = arguments.get("prompt")
    
    try:
        analysis = vision_server.analyze_image(image_path, prompt)
        return [{"type": "text", "text": analysis}]
    except Exception as e:
        return [{"type": "text", "text": f"Error running Vision Model: {str(e)}"}]

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
                        "serverInfo": {"name": "custom-vision-server", "version": "1.0.0"}
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
