"""Tests for evaluation utility functions."""

from evaluation.utils import count_words, clean_essay_text


def test_count_words_basic():
    """Test basic word counting."""
    assert count_words("hello world") == 2
    assert count_words("The quick brown fox") == 4
    assert count_words("") == 0
    assert count_words("   ") == 0


def test_count_words_contractions():
    """Test word counting with contractions."""
    # Contractions should count as one word
    assert count_words("don't") == 1
    assert count_words("I've") == 1
    assert count_words("it's") == 1
    assert count_words("they're") == 1
    assert count_words("can't") == 1
    assert count_words("won't") == 1
    assert count_words("shouldn't") == 1
    assert count_words("don't know") == 2


def test_count_words_possessives():
    """Test word counting with possessives."""
    # Possessives should count as one word
    assert count_words("student's") == 1
    assert count_words("teacher's") == 1
    assert count_words("John's") == 1
    assert count_words("student's work") == 2


def test_count_words_hyphenated():
    """Test word counting with hyphenated words."""
    # Hyphenated words should count as one word
    assert count_words("well-known") == 1
    assert count_words("twenty-one") == 1
    assert count_words("mother-in-law") == 1
    assert count_words("state-of-the-art") == 1
    assert count_words("well-known fact") == 2


def test_count_words_numbers():
    """Test word counting with numbers."""
    # Numbers should count as words
    assert count_words("123") == 1
    assert count_words("3.14") == 1
    assert count_words("1,000,000") == 1
    assert count_words("2023") == 1
    assert count_words("I have 5 apples") == 4


def test_count_words_abbreviations():
    """Test word counting with abbreviations."""
    # Abbreviations should count as words
    assert count_words("Dr. Smith") == 2
    assert count_words("etc.") == 1
    assert count_words("e.g.") == 1
    assert count_words("U.S.A.") == 1


def test_count_words_punctuation():
    """Test word counting with various punctuation."""
    # Punctuation should not affect word count
    assert count_words("Hello, world!") == 2
    assert count_words("What?") == 1
    assert count_words("Yes... maybe.") == 2
    assert count_words("(parenthetical)") == 1
    assert count_words("[bracketed]") == 1
    assert count_words("{curly}") == 1


def test_count_words_complex():
    """Test word counting with complex sentences."""
    # Complex example from IELTS
    text = "The quick brown fox jumps over the lazy dog."
    assert count_words(text) == 9
    
    # Example with contractions and numbers
    text = "I've studied for 10 years, but I can't learn Vietnamese."
    assert count_words(text) == 11
    
    # Example with possessives
    text = "It's the teacher's job to help students."
    assert count_words(text) == 7
    
    # Real IELTS-style text
    text = "The 21st century presents well-known challenges. We can't ignore them."
    assert count_words(text) == 11


def test_count_words_whitespace_variations():
    """Test word counting with different whitespace."""
    assert count_words("hello  world") == 2  # Double space
    assert count_words("  hello  ") == 1  # Leading/trailing spaces
    assert count_words("hello\nworld") == 2  # Newline
    assert count_words("hello\t world") == 2  # Tab and space
    assert count_words("hello\n\nworld") == 2  # Multiple newlines


def test_clean_essay_text():
    """
    Verifies clean_essay_text normalizes and trims essay-style text.
    
    Checks that the function:
    - Collapses runs of consecutive newlines (no occurrences of three or more consecutive newline characters).
    - Collapses multiple spaces into a single space.
    - Removes leading indentation at the start of lines.
    - Trims leading and trailing whitespace from the overall text.
    """
    # Normalize multiple newlines
    text = "Line 1\n\n\nLine 2"
    result = clean_essay_text(text)
    assert "\n\n\n" not in result
    
    # Collapse multiple spaces
    text = "Hello    world"
    result = clean_essay_text(text)
    assert result == "Hello world"
    
    # Remove indentation
    text = "Line 1\n  Line 2"
    result = clean_essay_text(text)
    assert not result.startswith(" ")
    
    # Trim whitespace
    text = "   Hello world   "
    result = clean_essay_text(text)
    assert result == "Hello world"


if __name__ == '__main__':
    # Run all tests
    test_count_words_basic()
    test_count_words_contractions()
    test_count_words_possessives()
    test_count_words_hyphenated()
    test_count_words_numbers()
    test_count_words_abbreviations()
    test_count_words_punctuation()
    test_count_words_complex()
    test_count_words_whitespace_variations()
    test_clean_essay_text()
    
    print("✅ All tests passed!")