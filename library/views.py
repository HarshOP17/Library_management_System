from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from datetime import timedelta
import stripe
import json

from .models import (
    Book, Author, Category, Member, Borrow, 
    Fine, Payment, Reservation, Review
)
from .forms import (
    BookForm, AuthorForm, CategoryForm, MemberForm,
    BorrowForm, ReviewForm, UserUpdateForm, MemberUpdateForm
)


def home(request):
    """Home page with library statistics and featured books"""
    if request.user.is_authenticated:
        try:
            member = Member.objects.get(user=request.user)
            active_borrows = Borrow.objects.filter(member=member, status='active').count()
            pending_fines = Fine.objects.filter(borrow__member=member, status='pending').aggregate(total=Sum('amount'))['total'] or 0
        except Member.DoesNotExist:
            member = None
            active_borrows = 0
            pending_fines = 0
    else:
        member = None
        active_borrows = 0
        pending_fines = 0
    
    # Library statistics
    total_books = Book.objects.count()
    available_books = Book.objects.filter(status='available').count()
    total_members = Member.objects.count()
    active_borrows_count = Borrow.objects.filter(status='active').count()
    
    # Featured books (highly rated)
    featured_books = Book.objects.annotate(
        avg_rating=Avg('reviews__rating')
    ).filter(avg_rating__gte=4).order_by('-avg_rating')[:6]
    
    context = {
        'member': member,
        'active_borrows': active_borrows,
        'pending_fines': pending_fines,
        'total_books': total_books,
        'available_books': available_books,
        'total_members': total_members,
        'active_borrows_count': active_borrows_count,
        'featured_books': featured_books,
    }
    return render(request, 'library/home.html', context)


def book_catalog(request):
    """Book catalog with search and filtering"""
    books = Book.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(authors__name__icontains=search_query) |
            Q(isbn__icontains=search_query)
        ).distinct()
    
    # Category filter
    category_filter = request.GET.get('category', '')
    if category_filter:
        books = books.filter(category__name=category_filter)
    
    # Status filter
    status_filter = request.GET.get('status', '')
    if status_filter:
        books = books.filter(status=status_filter)
    
    # Sorting
    sort_by = request.GET.get('sort', 'title')
    if sort_by == 'title':
        books = books.order_by('title')
    elif sort_by == 'author':
        books = books.order_by('authors__name')
    elif sort_by == 'rating':
        books = books.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
    elif sort_by == 'newest':
        books = books.order_by('-added_date')
    
    # Pagination
    paginator = Paginator(books, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
        'status_filter': status_filter,
        'sort_by': sort_by,
    }
    return render(request, 'library/book_catalog.html', context)


def book_detail(request, book_id):
    """Detailed view of a single book"""
    book = get_object_or_404(Book, id=book_id)
    reviews = book.reviews.all().order_by('-review_date')
    
    # Check if user has already reviewed this book
    user_review = None
    if request.user.is_authenticated:
        try:
            member = Member.objects.get(user=request.user)
            user_review = reviews.filter(member=member).first()
        except Member.DoesNotExist:
            pass
    
    # Calculate average rating
    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
    
    context = {
        'book': book,
        'reviews': reviews,
        'user_review': user_review,
        'avg_rating': avg_rating,
    }
    return render(request, 'library/book_detail.html', context)


@login_required
@require_POST
def borrow_book(request, book_id):
    """Borrow a book"""
    book = get_object_or_404(Book, id=book_id)
    
    try:
        member = Member.objects.get(user=request.user)
    except Member.DoesNotExist:
        messages.error(request, 'You are not registered as a library member.')
        return redirect('book_detail', book_id=book_id)
    
    if not member.can_borrow:
        messages.error(request, 'You cannot borrow more books. Return some books first.')
        return redirect('book_detail', book_id=book_id)
    
    if not book.is_available:
        messages.error(request, 'This book is not available for borrowing.')
        return redirect('book_detail', book_id=book_id)
    
    # Create borrow record
    borrow = Borrow.objects.create(
        book=book,
        member=member,
        due_date=timezone.now().date() + timedelta(days=14)
    )
    
    # Update book availability
    book.available_copies -= 1
    if book.available_copies == 0:
        book.status = 'borrowed'
    book.save()
    
    # Update member's borrowed books count
    member.current_books_borrowed += 1
    member.save()
    
    messages.success(request, f'You have successfully borrowed "{book.title}". Due date: {borrow.due_date}')
    return redirect('my_borrows')


