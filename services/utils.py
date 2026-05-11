import re

def sanitize_input(text):
    """
    🔐 Remove HTML tags and basic injection patterns
    """
    text = re.sub(r"<.*?>", "", text)  # remove HTML
    return text.strip().lower()