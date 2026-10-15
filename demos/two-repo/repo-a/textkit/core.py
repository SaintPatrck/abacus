"""textkit: tiny text helpers shared across demo repositories."""


def slugify(text):
    """Lowercase, keep alphanumerics, join words with hyphens."""
    words = "".join(c.lower() if c.isalnum() else " " for c in text).split()
    return "-".join(words)
