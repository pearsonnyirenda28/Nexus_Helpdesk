from django.db import migrations


def insert_categories(apps, schema_editor):
    Category = apps.get_model('helpdesk', 'Category')

    categories = [
        "Network / Connectivity",
        "Hardware",
        "Software / Applications",
        "Email / Communication",
        "Security / Access",
        "Printers / Peripherals",
        "VoIP / Telephony",
        "User Account",
    ]

    for name in categories:
        Category.objects.get_or_create(name=name)


def remove_categories(apps, schema_editor):
    Category = apps.get_model('helpdesk', 'Category')
    categories = [
        "Network / Connectivity",
        "Hardware",
        "Software / Applications",
        "Email / Communication",
        "Security / Access",
        "Printers / Peripherals",
        "VoIP / Telephony",
        "User Account",
    ]
    Category.objects.filter(name__in=categories).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('helpdesk', '0004_add_requester_section'),
    ]

    operations = [
        migrations.RunPython(insert_categories, reverse_code=remove_categories),
    ]