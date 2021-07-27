import re

def list_from_string(str):
    sanitized_str = re.sub("\]|\[|\'", '', str)
    return list(map(lambda x: x.strip(), sanitized_str.split(',')))

# https://stackoverflow.com/questions/250357/truncate-a-string-without-ending-in-the-middle-of-a-word
def smart_truncate(content, length=100, suffix='...'):
    if len(content) > length:
        content = content[:length].rsplit(' ', 1)[0]
        content = content.rstrip(',')
        content = content.rstrip(';')
        content += suffix
    return content