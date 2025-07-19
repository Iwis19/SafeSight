import os
from supabase import create_client, Client

#config
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://gvpzjcreyzwrumwyvhim.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd2cHpqY3JleXp3cnVtd3l2aGltIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI4OTY5OTAsImV4cCI6MjA2ODQ3Mjk5MH0.0I0pvNFVccVy4ZmhMU38NcanujWDaexoWh291NnGelA')

#initialization + get instance
def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

#database table names
CRASHES_TABLE = 'crashes'
DEVICES_TABLE = 'devices'

#storage bucket
VIDEO_BUCKET = 'crash_videos' 