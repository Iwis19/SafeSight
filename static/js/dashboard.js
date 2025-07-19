//dashboard functionality

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

//enhanced features

let currentCrashId = null;
let currentCrashData = null;

function openVideoModal(crashId, videoUrl, crashData) {
    currentCrashId = crashId;
    currentCrashData = crashData;
    
    document.getElementById('modal-video-source').src = videoUrl;
    document.getElementById('modal-video').load();
    document.getElementById('modal-title').textContent = `Crash Report #${crashId}`;
    
    //populate details (commented in .html)
    const detailsDiv = document.getElementById('video-details');
    detailsDiv.innerHTML = `
        <div class="detail-row">
            <span class="detail-label">Device ID:</span>
            <span class="detail-value">${crashData.device_id || 'Unknown'}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">Timestamp:</span>
            <span class="detail-value">${new Date(crashData.timestamp).toLocaleString()}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">Status:</span>
            <span class="detail-value">
                <span class="status-badge status-${crashData.status}">${crashData.status}</span>
            </span>
        </div>
        <div class="detail-row">
            <span class="detail-label">Created:</span>
            <span class="detail-value">${new Date(crashData.created_at).toLocaleString()}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">Video URL:</span>
            <span class="detail-value">${crashData.video_url || crashData.video_filename || 'N/A'}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">Crash Data:</span>
            <span class="detail-value">${JSON.stringify(crashData.crash_data || {}, null, 2)}</span>
        </div>
    `;
    
    document.getElementById('videoModal').style.display = 'block';
}

function closeVideoModal() {
    document.getElementById('videoModal').style.display = 'none';
    currentCrashId = null;
    currentCrashData = null;
}

function markUrgentModal() {
    if (currentCrashId) {
        markUrgent(currentCrashId);
        closeVideoModal();
    }
}

function markReviewedModal() {
    if (currentCrashId) {
        markReviewed(currentCrashId);
        closeVideoModal();
    }
}

function downloadVideo() {
    if (currentCrashData) {
        const videoUrl = currentCrashData.video_url || `/static/crash_videos/${currentCrashData.video_filename}`;
        const link = document.createElement('a');
        link.href = videoUrl;
        link.download = `crash_${currentCrashId}_${new Date().getTime()}.avi`;
        link.click();
    }
}

function exportCrashData() {
    if (currentCrashData) {
        const dataStr = JSON.stringify(currentCrashData, null, 2);
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `crash_data_${currentCrashId}.json`;
        link.click();
    }
}

function deleteCrash() {
    if (currentCrashId && confirm('Are you sure you want to delete this crash report?')) {
        //add/delete
        alert('Delete functionality would be implemented here');
        closeVideoModal();
    }
}

function exportData() {
    fetch('/api/crashes')
        .then(response => response.json())
        .then(data => {
            const dataStr = JSON.stringify(data, null, 2);
            const dataBlob = new Blob([dataStr], {type: 'application/json'});
            const link = document.createElement('a');
            link.href = URL.createObjectURL(dataBlob);
            link.download = `all_crash_data_${new Date().getTime()}.json`;
            link.click();
        })
        .catch(error => {
            console.error('Error exporting data:', error);
            alert('Error exporting data. Please try again.');
        });
}

//close modal when click outside
window.onclick = function(event) {
    const modal = document.getElementById('videoModal');
    if (event.target === modal) {
        closeVideoModal();
    }
}

//close modal with esc
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeVideoModal();
    }
});

//auto refresh if modal is not open every 30s
setInterval(function() {
    if (!document.getElementById('videoModal').style.display || 
        document.getElementById('videoModal').style.display === 'none') {
        refreshData();
    }
}, 30000);

//update stats
document.addEventListener('DOMContentLoaded', function() {
    updateStats();
}); 