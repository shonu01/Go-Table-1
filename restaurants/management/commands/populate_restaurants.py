from django.core.management.base import BaseCommand
from restaurants.models import Restaurant
from django.utils import timezone

class Command(BaseCommand):
    help = 'Populate the database with sample restaurants'

    def handle(self, *args, **kwargs):
        # Sample data for restaurants
        restaurants_data = [
            {
                'name': 'Italiano Delight',
                'cuisine': 'Italian',
                'location': 'Downtown',
                'price_range': 2,
                'rating': 4.5,
                'description': 'Authentic Italian cuisine in the heart of downtown.',
                'is_active': True,
            },
            {
                'name': 'Dragon Palace',
                'cuisine': 'Chinese',
                'location': 'Uptown',
                'price_range': 2,
                'rating': 4.3,
                'description': 'Traditional Chinese dishes with a modern twist.',
                'is_active': True,
            },
            {
                'name': 'Taj Mahal',
                'cuisine': 'Indian',
                'location': 'Midtown',
                'price_range': 2,
                'rating': 4.4,
                'description': 'Authentic Indian cuisine with rich flavors.',
                'is_active': True,
            },
            {
                'name': 'Sushi Master',
                'cuisine': 'Japanese',
                'location': 'Downtown',
                'price_range': 3,
                'rating': 4.7,
                'description': 'Premium sushi and Japanese delicacies.',
                'is_active': True,
            },
            {
                'name': 'Mediterranean Oasis',
                'cuisine': 'Mediterranean',
                'location': 'Uptown',
                'price_range': 2,
                'rating': 4.2,
                'description': 'Fresh Mediterranean dishes in a cozy atmosphere.',
                'is_active': True,
            },
            {
                'name': 'Taco Fiesta',
                'cuisine': 'Mexican',
                'location': 'Midtown',
                'price_range': 1,
                'rating': 4.1,
                'description': 'Authentic Mexican street food and tacos.',
                'is_active': True,
            },
            {
                'name': 'Le Petit Bistro',
                'cuisine': 'French',
                'location': 'Downtown',
                'price_range': 3,
                'rating': 4.6,
                'description': 'Classic French cuisine in an elegant setting.',
                'is_active': True,
            },
            {
                'name': 'Seoul Kitchen',
                'cuisine': 'Korean',
                'location': 'Uptown',
                'price_range': 2,
                'rating': 4.4,
                'description': 'Authentic Korean BBQ and traditional dishes.',
                'is_active': True,
            },
        ]

        # Create restaurants
        created_count = 0
        for data in restaurants_data:
            restaurant, created = Restaurant.objects.get_or_create(
                name=data['name'],
                defaults={
                    'cuisine': data['cuisine'],
                    'location': data['location'],
                    'price_range': data['price_range'],
                    'rating': data['rating'],
                    'description': data['description'],
                    'is_active': data['is_active'],
                    'created_at': timezone.now(),
                }
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} restaurants')
        )
