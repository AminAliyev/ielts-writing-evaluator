"""Views for IELTS Writing Platform."""

import json
import logging
from typing import Any, Dict, List, Optional
from datetime import timedelta
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST
from django.http import JsonResponse, HttpResponse, HttpRequest
from django.db import transaction
from django.utils import timezone
from django.core.paginator import Paginator

from .models import Task, Attempt, Job, EvaluationResult
from .forms import SignUpForm, LoginForm
from .constants import TaskType, AttemptStatus, JobStatus, JobType
from .errors import (
    error_response,
    success_response,
    InvalidJSONError,
    MissingFieldError,
    TaskNotFoundError,
    AttemptNotFoundError,
    MinWordCountError,
    DuplicateSubmissionError,
    InvalidStatusTransitionError,
    APIError,
)
from evaluation.utils import count_words

logger = logging.getLogger(__name__)


# Authentication Views

def signup_view(request: HttpRequest) -> HttpResponse:
    """User registration page.
    
    Args:
        request: The HTTP request object.
        
    Returns:
        Rendered signup template or redirect to writing list.
    """
    if request.user.is_authenticated:
        return redirect('writing_list')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            logger.info(f"New user registered: {user.username}")
            return redirect('writing_list')
    else:
        form = SignUpForm()
    
    return render(request, 'signup.html', {'form': form})


def login_view(request: HttpRequest) -> HttpResponse:
    """User login page.
    
    Args:
        request: The HTTP request object.
        
    Returns:
        Rendered login template or redirect to writing list.
    """
    if request.user.is_authenticated:
        return redirect('writing_list')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            logger.info(f"User logged in: {user.username}")
            next_url = request.GET.get('next', 'writing_list')
            return redirect(next_url)
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})


@require_POST
def logout_view(request: HttpRequest) -> HttpResponse:
    """User logout.
    
    Args:
        request: The HTTP request object.
        
    Returns:
        Redirect to login page.
    """
    username = request.user.username
    logout(request)
    logger.info(f"User logged out: {username}")
    return redirect('login')


# HTML Pages

@login_required
def writing_list_view(request: HttpRequest) -> HttpResponse:
    """Writing task list page.
    
    Args:
        request: The HTTP request object.
        
    Returns:
        Rendered writing list template.
    """
    return render(request, 'writing_list.html')


@login_required
def writing_editor_view(request: HttpRequest, task_id: str) -> HttpResponse:
    """Writing editor page.
    
    Args:
        request: The HTTP request object.
        task_id: UUID of the task.
        
    Returns:
        Rendered writing editor template.
    """
    task = get_object_or_404(Task, id=task_id, is_active=True)
    
    draft = Attempt.objects.filter(
        user=request.user,
        task=task,
        status=AttemptStatus.DRAFT.value
    ).order_by('-created_at').first()
    
    context = {
        'task': task,
        'draft': draft,
    }
    return render(request, 'writing_editor.html', context)


@login_required
def processing_view(request: HttpRequest, attempt_id: str) -> HttpResponse:
    """Processing status page.
    
    Args:
        request: The HTTP request object.
        attempt_id: UUID of the attempt.
        
    Returns:
        Rendered processing status template.
    """
    attempt = get_object_or_404(Attempt, id=attempt_id, user=request.user)
    
    context = {
        'attempt': attempt,
    }
    return render(request, 'processing.html', context)


@login_required
def result_view(request: HttpRequest, attempt_id: str) -> HttpResponse:
    """Evaluation result page.
    
    Args:
        request: The HTTP request object.
        attempt_id: UUID of the attempt.
        
    Returns:
        Rendered result template or redirect to processing page.
    """
    attempt = get_object_or_404(
        Attempt.objects.select_related('task', 'result'),
        id=attempt_id,
        user=request.user
    )
    
    if attempt.status != AttemptStatus.DONE.value:
        return redirect('processing', attempt_id=attempt.id)
    
    context = {
        'attempt': attempt,
        'result': attempt.result,
    }
    return render(request, 'result.html', context)


