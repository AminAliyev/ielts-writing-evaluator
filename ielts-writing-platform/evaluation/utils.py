"""Utility functions for evaluation."""

import re
from typing import List


def count_words(text: str) -> int:
    """
    Count words in text using IELTS-compliant rules.
    
    Counts tokens where contractions, hyphenated words, numbers, abbreviations, and possessives are each treated as a single word (e.g., don't, well-known, 3.14, Dr., student's).
    
    Parameters:
        text (str): Input text to count.
    
    Returns:
        int: Number of words found.
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
    """
    Normalize and clean essay text by collapsing excessive whitespace and trimming edges.
    
    Parameters:
        text (str): Raw essay text to normalize.
    
    Returns:
        str: Cleaned essay text with condensed spaces/tabs, normalized newlines (maximum two consecutive), removed indentation after newlines, and trimmed leading/trailing whitespace.
    """
    # Normalize whitespace
    text = re.sub(r'\n\s*\n', '\n\n', text)  # Normalize multiple newlines
    text = re.sub(r'[ \t]+', ' ', text)      # Collapse multiple spaces/tabs
    text = re.sub(r'\n[ \t]+', '\n', text)   # Remove indentation
    return text.strip()