import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from supabase_config import get_supabase_client, CRASHES_TABLE, VIDEO_BUCKET

class SupabaseService:
    def __init__(self):
        self.supabase = get_supabase_client()
    
    def upload_crash_video(self, video_path: str, crash_data: Dict) -> Dict:
        """Upload crash video to Supabase Storage and save metadata to database"""
        try:
            # Upload video to Supabase Storage
            video_filename = os.path.basename(video_path)
            with open(video_path, 'rb') as video_file:
                result = self.supabase.storage.from_(VIDEO_BUCKET).upload(
                    path=video_filename,
                    file=video_file,
                    file_options={"content-type": "video/avi"}
                )
            
            # Get public URL for the video
            video_url = self.supabase.storage.from_(VIDEO_BUCKET).get_public_url(video_filename)
            
            # Save crash metadata to database
            crash_record = {
                'device_id': crash_data.get('device_id', 'unknown'),
                'timestamp': crash_data.get('timestamp', datetime.now().isoformat()),
                'video_filename': video_filename,
                'video_url': video_url,
                'crash_data': json.dumps(crash_data),
                'status': 'new',
                'created_at': datetime.now().isoformat()
            }
            
            result = self.supabase.table(CRASHES_TABLE).insert(crash_record).execute()
            
            return {
                'success': True,
                'video_url': video_url,
                'crash_id': result.data[0]['id'] if result.data else None
            }
            
        except Exception as e:
            print(f"Supabase upload error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_crashes(self, limit: int = 100) -> List[Dict]:
        """Get all crashes from database"""
        try:
            result = self.supabase.table(CRASHES_TABLE)\
                .select('*')\
                .order('created_at', desc=True)\
                .limit(limit)\
                .execute()
            
            crashes = []
            for crash in result.data:
                crash['crash_data'] = json.loads(crash['crash_data']) if crash['crash_data'] else {}
                crashes.append(crash)
            
            return crashes
            
        except Exception as e:
            print(f"Supabase get crashes error: {str(e)}")
            return []
    
    def update_crash_status(self, crash_id: int, status: str) -> bool:
        """Update crash status"""
        try:
            result = self.supabase.table(CRASHES_TABLE)\
                .update({'status': status})\
                .eq('id', crash_id)\
                .execute()
            
            return len(result.data) > 0
            
        except Exception as e:
            print(f"Supabase update status error: {str(e)}")
            return False
    
    def get_crash_stats(self) -> Dict:
        """Get crash statistics"""
        try:
            # Get total crashes
            total_result = self.supabase.table(CRASHES_TABLE)\
                .select('id', count='exact')\
                .execute()
            
            # Get crashes by status
            new_result = self.supabase.table(CRASHES_TABLE)\
                .select('id', count='exact')\
                .eq('status', 'new')\
                .execute()
            
            urgent_result = self.supabase.table(CRASHES_TABLE)\
                .select('id', count='exact')\
                .eq('status', 'urgent')\
                .execute()
            
            reviewed_result = self.supabase.table(CRASHES_TABLE)\
                .select('id', count='exact')\
                .eq('status', 'reviewed')\
                .execute()
            
            return {
                'total': total_result.count or 0,
                'new': new_result.count or 0,
                'urgent': urgent_result.count or 0,
                'reviewed': reviewed_result.count or 0
            }
            
        except Exception as e:
            print(f"Supabase stats error: {str(e)}")
            return {'total': 0, 'new': 0, 'urgent': 0, 'reviewed': 0}

# Global Supabase service instance
supabase_service = SupabaseService() 