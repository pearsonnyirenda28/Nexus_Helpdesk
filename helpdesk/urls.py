from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('tickets/', views.ticket_list, name='ticket_list'),
    path('tickets/create/', views.ticket_create, name='ticket_create'),
    path('tickets/<str:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    path('tickets/<str:ticket_id>/edit/', views.ticket_edit, name='ticket_edit'),
    path('reports/', views.reports, name='reports'),
    path('audit/', views.audit_log, name='audit_log'),
    path('api/stats/', views.api_stats, name='api_stats'),
]
