// Main JavaScript file for Face Recognition Attendance System

// Global variables
let videoStream = null;
let recognitionInterval = null;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeComponents();
});

// Initialize all components
function initializeComponents() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Add loading states to buttons
    initializeButtonLoading();

    // Initialize form validation
    initializeFormValidation();

    // Initialize webcam if on recognition page
    if (document.getElementById('video')) {
        initializeWebcam();
    }
}


'''
# Public Showcase Version
# Certain sensitive/internal implementation details have been intentionally omitted for security and project protection purposes.
'''
