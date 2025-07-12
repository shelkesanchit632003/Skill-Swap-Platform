// Enhanced Main JavaScript for Skill Swap Platform

document.addEventListener('DOMContentLoaded', function() {
    try {
        // Initialize all components with error handling
        initializeAlerts();
        initializeModals();
        initializeTooltips();
        initializeFormValidation();
        initializeAnimations();
        initializeSearch();
        initializeCopyButtons();
        initializeAutoRefresh();
        
        console.log('All components initialized successfully');
    } catch (error) {
        console.error('Error during component initialization:', error);
        // Still try to initialize basic functionality
        try {
            initializeModals();
            initializeFormValidation();
        } catch (fallbackError) {
            console.error('Fallback initialization failed:', fallbackError);
        }
    }
});

// Auto-dismiss alerts with enhanced styling
function initializeAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach((alert, index) => {
        // Add entrance animation
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-20px)';
        
        setTimeout(() => {
            alert.style.transition = 'all 0.3s ease';
            alert.style.opacity = '1';
            alert.style.transform = 'translateY(0)';
        }, index * 100);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alert.classList.contains('show')) {
                alert.style.transform = 'translateX(100%)';
                setTimeout(() => {
                    const bsAlert = new bootstrap.Alert(alert);
                    bsAlert.close();
                }, 300);
            }
        }, 5000);
    });
}

// Simplified Bootstrap modals initialization
function initializeModals() {
    try {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            // Prevent multiple event listeners
            if (modal.hasAttribute('data-modal-initialized')) {
                return;
            }
            modal.setAttribute('data-modal-initialized', 'true');
            
            // Simple focus management
            modal.addEventListener('shown.bs.modal', function() {
                try {
                    setTimeout(() => {
                        const firstInput = modal.querySelector('input:not([type="hidden"]), textarea, select');
                        if (firstInput && typeof firstInput.focus === 'function') {
                            firstInput.focus();
                        }
                        // Ensure modal itself receives focus for accessibility
                        if (typeof modal.focus === 'function') {
                            modal.focus();
                        }
                    }, 200);
                } catch (error) {
                    console.error('Modal focus error:', error);
                }
            });
            
            // Reset form when modal is closed
            modal.addEventListener('hidden.bs.modal', function() {
                try {
                    const form = modal.querySelector('form');
                    if (form) {
                        form.classList.remove('was-validated');
                        form.reset();
                        
                        // Reset any loading states
                        const submitButton = form.querySelector('button[type="submit"]');
                        if (submitButton) {
                            submitButton.disabled = false;
                            const originalText = submitButton.getAttribute('data-original-text') || 'Submit';
                            submitButton.innerHTML = originalText;
                        }
                    }
                } catch (error) {
                    console.error('Modal cleanup error:', error);
                }
            });
        });
    } catch (error) {
        console.error('Modal initialization error:', error);
    }
}

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Form validation enhancements - simplified to prevent freezing
function initializeFormValidation() {
    try {
        const forms = document.querySelectorAll('.needs-validation');
        forms.forEach(form => {
            // Prevent multiple listeners
            if (form.hasAttribute('data-validation-initialized')) {
                return;
            }
            form.setAttribute('data-validation-initialized', 'true');
            
            form.addEventListener('submit', function(event) {
                try {
                    // Simple validation check without blocking
                    if (!form.checkValidity()) {
                        event.preventDefault();
                        event.stopPropagation();
                        form.classList.add('was-validated');
                        return false;
                    }
                    
                    // Allow form to submit normally
                    form.classList.add('was-validated');
                    
                    // Add loading state to submit button
                    const submitButton = form.querySelector('button[type="submit"]');
                    if (submitButton) {
                        submitButton.disabled = true;
                        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Submitting...';
                    }
                    
                } catch (error) {
                    console.error('Form validation error:', error);
                    // Don't prevent form submission if validation fails
                }
            });
        });

        // Simplified real-time validation
        const inputs = document.querySelectorAll('input[required], textarea[required], select[required]');
        inputs.forEach(input => {
            // Prevent multiple listeners
            if (input.hasAttribute('data-validation-initialized')) {
                return;
            }
            input.setAttribute('data-validation-initialized', 'true');
            
            input.addEventListener('blur', function() {
                try {
                    const isValid = this.checkValidity();
                    this.classList.remove('is-valid', 'is-invalid');
                    if (this.value.trim() !== '') {
                        this.classList.add(isValid ? 'is-valid' : 'is-invalid');
                    }
                } catch (error) {
                    console.error('Field validation error:', error);
                }
            });
        });
    } catch (error) {
        console.error('Form validation initialization error:', error);
    }
}

