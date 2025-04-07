import os
import django
import random
from datetime import time
from django.utils.text import slugify

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gotable.settings')
django.setup()

# Import models after Django setup
from django.contrib.auth import get_user_model
from restaurants.models import Restaurant
from accounts.models import CustomUser

def create_sample_restaurants():
    # Sample cuisine types
    cuisine_types = [
        'Italian', 'Chinese', 'Indian', 'Mexican', 'Japanese', 
        'Thai', 'French', 'Greek', 'American', 'Spanish'
    ]
    
    # Sample price ranges
    price_ranges = ['$', '$$', '$$$', '$$$$']
    
    # Create admin user if not exists
    User = get_user_model()
    
    try:
        admin_user = User.objects.get(username='admin')
    except User.DoesNotExist:
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123',
            is_restaurant_owner=True
        )
        print("Admin user created")
    
    # Create 10 sample restaurants
    for i in range(1, 11):
        cuisine = random.choice(cuisine_types)
        price_range = random.choice(price_ranges)
        name = f"{cuisine} Restaurant {i}"
        
        # Create restaurant if not exists
        if not Restaurant.objects.filter(slug=slugify(name)).exists():
            restaurant = Restaurant.objects.create(
                name=name,
                owner=admin_user,
                description=f"A wonderful {cuisine.lower()} restaurant offering delicious food in a cozy atmosphere.",
                address=f"{random.randint(100, 999)} Main Street",
                city=random.choice(['New York', 'Chicago', 'Los Angeles', 'San Francisco', 'Miami']),
                state=random.choice(['NY', 'IL', 'CA', 'CA', 'FL']),
                country='USA',
                postal_code=f"{random.randint(10000, 99999)}",
                phone=f"+1-{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                email=f"info@{name.lower().replace(' ', '')}.com",
                website=f"https://www.{name.lower().replace(' ', '')}.com",
                cuisine_type=cuisine,
                price_range=price_range,
                opening_time=time(hour=11, minute=0),
                closing_time=time(hour=22, minute=0),
                is_active=True,
                is_featured=random.choice([True, False]),
                rating=round(random.uniform(3.0, 5.0), 1)
            )
            print(f"Created restaurant: {name}")
        else:
            print(f"Restaurant already exists: {name}")
    
    print(f"Total restaurants in database: {Restaurant.objects.count()}")

if __name__ == "__main__":
    print("Creating sample restaurants...")
    create_sample_restaurants()
    print("Done!") 