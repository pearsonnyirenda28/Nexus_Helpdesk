from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class VoIPProvider(models.Model):
    name = models.CharField(max_length=100)
    host = models.CharField(max_length=255)
    port = models.PositiveIntegerField(default=5060)
    protocol = models.CharField(max_length=10, default='SIP', choices=[('SIP', 'SIP'), ('IAX2', 'IAX2'), ('H323', 'H.323'), ('WebRTC', 'WebRTC')])
    username = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} ({self.protocol})'


class Extension(models.Model):
    extension_number = models.CharField(max_length=20, unique=True)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='extension')
    display_name = models.CharField(max_length=100)
    department = models.CharField(max_length=100, blank=True)
    voip_provider = models.ForeignKey(VoIPProvider, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Ext {self.extension_number} - {self.display_name}'


class VoIPCall(models.Model):
    STATUS_RINGING = 'RINGING'
    STATUS_ACTIVE = 'ACTIVE'
    STATUS_ON_HOLD = 'ON_HOLD'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_MISSED = 'MISSED'
    STATUS_FAILED = 'FAILED'
    STATUS_VOICEMAIL = 'VOICEMAIL'

    STATUS_CHOICES = [
        (STATUS_RINGING, 'Ringing'),
        (STATUS_ACTIVE, 'Active'),
        (STATUS_ON_HOLD, 'On Hold'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_MISSED, 'Missed'),
        (STATUS_FAILED, 'Failed'),
        (STATUS_VOICEMAIL, 'Voicemail'),
    ]

    DIRECTION_INBOUND = 'INBOUND'
    DIRECTION_OUTBOUND = 'OUTBOUND'
    DIRECTION_INTERNAL = 'INTERNAL'

    DIRECTION_CHOICES = [
        (DIRECTION_INBOUND, 'Inbound'),
        (DIRECTION_OUTBOUND, 'Outbound'),
        (DIRECTION_INTERNAL, 'Internal'),
    ]

    call_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    # Caller information
    caller_number = models.CharField(max_length=50, help_text='Caller ID / phone number')
    caller_name = models.CharField(max_length=150, blank=True, help_text='Caller ID name if provided')
    caller_extension = models.ForeignKey(Extension, on_delete=models.SET_NULL, null=True, blank=True, related_name='outgoing_calls')

    # Callee / destination
    destination_number = models.CharField(max_length=50)
    destination_extension = models.ForeignKey(Extension, on_delete=models.SET_NULL, null=True, blank=True, related_name='incoming_calls')
    answered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='calls_answered')

    # Call metadata
    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES, default=DIRECTION_INBOUND)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_RINGING)
    voip_provider = models.ForeignKey(VoIPProvider, on_delete=models.SET_NULL, null=True, blank=True)

    # Timing
    initiated_at = models.DateTimeField(default=timezone.now)
    answered_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    # Computed duration fields (in seconds)
    ring_duration_seconds = models.PositiveIntegerField(default=0)
    talk_duration_seconds = models.PositiveIntegerField(default=0)
    hold_duration_seconds = models.PositiveIntegerField(default=0)

    # Call notes & disposition
    notes = models.TextField(blank=True)
    is_recorded = models.BooleanField(default=False)
    recording_path = models.CharField(max_length=500, blank=True)
    transferred_to = models.CharField(max_length=50, blank=True)
    disposition_code = models.CharField(max_length=50, blank=True, help_text='Resolution code e.g. RESOLVED, TRANSFERRED')

    # Linked entities
    ticket_created = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-initiated_at']
        indexes = [
            models.Index(fields=['caller_number']),
            models.Index(fields=['status']),
            models.Index(fields=['initiated_at']),
        ]

    def __str__(self):
        return f'Call {self.call_uuid} | {self.caller_number} → {self.destination_number}'

    def save(self, *args, **kwargs):
        if self.answered_at and self.initiated_at:
            ring_delta = self.answered_at - self.initiated_at
            self.ring_duration_seconds = max(0, int(ring_delta.total_seconds()))

        if self.ended_at and self.answered_at:
            talk_delta = self.ended_at - self.answered_at
            self.talk_duration_seconds = max(0, int(talk_delta.total_seconds()))

        super().save(*args, **kwargs)

    @property
    def talk_duration_display(self):
        total = self.talk_duration_seconds
        hours = total // 3600
        minutes = (total % 3600) // 60
        seconds = total % 60
        if hours:
            return f'{hours}h {minutes}m {seconds}s'
        elif minutes:
            return f'{minutes}m {seconds}s'
        return f'{seconds}s'

    @property
    def talk_duration_minutes(self):
        return round(self.talk_duration_seconds / 60, 2)

    @property
    def is_active(self):
        return self.status in [self.STATUS_RINGING, self.STATUS_ACTIVE, self.STATUS_ON_HOLD]

    @property
    def status_badge_class(self):
        classes = {
            'RINGING': 'warning',
            'ACTIVE': 'success',
            'ON_HOLD': 'info',
            'COMPLETED': 'secondary',
            'MISSED': 'danger',
            'FAILED': 'danger',
            'VOICEMAIL': 'primary',
        }
        return classes.get(self.status, 'secondary')


class CallEvent(models.Model):
    """Tracks every state change in a call for full audit trail"""
    EVENT_INITIATED = 'INITIATED'
    EVENT_ANSWERED = 'ANSWERED'
    EVENT_HOLD = 'HOLD'
    EVENT_UNHOLD = 'UNHOLD'
    EVENT_TRANSFER = 'TRANSFER'
    EVENT_ENDED = 'ENDED'
    EVENT_MISSED = 'MISSED'

    EVENT_CHOICES = [
        (EVENT_INITIATED, 'Call Initiated'),
        (EVENT_ANSWERED, 'Call Answered'),
        (EVENT_HOLD, 'Put on Hold'),
        (EVENT_UNHOLD, 'Resumed from Hold'),
        (EVENT_TRANSFER, 'Transferred'),
        (EVENT_ENDED, 'Call Ended'),
        (EVENT_MISSED, 'Call Missed'),
    ]

    call = models.ForeignKey(VoIPCall, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=20, choices=EVENT_CHOICES)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    metadata = models.JSONField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f'{self.call.call_uuid} | {self.event_type} @ {self.timestamp}'


class CallerProfile(models.Model):
    """Known callers with history"""
    phone_number = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=150, blank=True)
    company = models.CharField(max_length=150, blank=True)
    department = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    notes = models.TextField(blank=True)
    is_vip = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    total_calls = models.PositiveIntegerField(default=0)
    last_call = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.phone_number} - {self.name or "Unknown"}'

    @property
    def display_name(self):
        return self.name or self.phone_number
