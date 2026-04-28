def unwrap(value):
    if isinstance(value, list):
        return value[0] if value else None
    return value

def is_empty(value):
    if value is None:
        return True
    if isinstance(value, bool):
        return False
    if isinstance(value, str) and value.strip() == "":
        return True
    return not value and not isinstance(value, (int, float))