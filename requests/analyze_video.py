#!/usr/bin/env python3
"""
Clean video analysis script with proper participant identification using Vertex AI.
"""

import json
import requests
import sys
import os
from datetime import datetime
import sys
sys.path.append('..')
from transcript_analyzer import DebateTranscriptAnalyzer

def get_transcript(video_url):
    """Get transcript from Flask API"""
    try:
        response = requests.get(
            'http://localhost:5001/transcript/parsed',
            params={'url': video_url, 'lang': 'en'},
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Flask server is not running. Please start it with 'python app.py'")
        return None
    except requests.exceptions.Timeout:
        print("❌ Error: Request timed out")
        return None

def analyze_with_vertex_ai(transcript_data):
    """Analyze transcript using Vertex AI to identify real participants"""
    print("🤖 Initializing Vertex AI analyzer...")
    
    try:
        analyzer = DebateTranscriptAnalyzer(
            project_id="argumizer",
            location="us-central1"
        )
        
        print("🔍 Analyzing transcript with Gemini 2.5 Pro...")
        print("   This will identify real participants and their speech...")
        
        # Run the full analysis
        analysis = analyzer.analyze_debate(transcript_data)
        
        # Convert to clean format
        clean_format = {
            "video_title": transcript_data.get('video_title', 'Unknown'),
            "participants": analysis.participants,
            "turns": []
        }
        
        for turn in analysis.turns:
            clean_turn = {
                'participant': turn.participant,
                'text': turn.combined_text,
                'start_time': turn.start_time,
                'end_time': turn.end_time
            }
            clean_format["turns"].append(clean_turn)
        
        return clean_format
        
    except Exception as e:
        print(f"❌ Error during Vertex AI analysis: {str(e)}")
        return None

def save_results(clean_format, video_url):
    """Save results with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    video_id = video_url.split('v=')[-1] if 'v=' in video_url else 'unknown'
    
    # Save clean format
    filename = f"clean_debate_{video_id}_{timestamp}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(clean_format, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Results saved to: {filename}")
    return filename

def main():
    """Main function"""
    video_url = "https://www.youtube.com/watch?v=n2UXp2CqpG4"
    
    print("🎬 YouTube Transcript Analysis with Real Participant Identification")
    print("=" * 60)
    print(f"📺 Video: {video_url}")
    
    # Get transcript
    print("📥 Getting transcript...")
    transcript_data = get_transcript(video_url)
    
    if not transcript_data:
        print("❌ Failed to get transcript")
        return 1
    
    print(f"✅ Got transcript: {transcript_data['video_title']}")
    print(f"📝 Segments: {len(transcript_data['transcript'])}")
    
    # Analyze with Vertex AI
    print("🧠 Analyzing with Vertex AI (Gemini 2.5 Pro)...")
    clean_format = analyze_with_vertex_ai(transcript_data)
    
    if not clean_format:
        print("❌ Failed to analyze transcript")
        return 1
    
    # Save results
    filename = save_results(clean_format, video_url)
    
    # Show summary
    print(f"\n📊 Analysis Summary:")
    print(f"   Video: {clean_format['video_title']}")
    print(f"   Real Participants: {', '.join(clean_format['participants'])}")
    print(f"   Total Turns: {len(clean_format['turns'])}")
    
    # Show sample
    if clean_format['turns']:
        print(f"\n📋 Sample Turns:")
        for i, turn in enumerate(clean_format['turns'][:3]):
            print(f"   Turn {i+1}: {turn['participant']}")
            print(f"   Time: {turn['start_time']} - {turn['end_time']}")
            print(f"   Text: {turn['text'][:100]}...")
            print()
    
    print(f"\n🎉 Analysis complete! Check {filename} for full results.")
    return 0

if __name__ == "__main__":
    exit(main()) 
