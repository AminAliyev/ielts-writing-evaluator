"""Django admin configuration for core models."""

from typing import Any, Optional
from django.contrib import admin
from django.http import HttpRequest
from .models import Task, Attempt, EvaluationResult, Job


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'task_type', 'min_words', 'suggested_time', 'is_active', 'created_at']
    list_filter = ['task_type', 'is_active', 'exam_code']
    search_fields = ['title', 'prompt']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'task', 'status', 'word_count', 'submitted_at', 'created_at']
    list_filter = ['status', 'is_random', 'created_at']
    search_fields = ['user__username', 'user__email', 'task__title']
    readonly_fields = ['id', 'created_at', 'updated_at', 'word_count']
    raw_id_fields = ['user', 'task']
    
    def has_add_permission(self, request: HttpRequest) -> bool:
        """
        Prevent adding new objects via the admin interface.
        
        Returns:
            bool: `False` to disallow creating new objects through the admin.
        """
        return False


@admin.register(EvaluationResult)
class EvaluationResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'attempt', 'overall_band', 'created_at']
    search_fields = ['attempt__id', 'attempt__user__username']
    readonly_fields = ['id', 'created_at', 'attempt', 'overall_band', 'criteria_scores', 
                      'feedback', 'priority_fixes', 'improved_essay', 'raw_response']
    
    def has_add_permission(self, request: HttpRequest) -> bool:
        """
        Prevent adding new objects via the admin interface.
        
        Returns:
            bool: `False` to disallow creating new objects through the admin.
        """
        return False
    
    def has_change_permission(self, request: HttpRequest, obj: Optional[Any] = None) -> bool:
        """
        Disallow changing EvaluationResult objects via the admin interface.
        
        Parameters:
            request (HttpRequest): The incoming HTTP request from the admin user.
            obj (Optional[Any]): The model instance being checked, or `None` when checking general permissions.
        
        Returns:
            bool: `False` always.
        """
        return False


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['id', 'type', 'status', 'attempts', 'run_after', 'created_at']
    list_filter = ['type', 'status', 'created_at']
    search_fields = ['attempt__id', 'attempt__user__username']
    readonly_fields = ['id', 'created_at', 'updated_at', 'locked_at', 'locked_by']
    raw_id_fields = ['attempt']
    
    def has_add_permission(self, request: HttpRequest) -> bool:
        """
        Prevent adding new objects via the admin interface.
        
        Returns:
            bool: `False` to disallow creating new objects through the admin.
        """
        return False