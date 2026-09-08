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

        # ── Terms & Conditions ────────────────────────────────────────────────
        from accounts.models import TermsVersion
        if not TermsVersion.objects.filter(is_current=True).exists():
            from django.utils import timezone as tz
            admin_user = User.objects.filter(is_superuser=True).first()
            today = tz.now().strftime('%d %B %Y')
            TermsVersion.objects.create(
                version='1.0',
                title='BeitDesk System Terms & Conditions',
                is_current=True,
                effective_date=tz.now().date(),
                created_by=admin_user,
                content=f"""MUNICIPALITY OF BEITBRIDGE — IT HELP DESK SYSTEM
TERMS AND CONDITIONS OF USE — Version 1.0
Effective Date: {today}

1. SYSTEM OVERVIEW
BeitDesk is the official IT Help Desk and Asset Management System of the Municipality of Beitbridge. By logging in you agree to these Terms and Conditions.

2. AUTHORISED USE
2.1 Access is granted exclusively to authorised employees, contractors, and agents of the Municipality of Beitbridge.
2.2 You must use only your own login credentials. Sharing your username or password is strictly prohibited.
2.3 This system must be used only for legitimate municipal IT support and asset management purposes.
2.4 Unauthorised access or misuse constitutes a disciplinary offence and may result in criminal prosecution under the Zimbabwean Cyber and Data Protection Act [Chapter 12:07].

3. DATA PRIVACY AND PROTECTION
3.1 This system collects personal data (names, email addresses, phone numbers, department information) solely for IT support purposes.
3.2 All data is processed in accordance with the Cyber and Data Protection Act [Chapter 12:07] of Zimbabwe.
3.3 Your activity within this system is fully logged and audited. Every action you perform — including ticket creation, status changes, comments, and logins — is recorded with a timestamp and IP address.
3.4 Data stored in this system is the property of the Municipality of Beitbridge and must not be shared externally without authorisation from the IT Manager or Municipal Director.

4. SENSITIVE DATA
4.1 Do NOT include classified government information, financial account numbers, banking details, or national ID numbers in ticket descriptions or comments.
4.2 Ticket data may be reviewed by IT staff and administrators for support, reporting, and audit purposes.
4.3 Support tickets may be used for IT trend analysis and service improvement planning.

5. MULTI-FACTOR AUTHENTICATION (MFA)
5.1 The Municipality of Beitbridge strongly recommends that all users enable Multi-Factor Authentication (MFA) to protect their accounts and municipal data.
5.2 Two MFA methods are available: Face Recognition (browser-based, no data leaves your device) and Time-Based One-Time Password (TOTP) via Google Authenticator, Authy, or Microsoft Authenticator.
5.3 Users may enable or disable MFA at any time from the Security section in their account settings.
5.4 Face biometric embeddings are stored securely on the municipal server only and are never transmitted to or shared with any third party.
5.5 The Municipality of Beitbridge accepts no liability for unauthorised account access where MFA was available but not enabled by the user.
5.6 After 5 consecutive failed face recognition attempts, your account will be temporarily locked for 15 minutes. Contact the IT Help Desk to unlock immediately.

6. IT ASSET REGISTRY
6.1 IT assets assigned to you remain the property of the Municipality of Beitbridge at all times.
6.2 You are personally responsible for the care, security, and safekeeping of any IT equipment assigned to you.
6.3 Loss, damage, theft, or unauthorised transfer of municipal IT assets must be reported immediately to the IT Help Desk by raising a ticket.
6.4 Asset tags must not be removed or defaced.

7. KNOWLEDGE BASE
7.1 Knowledge Base articles are internal IT guidance documents provided to help staff resolve common IT issues.
7.2 Do not share Knowledge Base content externally without IT Manager authorisation.
7.3 Only authorised IT staff may create, edit, or delete Knowledge Base articles.

8. SYSTEM AVAILABILITY
8.1 BeitDesk is maintained on a best-effort basis during business hours: 08:00–17:00, Monday to Friday (excluding public holidays).
8.2 Planned maintenance will be communicated in advance where possible. Emergency maintenance may occur without prior notice.

9. PROHIBITED ACTIONS
You must NOT:
- Attempt to access other users' accounts, tickets, or data without authorisation
- Store, share, or distribute offensive, illegal, or inappropriate content through this system
- Attempt to circumvent, disable, or bypass security controls or audit logging
- Use automated scripts, bots, or tools to interact with this system without IT Manager approval
- Extract, copy, or share bulk data from the system for any unauthorised purpose
- Install unauthorised software using IT department resources

10. CONSEQUENCES OF VIOLATION
Violations of these Terms may result in:
- Immediate suspension or permanent revocation of system access
- Disciplinary action in accordance with the Municipal Human Resources Policy
- Civil or criminal prosecution where applicable under Zimbabwean law, including the Cyber and Data Protection Act [Chapter 12:07]

11. UPDATES TO THESE TERMS
The Municipality of Beitbridge reserves the right to update these Terms and Conditions at any time. When a new version is published, all users will be required to read and re-accept the updated Terms on their next login before accessing the system.

12. GOVERNING LAW
These Terms are governed by the laws of Zimbabwe. Any disputes shall be subject to the jurisdiction of the courts of Zimbabwe.

13. CONTACT
For questions about these Terms and Conditions, contact:
IT Department — Municipality of Beitbridge
Beitbridge, Matabeleland South, Zimbabwe

By clicking "I Accept — Enter BeitDesk" you confirm that you have read, fully understood, and agree to be legally bound by these Terms and Conditions of Use."""
            )
            self.stdout.write(self.style.SUCCESS('  ✓ T&C v1.0 seeded'))
        else:
            self.stdout.write('  ℹ  T&C already exists, skipping')