// Simplified field validation
function validateField(field) {
    try {
        if (!field || typeof field.checkValidity !== 'function') {
            return;
        }
        const isValid = field.checkValidity();
        field.classList.remove('is-valid', 'is-invalid');
        if (field.value.trim() !== '') {
            field.classList.add(isValid ? 'is-valid' : 'is-invalid');
        }
    } catch (error) {
        console.error('Field validation error:', error);
    }
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

// Enhanced search functionality with error handling
function initializeSearch() {
    try {
        const searchInput = document.querySelector('input[name="search"]');
        if (searchInput) {
            let searchTimeout;
            
            // Prevent multiple event listeners
            if (searchInput.hasAttribute('data-search-initialized')) {
                return;
            }
            searchInput.setAttribute('data-search-initialized', 'true');
            
            searchInput.addEventListener('input', function() {
                try {
                    clearTimeout(searchTimeout);
                    const query = this.value.trim();
                    
                    if (query.length >= 2) {
                        searchTimeout = setTimeout(() => {
                            try {
                                highlightSearchResults(query);
                            } catch (error) {
                                console.error('Search highlight error:', error);
                            }
                        }, 300);
                    } else {
                        clearHighlights();
                    }
                } catch (error) {
                    console.error('Search input error:', error);
                }
            });
        }
    } catch (error) {
        console.error('Search initialization error:', error);
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

// Enhanced copy to clipboard functionality
function initializeCopyButtons() {
    const copyButtons = document.querySelectorAll('[data-copy]');
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const textToCopy = this.getAttribute('data-copy') || 
                              this.previousElementSibling?.value || 
                              this.parentElement.querySelector('input')?.value;
            
            if (textToCopy) {
                copyToClipboard(textToCopy, this);
            }
        });
    });
}

function copyToClipboard(text, buttonElement) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showCopySuccess(buttonElement);
        }).catch(() => {
            fallbackCopyTextToClipboard(text, buttonElement);
        });
    } else {
        fallbackCopyTextToClipboard(text, buttonElement);
    }
}

function fallbackCopyTextToClipboard(text, buttonElement) {
    const textArea = document.createElement("textarea");
    textArea.value = text;
    textArea.style.position = "fixed";
    textArea.style.left = "-999999px";
    textArea.style.top = "-999999px";
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showCopySuccess(buttonElement);
    } catch (err) {
        console.error('Fallback: Could not copy text: ', err);
        showToast('Failed to copy to clipboard', 'danger');
    }
    
    document.body.removeChild(textArea);
}

function showCopySuccess(buttonElement) {
    const originalContent = buttonElement.innerHTML;
    const originalClasses = buttonElement.className;
    
    buttonElement.innerHTML = '<i class="fas fa-check"></i> Copied!';
    buttonElement.className = buttonElement.className.replace(/btn-\w+/, 'btn-success');
    
    setTimeout(() => {
        buttonElement.innerHTML = originalContent;
        buttonElement.className = originalClasses;
    }, 2000);
    
    showToast('Copied to clipboard!', 'success');
}

// Auto-refresh for chat and dynamic content
function initializeAutoRefresh() {
    // Auto-refresh chat messages - only if on room detail page
    const chatContainer = document.getElementById('chatMessages');
    if (chatContainer && window.location.pathname.includes('/room/')) {
        const refreshInterval = setInterval(() => {
            // Check if user is still on the page and container exists
            if (!document.getElementById('chatMessages')) {
                clearInterval(refreshInterval);
                return;
            }
            refreshChatMessages();
        }, 10000); // Increased to 10 seconds to reduce load
    }
    
    // Auto-refresh room member count - less frequent
    const memberCounts = document.querySelectorAll('[data-refresh="member-count"]');
    if (memberCounts.length > 0) {
        const memberRefreshInterval = setInterval(() => {
            // Check if elements still exist
            const currentMemberCounts = document.querySelectorAll('[data-refresh="member-count"]');
            if (currentMemberCounts.length === 0) {
                clearInterval(memberRefreshInterval);
                return;
            }
            refreshMemberCounts();
        }, 60000); // Increased to 1 minute
    }
}

