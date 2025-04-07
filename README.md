# GoTable - Restaurant Table Booking System

A comprehensive restaurant table booking system built with Django, Python, HTML, CSS, and JavaScript.

## Features

- User authentication (email/password and social login)
- Restaurant search and table booking
- Booking management system
- Payment integration (Stripe)
- Email notifications
- Admin dashboard
- Restaurant owner portal

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the root directory with the following variables:
```
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@localhost:5432/gotable
STRIPE_PUBLIC_KEY=your-stripe-public-key
STRIPE_SECRET_KEY=your-stripe-secret-key
```

4. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

## Project Structure

```
gotable/
├── accounts/          # User authentication and profiles
├── bookings/         # Booking management
├── restaurants/      # Restaurant management
├── payments/         # Payment processing
├── notifications/    # Email/SMS notifications
├── static/          # Static files (CSS, JS, images)
└── templates/       # HTML templates
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request 