@login_required
def history_view(request: HttpRequest) -> HttpResponse:
    """User's submission history.
    
    Args:
        request: The HTTP request object.
        
    Returns:
        Rendered history template.
    """
    return render(request, 'history.html')


# API Endpoints

@login_required
@require_http_methods(["GET"])
def api_tasks_list(request: HttpRequest) -> JsonResponse:
    """List tasks, optionally filtered by type.
    
    Args:
        request: The HTTP request object. Can include 'task_type' query parameter.
        
    Returns:
        JSON response with list of tasks.
    """
    task_type = request.GET.get('task_type')
    
    tasks = Task.objects.filter(is_active=True)
    if task_type:
        tasks = tasks.filter(task_type=task_type)
    
    tasks = tasks.order_by('task_type', 'created_at')
    
    data = {
        'tasks': [{
            'id': str(task.id),
            'task_type': task.task_type,
            'title': task.title,
            'prompt': task.prompt,
            'min_words': task.min_words,
            'suggested_time': task.suggested_time,
        } for task in tasks]
    }
    
    return success_response(data)


@login_required
@require_http_methods(["GET"])
def api_task_detail(request: HttpRequest, task_id: str) -> JsonResponse:
    """Get specific task details.
    
    Args:
        request: The HTTP request object.
        task_id: UUID of the task.
        
    Returns:
        JSON response with task details.
    """
    try:
        try:
            task = Task.objects.get(id=task_id, is_active=True)
        except Task.DoesNotExist:
            raise TaskNotFoundError()
        
        data = {
            'id': str(task.id),
            'task_type': task.task_type,
            'title': task.title,
            'prompt': task.prompt,
            'min_words': task.min_words,
            'suggested_time': task.suggested_time,
        }
        
        return success_response(data)
    except APIError as e:
        return error_response(e)


@login_required
@require_http_methods(["GET"])
def api_random_task(request: HttpRequest) -> JsonResponse:
    """Get random task by type.
    
    Args:
        request: The HTTP request object. Can include 'task_type' query parameter.
        
    Returns:
        JSON response with random task or 404 error.
    """
    task_type = request.GET.get('task_type')
    
    query = Task.objects.filter(is_active=True)
    if task_type:
        query = query.filter(task_type=task_type)
    
    task = query.order_by('?').first()
    
    if not task:
        error = TaskNotFoundError()
        return error_response(error)
    
    data = {
        'id': str(task.id),
        'task_type': task.task_type,
        'title': task.title,
        'prompt': task.prompt,
        'min_words': task.min_words,
        'suggested_time': task.suggested_time,
    }
    
    return success_response(data)


@login_required
@require_POST
def api_save_draft(request: HttpRequest) -> JsonResponse:
    """Save essay draft.
    
    Args:
        request: The HTTP request object with JSON body containing:
            - task_id (str): UUID of the task
            - essay_text (str): The essay text
            - is_random (bool, optional): Whether task was randomly selected
        
    Returns:
        JSON response with draft id and word count, or error message.
    """
    try:
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            raise InvalidJSONError()
        
        task_id = data.get('task_id')
        essay_text = data.get('essay_text', '')
        is_random = data.get('is_random', False)
        
        if not task_id:
            raise MissingFieldError('task_id')
        
        try:
            task = Task.objects.get(id=task_id, is_active=True)
        except Task.DoesNotExist:
            raise TaskNotFoundError()
        
        word_count = count_words(essay_text)
        
        draft, created = Attempt.objects.update_or_create(
            user=request.user,
            task=task,
            status=AttemptStatus.DRAFT.value,
            defaults={
                'essay_text': essay_text,
                'word_count': word_count,
                'is_random': is_random,
            }
        )
        
        response_data = {
            'id': str(draft.id),
            'word_count': word_count,
        }
        return success_response(response_data)
        
    except APIError as e:
        logger.warning(f"API error in save_draft: {e.message}")
        return error_response(e)
    except Exception as e:
        logger.error(f"Unexpected error in save_draft: {str(e)}", exc_info=True)
        generic_error = APIError(
            code='internal_error',
            message='An unexpected error occurred while saving the draft',
            status_code=500,
        )
        return error_response(generic_error)


