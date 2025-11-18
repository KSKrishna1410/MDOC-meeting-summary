"""
Document API routes
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Query
from typing import Optional
from src.backend.controllers import document_controller

router = APIRouter()


@router.post("/upload")
async def upload_meeting(
    file: UploadFile = File(...),
    client_name: str = Form(...),
    detection_mode: str = Form("basic"),
    use_speech: bool = Form(True),
    use_mouse_detection: bool = Form(True),
    use_scene_detection: bool = Form(False),
    use_ai_analysis: bool = Form(True)
):
    """
    Upload and process meeting recording
    
    - **file**: Video file (MP4, AVI, MOV, MKV)
    - **client_name**: Name of the client
    - **detection_mode**: Processing mode ("basic" or "advanced")
    - **use_speech**: Enable speech-based keyword detection
    - **use_mouse_detection**: Enable mouse cursor tracking
    - **use_scene_detection**: Enable scene change detection
    - **use_ai_analysis**: Enable AI-powered content analysis
    
    Returns:
    - **transcript**: Full transcript with timestamps (list of {timestamp, text})
    - **screenshots**: Screenshot metadata (list of {timestamp, reason})
    - **session_guid**: Use this for document generation
    - **video_path**: Use this for document generation
    - Processing statistics and video info
    """
    return await document_controller.process_meeting(
        file=file,
        client_name=client_name,
        detection_mode=detection_mode,
        use_speech=use_speech,
        use_mouse_detection=use_mouse_detection,
        use_scene_detection=use_scene_detection,
        use_ai_analysis=use_ai_analysis
    )


@router.post("/generate/meeting-summary")
async def generate_meeting_summary(
    doc_title: str = Form(...),
    session_guid: str = Form(...),
    doc_format: str = Form("PDF"),
    enable_missing_questions: bool = Form(True),
    enable_process_map: bool = Form(True),
    include_screenshots: bool = Form(True),
    video_path: Optional[str] = Form(None),
    client_name: Optional[str] = Form(None)
):
    """
    Generate Meeting Summary Document from processed video
    
    - **session_guid**: Session GUID from upload endpoint (REQUIRED)
    - **doc_title**: Title for the document
    - **doc_format**: Output format ("PDF", "DOCX", "Both")
    - **enable_missing_questions**: Include missing questions section
    - **enable_process_map**: Include process map diagram
    - **include_screenshots**: Include screenshots in document
    - **video_path**: Optional - only needed if session_guid not provided
    - **client_name**: Optional - only needed if session_guid not provided
    
    Returns:
    - **PDF format**: Returns PDF file directly (downloadable)
    - **DOCX format**: Returns DOCX file directly (downloadable)
    - **Both format**: Returns ZIP file containing both PDF and DOCX (downloadable)
    """
    return await document_controller.generate_meeting_document(
        doc_title=doc_title,
        doc_type="meeting_summary",
        doc_format=doc_format,
        enable_missing_questions=enable_missing_questions,
        enable_process_map=enable_process_map,
        include_screenshots=include_screenshots,
        session_guid=session_guid,
        video_path=video_path,
        client_name=client_name
    )


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "service": "MDoc API"}