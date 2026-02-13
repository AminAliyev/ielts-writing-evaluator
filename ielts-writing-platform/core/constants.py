"""Constants and enums for IELTS Writing Platform."""

from enum import Enum


class TaskType(str, Enum):
    """IELTS Writing Task Types."""
    
    TASK_1 = 'IELTS_T1'
    TASK_2 = 'IELTS_T2'
    
    @classmethod
    def choices(cls):
        """
        Provide Django model field choices for IELTS task types.
        
        Returns:
            list[tuple[str, str]]: List of (value, label) tuples:
                ('IELTS_T1', 'IELTS Task 1') and ('IELTS_T2', 'IELTS Task 2').
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
        """
        Provide Django-compatible (value, label) choices for the enum.
        
        Returns:
            list[tuple[str, str]]: List of (value, label) tuples where each value is the enum member's string value and each label is the human-readable name for use in Django model/field choices.
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
        """
        Return Django model field choices for this JobStatus enum.
        
        Returns:
            List[tuple[str, str]]: List of (value, label) tuples, where `value` is the enum member's string value and `label` is the human-readable name (e.g., `('PENDING', 'Pending')`).
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
        """
        Provide a list of choices suitable for Django model fields for this JobType enum.
        
        Returns:
            list: A list of (value, label) tuples where `value` is the enum value and `label` is the human-readable name.
        """
        return [
            (cls.EVALUATE_WRITING.value, 'Evaluate Writing'),
        ]