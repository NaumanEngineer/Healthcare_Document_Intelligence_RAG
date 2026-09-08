import re
import unicodedata


def normalize_unicode(text: str) -> str:
    """
    Normalize Unicode while preserving semantic content.
    """
    return unicodedata.normalize("NFKC", text)


def remove_control_characters(text: str) -> str:
    """
    Remove non-printable control characters while preserving
    common whitespace characters such as newline and tab.
    """
    return "".join(
        char
        for char in text
        if char in "\n\t" or unicodedata.category(char)[0] != "C"
    )


def normalize_whitespace(text: str) -> str:
    """
    Reduce formatting noise without collapsing paragraph boundaries.
    """
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def clean_text(text: str) -> str:
    """
    Apply the complete text-cleaning pipeline.
    """
    if not text:
        return ""

    text = normalize_unicode(text)
    text = remove_control_characters(text)
    text = normalize_whitespace(text)

    return text


def cleaning_summary(raw_text: str, cleaned_text: str) -> dict:
    """
    Return simple QA statistics for a cleaning operation.
    """
    return {
        "raw_character_count": len(raw_text),
        "clean_character_count": len(cleaned_text),
        "characters_removed": len(raw_text) - len(cleaned_text),
    }

