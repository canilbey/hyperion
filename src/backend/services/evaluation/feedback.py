def save_feedback(user_id, query, response, feedback):
    """
    Kullanıcıdan gelen feedback'i kaydet.
    """
    entry = {
        "user_id": user_id,
        "query": query,
        "response": response,
        "feedback": feedback
    }
    # ... feedback kaydetme işlemi ...
    return entry 