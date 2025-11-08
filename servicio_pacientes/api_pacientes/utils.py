def bool_to_int(value):
    """Convierte valores booleanos/string a enteros para SQLite"""
    if isinstance(value, bool):
        return 1 if value else 0
    if isinstance(value, str):
        return 1 if value.lower() in ('true', '1', 'yes') else 0
    return int(value) if value else 0