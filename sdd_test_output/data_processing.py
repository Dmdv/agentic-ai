def process_data(data):
    if not isinstance(data, dict):
        raise TypeError("Data must be a dictionary")
    if not data:
        raise ValueError("Data cannot be empty")
    required_fields = {'name', 'age'}
    if not required_fields.issubset(data):
        raise KeyError(f"Missing required fields: {required_fields - set(data.keys())}")
    if not isinstance(data['age'], int):
        raise ValueError("Age must be an integer")
    if data['age'] < 0:
        raise ValueError("Age cannot be negative")
    return data
