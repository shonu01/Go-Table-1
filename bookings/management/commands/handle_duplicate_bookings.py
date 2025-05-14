from django.core.management.base import BaseCommand
from django.db.models import Count
from bookings.models import Booking

class Command(BaseCommand):
    help = 'Handles duplicate bookings by keeping only the latest one for each time slot'

    def handle(self, *args, **options):
        # Find all duplicate bookings
        duplicates = (
            Booking.objects.values('restaurant_id', 'booking_date', 'booking_time')
            .annotate(count=Count('id'))
            .filter(count__gt=1)
        )

        for duplicate in duplicates:
            # Get all bookings for this combination
            bookings = Booking.objects.filter(
                restaurant_id=duplicate['restaurant_id'],
                booking_date=duplicate['booking_date'],
                booking_time=duplicate['booking_time']
            ).order_by('-created_at')  # Order by creation time, newest first

            # Keep the first one (newest) and delete the rest
            latest_booking = bookings.first()
            bookings.exclude(id=latest_booking.id).delete()

            self.stdout.write(
                self.style.SUCCESS(
                    f'Handled duplicate bookings for restaurant {duplicate["restaurant_id"]} '
                    f'at {duplicate["booking_date"]} {duplicate["booking_time"]}'
                )
            )
