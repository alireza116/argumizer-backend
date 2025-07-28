#!/bin/bash

# Curl command to analyze the video with proper participant identification
VIDEO_URL="https://www.youtube.com/watch?v=n2UXp2CqpG4"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
VIDEO_ID=$(echo $VIDEO_URL | sed 's/.*v=//')

echo "🎬 Analyzing video: $VIDEO_URL"
echo "📥 Getting transcript..."

# Get transcript and save
curl "http://localhost:5001/transcript/parsed?url=$VIDEO_URL&lang=en" > "requests/raw_transcript_${VIDEO_ID}_${TIMESTAMP}.json"

if [ $? -eq 0 ]; then
    echo "✅ Transcript saved"
    
    # Analyze with Vertex AI
    echo "🧠 Analyzing with Vertex AI (Gemini 2.5 Pro)..."
    python3 -c "
import json
import sys
from transcript_analyzer import DebateTranscriptAnalyzer

try:
    # Load raw transcript
    with open('requests/raw_transcript_${VIDEO_ID}_${TIMESTAMP}.json', 'r') as f:
        transcript_data = json.load(f)
    
    print('🤖 Initializing Vertex AI analyzer...')
    analyzer = DebateTranscriptAnalyzer(
        project_id='skydenai',
        location='us-central1'
    )
    
    print('🔍 Analyzing transcript with Gemini 2.5 Pro...')
    analysis = analyzer.analyze_debate(transcript_data)
    
    # Create clean format with real participants
    clean_format = {
        'video_title': transcript_data.get('video_title', 'Unknown'),
        'participants': analysis.participants,
        'turns': []
    }
    
    for turn in analysis.turns:
        clean_turn = {
            'participant': turn.participant,
            'text': turn.combined_text,
            'start_time': turn.start_time,
            'end_time': turn.end_time
        }
        clean_format['turns'].append(clean_turn)
    
    # Save clean format
    with open('requests/clean_debate_${VIDEO_ID}_${TIMESTAMP}.json', 'w') as f:
        json.dump(clean_format, f, indent=2)
    
    print(f'✅ Analysis complete!')
    print(f'📊 Real Participants: {', '.join(clean_format[\"participants\"])}')
    print(f'🗣️  Total Turns: {len(clean_format[\"turns\"])}')
    print(f'📁 Saved to: requests/clean_debate_${VIDEO_ID}_${TIMESTAMP}.json')
    
except Exception as e:
    print(f'❌ Error: {e}')
    sys.exit(1)
"
    
    echo "🎉 Analysis complete!"
    echo "📁 Check requests/clean_debate_${VIDEO_ID}_${TIMESTAMP}.json"
else
    echo "❌ Failed to get transcript"
    exit 1
fi 