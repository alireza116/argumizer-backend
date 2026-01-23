# YouTube Debate Transcript Analysis - Output Structure

## Overview
The analyzer processes YouTube debate transcripts and produces a structured output that can be used programmatically. Here's the complete structure:

## Final Output Structure

```json
{
  "participants": [
    "Scott Horton",
    "Mark Dubowitz", 
    "Lex Fridman"
  ],
  "turns": [
    {
      "turn_id": 1,
      "participant": "Mark Dubowitz",
      "start_time": "00:00:00,000",
      "end_time": "00:00:09,120",
      "combined_text": "If we want to avoid wars, we have to have serious deterrence because our enemies need to understand we will use selective, focused, overwhelming military power when we are facing threats like an Iranian nuclear weapon.",
      "segments": [
        {
          "index": 1,
          "start_time": "00:00:00,000",
          "text": "If we want to avoid wars, we have to"
        },
        {
          "index": 2,
          "start_time": "00:00:01,520", 
          "text": "have serious deterrence because our"
        }
        // ... more segments
      ]
    }
    // ... more turns
  ],
  "metadata": {
    "video_title": "Iran War Debate: Nuclear Weapons, Trump, Peace, Power & the Middle East | Lex Fridman Podcast #473",
    "total_segments": 218,
    "total_turns": 45,
    "success": true,
    "analysis_version": "1.0"
  }
}
```

## Data Types and Fields

### Participants Array
- **Type**: `List[string]`
- **Description**: All identified speakers in the debate
- **Example**: `["Scott Horton", "Mark Dubowitz", "Lex Fridman"]`

### Turns Array
Each turn represents a continuous speaking segment by one participant.

#### Turn Object Fields:
- **turn_id**: `integer` - Sequential turn identifier
- **participant**: `string` - Name of the speaker
- **start_time**: `string` - Timestamp when turn begins (format: "HH:MM:SS,mmm")
- **end_time**: `string` - Timestamp when turn ends
- **combined_text**: `string` - All text from this turn concatenated
- **segments**: `List[Segment]` - Individual transcript segments that make up this turn

#### Segment Object Fields:
- **index**: `integer` - Original segment index from input
- **start_time**: `string` - Segment timestamp
- **text**: `string` - Segment text content

### Metadata Object
- **video_title**: `string` - Title of the YouTube video
- **total_segments**: `integer` - Total number of original transcript segments
- **total_turns**: `integer` - Total number of identified speaking turns
- **success**: `boolean` - Whether the original transcript processing was successful
- **analysis_version**: `string` - Version of the analysis algorithm used

## Programmatic Usage Examples

### 1. Get All Text by Specific Speaker
```python
def get_speaker_content(analysis_result, speaker_name):
    content = []
    for turn in analysis_result['turns']:
        if turn['participant'] == speaker_name:
            content.append(turn['combined_text'])
    return " ".join(content)

# Usage
scott_content = get_speaker_content(result, "Scott Horton")
```

### 2. Find Turns Containing Keywords
```python
def find_turns_with_keywords(analysis_result, keywords):
    matching_turns = []
    for turn in analysis_result['turns']:
        if any(keyword.lower() in turn['combined_text'].lower() for keyword in keywords):
            matching_turns.append(turn)
    return matching_turns

# Usage
nuclear_turns = find_turns_with_keywords(result, ["nuclear", "weapon"])
```

### 3. Get Speaking Statistics
```python
def get_speaking_stats(analysis_result):
    stats = {}
    for turn in analysis_result['turns']:
        participant = turn['participant']
        if participant not in stats:
            stats[participant] = {
                'turns': 0,
                'segments': 0,
                'total_chars': 0
            }
        stats[participant]['turns'] += 1
        stats[participant]['segments'] += len(turn['segments'])
        stats[participant]['total_chars'] += len(turn['combined_text'])
    return stats

# Usage
speaking_stats = get_speaking_stats(result)
```

### 4. Extract Time-Based Segments
```python
def get_turns_in_timerange(analysis_result, start_time, end_time):
    def time_to_seconds(time_str):
        h, m, s = time_str.split(':')
        s, ms = s.split(',')
        return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
    
    start_seconds = time_to_seconds(start_time)
    end_seconds = time_to_seconds(end_time)
    
    relevant_turns = []
    for turn in analysis_result['turns']:
        turn_start = time_to_seconds(turn['start_time'])
        if start_seconds <= turn_start <= end_seconds:
            relevant_turns.append(turn)
    
    return relevant_turns

# Usage
first_minute_turns = get_turns_in_timerange(result, "00:00:00,000", "00:01:00,000")
```

### 5. Export to Different Formats
```python
# Simple conversation format
def to_conversation_format(analysis_result):
    conversation = []
    for turn in analysis_result['turns']:
        conversation.append({
            'speaker': turn['participant'],
            'timestamp': turn['start_time'],
            'message': turn['combined_text']
        })
    return conversation

# Transcript format
def to_transcript_format(analysis_result):
    lines = []
    for turn in analysis_result['turns']:
        lines.append(f"[{turn['start_time']}] {turn['participant']}: {turn['combined_text']}")
    return "\n\n".join(lines)
```

## Setup Requirements

1. **Google Cloud Project**: Set up a GCP project with Vertex AI API enabled
2. **Authentication**: Set up service account credentials
3. **Dependencies**: Install required Python packages:
   ```bash
   pip install google-cloud-aiplatform vertexai
   ```

## Error Handling

The analyzer includes several fallback mechanisms:
- If participant extraction fails, it attempts regex-based fallback
- If turn identification fails for a chunk, it creates a single "Unknown" turn
- Individual segment errors don't stop the overall analysis
- All errors are logged and analysis continues where possible

## Performance Considerations

- Large transcripts are processed in chunks to respect API limits
- Consecutive turns by the same speaker are automatically merged
- The analysis caches intermediate results to avoid reprocessing
- Memory usage scales linearly with transcript length

## Customization Options

The analyzer can be customized for different types of content:
- Adjust chunk size for different API limits
- Modify participant detection prompts for different formats
- Add custom post-processing for specific use cases
- Extend the output structure with additional metadata