@login_required
@require_POST
def api_submit_attempt(request: HttpRequest) -> JsonResponse:
    """Submit essay for evaluation.
    
    Args:
        request: The HTTP request object with JSON body containing:
            - task_id (str): UUID of the task
            - essay_text (str): The essay text
            - is_random (bool, optional): Whether task was randomly selected
        
    Returns:
        JSON response with attempt id and status, or error message.
    """
    try:
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            raise InvalidJSONError()
        
        task_id = data.get('task_id')
        essay_text = data.get('essay_text', '')
        is_random = data.get('is_random', False)
        
        if not task_id:
            raise MissingFieldError('task_id')
        
        try:
            task = Task.objects.get(id=task_id, is_active=True)
        except Task.DoesNotExist:
            raise TaskNotFoundError()
        
        word_count = count_words(essay_text)
        
        if word_count < task.min_words:
            raise MinWordCountError(task.min_words, word_count)
        
        two_minutes_ago = timezone.now() - timedelta(minutes=2)
        existing = Attempt.objects.filter(
            user=request.user,
            task=task,
            status__in=[AttemptStatus.QUEUED.value, AttemptStatus.PROCESSING.value],
            created_at__gte=two_minutes_ago
        ).first()
        
        if existing:
            logger.info(f"Returning existing attempt {existing.id} for user {request.user.username}")
            return success_response({
                'id': str(existing.id),
                'status': existing.status,
            })
        
        with transaction.atomic():
            attempt = Attempt.objects.create(
                user=request.user,
                task=task,
                status=AttemptStatus.QUEUED.value,
                essay_text=essay_text,
                word_count=word_count,
                is_random=is_random,
                submitted_at=timezone.now(),
            )
            
            job = Job.objects.create(
                type=JobType.EVALUATE_WRITING.value,
                attempt=attempt,
                status=JobStatus.PENDING.value,
            )
            
            logger.info(f"Created attempt {attempt.id} and job {job.id} for user {request.user.username}")
        
        return success_response({
            'id': str(attempt.id),
            'status': attempt.status,
        }, status_code=201)
        
    except APIError as e:
        logger.warning(f"API error in submit_attempt: {e.message}")
        return error_response(e)
    except Exception as e:
        logger.error(f"Unexpected error in submit_attempt: {str(e)}", exc_info=True)
        generic_error = APIError(
            code='internal_error',
            message='An unexpected error occurred while submitting the attempt',
            status_code=500,
        )
        return error_response(generic_error)


@login_required
@require_http_methods(["GET"])
def api_attempt_status(request: HttpRequest, attempt_id: str) -> JsonResponse:
    """Get attempt status for polling.
    
    Args:
        request: The HTTP request object.
        attempt_id: UUID of the attempt.
        
    Returns:
        JSON response with attempt status and optional redirect URL.
    """
    try:
        try:
            attempt = Attempt.objects.get(id=attempt_id, user=request.user)
        except Attempt.DoesNotExist:
            raise AttemptNotFoundError()
        
        data = {
            'status': attempt.status,
            'error_message': attempt.error_message,
        }
        
        if attempt.status == AttemptStatus.DONE.value:
            data['redirect_url'] = f'/attempts/{attempt.id}/result'
        elif attempt.status == AttemptStatus.FAILED.value:
            data['redirect_url'] = None
        
        return success_response(data)
    except APIError as e:
        return error_response(e)


