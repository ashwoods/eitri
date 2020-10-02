import yaml

def load_yaml(filename, encoding=None, binary=True):
    try:
        with open(filename, 'rb' if binary else 'r', encoding=encoding) as fh:
            return yaml.safe_load(fh)
    except (OSError, yaml.YAMLError, UnicodeDecodeError) as e:
        if encoding is None:
            # Sometimes the user's locale sets an encoding that doesn't match
            # the YAML files. Im such cases, retry once with the "default"
            # UTF-8 encoding
            return load_yaml(filename, encoding='utf-8-sig', binary=False)