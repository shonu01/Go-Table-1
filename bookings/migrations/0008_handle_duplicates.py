from django.db import migrations

def handle_duplicates(apps, schema_editor):
    Booking = apps.get_model('bookings', 'Booking')
    db_alias = schema_editor.connection.alias

    # Get all bookings
    bookings = Booking.objects.using(db_alias).all()
    seen = set()
    duplicates = []

    # Find duplicates
    for booking in bookings:
        key = (booking.restaurant_id, booking.booking_date, booking.booking_time)
        if key in seen:
            duplicates.append(booking)
        else:
            seen.add(key)

    # Delete duplicates
    for booking in duplicates:
        booking.delete()

class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0007_add_seating_preference'),
    ]

    operations = [
        migrations.RunPython(handle_duplicates),
    ]
