from django.db import migrations, models


def copy_customer_names(apps, schema_editor):
    Appointment = apps.get_model('agenda', 'Appointment')
    batch = []

    for appointment in Appointment.objects.select_related('customer').iterator():
        appointment.customer_name = appointment.customer.name
        batch.append(appointment)
        if len(batch) >= 500:
            Appointment.objects.bulk_update(batch, ['customer_name'])
            batch.clear()

    if batch:
        Appointment.objects.bulk_update(batch, ['customer_name'])


class Migration(migrations.Migration):

    dependencies = [
        ('agenda', '0002_provider_workspaces'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='customer_name',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
        migrations.RunPython(copy_customer_names, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='appointment',
            name='customer',
        ),
        migrations.RenameField(
            model_name='appointment',
            old_name='customer_name',
            new_name='customer',
        ),
        migrations.AlterField(
            model_name='appointment',
            name='customer',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
    ]
