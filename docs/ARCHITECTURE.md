# System Architecture

## Vertical Architecture Flow (Mermaid)

```mermaid
flowchart TB
    U[User / Technician] --> UI[Streamlit UI\nUpload / Batch / View / Triage / Analytics / Export]
    UI --> API[FastAPI Backend\n/api/batch /events /triage /history /stats]
    API --> ETL[ETL & Validation\nISO timestamps, collision_type, severity, status\nclean NaN/inf, dedup, recurrence, metrics]
    ETL --> STORE[Structured Events Store\n(in-memory; export CSV/JSON)]
    STORE --> AI[AI Triage (Azure OpenAI or mock)\n5-section recs, overrides, caching, history lookup]
    STORE --> ANALYTICS[Analytics & Exports\nTrend, cost impact, filters; CSV/JSON/report]
```

Notes:
- UI: Streamlit app for upload, processing triggers, viewing events, triage, analytics, exports.
- Backend: FastAPI endpoints for ETL, triage scoring, history lookup, stats, batch processing.
- ETL/Validation: normalization (ISO timestamps, collision_type, severity, status), cleaning (NaN/inf), deduplication, recurrence counting, metrics.
- Store: in-memory events_store, exportable to CSV/JSON.
- AI: Azure OpenAI (or mock) for 5-section maintenance recommendations; severity/recurrence overrides; caching; history lookup.
- Analytics/Exports: trend and cost impact, advanced filters, CSV/JSON/analytics report downloads.

## Overview

The Industrial Robot Event Triage System follows a three-tier architecture:

```
Horizontal (high-level, left-to-right):

```
[ Streamlit UI ]
  - Upload (CSV/TXT), Event Browser/Filter
  - Triage Analysis
        |
        v  (HTTP REST)
[ FastAPI Backend ]
  - ETL Pipeline: parse CSV/TXT, extract, normalize schema, deduplicate
  - Schema: standardize fields, ISO timestamps, severity, status, joint
  - Validation: accuracy & completeness, dedup stats
  - History: similar events, recurrence
  - Triage: prioritize, risk scoring
        |
        v  (API calls)
[ Azure AI Foundry (Azure OpenAI) ]
  - GPT-4/GPT-4o deployment
  - 5-section maintenance report, prompt templates
  - Token usage tracking
```
```

## Data Flow

### 1. Upload & Processing
```
User uploads file (CSV/TXT)
    ↓
ETL Service parses file
    ↓
Extract raw events
    ↓
Schema Service normalizes to standard format
    ↓
Validation Service checks accuracy
    ↓
Deduplication & recurrence calculation
    ↓
Store in events database
```

### 2. Triage Analysis
```
User selects event
    ↓
History Service finds similar events
    ↓
Triage Service prepares event data
    ↓
Azure AI Foundry analyzes event
    ↓
Generate 5-section maintenance report:
    1. Diagnose cause
    2. Inspection procedure
    3. Maintenance actions
    4. Safety clearance
    5. Return-to-service conditions
    ↓
Return to user with priority & recommendations
```

## Azure Services Integration

### Azure Blob Storage (Data Input)
- **Purpose**: Store uploaded dataset files
- **Integration**: Files uploaded via API, processed, then stored
- **Future**: Direct blob storage integration for large datasets

### Azure App Service (Backend)
- **Purpose**: Host FastAPI backend
- **Deployment**: Containerized FastAPI application
- **Scaling**: Auto-scaling based on load

### Azure OpenAI / AI Foundry
- **Model**: GPT-4 deployment
- **Purpose**: Intelligent event analysis and maintenance recommendations
- **Features**:
  - Custom prompt templates
  - Token usage monitoring
  - Structured output (5-section format)

## Component Details

### Frontend (Streamlit)
- **Technology**: Python Streamlit
- **Features**:
  - Drag-and-drop file upload
  - Real-time event browsing
  - Interactive triage analysis
  - Validation metrics display

### Backend Services

#### ETL Service
- Parses CSV files (sensor data, metrics)
- Parses TXT files (alerts, errors, maintenance notes)
- Handles various timestamp formats
- Extracts structured data

#### Schema Service
- Enforces hackathon-required schema
- Normalizes all fields to standard format
- Calculates derived fields (severity, confidence)
- Validates data quality

#### Validation Service
- Calculates extraction accuracy
- Tracks field completeness
- Measures against 75%+ target
- Provides deduplication statistics

#### History Service
- Finds similar historical events
- Calculates similarity scores
- Tracks recurrence patterns
- Provides context for AI analysis

#### Triage Service
- Prioritizes events
- Calculates risk scores
- Coordinates AI analysis
- Formats recommendations

#### Azure AI Service
- Manages Azure OpenAI connection
- Builds structured prompts
- Parses 5-section output
- Monitors token usage
- Falls back to heuristic analysis if unavailable

## Data Storage

### Current Implementation
- In-memory storage (events_store list)
- Suitable for MVP/demo

### Production Recommendations
- **Azure Cosmos DB**: Document store for events
- **Azure SQL Database**: Relational data for analytics
- **Azure Blob Storage**: Raw file storage

## API Endpoints

### ETL
- `POST /api/etl/process` - Upload and process files

### Events
- `GET /api/events` - List all events (with filters)
- `GET /api/events/{event_id}` - Get specific event

### History
- `POST /api/history/lookup` - Find similar events

### Triage
- `POST /api/triage/score` - Get AI-powered triage analysis

### Validation
- `GET /api/validation` - Get validation metrics
- `GET /api/stats` - Get system statistics

## Security Considerations

### Current (MVP)
- CORS enabled for development
- No authentication (local use)

### Production
- Azure AD authentication
- API key management
- HTTPS only
- Rate limiting
- Input validation

## Scalability

### Current Limitations
- In-memory storage (not persistent)
- Single instance (no load balancing)
- No caching

### Production Enhancements
- Database persistence
- Redis caching for frequent queries
- Queue-based processing for large files
- Horizontal scaling with Azure App Service
- CDN for static assets

## Monitoring & Observability

### Current
- Basic logging
- Token usage tracking
- Validation metrics

### Production
- Azure Application Insights
- Custom metrics dashboard
- Alerting on errors
- Performance monitoring