@login_required
@require_POST
def reserve_book(request, book_id):
    """Reserve a book"""
    book = get_object_or_404(Book, id=book_id)
    
    try:
        member = Member.objects.get(user=request.user)
    except Member.DoesNotExist:
        messages.error(request, 'You are not registered as a library member.')
        return redirect('book_detail', book_id=book_id)
    
    # Check if already reserved
    existing_reservation = Reservation.objects.filter(
        book=book, member=member, status='active'
    ).first()
    
    if existing_reservation:
        messages.error(request, 'You have already reserved this book.')
        return redirect('book_detail', book_id=book_id)
    
    # Create reservation
    reservation = Reservation.objects.create(
        book=book,
        member=member,
        expiry_date=timezone.now() + timedelta(days=7)
    )
    
    messages.success(request, f'You have successfully reserved "{book.title}".')
    return redirect('book_detail', book_id=book_id)


@login_required
def my_borrows(request):
    """View user's borrowed books"""
    try:
        member = Member.objects.get(user=request.user)
        borrows = Borrow.objects.filter(member=member).order_by('-borrow_date')
    except Member.DoesNotExist:
        messages.error(request, 'You are not registered as a library member.')
        return redirect('home')
    
    context = {
        'borrows': borrows,
        'member': member,
    }
    return render(request, 'library/my_borrows.html', context)


@login_required
@require_POST
def return_book(request, borrow_id):
    """Return a borrowed book"""
    borrow = get_object_or_404(Borrow, id=borrow_id)
    
    # Check if the user owns this borrow
    if borrow.member.user != request.user:
        messages.error(request, 'You can only return your own borrowed books.')
        return redirect('my_borrows')
    
    if borrow.status == 'returned':
        messages.error(request, 'This book has already been returned.')
        return redirect('my_borrows')
    
    # Update borrow record
    borrow.return_date = timezone.now()
    borrow.status = 'returned'
    
    # Calculate fine if overdue
    if borrow.is_overdue:
        fine_amount = borrow.calculated_fine
        if fine_amount > 0:
            borrow.fine_amount = fine_amount
            # Create fine record
            Fine.objects.create(
                borrow=borrow,
                amount=fine_amount,
                reason='Late return',
                due_date=timezone.now().date() + timedelta(days=7)
            )
    
    borrow.save()
    
    # Update book availability
    book = borrow.book
    book.available_copies += 1
    if book.status == 'borrowed' and book.available_copies > 0:
        book.status = 'available'
    book.save()
    
    # Update member's borrowed books count
    member = borrow.member
    member.current_books_borrowed -= 1
    member.save()
    
    messages.success(request, f'Book "{book.title}" returned successfully.')
    if borrow.fine_amount > 0:
        messages.warning(request, f'A fine of ${borrow.fine_amount} has been charged for late return.')
    
    return redirect('my_borrows')


@login_required
def payment_dashboard(request):
    """Payment dashboard for fines and fees"""
    try:
        member = Member.objects.get(user=request.user)
        pending_fines = Fine.objects.filter(borrow__member=member, status='pending')
        total_pending = pending_fines.aggregate(total=Sum('amount'))['total'] or 0
        payment_history = Payment.objects.filter(member=member).order_by('-payment_date')
    except Member.DoesNotExist:
        messages.error(request, 'You are not registered as a library member.')
        return redirect('home')
    
    context = {
        'member': member,
        'pending_fines': pending_fines,
        'total_pending': total_pending,
        'payment_history': payment_history,
    }
    return render(request, 'library/payment_dashboard.html', context)


