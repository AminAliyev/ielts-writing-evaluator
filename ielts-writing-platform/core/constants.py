"""Constants and enums for IELTS Writing Platform."""

from enum import Enum


class TaskType(str, Enum):
    """IELTS Writing Task Types."""
    
    TASK_1 = 'IELTS_T1'
    TASK_2 = 'IELTS_T2'
    
    @classmethod
    def choices(cls):
        """Return choices for Django model field.
        
        Returns:
            List of (value, label) tuples.
        """
        return [
            (cls.TASK_1.value, 'IELTS Task 1'),
            (cls.TASK_2.value, 'IELTS Task 2'),
        ]


class AttemptStatus(str, Enum):
    """User Attempt Status."""
    
    DRAFT = 'DRAFT'
    QUEUED = 'QUEUED'
    PROCESSING = 'PROCESSING'
    DONE = 'DONE'
    FAILED = 'FAILED'
    
    @classmethod
    def choices(cls):
        """Return choices for Django model field.
        
        Returns:
            List of (value, label) tuples.
        """
        return [
            (cls.DRAFT.value, 'Draft'),
            (cls.QUEUED.value, 'Queued'),
            (cls.PROCESSING.value, 'Processing'),
            (cls.DONE.value, 'Done'),
            (cls.FAILED.value, 'Failed'),
        ]


class JobStatus(str, Enum):
    """Background Job Status."""
    
    PENDING = 'PENDING'
    RUNNING = 'RUNNING'
    DONE = 'DONE'
    FAILED = 'FAILED'
    
    @classmethod
    def choices(cls):
        """Return choices for Django model field.
        
        Returns:
            List of (value, label) tuples.
        """
        return [
            (cls.PENDING.value, 'Pending'),
            (cls.RUNNING.value, 'Running'),
            (cls.DONE.value, 'Done'),
            (cls.FAILED.value, 'Failed'),
        ]


class JobType(str, Enum):
    """Background Job Types."""
    
    EVALUATE_WRITING = 'EVALUATE_WRITING'
    
    @classmethod
    def choices(cls):
        """Return choices for Django model field.
        
        Returns:
            List of (value, label) tuples.
        """
        return [
            (cls.EVALUATE_WRITING.value, 'Evaluate Writing'),
        ]
