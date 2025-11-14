// Custom JavaScript for Library Management System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Search functionality
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keyup', function() {
            const searchTerm = this.value.toLowerCase();
            const bookCards = document.querySelectorAll('.book-card');
            
            bookCards.forEach(function(card) {
                const title = card.querySelector('.book-title').textContent.toLowerCase();
                const author = card.querySelector('.book-author').textContent.toLowerCase();
                
                if (title.includes(searchTerm) || author.includes(searchTerm)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }

    // Filter functionality
    const filterSelect = document.getElementById('filterSelect');
    if (filterSelect) {
        filterSelect.addEventListener('change', function() {
            const filterValue = this.value;
            const bookCards = document.querySelectorAll('.book-card');
            
            bookCards.forEach(function(card) {
                if (filterValue === 'all') {
                    card.style.display = 'block';
                } else {
                    const status = card.dataset.status;
                    card.style.display = status === filterValue ? 'block' : 'none';
                }
            });
        });
    }

    // Payment form validation
    const paymentForm = document.getElementById('paymentForm');
    if (paymentForm) {
        paymentForm.addEventListener('submit', function(e) {
            const amount = document.getElementById('amount').value;
            if (amount <= 0) {
                e.preventDefault();
                showAlert('Please enter a valid amount', 'danger');
            }
        });
    }

    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item?')) {
                e.preventDefault();
            }
        });
    });

    // Dynamic form fields for book authors
    const addAuthorBtn = document.getElementById('addAuthorBtn');
    if (addAuthorBtn) {
        addAuthorBtn.addEventListener('click', function() {
            const authorFields = document.getElementById('authorFields');
            const newAuthorField = document.createElement('div');
            newAuthorField.className = 'mb-3';
            newAuthorField.innerHTML = `
                <label class="form-label">Author</label>
                <div class="d-flex">
                    <input type="text" name="authors" class="form-control me-2" placeholder="Author name">
                    <button type="button" class="btn btn-outline-danger btn-sm" onclick="this.parentElement.parentElement.remove()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            `;
            authorFields.appendChild(newAuthorField);
        });
    }
});

// Utility functions
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alertContainer');
    if (!alertContainer) return;
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.appendChild(alertDiv);
    
    // Auto-hide after 5 seconds
    setTimeout(function() {
        const bsAlert = new bootstrap.Alert(alertDiv);
        bsAlert.close();
    }, 5000);
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

function showLoadingSpinner(element) {
    element.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div>';
}

function hideLoadingSpinner(element, originalContent) {
    element.innerHTML = originalContent;
}

// Stripe payment handling
if (typeof Stripe !== 'undefined') {
    const stripe = Stripe('pk_test_your_publishable_key'); // This will be replaced with actual key
    
    function handleStripePayment(paymentIntentId) {
        stripe.confirmCardPayment(paymentIntentId).then(function(result) {
            if (result.error) {
                showAlert('Payment failed: ' + result.error.message, 'danger');
            } else {
                showAlert('Payment successful!', 'success');
                setTimeout(function() {
                    window.location.href = '/payments/success/';
                }, 2000);
            }
        });
    }
}

// Book reservation functionality
function reserveBook(bookId) {
    const btn = document.querySelector(`[data-book-id="${bookId}"]`);
    if (btn) {
        showLoadingSpinner(btn);
        
        fetch(`/books/${bookId}/reserve/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            hideLoadingSpinner(btn, 'Reserve');
            if (data.success) {
                showAlert('Book reserved successfully!', 'success');
                btn.disabled = true;
                btn.textContent = 'Reserved';
            } else {
                showAlert(data.error || 'Reservation failed', 'danger');
            }
        })
        .catch(error => {
            hideLoadingSpinner(btn, 'Reserve');
            showAlert('An error occurred. Please try again.', 'danger');
        });
    }
}

// Borrow book functionality
function borrowBook(bookId) {
    const btn = document.querySelector(`[data-borrow-book-id="${bookId}"]`);
    if (btn) {
        showLoadingSpinner(btn);
        
        fetch(`/books/${bookId}/borrow/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            hideLoadingSpinner(btn, 'Borrow');
            if (data.success) {
                showAlert('Book borrowed successfully!', 'success');
                btn.disabled = true;
                btn.textContent = 'Borrowed';
                updateBookStatus(bookId, 'borrowed');
            } else {
                showAlert(data.error || 'Borrowing failed', 'danger');
            }
        })
        .catch(error => {
            hideLoadingSpinner(btn, 'Borrow');
            showAlert('An error occurred. Please try again.', 'danger');
        });
    }
}

function updateBookStatus(bookId, status) {
    const statusElement = document.querySelector(`[data-status-book-id="${bookId}"]`);
    if (statusElement) {
        statusElement.className = `book-status status-${status}`;
        statusElement.textContent = status.charAt(0).toUpperCase() + status.slice(1);
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
