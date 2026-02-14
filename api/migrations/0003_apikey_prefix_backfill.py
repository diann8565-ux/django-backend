from django.db import migrations

def backfill_prefix(apps, schema_editor):
    ApiKey = apps.get_model('api', 'ApiKey')
    for ak in ApiKey.objects.filter(prefix=''):
        if ak.key:
            ak.prefix = ak.key[:7]
            ak.save(update_fields=['prefix'])

class Migration(migrations.Migration):
    dependencies = [
        ('api', '0002_sharelink_alter_activitylog_options_and_more'),
    ]

    operations = [
        migrations.RunPython(backfill_prefix, migrations.RunPython.noop),
    ]
