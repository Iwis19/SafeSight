import os
from supabase import create_client, Client

# Supabase Configuration
# You'll need to get these from your Supabase project dashboard
SUPABASE_URL = os.getenv('SUPABASE_URL', 'your-supabase-url-here')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY', 'your-supabase-anon-key-here')

# Initialize Supabase client
def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# Database table names
CRASHES_TABLE = 'crashes'
DEVICES_TABLE = 'devices'

# Storage bucket names
VIDEO_BUCKET = 'crash_videos' 