FORBIDDEN_KEYWORDS = [
    "drop",
    "delete",
    "update",
    "insert",
    "alter",
    "truncate",
    "grant"
]

def validate_sql(sql_query: str):

    sql = sql_query.lower().strip()

    if not sql.startswith("select"):
        return False

    for keyword in FORBIDDEN_KEYWORDS:
        if keyword in sql:
            return False

    return True