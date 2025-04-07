from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Restaurant, Table, MenuItem, Review
from .forms import RestaurantForm, TableForm, MenuItemForm, ReviewForm
from django.db.models import Avg
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
import json
from .chatbot import RestaurantChatbot

def home(request):
    featured_restaurants = Restaurant.objects.filter(is_active=True, is_featured=True)[:6]
    popular_restaurants = Restaurant.objects.filter(is_active=True).order_by('-rating')[:6]
    cities = Restaurant.objects.filter(is_active=True).values_list('city', flat=True).distinct()

    return render(request, 'restaurants/home.html', {
        'featured_restaurants': featured_restaurants,
        'popular_restaurants': popular_restaurants,
        'cities': cities,
    })

def restaurant_list(request):
    restaurants = Restaurant.objects.filter(is_active=True)

    # Get filter parameters
    query = request.GET.get('q', '')
    city = request.GET.get('city', '')
    cuisine = request.GET.get('cuisine', '')
    price_range = request.GET.get('price_range', '')
    rating = request.GET.get('rating', '')
    sort = request.GET.get('sort', 'rating')

    # Apply filters
    if query:
        restaurants = restaurants.filter(
            Q(name__icontains=query) |
            Q(cuisine_type__icontains=query) |
            Q(city__icontains=query) |
            Q(state__icontains=query)
        )

    if city:
        restaurants = restaurants.filter(city=city)

    if cuisine:
        restaurants = restaurants.filter(cuisine_type=cuisine)

    if price_range:
        restaurants = restaurants.filter(price_range=price_range)

    if rating:
        try:
            rating = float(rating)
            restaurants = restaurants.filter(rating__gte=rating)
        except ValueError:
            pass  # Ignore invalid rating values

    # Apply sorting
    sort_options = {
        'rating': '-rating',
        'price_low': 'price_range',
        'price_high': '-price_range'
    }
    restaurants = restaurants.order_by(sort_options.get(sort, '-rating'))  # Default sort by rating

    # Get unique values for filters
    cities = Restaurant.objects.filter(is_active=True).values_list('city', flat=True).distinct()
    cuisines = Restaurant.objects.filter(is_active=True).values_list('cuisine_type', flat=True).distinct()
    price_ranges = Restaurant.objects.filter(is_active=True).values_list('price_range', flat=True).distinct()
    ratings = [1, 2, 3, 4, 5]

    # Pagination
    paginator = Paginator(restaurants, 12)
    page = request.GET.get('page')
    restaurants = paginator.get_page(page)

    return render(request, 'restaurants/restaurant_list.html', {
        'restaurants': restaurants,
        'query': query,
        'selected_city': city,
        'selected_cuisine': cuisine,
        'selected_price': price_range,
        'selected_rating': rating,
        'sort': sort,
        'cities': cities,
        'cuisines': cuisines,
        'price_ranges': price_ranges,
        'ratings': ratings,
    })

def restaurant_detail_by_id(request, id):
    restaurant = get_object_or_404(Restaurant, id=id)
    return redirect('restaurants:detail', slug=restaurant.slug)

def restaurant_detail(request, slug):
    restaurant = get_object_or_404(Restaurant, slug=slug)
    menu_items = MenuItem.objects.filter(restaurant=restaurant, is_available=True)
    tables = Table.objects.filter(restaurant=restaurant)
    reviews = Review.objects.filter(restaurant=restaurant).select_related('user').order_by('-created_at')
    
    # Check if user has already reviewed
    user_has_reviewed = False
    if request.user.is_authenticated:
        user_has_reviewed = reviews.filter(user=request.user).exists()
    
    # Calculate average rating
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Group menu items by category
    menu_by_category = {}
    for item in menu_items:
        if item.category not in menu_by_category:
            menu_by_category[item.category] = []
        menu_by_category[item.category].append(item)
    
    context = {
        'restaurant': restaurant,
        'menu_by_category': menu_by_category,
        'tables': tables,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'user_has_reviewed': user_has_reviewed,
    }
    
    return render(request, 'restaurants/restaurant_detail.html', context)

