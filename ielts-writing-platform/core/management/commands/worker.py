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
        """Initialize worker."""
        super().__init__()
        self.shutdown: bool = False
        self.worker_id: str = f"{socket.gethostname()}-{id(self)}"
    
    def handle(self, *args: Any, **options: Any) -> None:
        """Execute worker loop.
        
        Args:
            *args: Variable length argument list.
            **options: Arbitrary keyword arguments.
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
        """Handle shutdown signals.
        
        Args:
            signum: Signal number.
            frame: Current stack frame.
        """
        logger.info(f"Received shutdown signal {signum}")
        self.shutdown = True
    
    def claim_job(self) -> Optional[Job]:
        """Claim next available job.
        
        Returns:
            Next pending job or None if no jobs available.
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
        """Process a job.
        
        Args:
            job: The Job instance to process.
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
        """Check if error is transient and should be retried.
        
        Args:
            error: The exception that occurred.
            
        Returns:
            True if error is transient, False otherwise.
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
        """Attempt to repair invalid evaluation result.
        
        Args:
            result: The evaluation result dictionary to repair.
            
        Returns:
            Repaired evaluation result dictionary.
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
