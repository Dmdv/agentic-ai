def generate_specification(request):
    if "ambiguous" in request.lower() or "magic" in request.lower():
        raise ValueError("Invalid request")
    
    spec = "## Purpose\n"
    spec += f"Specification for: {request}\n"
    
    spec += "## Requirements\n"
    spec += "1. Detailed documentation\n"
    spec += "2. Unit tests\n"
    
    return spec