@login_required
def restaurant_create(request):
    if not hasattr(request.user, 'is_restaurant_owner') or not request.user.is_restaurant_owner:
        messages.error(request, 'You must be a restaurant owner to create a restaurant.')
        return redirect('restaurants:home')

    form = RestaurantForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        restaurant = form.save(commit=False)
        restaurant.owner = request.user
        restaurant.save()
        messages.success(request, 'Restaurant created successfully!')
        return redirect('restaurants:detail', slug=restaurant.slug)

    return render(request, 'restaurants/restaurant_form.html', {'form': form})

@login_required
def restaurant_edit(request, slug):
    restaurant = get_object_or_404(Restaurant, slug=slug, owner=request.user)

    form = RestaurantForm(request.POST or None, request.FILES or None, instance=restaurant)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Restaurant updated successfully!')
        return redirect('restaurants:detail', slug=slug)

    return render(request, 'restaurants/restaurant_form.html', {'form': form})

@login_required
def table_management(request, slug):
    restaurant = get_object_or_404(Restaurant, slug=slug, owner=request.user)
    tables = restaurant.tables.all()

    form = TableForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        table = form.save(commit=False)
        table.restaurant = restaurant
        table.save()
        messages.success(request, 'Table added successfully!')
        return redirect('restaurants:table_management', slug=slug)

    return render(request, 'restaurants/table_management.html', {
        'restaurant': restaurant,
        'tables': tables,
        'form': form
    })

@login_required
def menu_management(request, slug):
    restaurant = get_object_or_404(Restaurant, slug=slug, owner=request.user)
    menu_items = restaurant.menu_items.all()

    form = MenuItemForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        menu_item = form.save(commit=False)
        menu_item.restaurant = restaurant
        menu_item.save()
        messages.success(request, 'Menu item added successfully!')
        return redirect('restaurants:menu_management', slug=slug)

    return render(request, 'restaurants/menu_management.html', {
        'restaurant': restaurant,
        'menu_items': menu_items,
        'form': form
    })

@require_http_methods(["GET", "POST"])
@ensure_csrf_cookie
def chatbot_view(request):
    if request.method == "GET":
        # Initialize chatbot state
        request.session['chatbot_state'] = {
            'conversation_state': 'greeting',
            'context': {}
        }
        request.session.save()
        return JsonResponse({
            'type': 'text',
            'content': 'Hi there! 👋 To get started, just say hello!'
        })

    try:
        # Ensure we have a session
        if not request.session.session_key:
            request.session.create()
        
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        
        if not message:
            return JsonResponse({
                'type': 'text',
                'content': 'Please enter a message.'
            })
        
        # Get or create chatbot instance
        chatbot = request.session.get('chatbot_state')
        if not chatbot:
            chatbot = {
                'conversation_state': 'greeting',
                'context': {}
            }
            request.session['chatbot_state'] = chatbot
            request.session.save()
        
        # Create chatbot instance with saved state
        bot = RestaurantChatbot()
        bot.conversation_state = chatbot.get('conversation_state', 'greeting')
        bot.context = chatbot.get('context', {})
        
        # Get response
        response = bot.get_response(message)
        
        # Save updated state
        request.session['chatbot_state'] = {
            'conversation_state': bot.conversation_state,
            'context': bot.context
        }
        request.session.modified = True
        request.session.save()
        
        return JsonResponse(response)
    except json.JSONDecodeError:
        return JsonResponse({
            'type': 'text',
            'content': 'Invalid request format.'
        }, status=400)
    except Exception as e:
        print(f'Chatbot error: {str(e)}')
        # Clear session state on error
        if 'chatbot_state' in request.session:
            del request.session['chatbot_state']
            request.session.save()
        return JsonResponse({
            'type': 'text',
            'content': 'I apologize, but I encountered an issue. Let\'s start over - just say hello! 👋'
        }, status=200)
