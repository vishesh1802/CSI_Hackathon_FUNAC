"""
Batch Process All Datasets
Processes all datasets, cleans them, and generates AI recommendations
"""

import asyncio
import sys
from pathlib import Path
import pandas as pd
from typing import List, Dict, Any
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.etl_service import ETLService
from backend.services.schema_service import SchemaService
from backend.services.validation_service import ValidationService
from backend.services.azure_ai_service import AzureAIService
from backend.services.triage_service import TriageService
from backend.services.history_service import HistoryService

# Directories
DATA_DIR = Path("Hackathon_Data")
CLEANED_DIR = Path("Hackathon_Data_Cleaned")
OUTPUT_DIR = Path("batch_processing_results")
OUTPUT_DIR.mkdir(exist_ok=True)

def get_all_data_files() -> List[Path]:
    """Get all CSV and TXT files from data directory"""
    files = []
    
    # Get CSV files
    csv_files = list(DATA_DIR.glob("*.csv"))
    files.extend(csv_files)
    
    # Get TXT files
    txt_files = list(DATA_DIR.glob("*.txt"))
    files.extend(txt_files)
    
    return sorted(files)

async def process_all_datasets():
    """Process all datasets, clean, and generate recommendations"""
    print("=" * 80)
    print("🚀 BATCH PROCESSING ALL DATASETS")
    print("=" * 80)
    print()
    
    # Initialize services
    etl_service = ETLService()
    schema_service = SchemaService()
    validation_service = ValidationService()
    azure_ai_service = AzureAIService()
    triage_service = TriageService(azure_ai_service)
    history_service = HistoryService()
    
    # Get all data files
    data_files = get_all_data_files()
    print(f"📁 Found {len(data_files)} data files to process")
    print()
    
    all_events = []
    processing_summary = {
        "files_processed": [],
        "total_events": 0,
        "events_with_recommendations": 0,
        "errors": []
    }
    
    # Process each file
    for file_path in data_files:
        print(f"📄 Processing: {file_path.name}")
        try:
            # Process file
            processed_data = await etl_service.process_file(file_path, "auto")
            raw_events = processed_data.get("events", [])
            
            # Normalize events
            normalized_events = []
            for raw_event in raw_events:
                normalized = schema_service.normalize_event(raw_event)
                is_valid, errors = schema_service.validate_schema(normalized)
                if is_valid:
                    normalized_events.append(normalized)
                else:
                    print(f"  ⚠️  Validation failed: {errors}")
            
            print(f"  ✅ Extracted {len(normalized_events)} valid events")
            all_events.extend(normalized_events)
            processing_summary["files_processed"].append({
                "filename": file_path.name,
                "events_count": len(normalized_events),
                "status": "success"
            })
            
        except Exception as e:
            print(f"  ❌ Error processing {file_path.name}: {str(e)}")
            processing_summary["errors"].append({
                "filename": file_path.name,
                "error": str(e)
            })
            processing_summary["files_processed"].append({
                "filename": file_path.name,
                "events_count": 0,
                "status": "error"
            })
    
    processing_summary["total_events"] = len(all_events)
    print()
    print(f"📊 Total events extracted: {len(all_events)}")
    print()
    
    # Deduplicate events
    print("🔄 Deduplicating events...")
    from backend.main import _deduplicate_events
    all_events = _deduplicate_events(all_events)
    print(f"  ✅ {len(all_events)} unique events after deduplication")
    print()
    
    # Generate recommendations for all events
    print("🤖 Generating AI recommendations...")
    print("  (This may take several minutes for all events)")
    print()
    
    events_with_recommendations = []
    
    for idx, event in enumerate(all_events, 1):
        if idx % 10 == 0:
            print(f"  Processing event {idx}/{len(all_events)}...")
        
        try:
            # Find similar events for context
            similar_events = await history_service.find_similar_events(
                event,
                all_events
            )
            
            # Get triage score and recommendations
            triage_result = await triage_service.score_event(
                event,
                similar_events
            )
            
            # Add recommendations to event
            event["triage_score"] = triage_result.get("score", 0)
            event["priority"] = triage_result.get("priority", "MEDIUM")
            event["recommended_action"] = triage_result.get("recommendation", "")
            event["maintenance_report"] = triage_result.get("maintenance_report", {})
            event["ai_analysis"] = triage_result.get("analysis", "")
            event["similar_events_count"] = len(similar_events)
            
            events_with_recommendations.append(event)
            processing_summary["events_with_recommendations"] += 1
            
        except Exception as e:
            print(f"  ⚠️  Error generating recommendation for event {idx}: {str(e)}")
            # Keep event without recommendation
            events_with_recommendations.append(event)
    
    print()
    print(f"✅ Generated recommendations for {processing_summary['events_with_recommendations']} events")
    print()
    
    # Save results
    print("💾 Saving results...")
    
    # Save all events with recommendations as JSON
    output_file = OUTPUT_DIR / f"all_events_with_recommendations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(events_with_recommendations, f, indent=2, default=str)
    print(f"  ✅ Saved to: {output_file}")
    
    # Save summary report
    summary_file = OUTPUT_DIR / f"processing_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    processing_summary["timestamp"] = datetime.now().isoformat()
    processing_summary["total_unique_events"] = len(events_with_recommendations)
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(processing_summary, f, indent=2, default=str)
    print(f"  ✅ Summary saved to: {summary_file}")
    
    # Create CSV export for easy viewing
    csv_file = OUTPUT_DIR / f"events_recommendations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    # Flatten events for CSV
    csv_data = []
    for event in events_with_recommendations:
        row = {
            "record_id": event.get("record_id"),
            "event_id": event.get("event_id"),
            "event_type": event.get("event_type"),
            "timestamp": event.get("timestamp"),
            "joint": event.get("joint"),
            "severity": event.get("severity"),
            "triage_score": event.get("triage_score"),
            "priority": event.get("priority"),
            "description": event.get("description"),
            "recommended_action": event.get("recommended_action", "")[:200],  # Truncate for CSV
            "similar_events_count": event.get("similar_events_count", 0),
            "recurrence_count": event.get("recurrence_count", 0)
        }
        
        # Add maintenance report sections
        maintenance_report = event.get("maintenance_report", {})
        if isinstance(maintenance_report, dict):
            row["diagnose_cause"] = maintenance_report.get("diagnose_cause", "")[:200]
            row["inspection_procedure"] = maintenance_report.get("inspection_procedure", "")[:200]
            row["maintenance_actions"] = maintenance_report.get("maintenance_actions", "")[:200]
            row["safety_clearance"] = maintenance_report.get("safety_clearance", "")[:200]
            row["return_to_service"] = maintenance_report.get("return_to_service", "")[:200]
        
        csv_data.append(row)
    
    df = pd.DataFrame(csv_data)
    df.to_csv(csv_file, index=False)
    print(f"  ✅ CSV export saved to: {csv_file}")
    print()
    
    # Print summary
    print("=" * 80)
    print("📊 PROCESSING SUMMARY")
    print("=" * 80)
    print(f"Files processed: {len(processing_summary['files_processed'])}")
    print(f"Total events extracted: {processing_summary['total_events']}")
    print(f"Unique events: {len(events_with_recommendations)}")
    print(f"Events with recommendations: {processing_summary['events_with_recommendations']}")
    print(f"Errors: {len(processing_summary['errors'])}")
    print()
    print(f"📁 Results saved in: {OUTPUT_DIR}")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(process_all_datasets())

