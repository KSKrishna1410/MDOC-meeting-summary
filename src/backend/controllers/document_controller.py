"""
Document controller for handling meeting document processing
"""

import os
import uuid
import logging
import zipfile
import io
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Union
from datetime import datetime
from fastapi import UploadFile, HTTPException, Response

# Import business logic from main.py
import sys
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from main import (
    process_video,
    generate_document,
    get_video_duration_ffprobe
)
from src.utils.media_utils import get_video_info

logger = logging.getLogger(__name__)

# In-memory storage for processed data (screenshots, etc.)
# In production, consider using Redis or a database
_session_storage: Dict[str, Dict[str, Any]] = {}


async def save_uploaded_file(upload_file: UploadFile) -> str:
    """
    Save uploaded file to temporary directory
    
    Args:
        upload_file: FastAPI UploadFile object
        
    Returns:
        Path to saved file
    """
    # Create temp directory if it doesn't exist
    temp_dir = Path("data/temp")
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    file_ext = Path(upload_file.filename).suffix
    temp_filename = f"{uuid.uuid4()}{file_ext}"
    temp_path = temp_dir / temp_filename
    
    try:
        # Save file
        with open(temp_path, "wb") as f:
            content = await upload_file.read()
            f.write(content)
        
        logger.info(f"Saved uploaded file to {temp_path}")
        return str(temp_path)
    except Exception as e:
        logger.error(f"Error saving uploaded file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")


async def process_meeting(
    file: UploadFile,
    client_name: str,
    detection_mode: str = "basic",
    use_speech: bool = True,
    use_mouse_detection: bool = True,
    use_scene_detection: bool = False,
    use_ai_analysis: bool = True
) -> Dict[str, Any]:
    """
    Process uploaded meeting video file
    
    Args:
        file: Uploaded video file
        client_name: Name of the client
        detection_mode: "basic" or "advanced"
        use_speech: Enable speech-based keyword detection
        use_mouse_detection: Enable mouse cursor tracking
        use_scene_detection: Enable scene change detection
        use_ai_analysis: Enable AI-powered content analysis
        
    Returns:
        Dictionary containing processing results
    """
    # Validate file type
    allowed_extensions = {".mp4", ".avi", ".mov", ".mkv"}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Save uploaded file
    video_path = await save_uploaded_file(file)
    session_guid = str(uuid.uuid4())
    
    try:
        # Process video
        result = process_video(
            video_path=video_path,
            client_name=client_name,
            detection_mode=detection_mode,
            use_speech=use_speech,
            use_mouse_detection=use_mouse_detection,
            use_scene_detection=use_scene_detection,
            use_ai_analysis=use_ai_analysis,
            progress_callback=None,  # No progress callback for API
            session_guid=session_guid
        )
        
        # Get video info
        video_info = get_video_info(video_path)
        video_duration = get_video_duration_ffprobe(video_path)
        
        # Store screenshots and other data in session storage
        # Convert screenshots to serializable format (store metadata)
        screenshots_metadata = []
        for img, timestamp, reason in result["screenshots"]:
            screenshots_metadata.append({
                "timestamp": timestamp,
                "reason": reason
            })
        
        # Store full data in memory for later use
        _session_storage[session_guid] = {
            "screenshots": result["screenshots"],  # Full screenshot objects
            "speech_timestamps": result["speech_timestamps"],
            "keyword_results": result.get("keyword_results", []),
            "video_path": video_path,
            "client_name": client_name
        }
        
        # Convert transcript to list of dicts for JSON serialization
        transcript = []
        for timestamp, text in result["speech_timestamps"]:
            transcript.append({
                "timestamp": timestamp,
                "text": text
            })
        
        # Prepare response with full transcript (like Streamlit)
        response = {
            "success": True,
            "session_guid": result["session_guid"],
            "session_id": result["session_id"],
            "video_path": video_path,
            "video_info": {
                "filename": os.path.basename(video_path),
                "duration_minutes": video_duration,
                "fps": video_info["fps"],
                "frame_count": video_info["frame_count"],
                "width": video_info["width"],
                "height": video_info["height"]
            },
            "screenshots": screenshots_metadata,  # Metadata only
            "screenshots_count": len(result["screenshots"]),
            "transcript": transcript,  # Full transcript like Streamlit
            "speech_segments": transcript,  # Alias for compatibility
            "speech_segments_count": len(result["speech_timestamps"]),
            "keyword_results": result.get("keyword_results", []),
            "processing_time": result["processing_time"],
            "message": "Video processed successfully"
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing meeting: {e}", exc_info=True)
        # Clean up temp file on error
        try:
            if os.path.exists(video_path):
                os.remove(video_path)
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}")


