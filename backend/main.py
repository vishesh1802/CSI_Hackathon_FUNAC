"""
FastAPI Backend for Industrial Robot Event Triage System
- ETL pipeline for processing uploaded data
- History lookup for similar events
- Triage scoring using Azure AI Foundry
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
from pathlib import Path
from dotenv import load_dotenv
import math

load_dotenv()

from services.etl_service import ETLService
from services.history_service import HistoryService
from services.triage_service import TriageService
from services.azure_ai_service import AzureAIService
from services.schema_service import SchemaService
from services.validation_service import ValidationService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Industrial Robot Event Triage API", version="1.0.0")

# CORS middleware for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
etl_service = ETLService()
history_service = HistoryService()
azure_ai_service = AzureAIService()
triage_service = TriageService(azure_ai_service)
schema_service = SchemaService()
validation_service = ValidationService()

# Data storage (in production, use a database)
events_store: List[Dict[str, Any]] = []


class EventRequest(BaseModel):
    event_id: str
    event_type: str
    timestamp: str
    description: str
    raw_data: Optional[Dict[str, Any]] = None


class TriageResponse(BaseModel):
    event_id: str
    triage_score: float
    priority: str
    recommendation: str
    similar_events: List[Dict[str, Any]]
    analysis: str
    maintenance_report: Optional[Dict[str, Any]] = None


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Industrial Robot Event Triage API"}


@app.post("/api/etl/process")
async def process_upload(
    file: UploadFile = File(...),
    file_type: str = "auto"
):
    """
    ETL Pipeline: Process uploaded data files
    Supports CSV, TXT files with sensor data, alerts, errors, etc.
    """
    try:
        logger.info(f"Processing uploaded file: {file.filename}, type: {file_type}")
        
        # Save uploaded file temporarily
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        file_path = upload_dir / file.filename
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process file based on type
        processed_data = await etl_service.process_file(file_path, file_type)
        
        # Normalize events to hackathon schema
        normalized_events = []
        for raw_event in processed_data.get("events", []):
            normalized = schema_service.normalize_event(raw_event)
            # Validate schema
            is_valid, errors = schema_service.validate_schema(normalized)
            if is_valid:
                normalized_events.append(normalized)
            else:
                logger.warning(f"Event validation failed: {errors}")
        
        # Deduplicate and calculate recurrence
        normalized_events = _deduplicate_events(normalized_events)
        
        # Store normalized events
        for event in normalized_events:
            events_store.append(event)
        
        # Calculate validation metrics
        validation_result = validation_service.validate_extraction(normalized_events)
        
        return JSONResponse(content={
            "status": "success",
            "filename": file.filename,
            "events_processed": len(normalized_events),
            "events": normalized_events[:10],  # Return first 10 for preview
            "metadata": processed_data.get("metadata", {}),
            "validation": validation_result
        })
    
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@app.get("/api/events")
async def get_events(
    limit: int = 100,
    event_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Get all processed events with optional filtering"""
    try:
        filtered_events = list(events_store)  # Create a copy to avoid modification
        
        if event_type:
            filtered_events = [e for e in filtered_events if e.get("event_type") == event_type]
        
        if start_date:
            filtered_events = [e for e in filtered_events if e.get("timestamp", "") >= start_date]
        
        if end_date:
            filtered_events = [e for e in filtered_events if e.get("timestamp", "") <= end_date]
        
        # Limit results and ensure JSON serializable
        limited_events = filtered_events[:limit]
        
        # Helper function to recursively clean values for JSON serialization
        def clean_for_json(obj):
            """Recursively clean object to ensure JSON serializability"""
            if isinstance(obj, float):
                # Handle NaN and Infinity values
                if math.isnan(obj) or math.isinf(obj):
                    return None
                return obj
            elif isinstance(obj, dict):
                return {k: clean_for_json(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [clean_for_json(item) for item in obj]
            elif isinstance(obj, (str, int, bool, type(None))):
                return obj
            elif hasattr(obj, '__dict__'):
                # Handle complex objects
                return str(obj)
            else:
                # Try to convert to string as last resort
                try:
                    # Check if it's a numpy/pandas NaN
                    if hasattr(obj, '__float__'):
                        try:
                            fval = float(obj)
                            if math.isnan(fval) or math.isinf(fval):
                                return None
                        except:
                            pass
                    return str(obj)
                except:
                    return None
        
        # Ensure all values are JSON serializable
        serializable_events = []
        for event in limited_events:
            try:
                # Clean the entire event recursively
                serializable_event = clean_for_json(event)
                serializable_events.append(serializable_event)
            except Exception as e:
                logger.warning(f"Error serializing event {event.get('event_id', 'unknown')}: {str(e)}")
                # Skip problematic events
                continue
        
        # Clean the entire response before returning
        response_data = {
            "total": len(filtered_events),
            "events": serializable_events
        }
        
        # Final cleanup pass to ensure everything is JSON serializable
        cleaned_response = clean_for_json(response_data)
        
        return JSONResponse(content=cleaned_response)
    except Exception as e:
        logger.error(f"Error in get_events: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error fetching events: {str(e)}")


@app.get("/api/events/{event_id}")
async def get_event(event_id: str):
    """Get a specific event by ID"""
    event = next((e for e in events_store if e.get("event_id") == event_id), None)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@app.post("/api/history/lookup")
async def lookup_history(event_request: EventRequest):
    """
    History Lookup: Find similar events from the past
    """
    try:
        logger.info(f"Looking up history for event: {event_request.event_id}")
        
        similar_events = await history_service.find_similar_events(
            event_request.dict(),
            events_store
        )
        
        return {
            "event_id": event_request.event_id,
            "similar_events_count": len(similar_events),
            "similar_events": similar_events
        }
    
    except Exception as e:
        logger.error(f"Error in history lookup: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in history lookup: {str(e)}")


@app.post("/api/triage/score")
async def score_triage(event_request: EventRequest):
    """
    Triage Scoring: Analyze event and provide priority score
    Uses Azure AI Foundry GPT model for intelligent analysis
    """
    try:
        logger.info(f"Scoring triage for event: {event_request.event_id}")
        
        # Find the full event from events_store (contains severity, recurrence_count, etc.)
        full_event = next(
            (e for e in events_store if e.get("event_id") == event_request.event_id),
            None
        )
        
        # If not found, use the request data (fallback)
        if not full_event:
            logger.warning(f"Event {event_request.event_id} not found in store, using request data")
            full_event = event_request.dict()
        else:
            logger.info(f"Found full event - severity: {full_event.get('severity')}, recurrence: {full_event.get('recurrence_count')}")
        
        # Find similar events for context
        similar_events = await history_service.find_similar_events(
            full_event,
            events_store
        )
        
        # Get triage score and analysis (use full event with all fields)
        triage_result = await triage_service.score_event(
            full_event,
            similar_events
        )
        
        return TriageResponse(
            event_id=event_request.event_id,
            triage_score=triage_result["score"],
            priority=triage_result["priority"],
            recommendation=triage_result["recommendation"],
            similar_events=similar_events[:5],  # Top 5 similar events
            analysis=triage_result["analysis"],
            maintenance_report=triage_result.get("maintenance_report")
        )
    
    except Exception as e:
        logger.error(f"Error in triage scoring: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in triage scoring: {str(e)}")


@app.post("/api/batch/process-all")
async def batch_process_all(request: Request):
    """
    Batch process all datasets: clean, normalize, and generate recommendations
    Processes all CSV and TXT files in Hackathon_Data directory
    
    Optional JSON body: {"skip_ai_recommendations": true} for fast mode
    """
    try:
        # Check if skip_ai_recommendations flag is set
        skip_ai = False
        try:
            body = await request.json()
            skip_ai = body.get("skip_ai_recommendations", False)
            logger.info(f"Received skip_ai_recommendations flag: {skip_ai}")
        except Exception as e:
            logger.info(f"No JSON body provided or error reading body: {e}")
            skip_ai = False
        
        from pathlib import Path
        
        # Get project root (backend/main.py is in backend/, so go up one level)
        project_root = Path(__file__).parent.parent
        data_dir = project_root / "Hackathon_Data"
        
        logger.info(f"Looking for files in: {data_dir.absolute()}")
        
        all_events = []
        files_processed = []
        
        # Get all data files
        csv_files = list(data_dir.glob("*.csv"))
        txt_files = list(data_dir.glob("*.txt"))
        all_files = sorted(csv_files + txt_files)
        
        logger.info(f"Found {len(all_files)} files: {[f.name for f in all_files]}")
        
        if not all_files:
            return JSONResponse(content={
                "status": "error",
                "message": f"No CSV or TXT files found in {data_dir.absolute()}",
                "files_processed": 0,
                "total_events": 0,
                "events_with_recommendations": 0,
                "files": []
            })
        
        # Process each file
        for file_path in all_files:
            logger.info(f"Processing file: {file_path.name} (exists: {file_path.exists()})")
            try:
                processed_data = await etl_service.process_file(file_path, "auto")
                raw_events = processed_data.get("events", [])
                logger.info(f"  Extracted {len(raw_events)} raw events from {file_path.name}")
                
                # Normalize events
                normalized_events = []
                for raw_event in raw_events:
                    normalized = schema_service.normalize_event(raw_event)
                    is_valid, errors = schema_service.validate_schema(normalized)
                    if is_valid:
                        normalized_events.append(normalized)
                    else:
                        logger.warning(f"  Validation failed for event: {errors}")
                
                logger.info(f"  Normalized {len(normalized_events)} valid events from {file_path.name}")
                all_events.extend(normalized_events)
                files_processed.append({
                    "filename": file_path.name,
                    "events_count": len(normalized_events),
                    "status": "success"
                })
                
            except Exception as e:
                logger.error(f"Error processing {file_path.name}: {str(e)}", exc_info=True)
                files_processed.append({
                    "filename": file_path.name,
                    "events_count": 0,
                    "status": "error",
                    "error": str(e)
                })
        
        # Deduplicate
        all_events = _deduplicate_events(all_events)
        
        # Store all events
        events_store.clear()  # Clear existing events
        events_store.extend(all_events)
        
        # Generate recommendations (or skip if fast mode)
        events_with_recommendations = []
        
        if skip_ai:
            logger.info("Fast mode: Skipping AI recommendations, using heuristic scoring only")
            # Apply heuristic scoring to all events (instant)
            for event in all_events:
                # Calculate score using multiple factors
                score = 30  # Base score
                severity = event.get("severity", "low")
                
                # Severity-based scoring
                if severity == "critical":
                    score = 90
                    priority = "CRITICAL"
                elif severity == "high":
                    score = 75
                    priority = "HIGH"
                elif severity == "med":
                    score = 50
                    priority = "MEDIUM"
                else:
                    # For "low" or missing severity, use enhanced heuristics
                    score = 30
                    priority = "LOW"
                    
                    # Boost score based on error codes
                    error_code = str(event.get("error_code", "")).upper()
                    if "SRVO" in error_code:
                        if "COLLISION" in error_code or "324" in error_code:
                            score = 70  # Collision events are high priority
                            priority = "HIGH"
                        else:
                            score = 55  # Other SRVO errors are medium-high
                            priority = "MEDIUM"
                    elif "TEMP" in error_code:
                        score = 50
                        priority = "MEDIUM"
                    elif "MOTN" in error_code or "INTP" in error_code:
                        score = 45
                        priority = "MEDIUM"
                    
                    # Boost based on event type
                    event_type = event.get("event_type", "")
                    if event_type == "error_log":
                        score = max(score, 50)  # Error logs are at least medium
                        priority = "MEDIUM" if score >= 50 else priority
                    elif event_type == "system_alert":
                        alert_severity = str(event.get("raw_data", {}).get("severity", "")).upper()
                        if "ALERT" in alert_severity or "CRITICAL" in alert_severity:
                            score = 70
                            priority = "HIGH"
                        elif "WARN" in alert_severity:
                            score = 50
                            priority = "MEDIUM"
                    
                    # Boost based on collision type
                    collision_type = event.get("collision_type", "")
                    if collision_type == "hard_impact":
                        score = 80
                        priority = "HIGH"
                    elif collision_type == "emergency_stop":
                        score = 75
                        priority = "HIGH"
                    elif collision_type == "soft_collision":
                        score = 60
                        priority = "MEDIUM"
                    
                    # Boost based on force value if available
                    force_value = event.get("force_value")
                    if force_value is not None:
                        if force_value > 800:
                            score = 85
                            priority = "CRITICAL"
                        elif force_value > 600:
                            score = 70
                            priority = "HIGH"
                        elif force_value > 300:
                            score = 55
                            priority = "MEDIUM"
                    
                    # Boost based on recurrence (chronic issues)
                    recurrence = event.get("recurrence_count", 0)
                    if recurrence > 10:
                        score = min(score + 20, 100)
                        if priority == "LOW":
                            priority = "MEDIUM"
                    elif recurrence > 5:
                        score = min(score + 15, 100)
                    elif recurrence > 1:
                        score = min(score + 10, 100)
                
                event["triage_score"] = min(max(score, 0), 100)  # Clamp to 0-100
                event["priority"] = priority
                event["recommended_action"] = "Review event details and follow standard maintenance procedures. Use 'Score Triage' for AI-powered recommendations."
        else:
            # Generate recommendations for a smaller sample to avoid timeout
            # Process only high-priority events (critical/high severity) or first 10 events
            # Prioritize events: critical/high severity first, then sample others
            high_priority_events = [e for e in all_events if e.get("severity") in ["critical", "high"]]
            other_events = [e for e in all_events if e.get("severity") not in ["critical", "high"]]
            
            # Process up to 10 high-priority events + 5 others = max 15 events
            events_to_process = (high_priority_events[:10] + other_events[:5])[:15]
            
            logger.info(f"Generating AI recommendations for {len(events_to_process)} priority events (out of {len(all_events)} total)")
            
            for idx, event in enumerate(events_to_process, 1):
                try:
                    logger.info(f"Processing recommendation {idx}/{len(events_to_process)} for event {event.get('event_id', 'unknown')}")
                    
                    similar_events = await history_service.find_similar_events(
                        event,
                        all_events
                    )
                    
                    triage_result = await triage_service.score_event(
                        event,
                        similar_events
                    )
                    
                    event["triage_score"] = triage_result.get("score", 0)
                    event["priority"] = triage_result.get("priority", "MEDIUM")
                    event["recommended_action"] = triage_result.get("recommendation", "")
                    event["maintenance_report"] = triage_result.get("maintenance_report", {})
                    
                    events_with_recommendations.append(event)
                except Exception as e:
                    logger.error(f"Error generating recommendation: {str(e)}")
                    # Still add event without recommendation
                    events_with_recommendations.append(event)
            
            # For remaining events, add basic priority/score without AI (faster)
            for event in all_events:
                if event not in events_to_process:
                    # Use heuristic scoring for faster processing
                    severity = event.get("severity", "low")
                    if severity == "critical":
                        event["triage_score"] = 90
                        event["priority"] = "CRITICAL"
                    elif severity == "high":
                        event["triage_score"] = 75
                        event["priority"] = "HIGH"
                    elif severity == "med":
                        event["triage_score"] = 50
                        event["priority"] = "MEDIUM"
                    else:
                        event["triage_score"] = 30
                        event["priority"] = "LOW"
                    event["recommended_action"] = "Review event details and follow standard maintenance procedures"
        
        return JSONResponse(content={
            "status": "success",
            "files_processed": len(files_processed),
            "total_events": len(all_events),
            "events_with_recommendations": len(events_with_recommendations),
            "files": files_processed,
            "message": f"Processed {len(all_events)} events from {len(files_processed)} files. Generated recommendations for {len(events_with_recommendations)} events."
        })
    
    except Exception as e:
        logger.error(f"Error in batch processing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in batch processing: {str(e)}")


@app.get("/api/stats")
async def get_stats():
    """Get statistics about processed events"""
    if not events_store:
        return {
            "total_events": 0,
            "by_type": {},
            "by_priority": {},
            "by_severity": {}
        }
    
    by_type = {}
    by_priority = {}
    by_severity = {}
    
    for event in events_store:
        event_type = event.get("event_type", "unknown")
        by_type[event_type] = by_type.get(event_type, 0) + 1
        
        priority = event.get("priority", "unknown")
        by_priority[priority] = by_priority.get(priority, 0) + 1
        
        severity = event.get("severity", "unknown")
        by_severity[severity] = by_severity.get(severity, 0) + 1
    
    # Get validation stats
    validation_result = validation_service.validate_extraction(events_store)
    dedup_stats = validation_service.calculate_deduplication_stats(events_store)
    
    # Add cache statistics
    try:
        if hasattr(azure_ai_service, 'get_cache_stats'):
            cache_stats = azure_ai_service.get_cache_stats()
            stats["cache"] = cache_stats
    except Exception:
        pass  # Cache stats optional
    
    return {
        "total_events": len(events_store),
        "by_type": by_type,
        "by_priority": by_priority,
        "by_severity": by_severity,
        "validation": validation_result,
        "deduplication": dedup_stats
    }


@app.get("/api/validation")
async def get_validation():
    """Get validation metrics for all processed events"""
    validation_result = validation_service.validate_extraction(events_store)
    dedup_stats = validation_service.calculate_deduplication_stats(events_store)
    
    return {
        "validation": validation_result,
        "deduplication": dedup_stats,
        "meets_target": validation_result.get("overall_score", 0) >= 75.0
    }


def _deduplicate_events(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Deduplicate events and calculate recurrence counts
    Groups by joint and date (24hr window)
    """
    from collections import defaultdict
    from datetime import datetime, timedelta
    
    # Group events by joint and date
    event_groups = defaultdict(list)
    
    for event in events:
        joint = event.get("joint", "UNKNOWN")
        timestamp = event.get("timestamp", "")
        
        try:
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            date_key = dt.date().isoformat()
        except:
            date_key = "unknown"
        
        key = f"{joint}_{date_key}"
        event_groups[key].append(event)
    
    # Calculate recurrence and keep unique events
    deduplicated = []
    for key, group in event_groups.items():
        if len(group) > 1:
            # Multiple occurrences - mark recurrence
            for event in group:
                event["recurrence_count"] = len(group)
                deduplicated.append(event)
        else:
            # Single occurrence
            group[0]["recurrence_count"] = 1
            deduplicated.append(group[0])
    
    return deduplicated


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

