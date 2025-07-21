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

function clearAllCrashes() {
    console.log('clearAllCrashes function called');
    if (confirm('Are you sure you want to delete ALL crash reports? This action cannot be undone.')) {
        console.log('User confirmed, making API call...');
        fetch('/api/clear-all-crashes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => {
            console.log('Response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('Response data:', data);
            if (data.success) {
                alert('All crashes cleared successfully!');
                location.reload();
            } else {
                alert('Error: ' + (data.error || 'Failed to clear crashes'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error clearing crashes. Please try again.');
        });
    }
}


//enhanced features

let currentCrashId = null;
let currentCrashData = null;

function openVideoModal(crashId, videoUrl) {
    console.log('openVideoModal called with:', { crashId, videoUrl });
    currentCrashId = crashId;
    
    // Use the proxy URL to avoid CORS issues
    const fullVideoUrl = `/video/${videoUrl}`;
    console.log('Setting video source to:', fullVideoUrl);
    document.getElementById('modal-video-source').src = fullVideoUrl;
    document.getElementById('modal-video').load();
    document.getElementById('modal-title').textContent = `Crash Report #${crashId}`;
    
    // Fetch crash data from server
    fetch(`/api/crashes`)
        .then(response => response.json())
        .then(crashes => {
            const crashData = crashes.find(crash => crash.id === crashId);
            if (crashData) {
                currentCrashData = crashData;
                populateModalDetails(crashData);
            } else {
                console.error('Crash data not found for ID:', crashId);
            }
        })
        .catch(error => {
            console.error('Error fetching crash data:', error);
        });
    
    document.getElementById('videoModal').style.display = 'block';
}

function populateModalDetails(crashData) {
    console.log('Populating modal details with:', crashData);
    const detailsDiv = document.getElementById('video-details');
    
    // Format crash data nicely
    let crashDataHtml = '';
    if (crashData.crash_data && typeof crashData.crash_data === 'object') {
        const crashInfo = crashData.crash_data;
        crashDataHtml = `
            <div class="detail-row">
                <span class="detail-label">Recording Interval:</span>
                <span class="detail-value">${crashInfo.recording_interval || 'N/A'} seconds</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Buffer Seconds:</span>
                <span class="detail-value">${crashInfo.buffer_seconds || 'N/A'} seconds</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Frame Rate:</span>
                <span class="detail-value">${crashInfo.frame_rate || 'N/A'} fps</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Detection Type:</span>
                <span class="detail-value">${crashInfo.detection_type || 'N/A'}</span>
            </div>
        `;
    }
    
    detailsDiv.innerHTML = `
        <div class="detail-row">
            <span class="detail-label">Device ID:</span>
            <span class="detail-value">${crashData.device_id || 'Unknown'}</span>
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
            <span class="detail-label">Video Filename:</span>
            <span class="detail-value">${crashData.video_filename || 'N/A'}</span>
        </div>
        ${crashDataHtml}
    `;
}

function closeVideoModal() {
    console.log('closeVideoModal called');
    const modal = document.getElementById('videoModal');
    console.log('Modal element:', modal);
    modal.style.display = 'none';
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
        fetch(`/api/crash/${currentCrashId}/delete`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Crash deleted successfully!');
                closeVideoModal();
                location.reload();
            } else {
                alert('Error: ' + (data.error || 'Failed to delete crash'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error deleting crash. Please try again.');
        });
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
    
    // Test video URLs to see if they're accessible
    const videos = document.querySelectorAll('video source');
    videos.forEach((source, index) => {
        const url = source.src;
        console.log(`Testing video ${index + 1}: ${url}`);
        
        fetch(url, { method: 'HEAD' })
            .then(response => {
                console.log(`Video ${index + 1} response:`, response.status, response.headers.get('content-type'));
            })
            .catch(error => {
                console.error(`Video ${index + 1} fetch error:`, error);
            });
    });
}); 