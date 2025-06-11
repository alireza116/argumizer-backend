# YouTube Transcript API

A Flask-based API service that extracts transcripts from YouTube videos using yt-dlp.

## Features

- Extract transcripts from YouTube videos
- Support for multiple languages
- Raw SRT format and parsed JSON format with timing information
- Temporary file handling for clean operation
- RESTful API endpoints
- Health check endpoint

## Prerequisites

- Python 3.x
- Git

## Setup

1. Clone the repository:

```bash
git clone <your-repo-url>
cd <repository-name>
```

2. Create and activate a virtual environment:

On macOS/Linux:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

On Windows:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the Application

1. Make sure your virtual environment is activated (you should see `(venv)` in your terminal prompt)

2. Start the Flask server:

```bash
python app.py
```

The server will start on `http://localhost:5001`

## API Endpoints

### Get Raw Transcript (SRT Format)

- **URL**: `/transcript/raw`
- **Method**: `GET`
- **URL Params**:
  - `url` (required): YouTube video URL
  - `lang` (optional): Language code (default: 'en')
- **Success Response**:
  ```json
  {
    "success": true,
    "video_title": "Video Title",
    "video_id": "video_id",
    "language": "en",
    "available_languages": ["en", "es", "fr"],
    "transcript": "1\n00:00:00,000 --> 00:00:02,500\nSubtitle text\n\n2..."
  }
  ```

### Get Parsed Transcript (JSON Format)

- **URL**: `/transcript/parsed`
- **Method**: `GET`
- **URL Params**:
  - `url` (required): YouTube video URL
  - `lang` (optional): Language code (default: 'en')
  - `include_metadata` (optional): Include additional video metadata (default: false)
- **Success Response**:
  ```json
  {
    "success": true,
    "video_title": "Video Title",
    "video_id": "video_id",
    "video_duration": 1234,
    "language": "en",
    "available_languages": ["en", "es", "fr"],
    "transcript": [
      {
        "index": 1,
        "start_time": 0.0,
        "end_time": 2.5,
        "start_time_text": "00:00:00,000",
        "end_time_text": "00:00:02,500",
        "text": "Subtitle text"
      }
    ],
    "metadata": {
      // Only included if include_metadata=true
      "uploader": "Channel Name",
      "upload_date": "20240610",
      "view_count": 12345,
      "like_count": 1234,
      "description": "Video description"
    }
  }
  ```

### Health Check

- **URL**: `/health`
- **Method**: `GET`
- **Success Response**:
  ```json
  {
    "status": "healthy"
  }
  ```

## Error Response

All endpoints return the following format for errors:

```json
{
  "error": "Error message"
}
```

## Development

The project structure:

- `app.py`: Flask server and API endpoints
- `transcript_service.py`: Core functionality for transcript extraction
- `requirements.txt`: Project dependencies

## Git Workflow

When working with this repository:

1. The `venv` directory is already in `.gitignore` and won't be tracked by Git
2. After cloning, always create a new virtual environment as shown in the Setup section
3. If you add new dependencies:
   ```bash
   pip freeze > requirements.txt
   ```
   to update the requirements.txt file

## Troubleshooting

1. If port 5001 is in use, modify the port number in `app.py`
2. If you see ffmpeg warnings, consider installing ffmpeg for better performance
