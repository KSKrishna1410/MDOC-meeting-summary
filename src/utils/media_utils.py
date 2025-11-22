import cv2
import datetime
import os
from .openai_config import get_chat_model_name, GEMINI_AVAILABLE
import litellm
from litellm import completion
import whisper
from .api_usage_logger import log_openai_usage, log_whisper_usage


def transcribe_with_whisper(audio_file_path):
    """
    Transcribe audio using local Whisper model first, then fallback to OpenAI's Whisper API.
    
    Args:
        audio_file_path (str): Path to the audio file to transcribe
        
    Returns:
        str: Transcribed text, or empty string if transcription failed
    """
    # First try: Use local Whisper model if available
    try:
        from ..processors.audio.whisper_processor import get_optimized_whisper_processor
        
        whisper_processor = get_optimized_whisper_processor()
        if whisper_processor and whisper_processor.model is not None:
            print("Using local Whisper model for transcription")
            result = whisper_processor.transcribe_audio(audio_file_path)
            text = result.get('text', '').strip()
            if text:
                return text
            else:
                print("Local Whisper returned empty text, falling back to API")
    except Exception as e:
        print(f"Local Whisper model not available or failed: {e}, falling back to API")
    
    # Note: OpenAI Whisper API fallback removed - using local Whisper only
    # If local Whisper fails, return empty string
    print("Local Whisper transcription failed, no API fallback available")
    return ""

def analyze_speech_transcript(transcript, prompt):
    """
    Analyze a speech transcript using Gemini via LiteLLM.
    
    Args:
        transcript (str): The transcribed text to analyze
        prompt (str): System prompt that tells the model what to do with the transcript
        
    Returns:
        dict: Analysis result as parsed from JSON response, or empty dict if failed
    """
    try:
        import json
        from typing import List, Dict, Any
        from .openai_config import get_chat_model_name, GEMINI_AVAILABLE
        
        if not GEMINI_AVAILABLE:
            print("Gemini API not configured. Cannot analyze speech transcript.")
            return {}
        
        model = get_chat_model_name()
        
        # Prepare messages for LiteLLM
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": transcript}
        ]
        
        print(f"Analyzing transcript with Gemini ({model})")
        
        try:
            # Use Gemini via LiteLLM
            # Note: Gemini may not support response_format, so we'll request JSON in the prompt
            response = completion(
                model=model,
                messages=messages,
                temperature=0.3
            )
            
            # Extract usage information correctly
            usage = response.usage
            if usage:
                log_openai_usage(
                    module_name=__name__,
                    model=model,
                    prompt_tokens=usage.prompt_tokens if hasattr(usage, 'prompt_tokens') else 0,
                    completion_tokens=usage.completion_tokens if hasattr(usage, 'completion_tokens') else 0,
                    function_name="analyze_speech_transcript"
                )
            
            # Parse and return the JSON response
            content = response.choices[0].message.content
            if content:
                # Try to extract JSON from response (Gemini may wrap it in markdown)
                content = content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()
                
                try:
                    return json.loads(content)
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON response: {e}")
                    print(f"Raw content: {content[:200]}...")
                    return {}
            
            return {}
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return {}
    except Exception as e:
        print(f"Error in analyze_speech_transcript: {e}")
        return {}

def _get_audio_duration(audio_file_path):
    """
    Get the duration of an audio file in seconds.
    
    Args:
        audio_file_path (str): Path to the audio file
        
    Returns:
        float: Duration in seconds
    """
    try:
        import librosa
        # Use librosa if available
        duration = librosa.get_duration(path=audio_file_path)
        return duration
    except ImportError:
        try:
            # Fallback to using OpenCV for video files with audio
            cap = cv2.VideoCapture(audio_file_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            duration = frame_count / fps if fps > 0 else 0
            cap.release()
            return duration
        except:
            # If we can't determine duration, estimate based on file size
            # This is a rough estimate: ~1MB per minute for typical audio
            file_size_mb = _get_file_size_mb(audio_file_path)
            return file_size_mb * 60  # Rough estimate

def _get_file_size_mb(file_path):
    """
    Get file size in megabytes.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        float: File size in MB
    """
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except:
        return 0.0

def get_video_info(video_path):
    """
    Extract information about a video file.
    
    Args:
        video_path (str): Path to the video file.
        
    Returns:
        dict: Dictionary containing video information.
    """
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_path}")
    
    info = {
        'fps': cap.get(cv2.CAP_PROP_FPS),
        'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
        'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
    }
    
    info['duration'] = info['frame_count'] / info['fps'] if info['fps'] > 0 else 0
    
    cap.release()
    return info

def format_timestamp(seconds, for_filename=False):
    """
    Format time in seconds to a readable string.
    
    Args:
        seconds (float): Time in seconds.
        for_filename (bool): If True, format for use in a filename.
        
    Returns:
        str: Formatted time string.
    """
    if for_filename:
        # Format for filenames: 00h00m00s
        hours, remainder = divmod(int(seconds), 3600)
        minutes, secs = divmod(remainder, 60)
        return f"{hours:02d}h{minutes:02d}m{secs:02d}s"
    else:
        # Format for display: 00:00:00
        time_obj = datetime.datetime.utcfromtimestamp(seconds)
        if seconds < 3600:  # Less than an hour
            return time_obj.strftime('%M:%S')
        else:
            return time_obj.strftime('%H:%M:%S')