async def generate_meeting_document(
    doc_title: str,
    doc_type: str = "meeting_summary",
    doc_format: str = "PDF",
    enable_missing_questions: bool = True,
    enable_process_map: bool = True,
    include_screenshots: bool = True,
    session_guid: Optional[str] = None,
    video_path: Optional[str] = None,
    client_name: Optional[str] = None
) -> Union[Response, Dict[str, Any]]:
    """
    Generate document from processed video
    
    Args:
        doc_title: Title for the document
        doc_type: Type of document
        doc_format: Output format ("PDF", "DOCX", "Both")
        enable_missing_questions: Include missing questions section
        enable_process_map: Include process map diagram
        include_screenshots: Include screenshots in document
        session_guid: Session GUID from upload endpoint (required if video_path/client_name not provided)
        video_path: Path to video file (optional if session_guid provided)
        client_name: Name of the client (optional if session_guid provided)
        
    Returns:
        Dictionary containing generated document info
    """
    try:
        # If session_guid is provided, retrieve all data from storage
        if session_guid:
            if session_guid not in _session_storage:
                raise HTTPException(
                    status_code=404,
                    detail=f"Session {session_guid} not found. Please upload and process video first."
                )
            
            stored_data = _session_storage[session_guid]
            video_path = stored_data.get("video_path")
            client_name = stored_data.get("client_name")
            screenshots = stored_data.get("screenshots")
            speech_segments = stored_data.get("speech_timestamps")
            
            if not video_path:
                raise HTTPException(
                    status_code=400,
                    detail="Session data incomplete. Missing video_path."
                )
            if not client_name:
                raise HTTPException(
                    status_code=400,
                    detail="Session data incomplete. Missing client_name."
                )
            
            logger.info(f"Retrieved all data from session storage for {session_guid}")
        else:
            # If no session_guid, video_path and client_name are required
            if not video_path or not client_name:
                raise HTTPException(
                    status_code=400,
                    detail="Either session_guid must be provided, or both video_path and client_name are required."
                )
            
            # Check if video file exists
            if not os.path.exists(video_path):
                raise HTTPException(status_code=404, detail="Video file not found")
            
            # If screenshots and speech_segments are not provided, process video first
            screenshots = None
            speech_segments = None
            if screenshots is None or speech_segments is None:
                logger.info("Processing video to get screenshots and transcript")
                session_guid = str(uuid.uuid4())
                # Process video to get screenshots and transcript
                process_result = process_video(
                    video_path=video_path,
                    client_name=client_name,
                    detection_mode="basic",
                    session_guid=session_guid
                )
                screenshots = process_result["screenshots"]
                speech_segments = process_result["speech_timestamps"]
        
        # Convert transcript from API format (list of dicts) to expected format (list of tuples)
        if speech_segments and isinstance(speech_segments, list) and len(speech_segments) > 0:
            if isinstance(speech_segments[0], dict):
                # Convert from API format: [{"timestamp": 1.0, "text": "..."}]
                # To expected format: [(1.0, "...")]
                speech_segments = [(seg["timestamp"], seg["text"]) for seg in speech_segments]
        
        # Generate document
        result = generate_document(
            video_path=video_path,
            screenshots=screenshots,
            client_name=client_name,
            doc_title=doc_title,
            doc_type=doc_type,
            doc_format=doc_format,
            speech_segments=speech_segments,
            enable_missing_questions=enable_missing_questions,
            enable_process_map=enable_process_map,
            include_screenshots=include_screenshots,
            session_guid=session_guid
        )
        
        # Return file(s) directly as downloadable
        doc_title_safe = result["title"].replace(" ", "_")
        today_date = datetime.now().strftime("%Y-%m-%d")
        
        # If format is "Both", return a zip file
        if result["format"] == "Both":
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                if result.get("pdf_bytes"):
                    zip_file.writestr(
                        f"{doc_title_safe}_{result['doc_type']}_{today_date}.pdf",
                        result["pdf_bytes"]
                    )
                if result.get("docx_bytes"):
                    zip_file.writestr(
                        f"{doc_title_safe}_{result['doc_type']}_{today_date}.docx",
                        result["docx_bytes"]
                    )
            zip_buffer.seek(0)
            
            return Response(
                content=zip_buffer.getvalue(),
                media_type="application/zip",
                headers={
                    "Content-Disposition": f'attachment; filename="{doc_title_safe}_{result["doc_type"]}_{today_date}.zip"'
                }
            )
        
        # If format is PDF only
        elif result["format"] == "PDF" and result.get("pdf_bytes"):
            return Response(
                content=result["pdf_bytes"],
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f'attachment; filename="{doc_title_safe}_{result["doc_type"]}_{today_date}.pdf"'
                }
            )
        
        # If format is DOCX only
        elif result["format"] in ["DOCX", "WORD"] and result.get("docx_bytes"):
            return Response(
                content=result["docx_bytes"],
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                headers={
                    "Content-Disposition": f'attachment; filename="{doc_title_safe}_{result["doc_type"]}_{today_date}.docx"'
                }
            )
        
        # Fallback: return JSON if no files generated
        else:
            return {
                "success": False,
                "message": "No document generated. Please check your parameters.",
                "has_pdf": result.get("pdf_bytes") is not None,
                "has_docx": result.get("docx_bytes") is not None
            }
        
    except Exception as e:
        logger.error(f"Error generating document: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating document: {str(e)}")

