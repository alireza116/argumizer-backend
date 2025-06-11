import yt_dlp
import os
import tempfile
import re
from datetime import datetime

def parse_timestamp(timestamp):
    """Convert SRT timestamp to seconds"""
    timestamp = timestamp.replace(',', '.')
    time_obj = datetime.strptime(timestamp, '%H:%M:%S.%f')
    total_seconds = time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second + time_obj.microsecond / 1000000
    return round(total_seconds, 3)

def parse_srt_to_json(srt_content):
    """Parse SRT format into structured JSON"""
    # Split the content into subtitle blocks
    subtitle_blocks = re.split(r'\n\n+', srt_content.strip())
    parsed_subtitles = []
    
    for block in subtitle_blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 3:  # Valid subtitle block should have at least 3 lines
            try:
                # Get index
                index = int(lines[0])
                
                # Parse timestamp line
                timestamp_line = lines[1]
                start_time, end_time = timestamp_line.split(' --> ')
                
                # Get text (might be multiple lines)
                text = ' '.join(lines[2:])
                
                parsed_subtitles.append({
                    'index': index,
                    'start_time': parse_timestamp(start_time),
                    'end_time': parse_timestamp(end_time),
                    'start_time_text': start_time,
                    'end_time_text': end_time,
                    'text': text
                })
            except (ValueError, IndexError) as e:
                print(f"Error parsing subtitle block: {e}")
                continue
    
    return parsed_subtitles

def get_video_transcript(video_url, lang='en'):
    with tempfile.TemporaryDirectory() as temp_dir:
        ydl_opts = {
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitlesformat': 'srt',
            'skip_download': True,
            'quiet': True,
            'outtmpl': os.path.join(temp_dir, 'subtitle'),
            'subtitleslangs': [lang],
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Get video info including available subtitles
                info = ydl.extract_info(video_url, download=False)
                
                # Get available subtitles
                available_subs = []
                if 'subtitles' in info:
                    available_subs.extend(list(info['subtitles'].keys()))
                if 'automatic_captions' in info:
                    available_subs.extend(list(info['automatic_captions'].keys()))
                
                # Download the subtitles
                ydl.download([video_url])
                
                # Read the downloaded subtitle file
                subtitle_file = os.path.join(temp_dir, f'subtitle.{lang}.srt')
                if os.path.exists(subtitle_file):
                    with open(subtitle_file, 'r', encoding='utf-8') as f:
                        transcript_text = f.read()
                        
                    # Parse the SRT content into JSON
                    parsed_transcript = parse_srt_to_json(transcript_text)
                    
                    return {
                        'success': True,
                        'video_title': info.get('title', ''),
                        'video_id': info.get('id', ''),
                        'video_duration': info.get('duration', 0),
                        'transcript': {
                            'raw': transcript_text,
                            'parsed': parsed_transcript
                        },
                        'language': lang,
                        'available_languages': available_subs,
                        'metadata': {
                            'uploader': info.get('uploader', ''),
                            'upload_date': info.get('upload_date', ''),
                            'view_count': info.get('view_count', 0),
                            'like_count': info.get('like_count', 0),
                            'description': info.get('description', '')
                        }
                    }
                else:
                    return {
                        'error': f'No transcript available in language: {lang}',
                        'available_languages': available_subs
                    }
                
        except Exception as e:
            return {'error': str(e)} 