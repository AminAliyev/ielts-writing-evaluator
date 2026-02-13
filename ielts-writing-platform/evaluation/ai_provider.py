"""AI provider abstraction for essay evaluation."""

import os
import logging
import json
from typing import Any, Dict

logger = logging.getLogger(__name__)


def evaluate_writing(task_prompt: str, essay_text: str) -> Dict[str, Any]:
    """Evaluate writing using configured AI provider.
    
    Args:
        task_prompt: The IELTS writing task prompt.
        essay_text: The student's essay text to evaluate.
        
    Returns:
        Dictionary containing evaluation results with keys:
        - overall_band (float)
        - criteria_scores (dict)
        - feedback (dict)
        - priority_fixes (list)
        - improved_essay (optional str)
    """
    provider: str = os.getenv('AI_PROVIDER', 'gemini').lower()
    api_key: str = os.getenv('AI_API_KEY', '').strip()
    
    if not api_key:
        logger.warning("No AI_API_KEY set, using mock evaluation")
        return get_mock_evaluation(essay_text)
    
    if provider == 'gemini':
        return evaluate_with_gemini(task_prompt, essay_text, api_key)
    else:
        logger.warning(f"Unknown provider '{provider}', using mock evaluation")
        return get_mock_evaluation(essay_text)


def evaluate_with_gemini(task_prompt: str, essay_text: str, api_key: str) -> Dict[str, Any]:
    """Evaluate using Google Gemini API.
    
    Args:
        task_prompt: The IELTS writing task prompt.
        essay_text: The student's essay text.
        api_key: Google API key for Gemini.
        
    Returns:
        Dictionary containing structured evaluation results.
        
    Raises:
        Exception: If API call fails or response parsing fails.
    """
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        system_prompt = """You are an expert IELTS examiner. Evaluate the essay according to IELTS Writing criteria.

Return ONLY valid JSON with this exact structure (no markdown, no explanations):

{
  "overall_band": 7.5,
  "criteria_scores": {
    "task_response": 7.5,
    "coherence_cohesion": 7.0,
    "lexical_resource": 8.0,
    "grammar_accuracy": 7.5
  },
  "feedback": {
    "task_response": ["Point 1", "Point 2"],
    "coherence_cohesion": ["Point 1", "Point 2"],
    "lexical_resource": ["Point 1", "Point 2"],
    "grammar_accuracy": ["Point 1", "Point 2"]
  },
  "priority_fixes": ["Fix 1", "Fix 2", "Fix 3"],
  "improved_essay": "Optional improved version"
}

Rules:
- All band scores: 1.0-9.0 in 0.5 increments
- Overall band is average of four criteria, rounded to nearest 0.5
- Each feedback array must have at least 1 item
- priority_fixes must have exactly 3-5 items
- Return ONLY the JSON object"""
        
        user_prompt = f"""Task Prompt:
{task_prompt}

Student's Essay:
{essay_text}

Evaluate this essay and return the JSON evaluation."""
        
        response = model.generate_content(
            f"{system_prompt}\n\n{user_prompt}",
            generation_config={
                'temperature': 0.3,
                'top_p': 0.95,
                'max_output_tokens': 2048,
            }
        )
        
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith('```'):
            lines = response_text.split('\n')
            response_text = '\n'.join(lines[1:-1] if lines[-1].strip() == '```' else lines[1:])
            if response_text.startswith('json'):
                response_text = response_text[4:].strip()
        
        result = json.loads(response_text)
        logger.info("Successfully received evaluation from Gemini")
        return result
        
    except Exception as e:
        logger.error(f"Error calling Gemini API: {str(e)}", exc_info=True)
        raise


def get_mock_evaluation(essay_text: str) -> Dict[str, Any]:
    """Return deterministic mock evaluation for testing without API key.
    
    Args:
        essay_text: The student's essay text.
        
    Returns:
        Dictionary containing mock evaluation data based on word count.
    """
    word_count: int = len(essay_text.split())
    
    base_score = 5.0
    if word_count >= 250:
        base_score = 7.0
    elif word_count >= 200:
        base_score = 6.5
    elif word_count >= 150:
        base_score = 6.0
    
    return {
        "overall_band": base_score,
        "criteria_scores": {
            "task_response": base_score,
            "coherence_cohesion": base_score - 0.5,
            "lexical_resource": base_score + 0.5,
            "grammar_accuracy": base_score,
        },
        "feedback": {
            "task_response": [
                "Your essay addresses the main task requirements.",
                "Consider developing your ideas more fully with specific examples.",
            ],
            "coherence_cohesion": [
                "The essay has a clear structure with introduction, body, and conclusion.",
                "Some paragraphs could be better linked with cohesive devices.",
            ],
            "lexical_resource": [
                "You demonstrate a reasonable range of vocabulary.",
                "Try to use more sophisticated vocabulary and collocations.",
            ],
            "grammar_accuracy": [
                "You use a variety of sentence structures.",
                "There are some minor grammatical errors that could be corrected.",
            ],
        },
        "priority_fixes": [
            "Develop your main arguments with more specific examples and evidence",
            "Improve paragraph cohesion using more linking words and phrases",
            "Expand your vocabulary range with more topic-specific terminology",
        ],
        "improved_essay": None,
    }
