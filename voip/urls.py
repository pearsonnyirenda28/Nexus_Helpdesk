from django.urls import path
from . import views

urlpatterns = [
    path('board/', views.call_board, name='call_board'),
    path('log/', views.call_log, name='call_log'),
    path('log-call/', views.log_call, name='log_call'),
    path('call/<uuid:call_uuid>/', views.call_detail, name='call_detail'),
    path('callers/', views.caller_directory, name='caller_directory'),
    path('api/active/', views.api_active_calls, name='api_active_calls'),
]
