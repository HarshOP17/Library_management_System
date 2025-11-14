from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Home and catalog
    path('', views.home, name='home'),
    path('books/', views.book_catalog, name='book_catalog'),
    path('books/<int:book_id>/', views.book_detail, name='book_detail'),
    
    # Book actions
    path('books/<int:book_id>/borrow/', views.borrow_book, name='borrow_book'),
    path('books/<int:book_id>/reserve/', views.reserve_book, name='reserve_book'),
    path('books/<int:book_id>/review/', views.add_review, name='add_review'),
    
    # Member borrows
    path('my-borrows/', views.my_borrows, name='my_borrows'),
    path('return-book/<int:borrow_id>/', views.return_book, name='return_book'),
    
    # Payments
    path('payments/', views.payment_dashboard, name='payment_dashboard'),
    path('payments/history/', views.payment_history, name='payment_history'),
    path('payments/create-intent/', views.create_payment_intent, name='create_payment_intent'),
    path('payments/success/', views.payment_success, name='payment_success'),
    
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='library/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    
    # Profile
    path('profile/', views.profile, name='profile'),
    
    # Other pages
    path('contact/', views.contact, name='contact'),
]
