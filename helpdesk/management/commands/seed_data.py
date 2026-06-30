"""
Management command: python manage.py seed_data
Seeds the database with realistic demo data for NexusDesk.
"""
import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone


class Command(BaseCommand):
    help = 'Seeds NexusDesk with demo data (users, tickets, VoIP calls, categories)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('\n🚀  Seeding NexusDesk demo data...\n'))
        self._create_users()
        self._create_categories()
        self._create_voip_providers()
        self._create_extensions()
        self._create_tickets()
        self._create_voip_calls()
        self.stdout.write(self.style.SUCCESS('\n✅  Seed complete! Login: admin / admin123!\n'))

    # ── Users ────────────────────────────────────────────────────────────────
    def _create_users(self):
        users = [
            ('admin',    'admin123!',   'Admin',    'User',  True,  True),
            ('tstark',   'pass1234!',   'Tony',     'Stark', True,  False),
            ('rrogers',  'pass1234!',   'Rumbi',    'Rogers',True,  False),
            ('nmutasa',  'pass1234!',   'Nyasha',   'Mutasa',True,  False),
            ('jdoe',     'pass1234!',   'Jane',     'Doe',   False, False),
        ]
        for username, password, first, last, is_staff, is_super in users:
            if not User.objects.filter(username=username).exists():
                u = User.objects.create_user(
                    username=username, password=password,
                    first_name=first, last_name=last,
                    email=f'{username}@nexusdesk.local',
                    is_staff=is_staff, is_superuser=is_super,
                )
                self.stdout.write(f'  Created user: {username}')
        self.stdout.write(self.style.SUCCESS('  ✓ Users done'))

    # ── Categories ───────────────────────────────────────────────────────────
    def _create_categories(self):
        from helpdesk.models import Category
        cats = [
            ('Network / Connectivity', 'fas fa-network-wired', '#1f6feb'),
            ('Hardware',               'fas fa-desktop',       '#3fb950'),
            ('Software / Applications','fas fa-code',          '#bc8cff'),
            ('Email / Communication',  'fas fa-envelope',      '#58a6ff'),
            ('Security / Access',      'fas fa-shield-halved', '#f85149'),
            ('Printers / Peripherals', 'fas fa-print',         '#d29922'),
            ('VoIP / Telephony',       'fas fa-phone',         '#79c0ff'),
            ('User Account',           'fas fa-user-circle',   '#ffa657'),
        ]
        for name, icon, color in cats:
            Category.objects.get_or_create(name=name, defaults={'icon': icon, 'color': color})
        self.stdout.write(self.style.SUCCESS('  ✓ Categories done'))

    # ── VoIP ─────────────────────────────────────────────────────────────────
    def _create_voip_providers(self):
        from voip.models import VoIPProvider
        VoIPProvider.objects.get_or_create(
            name='Asterisk PBX',
            defaults={'host': '192.168.1.10', 'port': 5060, 'protocol': 'SIP', 'is_active': True}
        )
        self.stdout.write(self.style.SUCCESS('  ✓ VoIP provider done'))

    def _create_extensions(self):
        from voip.models import Extension, VoIPProvider
        provider = VoIPProvider.objects.first()
        agents = User.objects.filter(is_staff=True)
        ext_num = 4001
        for agent in agents:
            if not hasattr(agent, 'extension'):
                Extension.objects.get_or_create(
                    extension_number=str(ext_num),
                    defaults={
                        'user': agent,
                        'display_name': agent.get_full_name() or agent.username,
                        'department': 'IT Help Desk',
                        'voip_provider': provider,
                    }
                )
                ext_num += 1
        self.stdout.write(self.style.SUCCESS('  ✓ Extensions done'))

    # ── Tickets ───────────────────────────────────────────────────────────────
    def _create_tickets(self):
        from helpdesk.models import Ticket, Category

        if Ticket.objects.count() > 5:
            self.stdout.write('  ℹ  Tickets already exist, skipping')
            return

        agents  = list(User.objects.filter(is_staff=True))
        cats    = list(Category.objects.all())
        now     = timezone.now()

        samples = [
            ('Cannot connect to VPN from home',             'HIGH',     'OPEN',        'NETWORK / CONNECTIVITY'),
            ('Outlook crashes on startup',                  'MEDIUM',   'IN_PROGRESS', 'SOFTWARE / APPLICATIONS'),
            ('Laptop screen flickering after update',       'HIGH',     'PENDING',     'HARDWARE'),
            ('Printer offline — Finance floor',             'MEDIUM',   'OPEN',        'PRINTERS / PERIPHERALS'),
            ('New user account setup for Chipo Mhuri',     'LOW',      'RESOLVED',    'USER ACCOUNT'),
            ('Wi-Fi drops every 30 minutes in boardroom',   'CRITICAL', 'IN_PROGRESS', 'NETWORK / CONNECTIVITY'),
            ('Microsoft Teams audio not working',           'MEDIUM',   'OPEN',        'VOIP / TELEPHONY'),
            ('Ransomware alert on workstation WS-042',      'CRITICAL', 'IN_PROGRESS', 'SECURITY / ACCESS'),
            ('Password reset for nduna@company.co.zw',     'LOW',      'RESOLVED',    'USER ACCOUNT'),
            ('Email delivery delays to external domains',   'HIGH',     'PENDING',     'EMAIL / COMMUNICATION'),
            ('Monitor not detected after desk move',        'LOW',      'RESOLVED',    'HARDWARE'),
            ('ERP login page showing 503 error',            'CRITICAL', 'OPEN',        'SOFTWARE / APPLICATIONS'),
            ('USB ports disabled on reception PC',          'LOW',      'CLOSED',      'HARDWARE'),
            ('Need Adobe Acrobat licence for new hire',     'LOW',      'PENDING',     'SOFTWARE / APPLICATIONS'),
            ('Internet very slow — ops department',         'HIGH',     'IN_PROGRESS', 'NETWORK / CONNECTIVITY'),
        ]

        requesters = [
            ('Tendai Moyo',     'tendai@company.co.zw',     '+263773001001', 'Finance'),
            ('Rutendo Chikwava', 'rutendo@company.co.zw',   '+263773001002', 'Operations'),
            ('Farai Dube',      'farai@company.co.zw',      '+263773001003', 'HR'),
            ('Blessed Mutema',  'blessed@company.co.zw',    '+263773001004', 'Management'),
            ('Simba Ncube',     'simba@company.co.zw',      '+263773001005', 'Sales'),
        ]
        sources = ['WEB', 'EMAIL', 'PHONE', 'VOIP', 'WALK_IN']

        for i, (title, priority, status, cat_name) in enumerate(samples):
            cat = next((c for c in cats if cat_name.lower() in c.name.lower()), cats[0])
            req = requesters[i % len(requesters)]
            created_at = now - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
            t = Ticket(
                title=title,
                description=f'Issue reported by {req[0]}.\n\nDetails: User is experiencing "{title.lower()}". '
                             f'Please investigate and resolve as soon as possible.\n\nEnvironment: Windows 11, Office 365.',
                category=cat,
                priority=priority,
                status=status,
                source=sources[i % len(sources)],
                requester_name=req[0],
                requester_email=req[1],
                requester_phone=req[2],
                requester_department=req[3],
                assigned_to=agents[i % len(agents)] if agents else None,
            )
            t.save()
            # Back-date created_at via update to bypass auto_now_add
            Ticket.objects.filter(pk=t.pk).update(created_at=created_at)

        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(samples)} tickets created'))

    # ── VoIP Calls ────────────────────────────────────────────────────────────
    def _create_voip_calls(self):
        from voip.models import VoIPCall, Extension, CallerProfile

        if VoIPCall.objects.count() > 5:
            self.stdout.write('  ℹ  VoIP calls already exist, skipping')
            return

        agents = list(User.objects.filter(is_staff=True))
        extensions = list(Extension.objects.all())
        now = timezone.now()

        caller_data = [
            ('+263771100001', 'Tendai Moyo'),
            ('+263771100002', 'Rutendo Chikwava'),
            ('+263772200001', 'Farai Dube'),
            ('+263772200002', 'Blessed Mutema'),
            ('+263773300001', 'Simba Ncube'),
            ('+263773300002', 'Chipo Mhuri'),
            ('+263771100003', None),
            ('+263712345678', 'External Caller'),
        ]

        statuses = ['COMPLETED', 'COMPLETED', 'COMPLETED', 'MISSED', 'COMPLETED', 'VOICEMAIL']
        directions = ['INBOUND', 'INBOUND', 'OUTBOUND', 'INBOUND', 'INTERNAL', 'INBOUND']

        calls_created = 0
        for i in range(20):
            caller_num, caller_name = caller_data[i % len(caller_data)]
            status = statuses[i % len(statuses)]
            direction = directions[i % len(directions)]
            talk_secs = random.randint(30, 900) if status == 'COMPLETED' else 0
            initiated = now - timedelta(days=random.randint(0, 7), hours=random.randint(0, 12), minutes=random.randint(0, 59))
            answered = initiated + timedelta(seconds=random.randint(3, 20)) if status not in ['MISSED', 'VOICEMAIL'] else None
            ended = answered + timedelta(seconds=talk_secs) if answered else None
            dest_ext = extensions[i % len(extensions)] if extensions else None

            call = VoIPCall.objects.create(
                caller_number=caller_num,
                caller_name=caller_name or '',
                destination_number=dest_ext.extension_number if dest_ext else '4001',
                destination_extension=dest_ext,
                direction=direction,
                status=status,
                initiated_at=initiated,
                answered_at=answered,
                ended_at=ended,
                answered_by=agents[i % len(agents)] if agents and answered else None,
                talk_duration_seconds=talk_secs,
                notes='Demo call entry' if i % 3 == 0 else '',
            )

            # Update/create caller profile
            profile, _ = CallerProfile.objects.get_or_create(phone_number=caller_num)
            if caller_name and not profile.name:
                profile.name = caller_name
            profile.total_calls += 1
            profile.last_call = initiated
            profile.save()
            calls_created += 1

        self.stdout.write(self.style.SUCCESS(f'  ✓ {calls_created} VoIP calls created'))
