from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0008_handle_duplicates'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='booking',
            constraint=models.UniqueConstraint(
                fields=['restaurant', 'booking_date', 'booking_time'],
                name='unique_restaurant_booking'
            ),
        ),
    ]
