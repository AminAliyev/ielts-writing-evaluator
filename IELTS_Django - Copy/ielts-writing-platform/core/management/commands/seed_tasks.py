"""Management command to seed initial IELTS writing tasks."""

from typing import Any, Dict, List
from django.core.management.base import BaseCommand
from core.models import Task
from core.constants import TaskType


class Command(BaseCommand):
    """Seed database with initial IELTS writing tasks."""
    
    help: str = 'Seed database with initial IELTS writing tasks'
    
    def handle(self, *args: Any, **options: Any) -> None:
        """Execute command.
        
        Args:
            *args: Variable length argument list.
            **options: Arbitrary keyword arguments.
        """
        tasks_data: List[Dict[str, Any]] = [
            {
                'task_type': TaskType.TASK_1.value,
                'title': 'Population Growth in Major Cities',
                'prompt': '''The graph below shows the population growth in three major cities between 2000 and 2020.

Summarize the information by selecting and reporting the main features, and make comparisons where relevant.

Write at least 150 words.

[Imagine a line graph showing population trends for Tokyo, London, and New York from 2000-2020]''',
                'min_words': 150,
                'suggested_time': 20,
            },
            {
                'task_type': TaskType.TASK_1.value,
                'title': 'Coffee Production Process',
                'prompt': '''The diagram below shows the process of coffee production from bean to cup.

Summarize the information by selecting and reporting the main features.

Write at least 150 words.''',
                'min_words': 150,
                'suggested_time': 20,
            },
            {
                'task_type': TaskType.TASK_1.value,
                'title': 'Energy Consumption by Source',
                'prompt': '''The pie charts below show the percentage of energy consumption from different sources in a country in 1990 and 2020.

Summarize the information by selecting and reporting the main features, and make comparisons where relevant.

Write at least 150 words.''',
                'min_words': 150,
                'suggested_time': 20,
            },
            {
                'task_type': TaskType.TASK_2.value,
                'title': 'Online Education vs Traditional Education',
                'prompt': '''Some people believe that online education is more effective than traditional classroom learning, while others think traditional methods are superior.

Discuss both views and give your own opinion.

Give reasons for your answer and include any relevant examples from your own knowledge or experience.

Write at least 250 words.''',
                'min_words': 250,
                'suggested_time': 40,
            },
            {
                'task_type': TaskType.TASK_2.value,
                'title': 'Environmental Protection Responsibility',
                'prompt': '''Some people think that environmental problems should be solved on a global scale while others believe it is better to deal with them nationally.

Discuss both views and give your opinion.

Give reasons for your answer and include any relevant examples from your own knowledge or experience.

Write at least 250 words.''',
                'min_words': 250,
                'suggested_time': 40,
            },
            {
                'task_type': TaskType.TASK_2.value,
                'title': 'Work-Life Balance',
                'prompt': '''Many people find it difficult to balance their work and personal life.

What are the causes of this problem? How can individuals and employers address these issues?

Give reasons for your answer and include any relevant examples from your own knowledge or experience.

Write at least 250 words.''',
                'min_words': 250,
                'suggested_time': 40,
            },
        ]
        
        created_count = 0
        for task_data in tasks_data:
            task, created = Task.objects.get_or_create(
                title=task_data['title'],
                defaults=task_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created task: {task.title}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Task already exists: {task.title}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully created {created_count} new tasks')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Total tasks in database: {Task.objects.count()}')
        )