function refreshChatMessages() {
    const chatContainer = document.getElementById('chatMessages');
    if (!chatContainer) return;
    
    const roomId = chatContainer.getAttribute('data-room-id');
    if (!roomId) return;
    
    fetch(window.location.href)
        .then(response => response.text())
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const newMessages = doc.getElementById('chatMessages');
            
            if (newMessages && chatContainer.innerHTML !== newMessages.innerHTML) {
                const wasAtBottom = chatContainer.scrollTop + chatContainer.clientHeight >= chatContainer.scrollHeight - 10;
                chatContainer.innerHTML = newMessages.innerHTML;
                
                if (wasAtBottom) {
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                }
                
                // Re-initialize tooltips for new content
                initializeTooltips();
            }
        })
        .catch(error => {
            console.error('Failed to refresh messages:', error);
        });
}

// Enhanced toast notification system
function showToast(message, type = 'success', duration = 5000) {
    const toastContainer = getOrCreateToastContainer();
    
    const toastId = 'toast-' + Date.now();
    const iconMap = {
        'success': 'check-circle',
        'danger': 'exclamation-circle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    
    const toast = document.createElement('div');
    toast.id = toastId;
    toast.className = `toast align-items-center text-white bg-${type} border-0 mb-2`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="fas fa-${iconMap[type] || 'info-circle'} me-2"></i>
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast, {
        autohide: true,
        delay: duration
    });
    
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
    
    return toastId;
}

function getOrCreateToastContainer() {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '1200';
        document.body.appendChild(container);
    }
    return container;
}

// Enhanced loading states
function setLoadingState(button, loading = true) {
    if (loading) {
        button.disabled = true;
        button.setAttribute('data-original-text', button.innerHTML);
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Loading...';
    } else {
        button.disabled = false;
        const originalText = button.getAttribute('data-original-text');
        if (originalText) {
            button.innerHTML = originalText;
        }
    }
}

// Enhanced search with debouncing
function initializeEnhancedSearch() {
    const searchInputs = document.querySelectorAll('[data-search]');
    
    searchInputs.forEach(input => {
        let debounceTimer;
        
        input.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            
            debounceTimer = setTimeout(() => {
                const searchTerm = this.value.toLowerCase().trim();
                const targetSelector = this.getAttribute('data-search');
                performSearch(searchTerm, targetSelector);
            }, 300);
        });
        
        // Clear search on escape
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                this.value = '';
                const targetSelector = this.getAttribute('data-search');
                performSearch('', targetSelector);
            }
        });
    });
}

function performSearch(searchTerm, targetSelector) {
    const targets = document.querySelectorAll(targetSelector);
    let visibleCount = 0;
    
    targets.forEach(target => {
        const text = target.textContent.toLowerCase();
        const container = target.closest('.col-lg-4, .col-md-6, .col-12, .card, .list-group-item');
        
        if (searchTerm === '' || text.includes(searchTerm)) {
            if (container) {
                container.style.display = '';
                container.style.opacity = '1';
                container.style.transform = 'translateY(0)';
            }
            visibleCount++;
        } else {
            if (container) {
                container.style.opacity = '0';
                container.style.transform = 'translateY(-10px)';
                setTimeout(() => {
                    container.style.display = 'none';
                }, 200);
            }
        }
    });
    
    // Show no results message
    updateSearchResults(searchTerm, visibleCount, targetSelector);
}

