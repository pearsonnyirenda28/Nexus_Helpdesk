from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Tickets
    path('tickets/',                              views.ticket_list,         name='ticket_list'),
    path('tickets/create/',                       views.ticket_create,       name='ticket_create'),
    path('tickets/print/',                        views.print_tickets,       name='print_tickets'),
    path('tickets/export/',                       views.export_tickets_csv,  name='export_tickets_csv'),
    path('tickets/<str:ticket_id>/',              views.ticket_detail,       name='ticket_detail'),
    path('tickets/<str:ticket_id>/edit/',         views.ticket_edit,         name='ticket_edit'),
    path('tickets/<str:ticket_id>/print/',        views.print_ticket_single, name='print_ticket_single'),

    # Reports & Audit
    path('reports/',                              views.reports,             name='reports'),
    path('audit/',                                views.audit_log,           name='audit_log'),
    path('users/<int:user_id>/activity/',         views.user_activity,       name='user_activity'),

    # Knowledge Base
    path('kb/',                                   views.kb_list,             name='kb_list'),
    path('kb/create/',                            views.kb_create,           name='kb_create'),
    path('kb/<int:pk>/',                          views.kb_detail,           name='kb_detail'),
    path('kb/<int:pk>/edit/',                     views.kb_edit,             name='kb_edit'),

    # Asset Registry
    path('assets/',                               views.asset_list,          name='asset_list'),
    path('assets/create/',                        views.asset_create,        name='asset_create'),
    path('assets/<int:pk>/',                      views.asset_detail,        name='asset_detail'),
    path('assets/<int:pk>/edit/',                 views.asset_edit,          name='asset_edit'),

    # Database Backup
    path('backup/',                               views.db_backup,           name='db_backup'),

    # Utilities
    path('glossary/',                             views.glossary,            name='glossary'),
    path('database/',                             views.database_switcher,   name='database_switcher'),

    # API
    path('api/stats/',                            views.api_stats,           name='api_stats'),
    path('api/suggest/',                          views.api_suggest,         name='api_suggest'),
    path('api/learn/',                            views.api_learn,           name='api_learn'),
    path('api/notifications/',                    views.api_notifications,   name='api_notifications'),
    path('api/push/subscribe/',                   views.api_push_subscribe,  name='api_push_subscribe'),
    path('api/theme/',                            views.api_theme,           name='api_theme'),
    path('api/bulk/',                             views.api_bulk_action,     name='api_bulk_action'),
]
