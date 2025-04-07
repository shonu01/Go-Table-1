from django.db.models import Q
from django.db.models import Avg
from .models import Restaurant
from difflib import get_close_matches
import re

class RestaurantChatbot:
    def __init__(self):
        self.greetings = ['hi', 'hello', 'hey', 'hola', 'good morning', 'good afternoon', 'good evening']
        self.farewells = ['bye', 'goodbye', 'see you', 'thanks', 'thank you', 'cya']
        self.context = {}
        self._cuisines = None
        self._locations = None
        self.price_keywords = {'cheap': 1, 'affordable': 2, 'moderate': 2, 'expensive': 3, 'luxury': 3}
        self.rating_keywords = {'best': 4.5, 'good': 4.0, 'average': 3.0, 'poor': 2.0}
        self.conversation_state = 'greeting'  # States: greeting, ask_cuisine, ask_location, searching, farewell

    @property
    def cuisines(self):
        if self._cuisines is None:
            try:
                self._cuisines = set(Restaurant.objects.values_list('cuisine_type', flat=True).distinct())
            except Exception:
                self._cuisines = set()
        return self._cuisines

    @property
    def locations(self):
        if self._locations is None:
            try:
                self._locations = set(Restaurant.objects.values_list('city', flat=True).distinct())
            except Exception:
                self._locations = set()
        return self._locations
        
    def get_response(self, message):
        """Process user message and return appropriate response"""
        try:
            message = message.lower().strip()
            
            # Check for farewells first
            if any(farewell in message for farewell in self.farewells):
                self.conversation_state = 'farewell'
                self.context = {}  # Clear context
                return {
                    'type': 'text',
                    'content': 'Thank you for chatting with me! I hope you found what you were looking for. Have a great meal and come back anytime! 👋'
                }

            # Handle different conversation states
            if self.conversation_state == 'greeting':
                if any(greeting in message for greeting in self.greetings):
                    self.conversation_state = 'ask_cuisine'
                    available_cuisines = list(self.cuisines)[:5] if self.cuisines else ['Italian', 'Chinese', 'Indian']
                    return {
                        'type': 'text',
                        'content': f'Hello! 👋 I\'m your restaurant guide. What type of cuisine are you in the mood for today? Some popular options are {", ".join(available_cuisines)}, but feel free to ask for any cuisine you like!'
                    }
                return self._get_greeting_prompt()

            elif self.conversation_state == 'ask_cuisine':
                cuisine_found = self._find_cuisine(message)
                if cuisine_found:
                    self.context['cuisine'] = cuisine_found
                    self.conversation_state = 'ask_location'
                    available_locations = list(self.locations)[:3] if self.locations else ['downtown', 'uptown', 'midtown']
                    return {
                        'type': 'text',
                        'content': f'Great choice! 😋 Which area would you like to find {cuisine_found} restaurants in? Some areas I know are {", ".join(available_locations)}.'
                    }
                return {
                    'type': 'text',
                    'content': 'I\'m not sure about that cuisine. Could you please specify a type of cuisine you\'d like to try? For example: Italian, Chinese, Indian, etc.'
                }

            elif self.conversation_state == 'ask_location':
                location_found = self._find_location(message)
                if location_found:
                    self.context['location'] = location_found
                    self.conversation_state = 'searching'
                    return self._search_and_respond()
                return {
                    'type': 'text',
                    'content': 'I\'m not sure about that location. Could you please specify an area or neighborhood?'
                }

            elif self.conversation_state == 'searching':
                # Handle refinements or new searches
                if 'start over' in message or 'new search' in message:
                    self.conversation_state = 'greeting'
                    self.context = {}
                    return self._get_greeting_prompt()
                
                # Check for cuisine or location updates
                cuisine_found = self._find_cuisine(message)
                location_found = self._find_location(message)
                
                if cuisine_found:
                    self.context['cuisine'] = cuisine_found
                if location_found:
                    self.context['location'] = location_found
                
                if cuisine_found or location_found:
                    return self._search_and_respond()
                
                # If no refinements found, suggest options
                return {
                    'type': 'text',
                    'content': 'Would you like to try a different cuisine or location? You can also say "start over" for a new search.'
                }

        except Exception as e:
            print(f'Error in get_response: {str(e)}')
            self.conversation_state = 'greeting'
            self.context = {}
            return {
                'type': 'text',
                'content': 'I apologize, but I encountered an error. Let\'s start over - just say hello! 👋'
            }

    def _find_cuisine(self, message):
        """Find cuisine in message with fuzzy matching"""
        message_words = message.lower().split()
        for cuisine in self.cuisines:
            if cuisine.lower() in message.lower():
                return cuisine
        return None

    def _find_location(self, message):
        """Find location in message with fuzzy matching"""
        message_words = message.lower().split()
        for location in self.locations:
            if location.lower() in message.lower():
                return location
        return None

    def _get_greeting_prompt(self):
        """Get initial greeting prompt"""
        return {
            'type': 'text',
            'content': 'Hi there! 👋 To get started, just say hello!'
        }

    def _search_and_respond(self):
        """Search restaurants and format response"""
        restaurants = self.search_restaurants(self.context)
        if restaurants:
            response = {
                'type': 'restaurants',
                'content': [
                    {
                        'id': r.id,
                        'name': r.name,
                        'cuisine': r.cuisine_type,
                        'location': r.city,
                        'rating': r.rating,
                        'price_range': r.price_range,
                        'image_url': r.image.url if r.image else None
                    } for r in restaurants[:5]
                ],
                'message': f'I found some great {self.context.get("cuisine", "")} restaurants in {self.context.get("location", "")}! 🎉 Would you like to see more options or try a different cuisine/location?'
            }
            return response
        else:
            self.conversation_state = 'ask_cuisine'  # Reset state for new search
            return {
                'type': 'text',
                'content': f'I couldn\'t find any {self.context.get("cuisine", "")} restaurants in {self.context.get("location", "")}. Would you like to try a different cuisine or location? 🤔'
            }

    def search_restaurants(self, criteria):
        """Search restaurants based on multiple criteria"""
        try:
            query = Restaurant.objects.all()
            
            if 'cuisine' in criteria:
                query = query.filter(cuisine_type__icontains=criteria['cuisine'])
            
            if 'location' in criteria:
                query = query.filter(city__icontains=criteria['location'])
            
            if 'price_range' in criteria:
                query = query.filter(price_range=criteria['price_range'])
            
            if 'min_rating' in criteria:
                query = query.filter(rating__gte=criteria['min_rating'])
            
            # Sort by rating by default
            return query.order_by('-rating')
        except Exception as e:
            print(f'Error in search_restaurants: {str(e)}')
            return []

    def _get_criteria_message(self, criteria):
        """Generate a message describing the search criteria"""
        parts = []
        if 'cuisine' in criteria:
            parts.append(criteria['cuisine'])
        if 'min_rating' in criteria:
            parts.append('highly-rated')
        if 'price_range' in criteria:
            price_text = ['budget', 'moderate', 'upscale'][criteria['price_range']-1]
            parts.append(price_text)
        parts.append('restaurants')
        if 'location' in criteria:
            parts.append(f"in {criteria['location']}")
        return ' '.join(parts)

    def _get_suggestion(self):
        """Generate a helpful suggestion when no results are found"""
        if 'cuisine' in self.context and 'location' in self.context:
            return "Try searching in a different area or consider a different cuisine."
        elif 'cuisine' in self.context:
            return f"We have restaurants serving {', '.join(list(self.cuisines)[:3])} cuisine."
        elif 'location' in self.context:
            return f"Try searching in other areas like {', '.join(list(self.locations)[:3])}."
        return "You can try searching by cuisine type (like Italian or Chinese) or by location."
