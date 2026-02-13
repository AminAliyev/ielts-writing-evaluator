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
    """
    Render the user signup page and handle new user registrations.
    
    On POST, validates the submitted form; if valid, creates the user, logs them in, and redirects to the writing list. On GET, renders an empty signup form.
    
    Returns:
        HttpResponse: A rendered signup page or a redirect response to the writing list.
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
    """
    Render the login page and authenticate users.
    
    Processes POST submissions using LoginForm; on successful authentication logs the user in and redirects to the `next` URL (or writing list). On GET or invalid form submission, renders the login template with the form.
    
    Returns:
        HttpResponse: A redirect after successful login or the rendered login page when showing the form or after failed validation.
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
    """
    Log out the current user and redirect to the login page.
    
    Returns:
        HttpResponse: Redirect response to the login page.
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
    """
    Render the writing editor page for the given active task and include the user's most recent draft if present.
    
    Parameters:
        request (HttpRequest): The incoming HTTP request; must be from an authenticated user.
        task_id (str): UUID of the active Task to open.
    
    Returns:
        HttpResponse: The rendered writing editor page with context keys `task` (Task) and `draft` (Attempt or `None`).
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
    """
    Render the processing status page for a user's attempt.
    
    Parameters:
        request (HttpRequest): The incoming HTTP request; user must be authenticated.
        attempt_id (str): UUID of the Attempt belonging to the current user.
    
    Returns:
        HttpResponse: Rendered processing status page for the specified attempt.
    """
    attempt = get_object_or_404(Attempt, id=attempt_id, user=request.user)
    
    context = {
        'attempt': attempt,
    }
    return render(request, 'processing.html', context)


@login_required
def result_view(request: HttpRequest, attempt_id: str) -> HttpResponse:
    """
    Render the evaluation result page for a completed attempt.
    
    Fetches the attempt belonging to the current user by `attempt_id`. If the attempt's status is DONE, renders the result template with the attempt and its result in the context; if the attempt is not DONE, redirects to the processing page. Raises Http404 if the attempt does not exist or does not belong to the user.
    
    Parameters:
        request (HttpRequest): The incoming HTTP request.
        attempt_id (str): UUID of the attempt to display.
    
    Returns:
        HttpResponse: The rendered result page response, or an HttpResponse redirecting to the processing page.
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
    """
    Render the user's submission history page.
    
    Returns:
        HttpResponse: The rendered history page response.
    """
    return render(request, 'history.html')


# API Endpoints

@login_required
@require_http_methods(["GET"])
def api_tasks_list(request: HttpRequest) -> JsonResponse:
    """
    List active tasks, optionally filtered by task type.
    
    Parameters:
        request (HttpRequest): The incoming request. May include the query parameter `task_type`
            to limit results to tasks of that type.
    
    Returns:
        JsonResponse: JSON object with a `tasks` list where each item contains:
            - `id` (str): Task UUID as a string.
            - `task_type` (str): The task's type.
            - `title` (str): Task title.
            - `prompt` (str): Task prompt text.
            - `min_words` (int): Minimum required word count for the task.
            - `suggested_time` (int): Suggested completion time in minutes.
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
    """
    Retrieve a random active Task, optionally filtered by the 'task_type' query parameter.
    
    Parameters:
    	request (HttpRequest): Django request; may include 'task_type' in GET to limit selection.
    
    Returns:
    	JsonResponse: On success, JSON with task fields `id`, `task_type`, `title`, `prompt`, `min_words`, and `suggested_time`. If no matching task exists, returns an API error response indicating a TaskNotFoundError.
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
    """
    Save or update the requesting user's draft essay for a specified task.
    
    Expects the HttpRequest body to be JSON with the fields:
    - task_id (str): UUID of the active task
    - essay_text (str, optional): Draft essay text (defaults to empty string)
    - is_random (bool, optional): Whether the task was randomly selected
    
    Parameters:
        request (HttpRequest): Request whose body contains the JSON payload described above.
    
    Returns:
        JsonResponse: On success, a JSON object with `id` (draft Attempt UUID as string) and `word_count` (int).
        On failure, an API error response describing the problem.
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
    """
    Submit an essay for evaluation and queue a background job if accepted.
    
    Parameters:
        request (HttpRequest): HTTP request whose JSON body must include:
            - task_id (str): UUID of the active task.
            - essay_text (str): The essay content.
            - is_random (bool, optional): Whether the task was randomly selected.
    
    Returns:
        dict: JSON object with keys:
            - `id` (str): Attempt UUID.
            - `status` (str): Attempt status. When an existing recent queued/processing attempt is reused this returns that attempt's id and status; when a new attempt is created the response contains the new attempt's id and status (created responses use HTTP 201).
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
    """
    Provide the current status of a user's attempt for polling.
    
    The response includes `status` and `error_message`. If the attempt is done, the response also includes `redirect_url` pointing to the attempt's result page; if the attempt failed, `redirect_url` is `null`.
    
    Parameters:
        request (HttpRequest): The HTTP request from the authenticated user.
        attempt_id (str): UUID of the attempt to check.
    
    Returns:
        JsonResponse: JSON object with `status`, `error_message`, and optionally `redirect_url`.
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
    """
    Retrieve detailed information for the authenticated user's attempt, including its task and evaluation result when available.
    
    Parameters:
        request (HttpRequest): Django request object for the authenticated user.
        attempt_id (str): UUID string identifying the Attempt to retrieve.
    
    Returns:
        JsonResponse: A success response containing an object with:
            - id: Attempt UUID string.
            - task: Object with `id`, `title`, and `task_type`.
            - status: Attempt status string.
            - essay_text: Submitted essay text.
            - word_count: Integer word count of the essay.
            - submitted_at: ISO 8601 timestamp string or `null`.
            - error_message: Error message string or `null`.
            - result (optional): Present when `status` is DONE and a result exists; object with:
                - overall_band: Overall band value.
                - criteria_scores: Criteria score breakdown.
                - feedback: Feedback text or structure.
                - priority_fixes: Priority fixes suggested.
                - improved_essay: Improved essay text (if available).
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
    """
    Return a paginated list of the current user's attempts.
    
    Parameters:
        request (HttpRequest): Django request; may include a 'page' query parameter (1-based).
    
    Returns:
        JsonResponse: JSON object with:
            - attempts (list): Each item contains:
                - id (str): Attempt UUID as a string.
                - task (dict): { 'title': str, 'task_type': str }.
                - status (str): Attempt status.
                - word_count (int): Word count of the submission.
                - submitted_at (str|None): ISO 8601 timestamp of submission or `None`.
                - overall_band (number|None): Result overall band if available, otherwise `None`.
            - page (int): Current page number.
            - total_pages (int): Total number of pages.
            - has_next (bool): True if a next page exists.
            - has_previous (bool): True if a previous page exists.
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
    """
    Queue a failed attempt for re-evaluation by creating a new pending job.
    
    Parameters:
        attempt_id (str): UUID of the attempt to retry.
    
    Returns:
        dict: JSON object containing the retried attempt's `id` and `status`.
    
    Raises:
        AttemptNotFoundError: If no attempt with the given id exists for the current user.
        InvalidStatusTransitionError: If the attempt is not in the FAILED status.
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