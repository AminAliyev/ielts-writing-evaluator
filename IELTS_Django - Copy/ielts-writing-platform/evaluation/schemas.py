"""Pydantic schemas for strict evaluation validation."""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class CriteriaScores(BaseModel):
    """IELTS criteria scores."""
    
    task_response: float = Field(ge=1.0, le=9.0)
    coherence_cohesion: float = Field(ge=1.0, le=9.0)
    lexical_resource: float = Field(ge=1.0, le=9.0)
    grammar_accuracy: float = Field(ge=1.0, le=9.0)
    
    @field_validator('task_response', 'coherence_cohesion', 'lexical_resource', 'grammar_accuracy')
    @classmethod
    def validate_half_point(cls, v):
        """Validate scores are in 0.5 increments."""
        if (v * 2) % 1 != 0:
            raise ValueError('Score must be in 0.5 increments')
        return v


class Feedback(BaseModel):
    """Detailed feedback for each criterion."""
    
    task_response: List[str] = Field(min_length=1)
    coherence_cohesion: List[str] = Field(min_length=1)
    lexical_resource: List[str] = Field(min_length=1)
    grammar_accuracy: List[str] = Field(min_length=1)


class EvaluationSchema(BaseModel):
    """Complete evaluation schema."""
    
    overall_band: float = Field(ge=1.0, le=9.0)
    criteria_scores: CriteriaScores
    feedback: Feedback
    priority_fixes: List[str] = Field(min_length=3, max_length=5)
    improved_essay: Optional[str] = None
    
    @field_validator('overall_band')
    @classmethod
    def validate_overall_band(cls, v):
        """Validate overall band is in 0.5 increments."""
        if (v * 2) % 1 != 0:
            raise ValueError('Overall band must be in 0.5 increments')
        return v
    
    class Config:
        """Pydantic config."""
        extra = 'forbid'
