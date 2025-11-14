from django.contrib import admin
from .models import (
    Category, Author, Book, Member, Borrow, 
    Fine, Payment, Reservation, Review
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'birth_date']
    search_fields = ['name', 'email']
    list_filter = ['birth_date']


class BookAuthorInline(admin.TabularInline):
    model = Book.authors.through
    extra = 1


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'primary_author', 'isbn', 'category', 
        'status', 'available_copies', 'total_copies'
    ]
    search_fields = ['title', 'isbn', 'authors__name']
    list_filter = ['status', 'category', 'language']
    inlines = [BookAuthorInline]
    exclude = ['authors']
    readonly_fields = ['added_date', 'updated_date']
    
    def primary_author(self, obj):
        return obj.primary_author.name if obj.primary_author else 'N/A'


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'member_id', 'phone', 'membership_status', 
        'current_books_borrowed', 'max_books_allowed'
    ]
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'member_id']
    list_filter = ['is_active', 'membership_expiry']
    readonly_fields = ['membership_date']


@admin.register(Borrow)
class BorrowAdmin(admin.ModelAdmin):
    list_display = [
        'book', 'member', 'borrow_date', 'due_date', 
        'return_date', 'status', 'fine_amount'
    ]
    search_fields = ['book__title', 'member__user__username']
    list_filter = ['status', 'borrow_date', 'due_date']
    readonly_fields = ['borrow_id']


@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    list_display = [
        'borrow', 'amount', 'reason', 'issue_date', 
        'due_date', 'status', 'payment_date'
    ]
    search_fields = ['borrow__book__title', 'borrow__member__user__username']
    list_filter = ['status', 'issue_date']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'member', 'amount', 'payment_method', 'status', 
        'payment_date', 'stripe_payment_intent_id'
    ]
    search_fields = ['member__user__username', 'payment_id']
    list_filter = ['status', 'payment_method', 'payment_date']
    readonly_fields = ['payment_id', 'payment_date']


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = [
        'book', 'member', 'reservation_date', 
        'expiry_date', 'status'
    ]
    search_fields = ['book__title', 'member__user__username']
    list_filter = ['status', 'reservation_date']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['book', 'member', 'rating', 'review_date']
    search_fields = ['book__title', 'member__user__username']
    list_filter = ['rating', 'review_date']
