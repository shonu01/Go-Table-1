import os
import django
import datetime
import random
from django.utils.text import slugify

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gotable.settings')
django.setup()

from restaurants.models import Restaurant
from accounts.models import CustomUser
from django.utils import timezone

def create_sample_restaurants():
    # Make sure we have at least one user who is a restaurant owner
    try:
        owner = CustomUser.objects.get(username='restaurantowner')
    except CustomUser.DoesNotExist:
        owner = CustomUser.objects.create_user(
            username='restaurantowner',
            email='owner@example.com',
            password='password123',
            is_restaurant_owner=True,
            first_name='Restaurant',
            last_name='Owner'
        )
    
    # Restaurant data with variety
    cuisines = ['Italian', 'Japanese', 'American', 'Indian', 'Mexican', 'French', 'Chinese', 'Greek', 'Thai', 'Mediterranean']
    cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Miami', 'San Francisco', 'Seattle', 'Boston', 'Dallas', 'Atlanta']
    states = ['NY', 'CA', 'IL', 'TX', 'FL', 'CA', 'WA', 'MA', 'TX', 'GA']
    price_ranges = ['$', '$$', '$$$', '$$$$']
    
    # Restaurant name parts
    prefixes = ['Delicious', 'Tasty', 'Gourmet', 'Savory', 'Classic', 'Spicy', 'Fresh', 'Modern', 'Royal', 'Elite']
    nouns = ['Kitchen', 'Bistro', 'Grill', 'House', 'Garden', 'Cafe', 'Diner', 'Restaurant', 'Eatery', 'Palace']
    
    # Opening and closing times
    opening_times = [
        datetime.time(8, 0), datetime.time(9, 0), datetime.time(10, 0), 
        datetime.time(11, 0), datetime.time(12, 0)
    ]
    closing_times = [
        datetime.time(20, 0), datetime.time(21, 0), datetime.time(22, 0), 
        datetime.time(23, 0), datetime.time(0, 0)
    ]
    
    # Generate 10 random restaurants
    for i in range(10):
        cuisine = cuisines[i % len(cuisines)]
        city = cities[i % len(cities)]
        state = states[i % len(states)]
        
        # Create a random restaurant name
        name = f"{random.choice(prefixes)} {cuisine} {random.choice(nouns)}"
        
        # Skip if restaurant with same name already exists
        if Restaurant.objects.filter(name=name).exists():
            print(f"Restaurant '{name}' already exists, skipping...")
            continue
            
        # Random data for each restaurant
        restaurant_data = {
            'name': name,
            'description': f"Experience authentic {cuisine} cuisine in a {random.choice(['cozy', 'elegant', 'modern', 'rustic', 'vibrant'])} atmosphere. Our chefs use only the freshest ingredients to create memorable dining experiences.",
            'address': f"{random.randint(100, 999)} {random.choice(['Main', 'Oak', 'Maple', 'Pine', 'Cedar'])} {random.choice(['St', 'Ave', 'Blvd', 'Rd'])}",
            'city': city,
            'state': state,
            'country': 'USA',
            'postal_code': f"{random.randint(10000, 99999)}",
            'phone': f"({random.randint(200, 999)}) {random.randint(100, 999)}-{random.randint(1000, 9999)}",
            'email': f"info@{name.lower().replace(' ', '')}.com",
            'website': f"http://www.{name.lower().replace(' ', '')}.com",
            'cuisine_type': cuisine,
            'price_range': random.choice(price_ranges),
            'opening_time': random.choice(opening_times),
            'closing_time': random.choice(closing_times),
            'is_active': True,
            'is_featured': random.choice([True, False]),
            'rating': round(random.uniform(3.0, 5.0), 1)  # Random rating between 3.0 and 5.0
        }
        
        # Create slug from name
        slug = slugify(restaurant_data['name'])
        
        # Create the restaurant
        restaurant = Restaurant(
            name=restaurant_data['name'],
            slug=slug,
            owner=owner,
            description=restaurant_data['description'],
            address=restaurant_data['address'],
            city=restaurant_data['city'],
            state=restaurant_data['state'],
            country=restaurant_data['country'],
            postal_code=restaurant_data['postal_code'],
            phone=restaurant_data['phone'],
            email=restaurant_data['email'],
            website=restaurant_data['website'],
            cuisine_type=restaurant_data['cuisine_type'],
            price_range=restaurant_data['price_range'],
            opening_time=restaurant_data['opening_time'],
            closing_time=restaurant_data['closing_time'],
            is_active=restaurant_data['is_active'],
            is_featured=restaurant_data['is_featured'],
            rating=restaurant_data['rating'],
        )
        restaurant.save()
        print(f"Created restaurant: {restaurant.name} ({restaurant.cuisine_type})")

if __name__ == '__main__':
    print("Creating sample restaurants...")
    create_sample_restaurants()
    print("Done!") 