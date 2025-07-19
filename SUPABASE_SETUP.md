# Supabase Setup Guide for AngelEye

This guide will help you set up Supabase as your cloud database for the AngelEye emergency crash detection system.

## 🚀 Step 1: Create Supabase Account

1. Go to [supabase.com](https://supabase.com)
2. Click "Start your project"
3. Sign up with GitHub or email
4. Create a new organization

## 🏗️ Step 2: Create New Project

1. Click "New Project"
2. Choose your organization
3. Enter project details:
   - **Name**: `angeleye-emergency`
   - **Database Password**: Create a strong password
   - **Region**: Choose closest to you
4. Click "Create new project"
5. Wait for setup to complete (2-3 minutes)

## 📊 Step 3: Create Database Tables

### Create the `crashes` table:

```sql
-- Run this in Supabase SQL Editor
CREATE TABLE crashes (
    id BIGSERIAL PRIMARY KEY,
    device_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    video_filename TEXT NOT NULL,
    video_url TEXT NOT NULL,
    crash_data JSONB,
    status TEXT DEFAULT 'new',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_crashes_status ON crashes(status);
CREATE INDEX idx_crashes_created_at ON crashes(created_at DESC);
CREATE INDEX idx_crashes_device_id ON crashes(device_id);
```

### Create the `devices` table (optional):

```sql
CREATE TABLE devices (
    id BIGSERIAL PRIMARY KEY,
    device_id TEXT UNIQUE NOT NULL,
    name TEXT,
    location TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 🗄️ Step 4: Create Storage Bucket

1. Go to **Storage** in your Supabase dashboard
2. Click **New Bucket**
3. Enter:
   - **Name**: `crash_videos`
   - **Public bucket**: ✅ Check this
4. Click **Create bucket**

## 🔑 Step 5: Get API Keys

1. Go to **Settings** → **API**
2. Copy these values:
   - **Project URL** (looks like: `https://your-project.supabase.co`)
   - **anon public** key (starts with `eyJ...`)

## ⚙️ Step 6: Configure Environment Variables

Create a `.env` file in your project root:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
```

## 🧪 Step 7: Test the Setup

1. **Install dependencies**:
   ```bash
   pip install python-dotenv
   ```

2. **Update supabase_config.py**:
   ```python
   from dotenv import load_dotenv
   load_dotenv()  # Add this line at the top
   ```

3. **Test connection**:
   ```bash
   python -c "from supabase_service import supabase_service; print('Supabase connected!')"
   ```

## 🚀 Step 8: Run Supabase Server

```bash
python emergency_server_supabase.py
```

## 📱 Step 9: Update Raspberry Pi Configuration

Update your `config.py` to point to your Supabase server:

```python
CLIENT_CONFIG = {
    'server_url': 'http://your-server-ip:5000',  # Your server running Supabase
    'api_key': None,
    # ... other settings
}
```

## 🔒 Step 10: Security Settings (Optional)

### Row Level Security (RLS):

```sql
-- Enable RLS on crashes table
ALTER TABLE crashes ENABLE ROW LEVEL SECURITY;

-- Create policy for reading crashes
CREATE POLICY "Allow read access to crashes" ON crashes
    FOR SELECT USING (true);

-- Create policy for inserting crashes
CREATE POLICY "Allow insert access to crashes" ON crashes
    FOR INSERT WITH CHECK (true);

-- Create policy for updating crashes
CREATE POLICY "Allow update access to crashes" ON crashes
    FOR UPDATE USING (true);
```

### Storage Policies:

```sql
-- Allow public read access to crash videos
CREATE POLICY "Public Access" ON storage.objects
    FOR SELECT USING (bucket_id = 'crash_videos');

-- Allow authenticated uploads
CREATE POLICY "Authenticated uploads" ON storage.objects
    FOR INSERT WITH CHECK (bucket_id = 'crash_videos');
```

## 🌐 Benefits of Supabase:

- ✅ **Cloud Database**: No local storage needed
- ✅ **Real-time**: Live updates across devices
- ✅ **File Storage**: Videos stored in the cloud
- ✅ **Scalable**: Handles multiple emergency departments
- ✅ **Secure**: Built-in authentication and security
- ✅ **Backup**: Automatic backups and recovery

## 🐛 Troubleshooting:

### Common Issues:

1. **Connection Error**: Check your API keys and URL
2. **Upload Fails**: Verify storage bucket exists and is public
3. **Permission Denied**: Check RLS policies
4. **Video Not Playing**: Ensure storage bucket is public

### Debug Mode:

```python
# Add to supabase_service.py for debugging
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📞 Support:

- **Supabase Docs**: [supabase.com/docs](https://supabase.com/docs)
- **Community**: [github.com/supabase/supabase](https://github.com/supabase/supabase)

---

**🎉 Congratulations!** Your AngelEye system is now powered by Supabase cloud database! 