"""Background worker for processing evaluation jobs."""

import logging
import signal
import sys
import time
import socket
from typing import Optional, Any
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from core.models import Job, Attempt, EvaluationResult
from core.constants import AttemptStatus, JobStatus, JobType
from evaluation.ai_provider import evaluate_writing
from evaluation.schemas import EvaluationSchema

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Background worker management command."""
    
    help: str = 'Run background worker for processing evaluation jobs'
    
    def __init__(self) -> None:
        """
        Initialize the worker command.
        
        Sets an internal shutdown flag to False and creates a unique `worker_id` combining the host name and the instance id.
        """
        super().__init__()
        self.shutdown: bool = False
        self.worker_id: str = f"{socket.gethostname()}-{id(self)}"
    
    def handle(self, *args: Any, **options: Any) -> None:
        """
        Run the worker's main loop to claim and process evaluation jobs until a shutdown signal is received.
        
        Registers SIGINT and SIGTERM handlers, logs worker start and shutdown, repeatedly attempts to claim a pending job and process it, sleeps briefly when no job is available, and logs unexpected errors before retrying.
        """
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)
        
        logger.info(f"Worker {self.worker_id} started")
        
        while not self.shutdown:
            try:
                job: Optional[Job] = self.claim_job()
                if job:
                    self.process_job(job)
                else:
                    time.sleep(1)
            except Exception as e:
                logger.error(f"Unexpected error in worker loop: {str(e)}", exc_info=True)
                time.sleep(5)
        
        logger.info(f"Worker {self.worker_id} shutting down gracefully")
    
    def handle_shutdown(self, signum: int, frame: Any) -> None:
        """
        Set the command's shutdown flag and log receipt of a termination signal.
        
        Parameters:
            signum (int): Signal number received.
            frame (Any): Current stack frame provided to the signal handler.
        """
        logger.info(f"Received shutdown signal {signum}")
        self.shutdown = True
    
    def claim_job(self) -> Optional[Job]:
        """
        Atomically claim the next pending job that is due and mark it as running.
        
        Searches for the oldest job with status Pending and run_after <= now; if found, marks it RUNNING, records lock metadata and increments its attempt count, then returns that Job instance. If no job is available or an error occurs, returns None.
        
        Returns:
            Optional[Job]: The claimed Job instance, or `None` if no job was claimed.
        """
        try:
            with transaction.atomic():
                job = Job.objects.select_for_update(skip_locked=True).filter(
                    status=JobStatus.PENDING.value,
                    run_after__lte=timezone.now()
                ).order_by('created_at').first()
                
                if job:
                    job.status = JobStatus.RUNNING.value
                    job.locked_at = timezone.now()
                    job.locked_by = self.worker_id
                    job.attempts += 1
                    job.save()
                    
                    logger.info(f"Claimed job {job.id} (attempt {job.attempts})")
                    return job
        except Exception as e:
            logger.error(f"Error claiming job: {str(e)}", exc_info=True)
        
        return None
    
    def process_job(self, job: Job) -> None:
        """
        Process the given evaluation job: run the evaluation, persist results, and update attempt and job statuses.
        
        This updates the associated Attempt to PROCESSING, invokes the evaluation provider, validates (and attempts to repair) the returned evaluation data, creates an EvaluationResult, and marks the Attempt and Job DONE on success. On error, logs the failure; if the error is considered transient and the job has remaining retries (fewer than 2 attempts), reschedules the Job with a backoff and records the error; otherwise marks the Attempt and Job as FAILED and records the error message.
        
        Parameters:
            job (Job): The Job instance to process; its related Attempt is updated and an EvaluationResult may be created.
        """
        attempt = job.attempt
        
        try:
            attempt.status = AttemptStatus.PROCESSING.value
            attempt.save()
            
            logger.info(f"Processing job {job.id} for attempt {attempt.id}")
            
            if 'FAILME' in attempt.essay_text:
                raise Exception("Test failure triggered by FAILME keyword")
            
            result = evaluate_writing(
                task_prompt=attempt.task.prompt,
                essay_text=attempt.essay_text
            )
            
            try:
                validated = EvaluationSchema.model_validate(result)
            except Exception as validation_error:
                logger.warning(f"Initial validation failed: {str(validation_error)}")
                
                result = self.repair_evaluation(result)
                try:
                    validated = EvaluationSchema.model_validate(result)
                    logger.info("Successfully repaired evaluation data")
                except Exception as repair_error:
                    raise Exception(f"Validation failed after repair: {str(repair_error)}")
            
            EvaluationResult.objects.create(
                attempt=attempt,
                overall_band=validated.overall_band,
                criteria_scores=validated.criteria_scores.model_dump(),
                feedback=validated.feedback.model_dump(),
                priority_fixes=validated.priority_fixes,
                improved_essay=validated.improved_essay,
                raw_response=str(result)
            )
            
            attempt.status = AttemptStatus.DONE.value
            attempt.completed_at = timezone.now()
            attempt.save()
            
            job.status = JobStatus.DONE.value
            job.save()
            
            logger.info(f"Successfully processed job {job.id}")
            
        except Exception as e:
            error_message = str(e)
            logger.error(f"Error processing job {job.id}: {error_message}", exc_info=True)
            
            is_transient = self.is_transient_error(e)
            
            if is_transient and job.attempts < 2:
                job.status = JobStatus.PENDING.value
                job.run_after = timezone.now() + timedelta(seconds=30 * job.attempts)
                job.last_error = error_message
                job.save()
                
                logger.info(f"Job {job.id} will be retried after {job.run_after}")
            else:
                attempt.status = AttemptStatus.FAILED.value
                attempt.error_message = error_message
                attempt.save()
                
                job.status = JobStatus.FAILED.value
                job.last_error = error_message
                job.save()
                
                logger.error(f"Job {job.id} marked as FAILED")
    
    def is_transient_error(self, error: Exception) -> bool:
        """
        Determine whether an exception represents a transient, likely retryable error.
        
        Inspects the exception message for common transient indicators like "timeout", "connection", "network", "temporary", "rate limit", or "quota".
        
        Returns:
            True if the error message contains any transient keyword, False otherwise.
        """
        error_str: str = str(error).lower()
        transient_keywords: list[str] = [
            'timeout',
            'connection',
            'network',
            'temporary',
            'rate limit',
            'quota',
        ]
        return any(keyword in error_str for keyword in transient_keywords)
    
    def repair_evaluation(self, result: dict[str, Any]) -> dict[str, Any]:
        """
        Repair an evaluation result dictionary to ensure required keys and value shapes are present.
        
        Parameters:
            result (dict[str, Any]): Evaluation result that may be missing keys or contain malformed values.
        
        Returns:
            dict[str, Any]: The repaired evaluation result dictionary; guaranteed to contain `overall_band`, a `criteria_scores` mapping with keys `task_response`, `coherence_cohesion`, `lexical_resource`, `grammar_accuracy`, a `feedback` mapping where each value is a list, and a `priority_fixes` list (length between 3 and 5).
        """
        if 'overall_band' not in result:
            result['overall_band'] = 5.0
        
        if 'criteria_scores' not in result:
            result['criteria_scores'] = {}
        
        criteria_keys = ['task_response', 'coherence_cohesion', 'lexical_resource', 'grammar_accuracy']
        for key in criteria_keys:
            if key not in result['criteria_scores']:
                result['criteria_scores'][key] = 5.0
        
        if 'feedback' not in result:
            result['feedback'] = {}
        
        for key in criteria_keys:
            if key not in result['feedback']:
                result['feedback'][key] = ["No feedback available"]
            elif not isinstance(result['feedback'][key], list):
                result['feedback'][key] = [str(result['feedback'][key])]
        
        if 'priority_fixes' not in result:
            result['priority_fixes'] = ["Focus on task requirements", "Improve organization", "Enhance vocabulary"]
        elif not isinstance(result['priority_fixes'], list):
            result['priority_fixes'] = [str(result['priority_fixes'])]
        
        if len(result['priority_fixes']) < 3:
            result['priority_fixes'].extend(['Improve clarity', 'Enhance coherence', 'Develop ideas'][:3 - len(result['priority_fixes'])])
        elif len(result['priority_fixes']) > 5:
            result['priority_fixes'] = result['priority_fixes'][:5]
        
        return result