@login_required
def payment_history(request):
    """View payment history"""
    try:
        member = Member.objects.get(user=request.user)
        payments = Payment.objects.filter(member=member).order_by('-payment_date')
    except Member.DoesNotExist:
        messages.error(request, 'You are not registered as a library member.')
        return redirect('home')
    
    context = {
        'payments': payments,
    }
    return render(request, 'library/payment_history.html', context)


@login_required
@require_POST
def create_payment_intent(request):
    """Create Stripe payment intent"""
    try:
        member = Member.objects.get(user=request.user)
        data = json.loads(request.body)
        amount = int(float(data.get('amount', 0)) * 100)  # Convert to cents
        
        if amount <= 0:
            return JsonResponse({'error': 'Invalid amount'}, status=400)
        
        stripe.api_key = 'sk_test_your_secret_key'  # This should be from settings
        
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='usd',
            metadata={'member_id': member.id}
        )
        
        return JsonResponse({'client_secret': intent.client_secret})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@csrf_exempt
@require_POST
def payment_success(request):
    """Handle successful payment"""
    try:
        data = json.loads(request.body)
        payment_intent_id = data.get('payment_intent_id')
        amount = data.get('amount', 0)
        
        member = Member.objects.get(user=request.user)
        
        # Create payment record
        payment = Payment.objects.create(
            member=member,
            amount=amount,
            payment_method='stripe',
            status='completed',
            stripe_payment_intent_id=payment_intent_id,
            description='Online payment for library fines'
        )
        
        # Update fines status (simplified - in real app, match specific fines)
        pending_fines = Fine.objects.filter(borrow__member=member, status='pending')
        total_fine_amount = pending_fines.aggregate(total=Sum('amount'))['total'] or 0
        
        if total_fine_amount <= amount:
            pending_fines.update(status='paid', payment_date=timezone.now())
            payment.fines.set(pending_fines)
        
        messages.success(request, f'Payment of ${amount} processed successfully!')
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def register(request):
    """User registration"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! Please complete your member profile.')
            login(request, user)
            return redirect('profile')
    else:
        form = UserCreationForm()
    
    return render(request, 'library/register.html', {'form': form})


@login_required
def profile(request):
    """User profile management"""
    try:
        member = Member.objects.get(user=request.user)
    except Member.DoesNotExist:
        member = None
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        member_form = MemberUpdateForm(request.POST, request.FILES, instance=member)
        
        if user_form.is_valid() and member_form.is_valid():
            user_form.save()
            member_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        member_form = MemberUpdateForm(instance=member)
    
    context = {
        'user_form': user_form,
        'member_form': member_form,
        'member': member,
    }
    return render(request, 'library/profile.html', context)


@login_required
@require_POST
def add_review(request, book_id):
    """Add a review for a book"""
    book = get_object_or_404(Book, id=book_id)
    
    try:
        member = Member.objects.get(user=request.user)
    except Member.DoesNotExist:
        messages.error(request, 'You must be a library member to add reviews.')
        return redirect('book_detail', book_id=book_id)
    
    # Check if already reviewed
    existing_review = Review.objects.filter(book=book, member=member).first()
    if existing_review:
        messages.error(request, 'You have already reviewed this book.')
        return redirect('book_detail', book_id=book_id)
    
    rating = request.POST.get('rating')
    comment = request.POST.get('comment')
    
    if rating and comment:
        Review.objects.create(
            book=book,
            member=member,
            rating=int(rating),
            comment=comment
        )
        messages.success(request, 'Your review has been added!')
    else:
        messages.error(request, 'Please provide both rating and comment.')
    
    return redirect('book_detail', book_id=book_id)


def contact(request):
    """Contact page"""
    return render(request, 'library/contact.html')
