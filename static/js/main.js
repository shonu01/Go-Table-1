// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Add smooth scrolling to all links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add animation to cards on scroll
    const cards = document.querySelectorAll('.card');
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, {
        threshold: 0.1
    });

    cards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(card);
    });

    // Handle form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Handle notification read status
    const notificationButtons = document.querySelectorAll('.mark-notification-read');
    notificationButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const notificationId = this.dataset.notificationId;
            fetch(`/notifications/${notificationId}/mark-read/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.closest('.notification-item').classList.add('read');
                    updateNotificationCount();
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });

    // Handle booking cancellation
    const cancelBookingButtons = document.querySelectorAll('.cancel-booking');
    cancelBookingButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const bookingId = this.dataset.bookingId;
            if (confirm('Are you sure you want to cancel this booking?')) {
                window.location.href = `/bookings/${bookingId}/delete/`;
            }
        });
    });

    // Profile picture preview
    const profilePictureInput = document.getElementById('profile-picture-input');
    const profilePicturePreview = document.getElementById('profile-picture-preview');
    
    if (profilePictureInput && profilePicturePreview) {
        profilePictureInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    profilePicturePreview.src = e.target.result;
                }
                reader.readAsDataURL(file);
            }
        });
    }

    // Helper function to get CSRF token from cookies
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

    // Update notification count
    function updateNotificationCount() {
        const badge = document.querySelector('.notification-badge');
        if (badge) {
            let count = parseInt(badge.textContent) - 1;
            if (count <= 0) {
                badge.style.display = 'none';
            } else {
                badge.textContent = count;
            }
        }
    }

    // Handle restaurant search
    const searchForm = document.getElementById('restaurant-search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const searchQuery = document.getElementById('search-query').value;
            const locationQuery = document.getElementById('location-query').value;
            
            window.location.href = `/restaurants/search/?q=${encodeURIComponent(searchQuery)}&location=${encodeURIComponent(locationQuery)}`;
        });
    }

    // Handle booking time slot selection
    const timeSlots = document.querySelectorAll('.time-slot');
    timeSlots.forEach(slot => {
        slot.addEventListener('click', function() {
            timeSlots.forEach(s => s.classList.remove('selected'));
            this.classList.add('selected');
            document.getElementById('selected_time').value = this.dataset.time;
        });
    });

    // Handle table selection
    const tables = document.querySelectorAll('.table-option');
    tables.forEach(table => {
        table.addEventListener('click', function() {
            if (!this.classList.contains('unavailable')) {
                tables.forEach(t => t.classList.remove('selected'));
                this.classList.add('selected');
                document.getElementById('selected_table').value = this.dataset.tableId;
            }
        });
    });
}); 