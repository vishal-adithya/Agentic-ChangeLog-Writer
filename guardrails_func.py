def sanitize_commit(message,guard):
    try:
        guard.validate(message)
        return message
    except Exception:
        return "[FLAGGED CONTENT REMOVED]"


