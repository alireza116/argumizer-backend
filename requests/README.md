# Video Analysis Requests

This directory contains tools for analyzing YouTube videos and saving results.

## Files

- `analyze_video.py` - Python script for video analysis
- `curl_analyze.sh` - Shell script for quick curl-based analysis
- `clean_debate_*.json` - Analysis results in clean format
- `raw_transcript_*.json` - Raw transcript data

## Usage

### Method 1: Python Script
```bash
python requests/analyze_video.py
```

### Method 2: Curl Command
```bash
./requests/curl_analyze.sh
```

## Output Format

The analysis creates a clean JSON format with:

```json
{
  "video_title": "Video Title",
  "participants": ["Speaker 1", "Speaker 2", "Speaker 3"],
  "turns": [
    {
      "participant": "Speaker 1",
      "text": "What the speaker said...",
      "start_time": "00:00:00,000",
      "end_time": "00:00:30,000"
    }
  ]
}
```

## Current Video

Currently configured for: `https://www.youtube.com/watch?v=n2UXp2CqpG4`

To change the video, edit the `video_url` variable in either script. 