function updateSearchResults(searchTerm, visibleCount, targetSelector) {
    const searchContainer = document.querySelector(targetSelector)?.closest('.row, .container');
    if (!searchContainer) return;
    
    let noResultsMessage = searchContainer.querySelector('.no-results-message');
    
    if (searchTerm && visibleCount === 0) {
        if (!noResultsMessage) {
            noResultsMessage = document.createElement('div');
            noResultsMessage.className = 'no-results-message col-12 text-center py-5';
            noResultsMessage.innerHTML = `
                <i class="fas fa-search fa-3x text-muted mb-3"></i>
                <h5 class="text-muted">No results found</h5>
                <p class="text-muted">Try adjusting your search terms</p>
            `;
            searchContainer.appendChild(noResultsMessage);
        }
        noResultsMessage.style.display = 'block';
    } else if (noResultsMessage) {
        noResultsMessage.style.display = 'none';
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Global shortcuts
    if (e.ctrlKey || e.metaKey) {
        switch(e.key) {
            case 'k':
                e.preventDefault();
                const searchInput = document.querySelector('input[type="search"], input[placeholder*="search" i]');
                if (searchInput) {
                    searchInput.focus();
                    searchInput.select();
                }
                break;
                
            case 'Enter':
                if (document.activeElement.tagName === 'TEXTAREA') {
                    const form = document.activeElement.closest('form');
                    if (form) {
                        e.preventDefault();
                        form.submit();
                    }
                }
                break;
        }
    }
    
    // Escape to clear search or close modals
    if (e.key === 'Escape') {
        const focusedElement = document.activeElement;
        if (focusedElement.hasAttribute('data-search')) {
            focusedElement.value = '';
            focusedElement.dispatchEvent(new Event('input'));
        }
    }
});

// Smooth reveal animations for new content
function animateNewContent(element) {
    element.style.opacity = '0';
    element.style.transform = 'translateY(20px)';
    
    setTimeout(() => {
        element.style.transition = 'all 0.4s ease';
        element.style.opacity = '1';
        element.style.transform = 'translateY(0)';
    }, 100);
}

// Form enhancement for better UX
function enhanceFormSubmission(form) {
    form.addEventListener('submit', function(e) {
        const submitButton = form.querySelector('button[type="submit"]');
        if (submitButton) {
            setLoadingState(submitButton, true);
        }
        
        // Re-enable button after 5 seconds as failsafe
        setTimeout(() => {
            if (submitButton) {
                setLoadingState(submitButton, false);
            }
        }, 5000);
    });
}

// Profile Viewer Functionality
function showProfileViewer(userId, userName, displayName, profilePhoto, skillsCount = 0, rating = 'N/A', joinDate = 'Unknown') {
    const modal = document.getElementById('profileViewerModal');
    const modalInstance = new bootstrap.Modal(modal);
    
    // Update modal content
    document.getElementById('profileUserName').textContent = userName;
    document.getElementById('profileDisplayName').textContent = displayName;
    document.getElementById('profileUsername').textContent = '@' + userName;
    
    // Handle profile photo
    const profilePhotoLarge = document.getElementById('profilePhotoLarge');
    if (profilePhoto && profilePhoto !== 'None' && profilePhoto !== '') {
        profilePhotoLarge.src = `/static/uploads/${profilePhoto}`;
        profilePhotoLarge.style.display = 'block';
    } else {
        // Create avatar placeholder
        profilePhotoLarge.style.display = 'none';
        const avatarPlaceholder = document.createElement('div');
        avatarPlaceholder.className = 'avatar-placeholder-large rounded-circle d-flex align-items-center justify-content-center mx-auto';
        avatarPlaceholder.style.cssText = `
            width: 150px; 
            height: 150px; 
            background: var(--gradient-1); 
            color: white; 
            font-size: 3rem; 
            font-weight: 600;
            border: 4px solid var(--primary-color);
        `;
        avatarPlaceholder.textContent = displayName.charAt(0).toUpperCase();
        
        // Replace or insert avatar placeholder
        const existingPlaceholder = modal.querySelector('.avatar-placeholder-large');
        if (existingPlaceholder) {
            existingPlaceholder.remove();
        }
        profilePhotoLarge.parentNode.insertBefore(avatarPlaceholder, profilePhotoLarge);
    }
    
    // Update stats
    document.getElementById('profileSkillsCount').textContent = skillsCount;
    document.getElementById('profileRating').textContent = rating;
    document.getElementById('profileJoinDate').textContent = joinDate;
    
    // Update profile link
    document.getElementById('profileViewFullButton').href = `/profile/${userId}`;
    
    // Show modal
    modalInstance.show();
}

