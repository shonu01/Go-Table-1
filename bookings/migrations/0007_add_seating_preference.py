from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0006_remove_otp_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='seating_preference',
            field=models.CharField(
                choices=[
                    ('standard', 'Standard Table'),
                    ('booth', 'Booth'),
                    ('outdoor', 'Outdoor Seating'),
                    ('private_room', 'Private Room'),
                    ('bar', 'Bar Seating'),
                    ('high_top', 'High Top Table'),
                    ('window', 'Window Table'),
                    ('counter', 'Counter Seating'),
                ],
                default='standard',
                max_length=20
            ),
        ),
    ]
