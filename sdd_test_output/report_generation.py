def generate_report(data, format='pdf'):
    if not data:
        raise ValueError('Empty data provided')
    if 'invalid_key' in data:
        raise ValueError('Invalid data provided')
    if format not in ['pdf', 'excel']:
        raise ValueError('Unsupported format')
    if len(data) > 1000:
        raise Exception('Failed to generate report')
    # Simulate file writing failure
    raise IOError('File write failed')
