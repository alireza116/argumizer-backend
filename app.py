from flask import Flask, request, jsonify
from transcript_service import get_video_transcript

app = Flask(__name__)

@app.route('/transcript/raw', methods=['GET'])
def get_raw_transcript():
    """Get transcript in raw SRT format"""
    video_url = request.args.get('url')
    lang = request.args.get('lang', 'en')
    
    if not video_url:
        return jsonify({'error': 'Missing video URL parameter'}), 400
    
    result = get_video_transcript(video_url, lang)
    
    if 'error' in result:
        return jsonify(result), 400
    
    # Return only the raw transcript and basic metadata
    return jsonify({
        'success': True,
        'video_title': result['video_title'],
        'video_id': result['video_id'],
        'language': result['language'],
        'available_languages': result['available_languages'],
        'transcript': result['transcript']['raw']
    })

@app.route('/transcript/parsed', methods=['GET'])
def get_parsed_transcript():
    """Get transcript in parsed JSON format with timing information"""
    video_url = request.args.get('url')
    lang = request.args.get('lang', 'en')
    include_metadata = request.args.get('include_metadata', 'false').lower() == 'true'
    
    if not video_url:
        return jsonify({'error': 'Missing video URL parameter'}), 400
    
    result = get_video_transcript(video_url, lang)
    
    if 'error' in result:
        return jsonify(result), 400
    
    response = {
        'success': True,
        'video_title': result['video_title'],
        'video_id': result['video_id'],
        'video_duration': result['video_duration'],
        'language': result['language'],
        'available_languages': result['available_languages'],
        'transcript': result['transcript']['parsed']
    }
    
    # Include additional metadata if requested
    if include_metadata:
        response['metadata'] = result['metadata']
    
    return jsonify(response)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001) 