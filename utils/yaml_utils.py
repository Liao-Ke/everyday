import os
from io import StringIO

from ruamel.yaml import YAML


def convert_path(path):
    return path.replace("./story", "")


def modify_frontmatter(file_path, key_path, new_value):
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.width = 120
    yaml.indent(mapping=2, sequence=4, offset=2)

    with open(file_path, encoding="utf-8") as f:
        content = f.read().splitlines()

    start_idx = None
    end_idx = None
    for i, line in enumerate(content):
        if line.strip() == "---":
            if start_idx is None:
                start_idx = i
            else:
                end_idx = i
                break

    if start_idx is None or end_idx is None:
        raise ValueError("未找到有效的YAML front matter")

    yaml_content = "\n".join(content[start_idx + 1 : end_idx])
    data = yaml.load(yaml_content)

    keys = key_path.split(".")
    current = data
    for key in keys[:-1]:
        if key.isdigit() and isinstance(current, list):
            key = int(key)
        current = current[key]

    last_key = keys[-1]
    if last_key.isdigit() and isinstance(current, list):
        last_key = int(last_key)
    current[last_key] = new_value

    stream = StringIO()
    yaml.dump(data, stream)
    stream.seek(0)
    updated_yaml = stream.getvalue().splitlines()

    new_content = content[:start_idx] + ["---"] + updated_yaml + ["---"] + content[end_idx + 1 :]

    temp_path = file_path + ".tmp"
    with open(temp_path, "w", encoding="utf-8") as f:
        f.write("\n".join(new_content))

    os.replace(temp_path, file_path)
