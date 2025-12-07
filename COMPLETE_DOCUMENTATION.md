# 📚 Complete Project Documentation
## Industrial Robot Event Triage System

**Version:** 1.0.0  
**Last Updated:** December 2025  
**Purpose:** Third-party diagnostic assistant for FANUC industrial robot maintenance teams

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Installation & Setup](#installation--setup)
4. [Data Flow & Processing](#data-flow--processing)
5. [Components Explained](#components-explained)
6. [API Documentation](#api-documentation)
7. [User Guide](#user-guide)
8. [Data Schema](#data-schema)
9. [Azure AI Integration](#azure-ai-integration)
10. [Troubleshooting](#troubleshooting)

---

## 1. Project Overview

### What is This System?

This is a **third-party diagnostic assistant** for industrial robot maintenance teams. It helps technicians:

- **Upload** robot data files (logs, sensor readings, alerts)
- **Analyze** collision events and performance metrics
- **Receive** AI-powered maintenance recommendations
- **Prioritize** events based on severity and risk

### Key Features

✅ **Data Structuring Pipeline** - Transforms unstructured robot data into clean, AI-consumable format  
✅ **AI Maintenance Agent** - Generates standardized 5-section maintenance procedures  
✅ **Event Triage System** - Scores and prioritizes events for maintenance teams  
✅ **History Lookup** - Finds similar historical events for context  
✅ **Batch Processing** - Process all datasets at once with cleaning and recommendations

### Technology Stack

- **Frontend:** Streamlit (Python web framework)
- **Backend:** FastAPI (Python async API framework)
- **AI:** Azure OpenAI (GPT-4o model)
- **Data Processing:** Pandas, NumPy
- **Storage:** In-memory (can be extended to database)

---

## 2. System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE                            │
│                  (Streamlit Frontend)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │  Upload  │  │   View   │  │  Triage  │                 │
│  │   Page   │  │  Events  │  │ Analysis │                 │
│  └──────────┘  └──────────┘  └──────────┘                 │
└───────────────────────┬─────────────────────────────────────┘
                          │ HTTP REST API
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  FASTAPI BACKEND                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ ETL Service  │  │Schema Service│  │Validation Svc│     │
│  │              │  │              │  │              │     │
│  │ - Extract    │  │ - Normalize  │  │ - Validate   │     │
│  │ - Transform  │  │ - Standardize│  │ - Deduplicate│     │
│  │ - Load       │  │ - Calculate  │  │ - Accuracy   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │History Service│  │Triage Service│  │Azure AI Svc │     │
│  │              │  │              │  │              │     │
│  │ - Find       │  │ - Score      │  │ - Analyze   │     │
│  │   Similar    │  │ - Prioritize │  │ - Generate   │     │
│  │ - Context    │  │ - Recommend  │  │   Reports   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└───────────────────────┬─────────────────────────────────────┘
                          │ API Calls
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              AZURE AI FOUNDRY                              │
│         (Azure OpenAI / GPT-4o)                            │
│  - Model Deployment: gpt-4o-2                              │
│  - Prompt Templates                                         │
│  - Token Usage Tracking                                     │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

#### Frontend (Streamlit)
- **File Upload:** Drag-and-drop or select files
- **Event Display:** Table view with filtering
- **Triage Analysis:** Select events and get recommendations
- **Visualization:** Show scores, priorities, and reports

#### Backend (FastAPI)
- **ETL Pipeline:** Process CSV/TXT files and extract events
- **Schema Normalization:** Standardize data to hackathon schema
- **Validation:** Ensure data quality and accuracy
- **History Lookup:** Find similar events using similarity matching
- **Triage Scoring:** Calculate priority and risk scores
- **AI Integration:** Call Azure OpenAI for intelligent analysis

#### Azure AI Service
- **Event Analysis:** Understand event context and severity
- **Recommendation Generation:** Create 5-section maintenance reports
- **Risk Assessment:** Calculate triage scores (0-100)

---

## 3. Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Azure OpenAI account (optional, system works with mock mode)

### Step 1: Install Dependencies

```bash
cd CSI_Hackathon
pip install -r requirements.txt
```

**Key Dependencies:**
- `fastapi` - Backend API framework
- `uvicorn` - ASGI server
- `streamlit` - Frontend UI framework
- `pandas` - Data processing
- `openai` - Azure OpenAI client
- `python-dotenv` - Environment variables
- `requests` - HTTP client

### Step 2: Configure Azure AI (Optional)

Create `.env` file in project root:

```bash
cp config.env.example .env
```

Edit `.env`:
```env
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.cognitiveservices.azure.com
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-2
AZURE_OPENAI_API_VERSION=2024-12-01-preview
```

**Note:** Without Azure AI credentials, the system uses mock analysis (still functional but less intelligent).

### Step 3: Verify Setup

```bash
# Test Azure connection (if configured)
python test_azure_connection.py

# Check if all files are in place
ls Hackathon_Data/
```

---

## 4. Data Flow & Processing

### Complete Data Flow

```
1. USER UPLOADS FILE
   └─> CSV or TXT file selected
   
2. FRONTEND SENDS TO BACKEND
   └─> POST /api/etl/process
   └─> File saved to uploads/ directory
   
3. ETL SERVICE PROCESSES FILE
   ├─> Detects file type (CSV/TXT)
   ├─> Extracts events based on type:
   │   ├─> CSV: sensor_readings, performance_metrics, generic
   │   └─> TXT: error_logs, system_alerts, maintenance_notes
   └─> Returns raw events
   
4. SCHEMA SERVICE NORMALIZES
   ├─> Normalizes timestamps to ISO 8601
   ├─> Extracts joint identifiers (J1-J6)
   ├─> Detects collision types
   ├─> Calculates severity (low/med/high/critical)
   ├─> Standardizes error codes
   └─> Generates record_id (UUID)
   
5. VALIDATION SERVICE VALIDATES
   ├─> Checks required fields
   ├─> Validates formats
   ├─> Calculates accuracy scores
   └─> Deduplicates events
   
6. EVENTS STORED IN MEMORY
   └─> events_store (List[Dict])
   
7. USER SELECTS EVENT FOR TRIAGE
   └─> POST /api/triage/score
   
8. TRIAGE SERVICE SCORES EVENT
   ├─> History Service finds similar events
   ├─> Azure AI analyzes event
   ├─> Generates 5-section maintenance report
   ├─> Calculates risk score (0-100)
   └─> Returns priority and recommendations
   
9. FRONTEND DISPLAYS RESULTS
   └─> Shows score, priority, maintenance report
```

### File Processing Details

#### CSV Files

**Sensor Readings** (`sensor_readings.csv`):
- Columns: Timestamp, Temperature_C, Vibration_g, Axis1_deg, Axis2_deg, Axis3_deg
- Extracted as: `sensor_reading` events
- Each row becomes an event

**Performance Metrics** (`performance_metrics.csv`):
- Columns: Timestamp, Metric1, Metric2, Metric3, Metric4
- Extracted as: `performance_metric` events
- Used for health monitoring

**Torque Events** (`torque_events_by_cycle.csv`):
- Contains torque data by cycle
- Extracted as: `generic` events (if not recognized)

#### TXT Files

**Error Logs** (`error_logs.txt`):
- Format: `[HH:MM:SS] SRVO-324 Collision detected`
- Extracted as: `error_log` events
- Parses FANUC error codes (SRVO, TEMP, MOTN, INTP, PROG)

**System Alerts** (`system_alerts.txt`):
- Format: `10:03:00 NOTICE: Vibration spike`
- Extracted as: `system_alert` events
- Includes severity levels (NOTICE, WARN, ALERT, CRITICAL)

**Maintenance Notes** (`maintenance_notes.txt`):
- Format: `2025-11-17 - Checked belts on axis 6.`
- Extracted as: `maintenance` events
- Tracks maintenance history

---

## 5. Components Explained

### 5.1 ETL Service (`backend/services/etl_service.py`)

**Purpose:** Extract, Transform, Load data from various file formats

**Key Methods:**
- `process_file()` - Main entry point for file processing
- `_process_csv()` - Handles CSV files
- `_process_txt()` - Handles TXT files
- `_extract_sensor_events()` - Extracts sensor readings
- `_extract_error_events()` - Extracts error logs
- `_extract_maintenance_events()` - Extracts maintenance notes

**How It Works:**
1. Detects file type (CSV or TXT)
2. Reads file content
3. Identifies specific format (sensor, error, maintenance, etc.)
4. Extracts events using appropriate parser
5. Returns list of raw events

### 5.2 Schema Service (`backend/services/schema_service.py`)

**Purpose:** Normalize events to hackathon-required schema

**Key Methods:**
- `normalize_event()` - Main normalization function
- `_normalize_timestamp()` - Converts to ISO 8601
- `_extract_joint()` - Finds joint identifier (J1-J6)
- `_detect_collision_type()` - Identifies collision type
- `_calculate_severity()` - Calculates severity level
- `_extract_force_value()` - Extracts force in Newtons

**Schema Fields:**
- `record_id` - UUID (unique identifier)
- `timestamp` - ISO 8601 format
- `joint` - J1 through J6 or UNKNOWN
- `collision_type` - hard_impact, soft_collision, emergency_stop, or None
- `force_value` - Float in Newtons (0-10,000N)
- `severity` - low, med, high, critical
- `recommended_action` - AI-generated text
- `confidence_flag` - high, medium, inferred
- `recurrence_count` - Number of similar events
- `notes` - Data quality notes

### 5.3 Validation Service (`backend/services/validation_service.py`)

**Purpose:** Validate data quality and accuracy

**Key Methods:**
- `validate_extraction()` - Overall validation
- `validate_events()` - Validates event list
- `calculate_accuracy()` - Calculates accuracy score
- `deduplicate_events()` - Removes duplicates

**Validation Checks:**
- Required fields present
- Valid timestamp format
- Valid severity enum
- Force value in range (0-10,000N)
- Field completeness

### 5.4 History Service (`backend/services/history_service.py`)

**Purpose:** Find similar historical events

**Key Methods:**
- `find_similar_events()` - Main similarity search
- `_extract_keywords()` - Extracts important keywords

**Similarity Calculation:**
- Event type match: 40% weight
- Description similarity: 30% weight
- Error code match: 20% weight
- Severity match: 10% weight
- Common keywords: Bonus points

**Threshold:** Events with similarity ≥ 0.3 are considered similar

### 5.5 Triage Service (`backend/services/triage_service.py`)

**Purpose:** Score and prioritize events

**Key Methods:**
- `score_event()` - Main scoring function
- `_score_to_priority()` - Converts score to priority

**Scoring Process:**
1. Gets AI analysis from Azure OpenAI
2. Calculates base score from AI risk_score
3. Adjusts based on similar events
4. Normalizes to 0-100 range
5. Maps to priority: CRITICAL (80+), HIGH (60+), MEDIUM (40+), LOW (<40)

### 5.6 Azure AI Service (`backend/services/azure_ai_service.py`)

**Purpose:** Interface with Azure OpenAI for intelligent analysis

**Key Methods:**
- `analyze_event()` - Main analysis function
- `_build_triage_prompt()` - Creates 5-section prompt
- `_parse_ai_response()` - Extracts structured response
- `_mock_analysis()` - Fallback when Azure unavailable

**5-Section Output Format:**
1. **DIAGNOSE CAUSE** - Root cause analysis
2. **STEP-BY-STEP INSPECTION PROCEDURE** - What to check
3. **REQUIRED MAINTENANCE ACTIONS** - What to fix
4. **SAFETY CLEARANCE PROCEDURE** - Safety checks
5. **RETURN-TO-SERVICE CONDITIONS** - When robot can resume

**Prompt Engineering:**
- Includes FANUC-specific context
- Provides event details (joint, force, severity, error codes)
- Includes similar historical events for context
- Uses controlled vocabulary for consistency

---

## 6. API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### 1. Health Check
```
GET /
```
**Response:**
```json
{
  "status": "healthy",
  "service": "Industrial Robot Event Triage API"
}
```

#### 2. Process File (ETL)
```
POST /api/etl/process
Content-Type: multipart/form-data
```

**Parameters:**
- `file` (file) - CSV or TXT file to process
- `file_type` (string, optional) - "auto", "csv", or "txt"

**Response:**
```json
{
  "status": "success",
  "filename": "error_logs.txt",
  "events_processed": 80,
  "events": [...],  // First 10 events
  "metadata": {
    "line_count": 80
  },
  "validation": {
    "total_events": 80,
    "accuracy": 85.5
  }
}
```

#### 3. Get Events
```
GET /api/events?limit=100&event_type=error_log
```

**Query Parameters:**
- `limit` (int, default: 100) - Max events to return
- `event_type` (string, optional) - Filter by event type
- `start_date` (string, optional) - Filter by start date
- `end_date` (string, optional) - Filter by end date

**Response:**
```json
{
  "total": 180,
  "events": [...]
}
```

#### 4. Lookup History
```
POST /api/history/lookup
Content-Type: application/json
```

**Request Body:**
```json
{
  "event_id": "error_0_1234567890",
  "event_type": "error_log",
  "timestamp": "2025-11-17T09:18:37",
  "description": "SRVO-324 Collision detected",
  "raw_data": {}
}
```

**Response:**
```json
{
  "event_id": "error_0_1234567890",
  "similar_events_count": 5,
  "similar_events": [
    {
      "event_id": "...",
      "description": "...",
      "similarity_score": 0.85,
      "match_reasons": ["same_type", "similar_description"]
    }
  ]
}
```

#### 5. Score Triage
```
POST /api/triage/score
Content-Type: application/json
```

**Request Body:**
```json
{
  "event_id": "error_0_1234567890",
  "event_type": "error_log",
  "timestamp": "2025-11-17T09:18:37",
  "description": "SRVO-324 Collision detected",
  "raw_data": {}
}
```

**Response:**
```json
{
  "event_id": "error_0_1234567890",
  "triage_score": 75.5,
  "priority": "HIGH",
  "recommendation": "Diagnosis: ...",
  "similar_events": [...],
  "analysis": "Full AI analysis text...",
  "maintenance_report": {
    "diagnose_cause": "...",
    "inspection_procedure": "...",
    "maintenance_actions": "...",
    "safety_clearance": "...",
    "return_to_service": "..."
  }
}
```

#### 6. Batch Process All Datasets
```
POST /api/batch/process-all
```

**Response:**
```json
{
  "status": "success",
  "files_processed": 7,
  "total_events": 500,
  "events_with_recommendations": 15,
  "files": [
    {
      "filename": "error_logs.txt",
      "events_count": 80,
      "status": "success"
    }
  ],
  "message": "Processed 500 events from 7 files..."
}
```

#### 7. Get Statistics
```
GET /api/stats
```

**Response:**
```json
{
  "total_events": 500,
  "by_type": {
    "error_log": 80,
    "system_alert": 50,
    "maintenance": 60
  },
  "by_priority": {
    "CRITICAL": 10,
    "HIGH": 25,
    "MEDIUM": 100,
    "LOW": 365
  },
  "by_severity": {
    "critical": 10,
    "high": 25,
    "med": 100,
    "low": 365
  }
}
```

---

## 7. User Guide

### 7.1 Starting the System

#### Terminal 1: Start Backend
```bash
./start_backend.sh
```
Backend runs on: http://localhost:8000

#### Terminal 2: Start Frontend
```bash
./start_frontend.sh
```
Frontend opens at: http://localhost:8501

### 7.2 Using Batch Processing (Recommended)

1. **Start both backend and frontend**
2. **Go to "Upload" page** in the frontend
3. **Click "🔄 Process All Datasets"** button
4. **Wait 5-10 minutes** for processing
5. **View results:**
   - See summary metrics
   - Check file processing details
   - Go to "View Events" to see all events

### 7.3 Processing Individual Files

1. **Go to "Upload" page**
2. **Click "Choose a file"** or drag and drop
3. **Select a CSV or TXT file**
4. **Click "Process File"**
5. **View preview** of processed events

### 7.4 Viewing Events

1. **Go to "View Events" page**
2. **Filter by type** (optional)
3. **Adjust "Max Events"** limit
4. **Click "🔄 Refresh Events"** to reload
5. **Click "Select"** on any event to analyze it

### 7.5 Triage Analysis

1. **Select an event** (from "View Events" or quick select)
2. **Go to "Triage Analysis" page**
3. **View event details** in the expandable section
4. **Click "🔍 Lookup History"** to find similar events
5. **Click "📊 Score Triage"** to get AI recommendations

**Triage Results Include:**
- **Triage Score** (0-100)
- **Priority** (CRITICAL, HIGH, MEDIUM, LOW)
- **Recommendation** (summary)
- **AI Analysis** (full text)
- **Maintenance Report** (5 sections)
- **Token Usage** (if Azure AI used)

---

## 8. Data Schema

### Standardized Event Schema

All events are normalized to this schema:

```python
{
    "record_id": "uuid-string",           # Unique identifier
    "timestamp": "2025-11-17T09:18:37",   # ISO 8601 format
    "joint": "J3",                        # J1-J6 or UNKNOWN
    "collision_type": "hard_impact",      # or soft_collision, emergency_stop, None
    "force_value": 645.0,                 # Float in Newtons (0-10,000N)
    "severity": "high",                   # low, med, high, critical
    "recommended_action": "...",         # AI-generated text
    "confidence_flag": "high",            # high, medium, inferred
    "recurrence_count": 3,                # Number of similar events
    "notes": "...",                       # Data quality notes
    "event_type": "error_log",           # Type of event
    "event_id": "error_0_1234567890",    # Original event ID
    "description": "SRVO-324 Collision detected",
    "error_code": "SRVO-324",            # FANUC error code
    "original_event": {...}              # Original raw event data
}
```

### Field Details

#### record_id
- **Type:** UUID string
- **Format:** `550e8400-e29b-41d4-a716-446655440000`
- **Generated:** Automatically, guaranteed unique

#### timestamp
- **Type:** ISO 8601 string
- **Format:** `YYYY-MM-DDTHH:MM:SS`
- **Example:** `2025-11-17T09:18:37`
- **Normalization:** Handles various formats, infers if missing

#### joint
- **Type:** String
- **Values:** `J1`, `J2`, `J3`, `J4`, `J5`, `J6`, `UNKNOWN`
- **Mapping:**
  - J1 = Base rotation
  - J2 = Shoulder
  - J3 = Elbow
  - J4 = Wrist Roll
  - J5 = Wrist Pitch
  - J6 = Wrist Yaw

#### collision_type
- **Type:** Enum or None
- **Values:** `hard_impact`, `soft_collision`, `emergency_stop`, `None`
- **Detection:** Based on keywords and error codes

#### force_value
- **Type:** Float or None
- **Unit:** Newtons (N)
- **Range:** 0-10,000N
- **Source:** Extracted from sensor data or JSON logs

#### severity
- **Type:** Enum
- **Values:** `low`, `med`, `high`, `critical`
- **Calculation:**
  - `low`: < 300N
  - `med`: 300-600N
  - `high`: 600-800N
  - `critical`: > 800N

#### recommended_action
- **Type:** Text
- **Source:** AI-generated (5-section format)
- **Format:** Structured maintenance procedure

#### confidence_flag
- **Type:** Enum
- **Values:** `high`, `medium`, `inferred`
- **Determined by:** Data completeness (timestamp, joint, force, error_code)

#### recurrence_count
- **Type:** Integer
- **Calculation:** Groups events by joint + date (24hr window)
- **Meaning:** Number of similar events in timeframe

---

## 9. Azure AI Integration

### Setup

1. **Get Azure OpenAI credentials:**
   - API Key
   - Endpoint URL
   - Deployment Name
   - API Version

2. **Configure in `.env` file:**
```env
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.cognitiveservices.azure.com
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-2
AZURE_OPENAI_API_VERSION=2024-12-01-preview
```

### Model Recommendations

**Recommended:** `gpt-4o-2` or `gpt-4o`
- Good balance of speed and quality
- Supports long context windows
- Cost-effective for batch processing

**Alternative:** `gpt-4-turbo`
- Faster responses
- Good for real-time analysis

### How It Works

1. **Event Analysis Request:**
   - Frontend calls `/api/triage/score`
   - Backend calls `AzureAIService.analyze_event()`
   - Service builds prompt with event details

2. **Prompt Construction:**
   - Includes event type, joint, force, severity
   - Adds FANUC error code context
   - Includes similar historical events
   - Requests 5-section output format

3. **AI Response:**
   - GPT model generates analysis
   - Service parses structured response
   - Extracts 5 sections and risk score
   - Returns formatted result

4. **Fallback:**
   - If Azure unavailable, uses mock analysis
   - Mock provides basic scoring and recommendations
   - System remains functional

### Token Usage

- **Prompt tokens:** ~500-1000 per request
- **Completion tokens:** ~800-1500 per response
- **Total:** ~1300-2500 tokens per event analysis
- **Cost:** Tracked in response metadata

### Verification

Test connection:
```bash
python test_azure_connection.py
```

Check in Azure Portal:
- Go to Azure AI Foundry
- View deployment metrics
- Check token usage
- Monitor API calls

---

## 10. Troubleshooting

### Common Issues

#### Backend Won't Start

**Problem:** Port 8000 already in use

**Solution:**
```bash
# Find process using port 8000
lsof -ti:8000

# Kill the process
kill -9 <PID>

# Or use different port
uvicorn main:app --reload --port 8001
```

#### Frontend Can't Connect

**Problem:** Connection timeout or refused

**Solutions:**
1. Verify backend is running: `curl http://localhost:8000/`
2. Check firewall settings
3. Hard refresh browser (Cmd+Shift+R)
4. Check backend logs for errors

#### No Events Showing

**Problem:** Events processed but not displayed

**Solutions:**
1. Click "🔄 Refresh Events" button
2. Check backend logs for processing errors
3. Verify files were uploaded successfully
4. Check if events passed validation

#### Azure AI Not Working

**Problem:** Mock analysis instead of real AI

**Solutions:**
1. Verify `.env` file exists and has correct credentials
2. Test connection: `python test_azure_connection.py`
3. Check Azure Portal for deployment status
4. Verify API key has correct permissions

#### Batch Processing Takes Too Long

**Problem:** Processing all events with AI takes hours

**Solution:** Already optimized! Now processes:
- Up to 15 events with full AI recommendations
- Remaining events get instant heuristic scores
- Total time: 5-10 minutes instead of hours

#### Timestamp Parsing Warnings

**Problem:** Many timestamp warnings in logs

**Solution:** This is normal! System handles:
- Missing timestamps (uses current time)
- Various formats (normalizes to ISO 8601)
- Date-only entries (sets to midnight)

#### Duplicate Widget Errors

**Problem:** Streamlit duplicate key errors

**Solution:** Already fixed! Uses:
- `record_id` (UUID) for unique keys
- Falls back to `event_id` or index
- Ensures all widgets have unique keys

---

## 11. File Structure

```
CSI_Hackathon/
├── backend/
│   ├── main.py                    # FastAPI application & endpoints
│   └── services/
│       ├── etl_service.py         # File processing & extraction
│       ├── schema_service.py      # Data normalization
│       ├── validation_service.py  # Data validation
│       ├── history_service.py     # Similarity search
│       ├── triage_service.py      # Scoring & prioritization
│       └── azure_ai_service.py    # Azure OpenAI integration
│
├── frontend/
│   └── app.py                     # Streamlit UI application
│
├── scripts/
│   ├── clean_dataset.py          # Dataset cleaning script
│   ├── clean_text_to_csv.py      # Text to CSV conversion
│   └── batch_process_all_datasets.py  # Full batch processing
│
├── Hackathon_Data/                # Input datasets
│   ├── error_logs.txt
│   ├── system_alerts.txt
│   ├── maintenance_notes.txt
│   ├── sensor_readings.csv
│   ├── performance_metrics.csv
│   ├── torque_events_by_cycle.csv
│   └── torque_timeseries.csv
│
├── Hackathon_Data_Cleaned/        # Cleaned datasets (generated)
│
├── docs/                          # Documentation
│   ├── SCHEMA.md
│   ├── ARCHITECTURE.md
│   ├── AZURE_SETUP_GUIDE.md
│   └── ROBOT_CONTEXT.md
│
├── .env                           # Environment variables (create this)
├── config.env.example            # Example env file
├── requirements.txt              # Python dependencies
├── README.md                     # Project overview
├── HOW_TO_RUN.md                # Quick start guide
└── COMPLETE_DOCUMENTATION.md     # This file
```

---

## 12. Data Processing Details

### ETL Pipeline Steps

#### Step 1: File Detection
- Checks file extension (.csv or .txt)
- Reads first 10 lines to identify format
- Determines specific type (sensor, error, maintenance, etc.)

#### Step 2: Event Extraction
- **CSV Files:**
  - Reads with pandas
  - Checks for specific column patterns
  - Extracts row-by-row as events
  
- **TXT Files:**
  - Reads line-by-line
  - Uses regex patterns to parse
  - Handles multiple timestamp formats

#### Step 3: Normalization
- Converts timestamps to ISO 8601
- Extracts joint identifiers
- Standardizes error codes
- Calculates severity from force values
- Generates unique record IDs

#### Step 4: Validation
- Checks required fields
- Validates formats
- Ensures data quality
- Calculates accuracy scores

#### Step 5: Deduplication
- Groups events by joint + date
- Counts recurrences
- Keeps unique events with recurrence counts

### Data Cleaning Decisions

#### Missing Timestamps
- **Approach:** Infer from sequence or use current time
- **Confidence:** Marked with `confidence_flag = 'inferred'`
- **Documentation:** Noted in `notes` field

#### Missing Force Values
- **Approach:** Calculate severity from other indicators
- **Fallback:** Use error codes and event type
- **Documentation:** Noted in `notes` field

#### Unknown Joints
- **Approach:** Set to "UNKNOWN", flag for manual review
- **Confidence:** Lower confidence flag
- **Documentation:** Noted in `notes` field

#### Duplicate Events
- **Approach:** Keep all, mark with recurrence_count
- **Grouping:** By joint + date (24hr window)
- **Use Case:** Identifies chronic issues

---

## 13. AI Prompt Engineering

### Triage Prompt Structure

The AI receives a carefully crafted prompt:

```
You are an expert FANUC industrial robot maintenance technician.

EVENT TYPE: [error_log/performance_metric/etc]

FANUC ROBOT EVENT DETAILS:
- Joint: J3 (J1=Base, J2=Shoulder, ...)
- Force Value: 645N
- Severity: high
- Collision Type: hard_impact
- Timestamp: 2025-11-17T09:18:37
- Description: SRVO-324 Collision detected
- FANUC Error Code: SRVO-324 (Collision detected)
- Recurrence: This event has occurred 3 times in the last 24 hours

SIMILAR HISTORICAL EVENTS:
1. SRVO-324 Collision detected (Similarity: 85%)
2. ...

REQUIRED OUTPUT FORMAT (provide all 5 sections):

1. DIAGNOSE CAUSE:
   [Explain root cause based on force level, joint location, frequency]

2. STEP-BY-STEP INSPECTION PROCEDURE:
   [List specific checks technician should perform]

3. REQUIRED MAINTENANCE ACTIONS:
   [Specify exact repairs, replacements, adjustments]

4. SAFETY CLEARANCE PROCEDURE:
   [What must be verified before restarting]

5. RETURN-TO-SERVICE CONDITIONS:
   [Criteria for putting robot back online]

At the END, also provide:
- RISK_SCORE: 0-100
- PRIORITY: CRITICAL/HIGH/MEDIUM/LOW
```

### Response Parsing

The system extracts:
- 5 maintenance report sections
- Risk score (0-100)
- Priority level
- Recommendation summary
- Full analysis text

---

## 14. Performance Optimization

### Batch Processing Optimization

**Original:** Processed 50 events with AI (25-50 minutes)

**Optimized:** 
- Processes 15 priority events with AI (5-10 minutes)
- Uses heuristic scoring for remaining events (instant)
- All events still get scores and priorities

### Similarity Search Optimization

- **Threshold:** Lowered from 0.6 to 0.3 (finds more matches)
- **Field Extraction:** Handles nested `original_event` structure
- **Keyword Matching:** Bonus points for common terms

### Caching Strategy

- Events stored in memory (`events_store`)
- Similar events cached during batch processing
- Recommendations cached per event

---

## 15. Extending the System

### Adding New File Types

1. **Add detection logic** in `etl_service.py`:
```python
elif "new_pattern" in content:
    events = self._extract_new_type_events(lines)
```

2. **Create extraction method:**
```python
def _extract_new_type_events(self, lines):
    events = []
    # Your extraction logic
    return events
```

3. **Update schema service** if new fields needed

### Adding New Event Types

1. **Update schema service** to handle new type
2. **Add to prompt templates** in Azure AI service
3. **Update frontend** to display new type

### Database Integration

Currently uses in-memory storage. To add database:

1. **Choose database** (PostgreSQL, MongoDB, etc.)
2. **Create models** for events
3. **Update `events_store`** to use database
4. **Add connection pooling**

### Real-time Processing

To process events in real-time:

1. **Add message queue** (RabbitMQ, Kafka)
2. **Create event listeners**
3. **Process asynchronously**
4. **Update frontend** with WebSocket for live updates

---

## 16. Best Practices

### Data Quality

- ✅ Always validate events before storing
- ✅ Document data quality issues in `notes` field
- ✅ Use `confidence_flag` to indicate data reliability
- ✅ Clean datasets before processing when possible

### AI Usage

- ✅ Batch process priority events only
- ✅ Cache recommendations when possible
- ✅ Monitor token usage for cost control
- ✅ Use mock mode for testing

### Error Handling

- ✅ Log all errors with context
- ✅ Provide user-friendly error messages
- ✅ Fall back gracefully when services unavailable
- ✅ Validate inputs before processing

### Performance

- ✅ Process files in batches
- ✅ Use async/await for I/O operations
- ✅ Limit AI calls to priority events
- ✅ Cache similarity calculations

---

## 17. Security Considerations

### API Security

- **CORS:** Currently allows all origins (restrict in production)
- **Authentication:** Not implemented (add for production)
- **Rate Limiting:** Not implemented (add for production)

### Data Security

- **Credentials:** Stored in `.env` (never commit to git)
- **File Uploads:** Saved to `uploads/` directory
- **Data Storage:** In-memory (consider encryption for sensitive data)

### Azure AI Security

- **API Keys:** Rotate regularly
- **Endpoint:** Use private endpoints in production
- **Token Usage:** Monitor for anomalies

---

## 18. Testing

### Manual Testing

1. **Test file upload:**
   - Upload each file type
   - Verify events extracted correctly
   - Check normalization

2. **Test triage scoring:**
   - Select different event types
   - Verify scores are reasonable
   - Check AI recommendations format

3. **Test batch processing:**
   - Process all datasets
   - Verify all files processed
   - Check summary metrics

### Automated Testing (Future)

- Unit tests for each service
- Integration tests for API endpoints
- End-to-end tests for full workflow

---

## 19. Deployment

### Local Development

```bash
# Terminal 1
./start_backend.sh

# Terminal 2
./start_frontend.sh
```

### Production Deployment

**Backend:**
- Deploy to Azure App Service or similar
- Use environment variables for config
- Enable logging and monitoring

**Frontend:**
- Deploy to Streamlit Cloud or similar
- Configure API endpoint URL
- Enable authentication

**Azure AI:**
- Use private endpoints
- Enable monitoring
- Set up alerts for high token usage

---

## 20. Support & Resources

### Documentation Files

- `README.md` - Project overview
- `HOW_TO_RUN.md` - Quick start guide
- `COMPLETE_DOCUMENTATION.md` - This file
- `docs/SCHEMA.md` - Data schema details
- `docs/ARCHITECTURE.md` - Architecture diagrams
- `docs/AZURE_SETUP_GUIDE.md` - Azure setup instructions
- `docs/ROBOT_CONTEXT.md` - FANUC robot specifics

### Key Scripts

- `scripts/clean_dataset.py` - Clean all datasets
- `scripts/batch_process_all_datasets.py` - Full batch processing
- `test_azure_connection.py` - Test Azure AI connection

### Getting Help

1. Check backend logs for errors
2. Check frontend browser console (F12)
3. Review this documentation
4. Check Azure Portal for AI service status

---

## Conclusion

This system provides a complete solution for analyzing and triaging FANUC industrial robot events. It combines:

- **Robust data processing** (handles various formats)
- **Intelligent AI analysis** (Azure OpenAI integration)
- **User-friendly interface** (Streamlit)
- **Scalable architecture** (FastAPI backend)

The system is designed to be:
- **Easy to use** - Simple UI, clear workflows
- **Reliable** - Handles errors gracefully
- **Extensible** - Easy to add new features
- **Production-ready** - Can be deployed and scaled

For questions or issues, refer to the troubleshooting section or check the logs.

---

**End of Documentation**

