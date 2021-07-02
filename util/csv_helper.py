import re

def list_from_string(str):
    sanitized_str = re.sub("\]|\[|\'", '', str)
    return list(map(lambda x: x.strip(), sanitized_str.split(',')))