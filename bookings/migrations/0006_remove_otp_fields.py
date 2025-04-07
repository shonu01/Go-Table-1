from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0005_booking_is_otp_verified'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='otp',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='is_otp_verified',
        ),
    ]
