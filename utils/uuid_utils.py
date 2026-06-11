import secrets


def fixed_length_uuid(length):
    if length < 1:
        raise ValueError("长度必须大于0")

    num_bytes = (length + 1) // 2
    random_bytes = secrets.token_bytes(num_bytes)
    hex_str = random_bytes.hex()

    if length % 2 == 1:
        last_char = format(random_bytes[-1] >> 4, "x")
        return hex_str[: length - 1] + last_char

    return hex_str[:length]
