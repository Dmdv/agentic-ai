import argparse
import time
import gc
from mlx_lm import load, generate

def run_test(model_name: str, prompt: str):
    print(f"Loading model: {model_name}...")
    print("This may take some time on the first run as it downloads the weights from HuggingFace.")
    
    start_load = time.time()
    # Load model and tokenizer. MLX automatically uses unified memory.
    model, tokenizer = load(model_name)
    load_time = time.time() - start_load
    print(f"Model loaded in {load_time:.2f} seconds.")
    
    print("\nGenerating response...")
    start_gen = time.time()
    
    # Generate the response
    response = generate(
        model, 
        tokenizer, 
        prompt=prompt, 
        max_tokens=500,
        verbose=True # MLX-LM will print tokens as they are generated
    )
    
    gen_time = time.time() - start_gen
    print(f"\nGeneration complete in {gen_time:.2f} seconds.")
    
    # Demonstrate zero-overhead memory clearing
    print("\nUnloading model to free Unified Memory...")
    del model
    del tokenizer
    gc.collect()
    print("Memory freed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Apple MLX with Qwen/Kimi models.")
    # Defaulting to a very capable but manageable 32B model for testing. 
    # You can pass the 80B Qwen3 or 1T Kimi models here once you are ready for the massive downloads.
    parser.add_argument("--model", type=str, default="mlx-community/Qwen3-235B-8bit",
                        help="HuggingFace model ID (must be an MLX format model).")
    parser.add_argument("--prompt", type=str, default="Write a Python function to compute the Fibonacci sequence, and explain its time complexity.",
                        help="The prompt to send to the model.")
    
    args = parser.parse_args()
    
    run_test(args.model, args.prompt)
