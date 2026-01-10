from django.db import migrations


def seed_starlink_asn(apps, schema_editor):
    StarlinkASN = apps.get_model('starlink_allowlist', 'StarlinkASN')
    StarlinkASN.objects.get_or_create(
        number=14593,
        defaults={
            'name': 'SpaceX / Starlink',
            'enabled': True,
            'americas_only': True,
        },
    )


def unseed_starlink_asn(apps, schema_editor):
    StarlinkASN = apps.get_model('starlink_allowlist', 'StarlinkASN')
    StarlinkASN.objects.filter(number=14593).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('starlink_allowlist', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_starlink_asn, reverse_code=unseed_starlink_asn),
    ]
