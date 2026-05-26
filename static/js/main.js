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

// Button loading states
function initializeButtonLoading() {
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            if (this.classList.contains('btn-loading')) {
                return;
            }

            // Add loading state
            this.classList.add('btn-loading');
            const originalText = this.innerHTML;
            this.innerHTML = '<span class="loading me-2"></span>Loading...';

            // Remove loading state after 3 seconds (or when response comes)
            setTimeout(() => {
                this.classList.remove('btn-loading');
                this.innerHTML = originalText;
            }, 3000);
        });
    });
}

// Form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
}

// Webcam functionality
function initializeWebcam() {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const startBtn = document.getElementById('start-recognition');
    const stopBtn = document.getElementById('stop-recognition');

    if (!video || !canvas) return;

    const ctx = canvas.getContext('2d');

    // Start webcam
    async function startWebcam() {
        try {
            videoStream = await navigator.mediaDevices.getUserMedia({
                video: { width: 640, height: 480 }
            });
            video.srcObject = videoStream;
            video.play();

            // Set canvas size to match video
            video.addEventListener('loadedmetadata', function() {
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
            });

            showAlert('Webcam started successfully', 'success');
        } catch (error) {
            console.error('Error accessing webcam:', error);
            showAlert('Error accessing webcam. Please check permissions.', 'danger');
        }
    }

    // Stop webcam
    function stopWebcam() {
        if (videoStream) {
            videoStream.getTracks().forEach(track => track.stop());
            video.srcObject = null;
            videoStream = null;
        }
        if (recognitionInterval) {
            clearInterval(recognitionInterval);
            recognitionInterval = null;
        }
    }

    // Start face recognition
    function startRecognition() {
        if (!videoStream) {
            showAlert('Please start the webcam first', 'warning');
            return;
        }

        recognitionInterval = setInterval(async function() {
            // Capture frame
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

            // Convert to blob and send to server
            canvas.toBlob(async function(blob) {
                const formData = new FormData();
                formData.append('frame', blob);

                try {
                    const response = await fetch('/recognize', {
                        method: 'POST',
                        body: formData
                    });

                    const result = await response.json();

                    if (result.success && result.recognized) {
                        showAlert(`Student recognized: ${result.name} (${result.roll})`, 'success');
                        // Mark attendance automatically
                        markAttendance(result.student_id, result.roll, result.name);
                    }
                } catch (error) {
                    console.error('Recognition error:', error);
                }
            }, 'image/jpeg');
        }, 1000); // Check every second

        showAlert('Face recognition started', 'info');
    }

    // Stop recognition
    function stopRecognition() {
        if (recognitionInterval) {
            clearInterval(recognitionInterval);
            recognitionInterval = null;
            showAlert('Face recognition stopped', 'info');
        }
    }

    // Mark attendance
    async function markAttendance(studentId, roll, name) {
        try {
            const response = await fetch('/mark_attendance', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    student_id: studentId,
                    roll: roll,
                    name: name
                })
            });

            const result = await response.json();
            if (result.success) {
                showAlert(`Attendance marked for ${name}`, 'success');
            }
        } catch (error) {
            console.error('Attendance marking error:', error);
        }
    }

    // Event listeners
    if (startBtn) {
        startBtn.addEventListener('click', startWebcam);
    }

    if (stopBtn) {
        stopBtn.addEventListener('click', stopWebcam);
    }

    // Add recognition controls if they exist
    const startRecBtn = document.getElementById('start-recognition-btn');
    const stopRecBtn = document.getElementById('stop-recognition-btn');

    if (startRecBtn) {
        startRecBtn.addEventListener('click', startRecognition);
    }

    if (stopRecBtn) {
        stopRecBtn.addEventListener('click', stopRecognition);
    }
}

// Utility functions
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alert-container') || createAlertContainer();

    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    alertContainer.appendChild(alert);

    // Auto remove after 5 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 5000);
}

function createAlertContainer() {
    const container = document.createElement('div');
    container.id = 'alert-container';
    container.className = 'position-fixed top-0 end-0 p-3';
    container.style.zIndex = '1050';
    document.body.appendChild(container);
    return container;
}

// Progress bar functions
function updateProgress(percent, message = '') {
    const progressBar = document.querySelector('.progress-bar');
    const progressText = document.getElementById('progress-text');

    if (progressBar) {
        progressBar.style.width = `${percent}%`;
        progressBar.setAttribute('aria-valuenow', percent);
    }

    if (progressText) {
        progressText.textContent = message || `${percent}% Complete`;
    }
}

// Table search functionality
function initializeTableSearch() {
    const searchInputs = document.querySelectorAll('.table-search');
    searchInputs.forEach(input => {
        input.addEventListener('input', function() {
            const table = this.closest('.table-container').querySelector('table');
            const filter = this.value.toLowerCase();
            const rows = table.querySelectorAll('tbody tr');

            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(filter) ? '' : 'none';
            });
        });
    });
}

// Modal functions
function showModal(modalId) {
    const modal = new bootstrap.Modal(document.getElementById(modalId));
    modal.show();
}

function hideModal(modalId) {
    const modal = bootstrap.Modal.getInstance(document.getElementById(modalId));
    if (modal) {
        modal.hide();
    }
}

// AJAX form submission
function submitFormAsync(formId, successCallback = null, errorCallback = null) {
    const form = document.getElementById(formId);
    if (!form) return;

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const formData = new FormData(form);
        const submitBtn = form.querySelector('button[type="submit"]');

        // Disable button
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="loading me-2"></span>Submitting...';
        }

        try {
            const response = await fetch(form.action, {
                method: form.method || 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok && result.success) {
                showAlert(result.message || 'Operation successful', 'success');
                if (successCallback) successCallback(result);
            } else {
                showAlert(result.message || 'Operation failed', 'danger');
                if (errorCallback) errorCallback(result);
            }
        } catch (error) {
            console.error('Form submission error:', error);
            showAlert('Network error occurred', 'danger');
            if (errorCallback) errorCallback(error);
        } finally {
            // Re-enable button
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = submitBtn.getAttribute('data-original-text') || 'Submit';
            }
        }
    });
}

// Export functions
function exportToCSV(tableId, filename = 'export.csv') {
    const table = document.getElementById(tableId);
    if (!table) return;

    let csv = [];
    const rows = table.querySelectorAll('tr');

    for (let i = 0; i < rows.length; i++) {
        const row = [];
        const cols = rows[i].querySelectorAll('td, th');

        for (let j = 0; j < cols.length; j++) {
            row.push('"' + cols[j].innerText.replace(/"/g, '""') + '"');
        }

        csv.push(row.join(','));
    }

    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');

    if (link.download !== undefined) {
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', filename);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

// Initialize table search
initializeTableSearch();

// Add fade-in animation to cards
document.querySelectorAll('.card').forEach((card, index) => {
    card.style.animationDelay = `${index * 0.1}s`;
    card.classList.add('fade-in');
});
