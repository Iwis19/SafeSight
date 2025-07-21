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

function openVideoModal(cardNumber, crashId, videoUrl) {
    console.log('openVideoModal called with:', { cardNumber, crashId, videoUrl });
    currentCrashId = crashId;
    currentCrashData = null;
    
    //uses proxy url to avoid bad bad cors problems
    const fullVideoUrl = `/video/${videoUrl}`;
    console.log('Setting video source to:', fullVideoUrl);
    document.getElementById('modal-video-source').src = fullVideoUrl;
    document.getElementById('modal-video').load();
    document.getElementById('modal-title').textContent = `Crash Report #${cardNumber}`;
    
    //fetch data
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
    const crashInfo = crashData.crash_data || {};

    //FOR DEMO PURPOSE ONLY!!1!1!!1!

    //randomly generates real life accel, speed, etc information for display (no sensor :((
    const accel = crashInfo.acceleration || (Math.random() * (6 - 1) + 1).toFixed(2); // 1g to 6g
    const speed = crashInfo.speed || (Math.random() * (120 - 20) + 20).toFixed(1); // 20 to 120 km/h
    const lat = crashInfo.location_lat || (37 + Math.random()).toFixed(6); // Random lat
    const lon = crashInfo.location_lon || (-122 + Math.random()).toFixed(6); // Random lon
    const location = crashInfo.location || `${lat}, ${lon}`;
    //end of random generator

    detailsDiv.innerHTML = `
        <div class="detail-row">
            <span class="detail-label">Driver ID:</span>
            <span class="detail-value">${crashData.crash_data && crashData.crash_data.driver_id ? crashData.crash_data.driver_id : 'N/A'}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">Device ID:</span>
            <span class="detail-value">${crashData.device_id || 'N/A'}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">Video URL:</span>
            <span class="detail-value">
                ${(crashData.video_url) ? `<a href="${crashData.video_url}" target="_blank">${crashData.video_url}</a>` : (crashData.video_filename || 'N/A')}
            </span>
        </div>
        <div class="detail-row">
            <span class="detail-label">Frame Rate:</span>
            <span class="detail-value">${crashInfo.frame_rate || '30'} fps</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">Acceleration (g):</span>
            <span class="detail-value">${accel}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">Speed (km/h):</span>
            <span class="detail-value">${speed}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">Detection Type:</span>
            <span class="detail-value">${crashInfo.detection_type || 'N/A'}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">Location (GPS):</span>
            <span class="detail-value">${location}</span>
        </div>
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

let pendingDeleteCrashId = null;
let confirmActionType = null;

function showConfirmModal(actionType, id = null) {
    confirmActionType = actionType;
    pendingDeleteCrashId = id;
    const modal = document.getElementById('confirmModal');
    const title = document.getElementById('confirmModalTitle');
    const message = document.getElementById('confirmModalMessage');
    const confirmBtn = document.getElementById('confirmModalConfirmBtn');

    if (actionType === 'delete') {
        title.textContent = 'Delete Crash Report?';
        message.textContent = 'Are you sure you want to delete this crash report? This action cannot be undone.';
        confirmBtn.textContent = 'Delete';
        confirmBtn.className = 'btn btn-danger';
        confirmBtn.onclick = confirmDeleteCrash;
    } else if (actionType === 'clearAll') {
        title.textContent = 'Clear All Crash Reports?';
        message.textContent = 'Are you sure you want to delete ALL crash reports? This action cannot be undone.';
        confirmBtn.textContent = 'Clear All';
        confirmBtn.className = 'btn btn-danger';
        confirmBtn.onclick = confirmClearAllCrashes;
    }
    modal.style.display = 'block';
}

function closeConfirmModal() {
    document.getElementById('confirmModal').style.display = 'none';
    pendingDeleteCrashId = null;
    confirmActionType = null;
}

function deleteCrashById(crashId) {
    showConfirmModal('delete', crashId);
}

function clearAllCrashes() {
    showConfirmModal('clearAll');
}

function confirmDeleteCrash() {
    if (!pendingDeleteCrashId) return closeConfirmModal();
    fetch(`/api/crash/${pendingDeleteCrashId}/delete`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('Error: ' + (data.error || 'Failed to delete crash'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error deleting crash. Please try again.');
    })
    .finally(() => {
        closeConfirmModal();
    });
}

function confirmClearAllCrashes() {
    fetch('/api/clear-all-crashes', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('Error: ' + (data.error || 'Failed to clear crashes'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error clearing crashes. Please try again.');
    })
    .finally(() => {
        closeConfirmModal();
    });
}

//closing modal

//w/ click
window.onclick = function(event) {
    const modal = document.getElementById('confirmModal');
    if (event.target === modal) {
        closeConfirmModal();
    }
}

//w/ escape
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeVideoModal();
    }
});

//auto refresh
setInterval(function() {
    if (!document.getElementById('videoModal').style.display || 
        document.getElementById('videoModal').style.display === 'none') {
        refreshData();
    }
}, 30000);

//update stats
document.addEventListener('DOMContentLoaded', function() {
    updateStats();
    
    //test video url - outputs in console
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