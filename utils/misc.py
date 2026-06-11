import re


def out_test(r, n):
    print(n, "<think>", r["reasoning_content"], "</think>\n\n", r["content"]) if "reasoning_content" in r else print(
        n, r["content"]
    )


def remove_leading_empty_line(d: dict) -> dict:
    lines = d["content"].splitlines(keepends=True)
    start_index = 0
    for line in lines:
        if line.strip():
            break
        start_index += 1
    d["content"] = "".join(lines[start_index:])
    return d


def process_reasoning_content(data_dict):
    if "content" in data_dict and isinstance(data_dict["content"], str):
        content = data_dict["content"]

        think_pattern = r"<think>(.*?)</think>"
        match = re.search(think_pattern, content, re.DOTALL)

        if not match:
            return data_dict

        reasoning_content = match.group(1) if match else ""
        data_dict["reasoning_content"] = reasoning_content

        data_dict["content"] = re.sub(think_pattern, "", content, count=1, flags=re.DOTALL)

    return data_dict
