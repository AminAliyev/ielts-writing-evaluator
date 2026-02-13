"""URL patterns for core app."""

from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('signup', views.signup_view, name='signup'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    
    # HTML Pages
    path('', views.writing_list_view, name='home'),
    path('writing', views.writing_list_view, name='writing_list'),
    path('writing/<uuid:task_id>', views.writing_editor_view, name='writing_editor'),
    path('attempts/<uuid:attempt_id>/processing', views.processing_view, name='processing'),
    path('attempts/<uuid:attempt_id>/result', views.result_view, name='result'),
    path('history', views.history_view, name='history'),
    
    # API Endpoints
    path('api/tasks/', views.api_tasks_list, name='api_tasks_list'),
    path('api/tasks/<uuid:task_id>/', views.api_task_detail, name='api_task_detail'),
    path('api/tasks/random/', views.api_random_task, name='api_random_task'),
    path('api/attempts/draft/', views.api_save_draft, name='api_save_draft'),
    path('api/attempts/submit/', views.api_submit_attempt, name='api_submit_attempt'),
    path('api/attempts/<uuid:attempt_id>/status/', views.api_attempt_status, name='api_attempt_status'),
    path('api/attempts/<uuid:attempt_id>/', views.api_attempt_detail, name='api_attempt_detail'),
    path('api/attempts/', views.api_attempts_list, name='api_attempts_list'),
    path('api/attempts/<uuid:attempt_id>/retry/', views.api_retry_attempt, name='api_retry_attempt'),
]
