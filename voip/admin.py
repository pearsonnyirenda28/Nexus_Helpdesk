from django.contrib import admin
from .models import VoIPCall, VoIPProvider, Extension, CallEvent, CallerProfile


@admin.register(VoIPProvider)
class VoIPProviderAdmin(admin.ModelAdmin):
    list_display = ['name', 'protocol', 'host', 'port', 'is_active']


@admin.register(Extension)
class ExtensionAdmin(admin.ModelAdmin):
    list_display = ['extension_number', 'display_name', 'user', 'department', 'is_active']
    search_fields = ['extension_number', 'display_name']


class CallEventInline(admin.TabularInline):
    model = CallEvent
    extra = 0
    readonly_fields = ['event_type', 'performed_by', 'timestamp', 'description']


@admin.register(VoIPCall)
class VoIPCallAdmin(admin.ModelAdmin):
    list_display = ['call_uuid', 'caller_number', 'caller_name', 'destination_number',
                    'direction', 'status', 'talk_duration_display', 'initiated_at']
    list_filter = ['status', 'direction']
    search_fields = ['caller_number', 'caller_name', 'destination_number']
    readonly_fields = ['call_uuid', 'ring_duration_seconds', 'talk_duration_seconds', 'hold_duration_seconds', 'created_at', 'updated_at']
    inlines = [CallEventInline]
    date_hierarchy = 'initiated_at'

    def talk_duration_display(self, obj):
        return obj.talk_duration_display
    talk_duration_display.short_description = 'Duration'


@admin.register(CallerProfile)
class CallerProfileAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'name', 'company', 'total_calls', 'last_call', 'is_vip', 'is_blocked']
    search_fields = ['phone_number', 'name', 'company']
    list_filter = ['is_vip', 'is_blocked']
