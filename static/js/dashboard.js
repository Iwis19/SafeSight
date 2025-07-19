// Dashboard JavaScript functionality

function updateStats() {
    const crashes = document.querySelectorAll('.crash-card');
    const total = crashes.length;
    const newCount = document.querySelectorAll('.status-new').length;
    const urgentCount = document.querySelectorAll('.status-urgent').length;
    const reviewedCount = document.querySelectorAll('.status-reviewed').length;
    
    document.getElementById('total-crashes').textContent = total;
    document.getElementById('new-crashes').textContent = newCount;
    document.getElementById('urgent-crashes').textContent = urgentCount;
    document.getElementById('reviewed-crashes').textContent = reviewedCount;
}

function markUrgent(crashId) {
    updateCrashStatus(crashId, 'urgent');
}

function markReviewed(crashId) {
    updateCrashStatus(crashId, 'reviewed');
}

function updateCrashStatus(crashId, status) {
    fetch(`/api/crash/${crashId}/status`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: status })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        }
    })
    .catch(error => console.error('Error:', error));
}

function refreshData() {
    location.reload();
}

// Auto-refresh every 30 seconds
setInterval(refreshData, 30000);

// Update stats on page load
document.addEventListener('DOMContentLoaded', function() {
    updateStats();
}); 