from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver


class AuditMiddleware:
    """Middleware to track login/logout in the audit log"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response


@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    try:
        from .models import AuditLog

        def get_ip(req):
            xff = req.META.get('HTTP_X_FORWARDED_FOR')
            return xff.split(',')[0].strip() if xff else req.META.get('REMOTE_ADDR')

        AuditLog.objects.create(
            user=user,
            action=AuditLog.ACTION_LOGIN,
            model_name='User',
            object_id=str(user.pk),
            object_repr=user.username,
            ip_address=get_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            notes='User logged in',
        )
    except Exception:
        pass


@receiver(user_logged_out)
def log_logout(sender, request, user, **kwargs):
    try:
        from .models import AuditLog

        def get_ip(req):
            xff = req.META.get('HTTP_X_FORWARDED_FOR')
            return xff.split(',')[0].strip() if xff else req.META.get('REMOTE_ADDR')

        if user:
            AuditLog.objects.create(
                user=user,
                action=AuditLog.ACTION_LOGOUT,
                model_name='User',
                object_id=str(user.pk),
                object_repr=user.username,
                ip_address=get_ip(request),
                notes='User logged out',
            )
    except Exception:
        pass
