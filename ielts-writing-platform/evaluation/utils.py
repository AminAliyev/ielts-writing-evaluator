"""Utility functions for evaluation."""

import re
from typing import List


def count_words(text: str) -> int:
    """Count words in text using IELTS-compliant word counting rules.
    
    Word counting rules:
    - Contractions count as one word (don't, it's, I've)
    - Hyphenated words count as one word (well-known, twenty-one)
    - Numbers count as one word (123, 3.14)
    - Abbreviations count as one word (etc., Dr., e.g.)
    - Possessives count as one word (student's, teacher's)
    - Only alphanumeric sequences separated by whitespace/punctuation count
    
    Args:
        text: Input text to count words from.
        
    Returns:
        Number of words in the text.
    """
    # Remove extra whitespace and normalize
    text = text.strip()
    if not text:
        return 0
    
    # Regex pattern to match words:
    # - Words with letters/apostrophes (contractions, possessives)
    # - Hyphenated words
    # - Numbers (with optional decimal points and commas)
    # - Abbreviations
    pattern = r"""
        (?:
            [a-zA-Z]+(?:'[a-zA-Z]+)*  # Words with optional apostrophes (contractions)
            |
            \d+(?:[.,]\d+)*            # Numbers with optional decimals/commas
            |
            [a-zA-Z]\.+                # Abbreviations (Dr., etc.)
        )
        (?:-[a-zA-Z]+)*               # Optional hyphenated parts
    """
    
    words: List[str] = re.findall(pattern, text, re.VERBOSE)
    return len(words)


def clean_essay_text(text: str) -> str:
    """Clean essay text for processing.
    
    Args:
        text: Raw essay text.
        
    Returns:
        Cleaned essay text with normalized whitespace.
    """
    # Normalize whitespace
    text = re.sub(r'\n\s*\n', '\n\n', text)  # Normalize multiple newlines
    text = re.sub(r'[ \t]+', ' ', text)      # Collapse multiple spaces/tabs
    text = re.sub(r'\n[ \t]+', '\n', text)   # Remove indentation
    return text.strip()