// Add click handlers for profile photos and avatars
document.addEventListener('DOMContentLoaded', function() {
    // Handle member avatars in room details
    const memberAvatars = document.querySelectorAll('.member-avatar');
    memberAvatars.forEach(avatar => {
        const img = avatar.querySelector('img');
        const placeholder = avatar.querySelector('.avatar-placeholder');
        const memberInfo = avatar.nextElementSibling;
        
        if (memberInfo) {
            const userName = memberInfo.querySelector('strong')?.textContent || 'Unknown';
            const userId = avatar.dataset.userId || '1';
            const profilePhoto = img?.src?.split('/').pop() || '';
            
            avatar.style.cursor = 'pointer';
            avatar.addEventListener('click', function() {
                showProfileViewer(userId, userName, userName, profilePhoto);
            });
        }
    });
    
    // Handle profile photos in skill listings
    const skillProfilePhotos = document.querySelectorAll('.skill-item img[src*="uploads/"]');
    skillProfilePhotos.forEach(photo => {
        photo.style.cursor = 'pointer';
        photo.classList.add('profile-photo-clickable');
        
        photo.addEventListener('click', function(e) {
            e.stopPropagation();
            const skillItem = this.closest('.skill-item');
            const userName = skillItem.querySelector('h6')?.textContent?.split(' - ')[0] || 'Unknown';
            const userId = this.dataset.userId || '1';
            const profilePhoto = this.src.split('/').pop();
            
            showProfileViewer(userId, userName, userName, profilePhoto);
        });
    });
    
    // Initialize tooltips for social links
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Enhanced hover effects for interactive elements
document.addEventListener('DOMContentLoaded', function() {
    // Add ripple effect to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.cssText = `
                position: absolute;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.4);
                transform: scale(0);
                animation: ripple-animation 0.6s linear;
                width: ${size}px;
                height: ${size}px;
                top: ${y}px;
                left: ${x}px;
                pointer-events: none;
            `;
            
            ripple.classList.add('ripple-effect');
            this.style.position = 'relative';
            this.style.overflow = 'hidden';
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
});

// Critical fix for dropdown menu visibility - simplified
document.addEventListener('DOMContentLoaded', function() {
    // Simple dropdown fix without conflicts
    document.addEventListener('click', function(e) {
        // Close all dropdowns when clicking outside
        if (!e.target.closest('.dropdown')) {
            document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                menu.classList.remove('show');
            });
        }
    });
});

// Simplified dropdown visibility fix
document.addEventListener('show.bs.dropdown', function(event) {
    try {
        const dropdown = event.target.nextElementSibling;
        if (dropdown && dropdown.classList.contains('dropdown-menu')) {
            dropdown.style.zIndex = '1090';
            dropdown.style.position = 'absolute';
        }
    } catch (error) {
        console.error('Dropdown show error:', error);
    }
});

// Global functions
window.showToast = showToast;
window.setLoadingState = setLoadingState;
window.copyToClipboard = copyToClipboard;
window.animateNewContent = animateNewContent;

// Simple form submission handler to prevent freezing
document.addEventListener('DOMContentLoaded', function() {
    // Handle all form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        // Skip if already initialized
        if (form.hasAttribute('data-submit-initialized')) {
            return;
        }
        form.setAttribute('data-submit-initialized', 'true');
        
        form.addEventListener('submit', function(e) {
            try {
                // Allow form to submit normally, just add loading state
                const submitButton = this.querySelector('button[type="submit"]');
                if (submitButton && !submitButton.disabled) {
                    // Store original text
                    if (!submitButton.hasAttribute('data-original-text')) {
                        submitButton.setAttribute('data-original-text', submitButton.innerHTML);
                    }
                    
                    // Set loading state
                    submitButton.disabled = true;
                    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
                    
                    // Reset after timeout as failsafe
                    setTimeout(() => {
                        if (submitButton.disabled) {
                            submitButton.disabled = false;
                            const originalText = submitButton.getAttribute('data-original-text');
                            if (originalText) {
                                submitButton.innerHTML = originalText;
                            }
                        }
                    }, 10000); // 10 second timeout
                }
            } catch (error) {
                console.error('Form submit handler error:', error);
                // Don't prevent submission even if handler fails
            }
        });
    });
});

// Specific fix for Add Skill Offered modal freezing issue
document.addEventListener('DOMContentLoaded', function() {
    const addSkillModal = document.getElementById('addSkillOfferedModal');
    const addSkillForm = addSkillModal ? addSkillModal.querySelector('form') : null;
    
    if (addSkillModal && addSkillForm) {
        console.log('Add Skill Modal found, applying fixes...');
        
        // Prevent default Bootstrap form validation conflicts
        addSkillForm.setAttribute('novalidate', 'true');
        
        // Remove any existing event listeners
        const newForm = addSkillForm.cloneNode(true);
        addSkillForm.parentNode.replaceChild(newForm, addSkillForm);
        
        // Add clean event listener
        newForm.addEventListener('submit', function(e) {
            console.log('Add Skill form submitted');
            
            // Simple validation
            const skillName = newForm.querySelector('#skill_name');
            if (!skillName || !skillName.value.trim()) {
                e.preventDefault();
                alert('Please enter a skill name');
                if (skillName) skillName.focus();
                return false;
            }
            
            // Add loading state
            const submitButton = newForm.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding Skill...';
            }
            
            // Allow form to submit normally
            console.log('Form validation passed, submitting...');
            return true;
        });
        
        // Reset form when modal opens
        addSkillModal.addEventListener('show.bs.modal', function() {
            console.log('Add Skill modal opening...');
            newForm.reset();
            newForm.classList.remove('was-validated');
            
            // Reset submit button
            const submitButton = newForm.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.innerHTML = '<i class="fas fa-plus"></i> Add Skill';
            }
        });
        
        // Clean up when modal closes
        addSkillModal.addEventListener('hidden.bs.modal', function() {
            console.log('Add Skill modal closed');
            newForm.reset();
            newForm.classList.remove('was-validated');
            
            // Reset submit button
            const submitButton = newForm.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.innerHTML = '<i class="fas fa-plus"></i> Add Skill';
            }
        });
        
        console.log('Add Skill Modal fixes applied successfully');
    } else {
        console.log('Add Skill Modal not found on this page');
    }
});

// Fix for modal trigger buttons
document.addEventListener('DOMContentLoaded', function() {
    // Fix Add Skill Offered button specifically
    const addSkillButton = document.querySelector('button[data-bs-target="#addSkillOfferedModal"]');
    if (addSkillButton) {
        console.log('Add Skill button found, applying click fix...');
        
        // Remove any existing click handlers and add clean one
        addSkillButton.addEventListener('click', function(e) {
            console.log('Add Skill button clicked');
            
            try {
                // Ensure modal exists
                const modal = document.getElementById('addSkillOfferedModal');
                if (modal) {
                    // Create or get Bootstrap modal instance
                    let modalInstance = bootstrap.Modal.getInstance(modal);
                    if (!modalInstance) {
                        modalInstance = new bootstrap.Modal(modal, {
                            backdrop: true,
                            keyboard: true,
                            focus: true
                        });
                    }
                    
                    // Show modal
                    modalInstance.show();
                    console.log('Modal shown successfully');
                } else {
                    console.error('Add Skill modal not found');
                }
            } catch (error) {
                console.error('Error showing Add Skill modal:', error);
                // Fallback - try to show modal anyway
                const modal = document.getElementById('addSkillOfferedModal');
                if (modal) {
                    modal.style.display = 'block';
                    modal.classList.add('show');
                    document.body.classList.add('modal-open');
                }
            }
        });
    }
    
    // Also fix other modal buttons
    const allModalButtons = document.querySelectorAll('[data-bs-toggle="modal"]');
    allModalButtons.forEach(button => {
        if (button.hasAttribute('data-modal-fixed')) return;
        button.setAttribute('data-modal-fixed', 'true');
        
        button.addEventListener('click', function(e) {
            const targetId = this.getAttribute('data-bs-target');
            if (targetId) {
                console.log('Modal button clicked for:', targetId);
                
                try {
                    const modal = document.querySelector(targetId);
                    if (modal) {
                        let modalInstance = bootstrap.Modal.getInstance(modal);
                        if (!modalInstance) {
                            modalInstance = new bootstrap.Modal(modal);
                        }
                        modalInstance.show();
                    }
                } catch (error) {
                    console.error('Error with modal button:', error);
                }
            }
        });
    });
});
