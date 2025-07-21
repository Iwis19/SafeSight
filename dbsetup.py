#!/usr/bin/env python3
"""
Supabase Setup Script for AngelEye
This script helps you configure Supabase for the AngelEye project.
"""

import os
import sys
from dbconfig import get_supabase_client

def setup_environment():
    """Setup environment variables for Supabase"""
    print("🔧 AngelEye Supabase Setup")
    print("=" * 40)
    
    # Check if environment variables are set
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not supabase_url or supabase_url == 'your-supabase-url-here':
        print("❌ SUPABASE_URL not set")
        print("Please set your Supabase URL:")
        print("Windows: set SUPABASE_URL=your-url-here")
        print("Linux/Mac: export SUPABASE_URL=your-url-here")
        return False
    
    if not supabase_key or supabase_key == 'your-supabase-anon-key-here':
        print("❌ SUPABASE_ANON_KEY not set")
        print("Please set your Supabase anonymous key:")
        print("Windows: set SUPABASE_ANON_KEY=your-key-here")
        print("Linux/Mac: export SUPABASE_ANON_KEY=your-key-here")
        return False
    
    print("✅ Environment variables are set")
    return True

def test_connection():
    """Test Supabase connection"""
    print("\n🔍 Testing Supabase connection...")
    
    try:
        supabase = get_supabase_client()
        
        # Test basic connection by trying to access a table
        # This will fail if connection is bad, but won't break if table doesn't exist
        result = supabase.table('crashes').select('id').limit(1).execute()
        print("✅ Supabase connection successful!")
        return True
        
    except Exception as e:
        print(f"❌ Supabase connection failed: {str(e)}")
        print("\nPossible issues:")
        print("1. Check your SUPABASE_URL and SUPABASE_ANON_KEY")
        print("2. Make sure your Supabase project is active")
        print("3. Check if you have the correct permissions")
        return False

def create_tables():
    """Create required tables in Supabase"""
    print("\n📋 Creating database tables...")
    print("Please run these SQL commands in your Supabase SQL editor:")
    
    sql_commands = """
-- Create crashes table
CREATE TABLE IF NOT EXISTS crashes (
    id BIGSERIAL PRIMARY KEY,
    device_id TEXT NOT NULL DEFAULT 'unknown',
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    video_filename TEXT,
    video_url TEXT,
    crash_data JSONB,
    status TEXT NOT NULL DEFAULT 'new',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create devices table
CREATE TABLE IF NOT EXISTS devices (
    id BIGSERIAL PRIMARY KEY,
    device_id TEXT UNIQUE NOT NULL,
    name TEXT,
    location TEXT,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_crashes_timestamp ON crashes(timestamp);
CREATE INDEX IF NOT EXISTS idx_crashes_status ON crashes(status);
CREATE INDEX IF NOT EXISTS idx_crashes_device_id ON crashes(device_id);
"""
    
    print(sql_commands)
    print("After running these commands, your Supabase database will be ready!")

def setup_storage():
    """Setup storage bucket"""
    print("\n📦 Setting up storage bucket...")
    print("Please create a storage bucket named 'crash_videos' in your Supabase dashboard:")
    print("1. Go to Storage in your Supabase dashboard")
    print("2. Click 'Create a new bucket'")
    print("3. Name it 'crash_videos'")
    print("4. Set it to public (for video access)")
    print("5. Click 'Create bucket'")

def main():
    """Main setup function"""
    print("🚀 Welcome to AngelEye Supabase Setup!")
    
    # Check environment
    if not setup_environment():
        print("\n📝 Next steps:")
        print("1. Set your environment variables")
        print("2. Run this script again")
        return
    
    # Test connection
    if not test_connection():
        print("\n📝 Next steps:")
        print("1. Check your Supabase credentials")
        print("2. Make sure your project is active")
        print("3. Run this script again")
        return
    
    # Setup database
    create_tables()
    
    # Setup storage
    setup_storage()
    
    print("\n🎉 Setup complete!")
    print("Your AngelEye project is ready to use with Supabase!")
    print("\nTo run with Supabase:")
    print("python3 insurance_server.py")

if __name__ == "__main__":
    main() 