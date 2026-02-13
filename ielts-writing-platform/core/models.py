"""Core data models for IELTS Writing Platform."""

import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from .constants import TaskType, AttemptStatus, JobStatus, JobType


class Task(models.Model):
    """IELTS Writing Task (Task 1 or Task 2)."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task_type = models.CharField(max_length=20, choices=TaskType.choices(), db_index=True)
    title = models.CharField(max_length=255)
    prompt = models.TextField()
    min_words = models.IntegerField()
    suggested_time = models.IntegerField(help_text="Suggested time in minutes")
    is_active = models.BooleanField(default=True, db_index=True)
    exam_code = models.CharField(max_length=20, default='IELTS')
    module_code = models.CharField(max_length=20, default='WRITING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tasks'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['task_type', 'is_active']),
        ]
    
    def __str__(self) -> str:
        return f"{self.get_task_type_display()}: {self.title}"


class Attempt(models.Model):
    """User's attempt at a writing task."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attempts', db_index=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='attempts')
    status = models.CharField(max_length=20, choices=AttemptStatus.choices(), default=AttemptStatus.DRAFT.value, db_index=True)
    essay_text = models.TextField()
    word_count = models.IntegerField(default=0)
    is_random = models.BooleanField(default=False)
    error_message = models.TextField(null=True, blank=True)
    provider_meta = models.JSONField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'attempts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['user', 'task', 'created_at']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self) -> str:
        return f"Attempt {self.id} - {self.user.username} - {self.status}"


class EvaluationResult(models.Model):
    """AI evaluation result for an attempt."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attempt = models.OneToOneField(Attempt, on_delete=models.CASCADE, related_name='result')
    overall_band = models.FloatField()
    criteria_scores = models.JSONField()
    feedback = models.JSONField()
    priority_fixes = models.JSONField()
    improved_essay = models.TextField(null=True, blank=True)
    raw_response = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'evaluation_results'
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return f"Result for Attempt {self.attempt.id} - Band {self.overall_band}"


class Job(models.Model):
    """Asynchronous job for background processing."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=50, choices=JobType.choices())
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name='jobs')
    status = models.CharField(max_length=20, choices=JobStatus.choices(), default=JobStatus.PENDING.value, db_index=True)
    run_after = models.DateTimeField(default=timezone.now, db_index=True)
    locked_at = models.DateTimeField(null=True, blank=True)
    locked_by = models.CharField(max_length=255, null=True, blank=True)
    attempts = models.IntegerField(default=0)
    last_error = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'jobs'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['status', 'run_after', 'created_at']),
        ]
    
    def __str__(self) -> str:
        return f"Job {self.id} - {self.type} - {self.status}"
