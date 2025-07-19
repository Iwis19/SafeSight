# AngelEye Configuration

# Client Configuration (Raspberry Pi)
CLIENT_CONFIG = {
    'server_url': 'http://10.24.22.66:5000',  # Your laptop's IP address
    'api_key': None,  # Add API key if required
    'upload_retry_attempts': 3,
    'upload_retry_delay': 5,  # seconds
    'acceleration_threshold': 20,
    'frame_rate': 30,
    'buffer_seconds': 10
}

# Server Configuration (Emergency Department)
SERVER_CONFIG = {
    'host': '0.0.0.0',
    'port': 5000,
    'upload_folder': 'crash_videos',
    'database': 'emergency_crashes.db',
    'allowed_video_extensions': {'avi', 'mp4', 'mov', 'mkv'},
    'max_file_size': 100 * 1024 * 1024  # 100MB
}

# Network Configuration
NETWORK_CONFIG = {
    'timeout': 30,  # seconds
    'max_connections': 100,
    'enable_ssl': False,  # Set to True for production
    'ssl_cert': None,
    'ssl_key': None
} 