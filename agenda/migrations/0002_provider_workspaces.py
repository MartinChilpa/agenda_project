from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def assign_existing_records(apps, schema_editor):
    User = apps.get_model(*settings.AUTH_USER_MODEL.split('.'))
    models_to_assign = [
        apps.get_model('agenda', 'ServiceType'),
        apps.get_model('agenda', 'Customer'),
        apps.get_model('agenda', 'BlockedSlot'),
        apps.get_model('agenda', 'Appointment'),
    ]

    provider = User.objects.filter(role='PROVIDER').order_by('id').first()
    if provider is None:
        provider = User.objects.order_by('id').first()

    has_existing_records = any(model.objects.exists() for model in models_to_assign)
    if has_existing_records and provider is None:
        raise RuntimeError(
            'No se pueden asignar los registros de agenda porque no existe un usuario proveedor.'
        )

    if provider is not None:
        for model in models_to_assign:
            model.objects.filter(provider__isnull=True).update(provider_id=provider.pk)


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('agenda', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicetype',
            name='provider',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='service_types',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='customer',
            name='provider',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='customers',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='blockedslot',
            name='provider',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='blocked_slots',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='appointment',
            name='provider',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='appointments',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(assign_existing_records, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='servicetype',
            name='provider',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='service_types',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name='customer',
            name='provider',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='customers',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name='blockedslot',
            name='provider',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='blocked_slots',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='provider',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='appointments',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
