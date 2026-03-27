import os

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)
        return f'Directory {path} created successfully.'
    else:
        return f'Directory {path} already exists.'