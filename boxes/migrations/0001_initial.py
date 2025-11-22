from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='GPSModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=255)),
                ('fabricante', models.CharField(blank=True, max_length=255)),
                ('tecnologia', models.CharField(blank=True, max_length=255)),
                ('interface_conexao', models.CharField(blank=True, max_length=255)),
                ('protocolo', models.CharField(blank=True, max_length=255)),
                ('taxa_atualizacao_hz', models.PositiveIntegerField(blank=True, null=True)),
                ('antena_externa', models.BooleanField(default=False)),
                ('observacoes', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'Modelo de GPS',
                'verbose_name_plural': 'Modelos de GPS',
            },
        ),
        migrations.CreateModel(
            name='HardwareModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=255)),
                ('fabricante', models.CharField(blank=True, max_length=255)),
                ('cpu', models.CharField(blank=True, max_length=255)),
                ('arquitetura', models.CharField(blank=True, max_length=100)),
                ('memoria_max_gb', models.PositiveIntegerField(blank=True, null=True)),
                ('armazenamento', models.CharField(blank=True, max_length=255)),
                ('portas_lan', models.PositiveIntegerField(blank=True, null=True)),
                ('wifi', models.BooleanField(default=False)),
                ('observacoes', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'Modelo de Hardware',
                'verbose_name_plural': 'Modelos de Hardware',
            },
        ),
        migrations.CreateModel(
            name='Box',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=255)),
                ('ativo', models.BooleanField(default=True)),
                ('hostname', models.CharField(max_length=255, unique=True)),
                ('chave_api_wireguard', models.CharField(blank=True, max_length=255)),
                ('chave_api_opnsense', models.CharField(blank=True, max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('gps_model', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='boxes', to='boxes.gpsmodel')),
                ('hardware_model', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='boxes', to='boxes.hardwaremodel')),
            ],
            options={
                'verbose_name': 'Box',
                'verbose_name_plural': 'Boxes',
                'ordering': ['-id'],
            },
        ),
    ]
