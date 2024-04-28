
import os
import time
import re

def is_valid_filename(text):
    pattern = r'^\.cache/[a-zA-Z0-9_]+\.[a-zA-Z0-9]+$'
    if re.match(pattern, text) and os.path.isfile(text):
        print(f"File available in cache {text} .")
        return True
    else:
        return False

def create_temp_file(extension='.tmp'):
    temp_dir = ".cache"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)    
    unique_filename = f"tempfile_{int(time.time())}{extension}"
    temp_file = os.path.join(temp_dir, unique_filename)
    return temp_file