@login_required
@require_http_methods(["GET"])
def api_attempt_detail(request: HttpRequest, attempt_id: str) -> JsonResponse:
    """Get attempt details with result.
    
    Args:
        request: The HTTP request object.
        attempt_id: UUID of the attempt.
        
    Returns:
        JSON response with attempt and result details.
    """
    try:
        try:
            attempt = Attempt.objects.select_related('task', 'result').get(
                id=attempt_id,
                user=request.user
            )
        except Attempt.DoesNotExist:
            raise AttemptNotFoundError()
        
        data = {
            'id': str(attempt.id),
            'task': {
                'id': str(attempt.task.id),
                'title': attempt.task.title,
                'task_type': attempt.task.task_type,
            },
            'status': attempt.status,
            'essay_text': attempt.essay_text,
            'word_count': attempt.word_count,
            'submitted_at': attempt.submitted_at.isoformat() if attempt.submitted_at else None,
            'error_message': attempt.error_message,
        }
        
        if attempt.status == AttemptStatus.DONE.value and hasattr(attempt, 'result'):
            result = attempt.result
            data['result'] = {
                'overall_band': result.overall_band,
                'criteria_scores': result.criteria_scores,
                'feedback': result.feedback,
                'priority_fixes': result.priority_fixes,
                'improved_essay': result.improved_essay,
            }
        
        return success_response(data)
    except APIError as e:
        return error_response(e)


@login_required
@require_http_methods(["GET"])
def api_attempts_list(request: HttpRequest) -> JsonResponse:
    """List user's attempts with pagination.
    
    Args:
        request: The HTTP request object. Can include 'page' query parameter.
        
    Returns:
        JSON response with paginated list of attempts.
    """
    attempts = Attempt.objects.filter(
        user=request.user,
        status__in=[AttemptStatus.DONE.value, AttemptStatus.FAILED.value, 
                    AttemptStatus.PROCESSING.value, AttemptStatus.QUEUED.value]
    ).select_related('task').order_by('-created_at')
    
    page = request.GET.get('page', 1)
    paginator = Paginator(attempts, 20)
    page_obj = paginator.get_page(page)
    
    data = {
        'attempts': [{
            'id': str(attempt.id),
            'task': {
                'title': attempt.task.title,
                'task_type': attempt.task.task_type,
            },
            'status': attempt.status,
            'word_count': attempt.word_count,
            'submitted_at': attempt.submitted_at.isoformat() if attempt.submitted_at else None,
            'overall_band': attempt.result.overall_band if hasattr(attempt, 'result') else None,
        } for attempt in page_obj],
        'page': page_obj.number,
        'total_pages': paginator.num_pages,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
    }
    
    return success_response(data)


@login_required
@require_POST
def api_retry_attempt(request: HttpRequest, attempt_id: str) -> JsonResponse:
    """Retry a failed attempt.
    
    Args:
        request: The HTTP request object.
        attempt_id: UUID of the attempt.
        
    Returns:
        JSON response with attempt id and status, or error message.
    """
    try:
        try:
            attempt = Attempt.objects.get(id=attempt_id, user=request.user)
        except Attempt.DoesNotExist:
            raise AttemptNotFoundError()
        
        if attempt.status != AttemptStatus.FAILED.value:
            raise InvalidStatusTransitionError(
                attempt.status,
                "retry",
            )
        
        with transaction.atomic():
            attempt.status = AttemptStatus.QUEUED.value
            attempt.error_message = None
            attempt.submitted_at = timezone.now()
            attempt.save()
            
            job = Job.objects.create(
                type=JobType.EVALUATE_WRITING.value,
                attempt=attempt,
                status=JobStatus.PENDING.value,
            )
            
            logger.info(f"Retry: Created job {job.id} for attempt {attempt.id}")
        
        return success_response({
            'id': str(attempt.id),
            'status': attempt.status,
        })
        
    except APIError as e:
        logger.warning(f"API error in retry_attempt: {e.message}")
        return error_response(e)
    except Exception as e:
        logger.error(f"Unexpected error in retry_attempt: {str(e)}", exc_info=True)
        generic_error = APIError(
            code='internal_error',
            message='An unexpected error occurred while retrying the attempt',
            status_code=500,
        )
        return error_response(generic_error)
