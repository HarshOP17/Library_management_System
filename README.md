# Library Management System

A modern, responsive Django-based library management system with integrated payment processing for fines and fees.

## Features

### 📚 Library Management
- **Book Catalog**: Comprehensive book management with search, filtering, and categorization
- **Author Management**: Track multiple authors per book with detailed profiles
- **Category System**: Organize books by categories with descriptions
- **Inventory Tracking**: Monitor available copies, borrowed books, and reservations

### 👤 Member Management
- **User Registration**: Simple member signup and authentication
- **Member Profiles**: Detailed member information with membership tracking
- **Borrowing Limits**: Configurable limits for books per member
- **Membership Status**: Active/inactive/expired membership tracking

### 📖 Borrowing System
- **Easy Borrowing**: One-click book borrowing with due date tracking
- **Return Management**: Simple return process with automatic fine calculation
- **Reservations**: Reserve unavailable books with expiry dates
- **Overdue Tracking**: Automatic detection and fine calculation for overdue books

### 💳 Payment System
- **Fine Management**: Automatic fine calculation for late returns
- **Online Payments**: Secure Stripe integration for online payments
- **Payment History**: Complete payment transaction records
- **Multiple Payment Methods**: Support for various payment options

### 🎨 User Interface
- **Responsive Design**: Mobile-friendly Bootstrap 5 interface
- **Modern UI**: Clean, professional design with smooth animations
- **Search & Filter**: Advanced search and filtering capabilities
- **Dashboard**: Personalized member dashboard with statistics

## Technology Stack

- **Backend**: Django 4.2.7
- **Frontend**: Bootstrap 5, Font Awesome icons
- **Database**: SQLite (development), PostgreSQL (production)
- **Payment**: Stripe integration
- **Deployment**: Gunicorn, WhiteNoise, WSGI
- **Static Files**: WhiteNoise for efficient static file serving

## Quick Start

### Prerequisites
- Python 3.11+
- pip package manager
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd library-management-system
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment setup**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Database setup**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

8. **Run development server**
   ```bash
   python manage.py runserver
   ```

Visit `http://localhost:8000` to access the application.

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key
STRIPE_SECRET_KEY=sk_test_your_secret_key
```

### Stripe Setup

1. Create a Stripe account at [stripe.com](https://stripe.com)
2. Get your API keys from the Stripe dashboard
3. Add the keys to your `.env` file
4. Update the Stripe public key in `templates/base.html`

## Deployment

### Heroku Deployment

1. **Install Heroku CLI**
   ```bash
   # Follow Heroku CLI installation guide
   ```

2. **Login to Heroku**
   ```bash
   heroku login
   ```

3. **Create Heroku app**
   ```bash
   heroku create your-app-name
   ```

4. **Set environment variables**
   ```bash
   heroku config:set SECRET_KEY=your-production-secret-key
   heroku config:set DEBUG=False
   heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com
   heroku config:set STRIPE_PUBLISHABLE_KEY=pk_live_your_key
   heroku config:set STRIPE_SECRET_KEY=sk_live_your_key
   ```

5. **Deploy**
   ```bash
   git push heroku main
   ```

6. **Run migrations**
   ```bash
   heroku run python manage.py migrate
   ```

7. **Create superuser**
   ```bash
   heroku run python manage.py createsuperuser
   ```

### Docker Deployment

```bash
# Build image
docker build -t library-management .

# Run container
docker run -p 8000:8000 library-management
```

## Project Structure

```
library-management/
├── library_management/         # Django project settings
│   ├── __init__.py
│   ├── settings.py            # Main settings file
│   ├── urls.py                # Project URLs
│   ├── wsgi.py                # WSGI configuration
│   └── asgi.py                # ASGI configuration
├── library/                   # Main library app
│   ├── models.py              # Database models
│   ├── views.py               # View functions
│   ├── forms.py               # Django forms
│   ├── urls.py                # App URLs
│   ├── admin.py               # Admin configuration
│   └── apps.py                # App configuration
├── templates/                 # HTML templates
│   ├── base.html              # Base template
│   └── library/               # App-specific templates
├── static/                    # Static files
│   ├── css/                   # CSS files
│   ├── js/                    # JavaScript files
│   └── images/                # Image files
├── media/                     # User uploaded files
├── requirements.txt            # Python dependencies
├── Procfile                   # Heroku process definition
├── gunicorn.conf.py          # Gunicorn configuration
├── runtime.txt               # Python version specification
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore file
├── manage.py                 # Django management script
└── README.md                 # This file
```

## API Endpoints

### Authentication
- `POST /register/` - User registration
- `POST /login/` - User login
- `POST /logout/` - User logout

### Books
- `GET /books/` - Book catalog
- `GET /books/<id>/` - Book details
- `POST /books/<id>/borrow/` - Borrow a book
- `POST /books/<id>/reserve/` - Reserve a book

### Payments
- `GET /payments/` - Payment dashboard
- `POST /payments/create-intent/` - Create payment intent
- `POST /payments/success/` - Payment success callback

## Admin Access

Access the Django admin panel at `/admin/` with your superuser credentials to:
- Manage books, authors, and categories
- View and manage member accounts
- Monitor borrowing activity
- Handle fines and payments

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Contact the development team
- Check the documentation

## Changelog

### v1.0.0
- Initial release
- Complete library management system
- Integrated payment processing
- Responsive Bootstrap 5 UI
- Production-ready deployment configuration
