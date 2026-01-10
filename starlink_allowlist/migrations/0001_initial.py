from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='StarlinkASN',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveIntegerField(unique=True)),
                ('name', models.CharField(blank=True, max_length=200)),
                ('enabled', models.BooleanField(default=True)),
                ('americas_only', models.BooleanField(default=True, help_text='Se true, a API padrão expõe apenas prefixes classificados como Américas.')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Starlink ASN',
                'verbose_name_plural': 'Starlink ASNs',
                'ordering': ['number'],
            },
        ),
        migrations.CreateModel(
            name='StarlinkUpdateRun',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('started_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('finished_at', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(choices=[('success', 'Success'), ('error', 'Error')], default='success', max_length=20)),
                ('source', models.CharField(default='bgpview', max_length=50)),
                ('asns', models.JSONField(blank=True, default=list)),
                ('total_prefixes', models.PositiveIntegerField(default=0)),
                ('added_prefixes', models.PositiveIntegerField(default=0)),
                ('removed_prefixes', models.PositiveIntegerField(default=0)),
                ('error', models.TextField(blank=True)),
                ('details', models.JSONField(blank=True, default=dict)),
            ],
            options={
                'verbose_name': 'Starlink Update Run',
                'verbose_name_plural': 'Starlink Update Runs',
                'ordering': ['-started_at'],
            },
        ),
        migrations.CreateModel(
            name='StarlinkPrefix',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cidr', models.CharField(max_length=43, unique=True)),
                ('ip_version', models.PositiveSmallIntegerField(choices=[(4, 'IPv4'), (6, 'IPv6')])),
                ('rir', models.CharField(blank=True, help_text='Ex: arin, lacnic, ripe, apnic, afrinic, nicbr', max_length=20)),
                ('country', models.CharField(blank=True, help_text='ISO-3166 alpha-2 quando disponível', max_length=2)),
                ('is_americas', models.BooleanField(default=True)),
                ('first_seen_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_seen_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('active', models.BooleanField(default=True)),
                ('asn', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='prefixes', to='starlink_allowlist.starlinkasn')),
            ],
            options={
                'verbose_name': 'Starlink Prefix',
                'verbose_name_plural': 'Starlink Prefixes',
                'ordering': ['ip_version', 'cidr'],
            },
        ),
    ]
