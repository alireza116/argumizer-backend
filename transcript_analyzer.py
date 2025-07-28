import json
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel
import vertexai

@dataclass
class TranscriptSegment:
    index: int
    start_time: str
    text: str

@dataclass
class Turn:
    turn_id: int
    participant: str
    segments: List[TranscriptSegment]
    start_time: str
    end_time: str
    combined_text: str

@dataclass
class DebateAnalysis:
    participants: List[str]
    turns: List[Turn]
    metadata: Dict[str, Any]

class DebateTranscriptAnalyzer:
    def __init__(self, project_id: str, location: str = "us-central1"):
        """Initialize the analyzer with Vertex AI credentials."""
        self.project_id = project_id
        self.location = location
        vertexai.init(project=project_id, location=location)
        self.model = GenerativeModel("gemini-2.5-pro")
    
    def extract_participants(self, transcript_data: Dict) -> List[str]:
        """Step 1: Extract all participants from the transcript."""
        
        # Combine all transcript text for analysis
        full_text = " ".join([segment["text"] for segment in transcript_data["transcript"]])
        
        prompt = f"""
        Analyze this debate transcript and identify all the participants/speakers.
        Look for:
        1. Direct mentions of names in introductions
        2. References to speakers (e.g., "Scott says", "Mark argues")
        3. Context clues about who is speaking
        4. Host introductions or descriptions
        
        Transcript text: {full_text}
        
        Return ONLY a JSON list of participant names, like: ["Name1", "Name2", "Host Name"]
        Be specific with full names when available.
        """
        
        response = self.model.generate_content(prompt)
        
        try:
            # Clean the response to extract JSON
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
                
            participants = json.loads(response_text)
            return participants
        except json.JSONDecodeError:
            # Fallback parsing
            return self._fallback_participant_extraction(response.text)
    
    def _fallback_participant_extraction(self, response_text: str) -> List[str]:
        """Fallback method to extract participants from response text."""
        # Look for names in quotes or lists
        names = re.findall(r'"([^"]*)"', response_text)
        return [name for name in names if len(name.split()) <= 3 and name.replace(' ', '').isalpha()]
    
    def identify_turns(self, transcript_data: Dict, participants: List[str]) -> List[Dict]:
        """Step 2 & 3: Group segments into turns and identify speakers."""
        
        segments = transcript_data["transcript"]
        
        # Create chunks of transcript for analysis (to handle API limits)
        chunk_size = 50  # segments per chunk
        turns = []
        
        for i in range(0, len(segments), chunk_size):
            chunk = segments[i:i + chunk_size]
            chunk_turns = self._analyze_chunk_for_turns(chunk, participants)
            turns.extend(chunk_turns)
        
        # Merge consecutive turns from the same speaker
        merged_turns = self._merge_consecutive_turns(turns)
        
        return merged_turns
    
    def _analyze_chunk_for_turns(self, segments: List[Dict], participants: List[str]) -> List[Dict]:
        """Analyze a chunk of segments to identify turns and speakers."""
        
        segments_text = "\n".join([
            f"[{seg['index']}] {seg['start_time_text']}: {seg['text']}" 
            for seg in segments
        ])
        
        participants_str = ", ".join(participants)
        
        prompt = f"""
        Analyze this transcript chunk and identify speaking turns. A turn is a continuous segment where one person speaks.
        
        Participants: {participants_str}
        
        Transcript segments:
        {segments_text}
        
        For each turn, identify:
        1. Which participant is speaking
        2. The segment indices that belong to this turn
        3. Use context, speaking patterns, and content to determine the speaker
        
        Return a JSON array where each turn has:
        {{
            "participant": "Speaker Name",
            "segment_indices": [1, 2, 3],
            "reasoning": "Brief explanation of why you think this speaker is talking"
        }}
        
        Guidelines:
        - Look for topic continuity, argument style, and contextual clues
        - When speakers change, start a new turn
        - If uncertain about a speaker, use "Unknown" but provide reasoning
        """
        
        response = self.model.generate_content(prompt)
        
        try:
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
                
            turns_data = json.loads(response_text)
            return turns_data
        except json.JSONDecodeError:
            # Fallback: create single turn for the chunk
            return [{
                "participant": "Unknown",
                "segment_indices": [seg["index"] for seg in segments],
                "reasoning": "Failed to parse AI response"
            }]
    
    def _merge_consecutive_turns(self, turns: List[Dict]) -> List[Dict]:
        """Merge consecutive turns from the same speaker."""
        if not turns:
            return []
        
        merged = []
        current_turn = turns[0].copy()
        
        for next_turn in turns[1:]:
            if (next_turn["participant"] == current_turn["participant"] and
                next_turn["participant"] != "Unknown"):
                # Merge turns
                current_turn["segment_indices"].extend(next_turn["segment_indices"])
                current_turn["reasoning"] += f" | {next_turn['reasoning']}"
            else:
                merged.append(current_turn)
                current_turn = next_turn.copy()
        
        merged.append(current_turn)
        return merged
    
    def create_final_structure(self, transcript_data: Dict, participants: List[str], 
                             turn_data: List[Dict]) -> DebateAnalysis:
        """Step 4: Create the final structured output."""
        
        segments_dict = {seg["index"]: seg for seg in transcript_data["transcript"]}
        
        turns = []
        for i, turn_info in enumerate(turn_data):
            # Get segments for this turn
            turn_segments = []
            for idx in sorted(turn_info["segment_indices"]):
                if idx in segments_dict:
                    seg_data = segments_dict[idx]
                    turn_segments.append(TranscriptSegment(
                        index=seg_data["index"],
                        start_time=seg_data["start_time_text"],
                        text=seg_data["text"]
                    ))
            
            if turn_segments:
                # Combine text
                combined_text = " ".join([seg.text for seg in turn_segments])
                
                turn = Turn(
                    turn_id=i + 1,
                    participant=turn_info["participant"],
                    segments=turn_segments,
                    start_time=turn_segments[0].start_time,
                    end_time=turn_segments[-1].start_time,
                    combined_text=combined_text
                )
                turns.append(turn)
        
        return DebateAnalysis(
            participants=participants,
            turns=turns,
            metadata={
                "video_title": transcript_data.get("video_title", ""),
                "total_segments": len(transcript_data["transcript"]),
                "total_turns": len(turns),
                "success": transcript_data.get("success", False),
                "analysis_version": "1.0"
            }
        )
    
    def analyze_debate(self, transcript_data: Dict) -> DebateAnalysis:
        """Main method to analyze the entire debate transcript."""
        
        print("Step 1: Extracting participants...")
        participants = self.extract_participants(transcript_data)
        print(f"Found participants: {participants}")
        
        print("Step 2 & 3: Identifying turns and speakers...")
        turn_data = self.identify_turns(transcript_data, participants)
        print(f"Identified {len(turn_data)} turns")
        
        print("Step 4: Creating final structure...")
        analysis = self.create_final_structure(transcript_data, participants, turn_data)
        
        return analysis
    
    def to_dict(self, analysis: DebateAnalysis) -> Dict[str, Any]:
        """Convert analysis to dictionary for programmatic use."""
        return {
            "participants": analysis.participants,
            "turns": [
                {
                    "turn_id": turn.turn_id,
                    "participant": turn.participant,
                    "start_time": turn.start_time,
                    "end_time": turn.end_time,
                    "combined_text": turn.combined_text,
                    "segments": [
                        {
                            "index": seg.index,
                            "start_time": seg.start_time,
                            "text": seg.text
                        } for seg in turn.segments
                    ]
                } for turn in analysis.turns
            ],
            "metadata": analysis.metadata
        }

# Usage example
def main():
    # Initialize analyzer (replace with your project ID)
    analyzer = DebateTranscriptAnalyzer(project_id="skydenai")
    
    # Load your transcript data
    transcript_data = {
        "success": True,
        "transcript": [
            # Your transcript segments here
        ],
        "video_title": "Your Video Title"
    }
    
    # Analyze the debate
    analysis = analyzer.analyze_debate(transcript_data)
    
    # Convert to dictionary for programmatic use
    result_dict = analyzer.to_dict(analysis)
    
    # Save results
    with open("debate_analysis.json", "w") as f:
        json.dump(result_dict, f, indent=2)
    
    print("Analysis complete!")
    print(f"Participants: {analysis.participants}")
    print(f"Total turns: {len(analysis.turns)}")
    
    # Example: Access specific turn
    if analysis.turns:
        first_turn = analysis.turns[0]
        print(f"\nFirst turn by {first_turn.participant}:")
        print(f"Text: {first_turn.combined_text[:200]}...")

if __name__ == "__main__":
    main()