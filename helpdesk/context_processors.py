from .models import Ticket


def global_stats(request):
    """Inject sidebar stats into all templates. VoIP is optional."""
    if not request.user.is_authenticated:
        return {}
    try:
        open_tickets = Ticket.objects.filter(status__in=['OPEN', 'IN_PROGRESS']).count()
        critical = Ticket.objects.filter(
            status__in=['OPEN', 'IN_PROGRESS'], priority='CRITICAL').count()
    except Exception:
        open_tickets = 0
        critical = 0

    # VoIP is optional — if the table doesn't exist yet or VoIP is disabled, return 0
    active_calls = 0
    try:
        from voip.models import VoIPCall
        active_calls = VoIPCall.objects.filter(status__in=['RINGING', 'ACTIVE']).count()
    except Exception:
        pass

    return {
        'sidebar_open_tickets': open_tickets,
        'sidebar_active_calls': active_calls,
        'sidebar_critical': critical,
    }
