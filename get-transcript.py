import yt_dlp

def get_video_transcript(video_url):
    ydl_opts = {
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitlesformat': 'srt',
        'skip_download': True,  # Skip downloading the video file
        'quiet': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # Get video info including available subtitles
            info = ydl.extract_info(video_url, download=False)
            
            # Print available subtitles
            if 'subtitles' in info:
                print("Available subtitles:", list(info['subtitles'].keys()))
            if 'automatic_captions' in info:
                print("Available auto-generated captions:", list(info['automatic_captions'].keys()))
            
            # Download the subtitles
            ydl_opts['writesubtitles'] = True
            ydl.download([video_url])
            
            print(f"Successfully downloaded transcripts for video: {info.get('title', video_url)}")
            
        except Exception as e:
            print(f"Error downloading transcript: {str(e)}")

if __name__ == "__main__":
    videoLink = "https://www.youtube.com/watch?v=ukVFg1OlA0M"
    get_video_transcript(videoLink)

