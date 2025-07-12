// Main JavaScript for Skill Swap Platform

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeAlerts();
    initializeModals();
    initializeTooltips();
    initializeFormValidation();
    initializeAnimations();
    initializeSearch();
});

// Auto-dismiss alerts after 5 seconds
function initializeAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert.classList.contains('show')) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    });
}

// Initialize Bootstrap modals
function initializeModals() {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('shown.bs.modal', function() {
            const firstInput = modal.querySelector('input, textarea, select');
            if (firstInput) {
                firstInput.focus();
            }
        });
    });
}

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Form validation enhancements
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Real-time validation feedback
    const inputs = document.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateField(this);
        });
        
        input.addEventListener('input', function() {
            if (this.classList.contains('is-invalid')) {
                validateField(this);
            }
        });
    });
}

function validateField(field) {
    const isValid = field.checkValidity();
    field.classList.remove('is-valid', 'is-invalid');
    field.classList.add(isValid ? 'is-valid' : 'is-invalid');
}

// Animate elements on scroll
function initializeAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, observerOptions);

    // Observe cards and other elements
    const animateElements = document.querySelectorAll('.card, .skill-item, .request-item');
    animateElements.forEach(element => {
        observer.observe(element);
    });
}

// Enhanced search functionality
function initializeSearch() {
    const searchInput = document.querySelector('input[name="search"]');
    if (searchInput) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            if (query.length >= 2) {
                searchTimeout = setTimeout(() => {
                    highlightSearchResults(query);
                }, 300);
            } else {
                clearHighlights();
            }
        });
    }
}

function highlightSearchResults(query) {
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        const text = card.textContent.toLowerCase();
        const searchTerm = query.toLowerCase();
        
        if (text.includes(searchTerm)) {
            card.style.order = '-1';
            card.classList.add('highlight-result');
        } else {
            card.style.order = '0';
            card.classList.remove('highlight-result');
        }
    });
}

function clearHighlights() {
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.style.order = '0';
        card.classList.remove('highlight-result');
    });
}

// Rating system functionality
function initializeRatingSystem() {
    const starRatings = document.querySelectorAll('.rating-stars');
    
    starRatings.forEach(rating => {
        const stars = rating.querySelectorAll('.star');
        const inputs = rating.querySelectorAll('input[type="radio"]');
        
        stars.forEach((star, index) => {
            star.addEventListener('click', function() {
                inputs[index].checked = true;
                updateStarDisplay(stars, index + 1);
            });
            
            star.addEventListener('mouseenter', function() {
                updateStarDisplay(stars, index + 1);
            });
        });
        
        rating.addEventListener('mouseleave', function() {
            const checkedIndex = Array.from(inputs).findIndex(input => input.checked);
            updateStarDisplay(stars, checkedIndex + 1);
        });
    });
}

function updateStarDisplay(stars, rating) {
    stars.forEach((star, index) => {
        if (index < rating) {
            star.style.color = '#ffc107';
        } else {
            star.style.color = '#ddd';
        }
    });
}

// File upload preview
function initializeFileUpload() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const file = this.files[0];
            if (file && file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    showImagePreview(input, e.target.result);
                };
                reader.readAsDataURL(file);
            }
        });
    });
}

function showImagePreview(input, src) {
    // Remove existing preview
    const existingPreview = input.parentNode.querySelector('.image-preview');
    if (existingPreview) {
        existingPreview.remove();
    }
    
    // Create new preview
    const preview = document.createElement('div');
    preview.className = 'image-preview mt-2';
    preview.innerHTML = `
        <img src="${src}" class="img-thumbnail" style="max-width: 200px; max-height: 200px;">
        <button type="button" class="btn btn-sm btn-outline-danger ms-2" onclick="removeImagePreview(this)">
            <i class="fas fa-times"></i> Remove
        </button>
    `;
    
    input.parentNode.insertBefore(preview, input.nextSibling);
}

function removeImagePreview(button) {
    const preview = button.closest('.image-preview');
    const fileInput = preview.previousElementSibling;
    
    preview.remove();
    fileInput.value = '';
}

// Loading states for buttons
function showLoading(button) {
    const originalText = button.innerHTML;
    button.setAttribute('data-original-text', originalText);
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
    button.disabled = true;
}

function hideLoading(button) {
    const originalText = button.getAttribute('data-original-text');
    if (originalText) {
        button.innerHTML = originalText;
        button.removeAttribute('data-original-text');
    }
    button.disabled = false;
}

// Confirmation dialogs
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Auto-save for forms (draft functionality)
function initializeAutoSave() {
    const forms = document.querySelectorAll('form[data-autosave]');
    
    forms.forEach(form => {
        const formId = form.getAttribute('data-autosave');
        const inputs = form.querySelectorAll('input, textarea, select');
        
        // Load saved data
        loadFormData(form, formId);
        
        // Save on input
        inputs.forEach(input => {
            input.addEventListener('input', () => {
                saveFormData(form, formId);
            });
        });
        
        // Clear saved data on successful submit
        form.addEventListener('submit', () => {
            clearFormData(formId);
        });
    });
}

function saveFormData(form, formId) {
    const formData = new FormData(form);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
        data[key] = value;
    }
    
    localStorage.setItem(`form_${formId}`, JSON.stringify(data));
}

function loadFormData(form, formId) {
    const savedData = localStorage.getItem(`form_${formId}`);
    
    if (savedData) {
        const data = JSON.parse(savedData);
        
        Object.keys(data).forEach(key => {
            const input = form.querySelector(`[name="${key}"]`);
            if (input && input.type !== 'file') {
                input.value = data[key];
            }
        });
    }
}

function clearFormData(formId) {
    localStorage.removeItem(`form_${formId}`);
}

// Notification system
function showNotification(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show notification`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        max-width: 500px;
    `;
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove
    setTimeout(() => {
        if (notification.parentNode) {
            const bsAlert = new bootstrap.Alert(notification);
            bsAlert.close();
        }
    }, duration);
}

// Utility functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function truncateText(text, maxLength = 100) {
    if (text.length <= maxLength) return text;
    return text.substr(0, maxLength) + '...';
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export functions for global use
window.SkillSwap = {
    showLoading,
    hideLoading,
    confirmAction,
    showNotification,
    formatDate,
    truncateText,
    removeImagePreview
};

// Initialize file upload and rating system when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initializeFileUpload();
    initializeRatingSystem();
    initializeAutoSave();
});
