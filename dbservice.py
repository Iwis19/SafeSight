import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from dbconfig import get_supabase_client, CRASHES_TABLE, VIDEO_BUCKET

class SupabaseService:
    def __init__(self):
        self.supabase = get_supabase_client()
    
    #upload crash vids to supabase storage
    def upload_crash_video(self, video_path: str, crash_data: Dict) -> Dict:
        try:
            #upload vid
            video_filename = os.path.basename(video_path)
            with open(video_path, 'rb') as video_file:
                result = self.supabase.storage.from_(VIDEO_BUCKET).upload(
                    path=video_filename,
                    file=video_file,
                    file_options={"content-type": "video/mp4"}
                )
            
            #get public url
            video_url = self.supabase.storage.from_(VIDEO_BUCKET).get_public_url(video_filename)
            # Clean the URL by removing trailing question mark if present
            if video_url.endswith('?'):
                video_url = video_url[:-1]
            
            #metadata 
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
    
    #get all crashes from db
    def get_crashes(self, limit: int = 100) -> List[Dict]:
        try:
            print("DEBUG: Fetching crashes from Supabase...")
            result = self.supabase.table(CRASHES_TABLE)\
                .select('*')\
                .order('created_at', desc=True)\
                .limit(limit)\
                .execute()
            
            print(f"DEBUG: Raw result from Supabase: {result}")
            print(f"DEBUG: Number of crashes returned: {len(result.data) if result.data else 0}")
            
            crashes = []
            for crash in result.data:
                crash['crash_data'] = json.loads(crash['crash_data']) if crash['crash_data'] else {}
                # Clean video URL by removing trailing question mark if present
                if crash.get('video_url') and crash['video_url'].endswith('?'):
                    crash['video_url'] = crash['video_url'][:-1]
                crashes.append(crash)
                print(f"DEBUG: Processed crash ID {crash.get('id')}: {crash.get('video_filename')}")
            
            print(f"DEBUG: Returning {len(crashes)} crashes")
            return crashes
            
        except Exception as e:
            print(f"Supabase get crashes error: {str(e)}")
            return []
    
    #update crash status
    def update_crash_status(self, crash_id: int, status: str) -> bool:
        try:
            result = self.supabase.table(CRASHES_TABLE)\
                .update({'status': status})\
                .eq('id', crash_id)\
                .execute()
            
            return len(result.data) > 0
            
        except Exception as e:
            print(f"Supabase update status error: {str(e)}")
            return False
    
    #get crash statistics
    def get_crash_stats(self) -> Dict:
        try:
            #ttotal crashes
            total_result = self.supabase.table(CRASHES_TABLE)\
                .select('id', count='exact')\
                .execute()
            
            #crashes by status
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
    
    #clear all crashes from database and reset auto-increment
    def clear_all_crashes(self) -> bool:
        try:
            print("DEBUG: Attempting to clear all crashes from database...")
            result = self.supabase.table(CRASHES_TABLE).delete().neq('id', 0).execute()
            print(f"DEBUG: Clear result: {result}")
            
            # Reset auto-increment counter
            self.reset_auto_increment()
            
            return True
        except Exception as e:
            print(f"Supabase clear crashes error: {str(e)}")
            return False
    
    #reset auto-increment counter to start from 1
    def reset_auto_increment(self) -> bool:
        try:
            print("DEBUG: Resetting auto-increment counter...")
            # Execute SQL to reset the sequence
            sql = f"ALTER SEQUENCE {CRASHES_TABLE}_id_seq RESTART WITH 1;"
            result = self.supabase.rpc('exec_sql', {'sql': sql}).execute()
            print(f"DEBUG: Reset auto-increment result: {result}")
            return True
        except Exception as e:
            print(f"Supabase reset auto-increment error: {str(e)}")
            # Try alternative method if RPC doesn't work
            try:
                print("DEBUG: Trying alternative reset method...")
                # Insert and immediately delete a dummy record to reset counter
                dummy_data = {
                    'device_id': 'reset_counter',
                    'timestamp': datetime.now().isoformat(),
                    'video_filename': 'dummy.mp4',
                    'video_url': 'dummy',
                    'crash_data': '{}',
                    'status': 'new',
                    'created_at': datetime.now().isoformat()
                }
                insert_result = self.supabase.table(CRASHES_TABLE).insert(dummy_data).execute()
                if insert_result.data:
                    dummy_id = insert_result.data[0]['id']
                    self.supabase.table(CRASHES_TABLE).delete().eq('id', dummy_id).execute()
                    print(f"DEBUG: Alternative reset successful, dummy ID was: {dummy_id}")
                return True
            except Exception as e2:
                print(f"Supabase alternative reset error: {str(e2)}")
                return False
    
    #delete specific crash by ID
    def delete_crash(self, crash_id: int) -> bool:
        try:
            print(f"DEBUG: Attempting to delete crash ID {crash_id}...")
            result = self.supabase.table(CRASHES_TABLE).delete().eq('id', crash_id).execute()
            print(f"DEBUG: Delete result: {result}")
            return len(result.data) > 0
        except Exception as e:
            print(f"Supabase delete crash error: {str(e)}")
            return False

supabase_service = SupabaseService() 