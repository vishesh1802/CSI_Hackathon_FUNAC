<<<<<<< HEAD
# CSI_Hackathon
=======
# FANUC Industrial Robot Event Triage System

A comprehensive system for analyzing and triaging **FANUC industrial robot** events using Streamlit UI, FastAPI backend, and Azure AI Foundry integration. Designed specifically for FANUC robot maintenance and diagnostics.

## Architecture

```
┌───────────────────────────────┐
│    Streamlit / Python UI      │
│  Upload → View → Select Event │
└──────────────┬────────────────┘
               │ HTTP
               ▼
┌───────────────────────────────┐
│         FastAPI Backend       │
│  - ETL pipeline               │
│  - History lookup             │
│  - Triage scoring             │
└──────────────┬────────────────┘
               │ calls
               ▼
┌───────────────────────────────┐
│    Azure AI Foundry (Aoai)    │
│  - GPT model deployment        │
│  - Prompt templates            │
│  - Token monitoring            │
└───────────────────────────────┘
```

## Features

### Frontend (Streamlit)
- **Upload**: Upload CSV/TXT files with sensor data, error logs, alerts, and maintenance notes
- **View Events**: Browse and filter processed events
- **Triage Analysis**: Select events for AI-powered triage scoring and recommendations

### Backend (FastAPI)
- **ETL Pipeline**: Process various file formats (CSV, TXT) and extract structured events
- **History Lookup**: Find similar historical events using similarity matching
- **Triage Scoring**: Intelligent event prioritization using Azure AI Foundry

### Azure AI Foundry Integration
- **GPT Model**: Uses Azure OpenAI for intelligent event analysis
- **Prompt Templates**: Customizable prompts for different analysis types
- **Token Monitoring**: Track token usage for cost optimization

## Installation

1. **Clone the repository**
   ```bash
   cd CSI_Hackathon
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Azure AI Foundry (Optional)**
   - Copy `.env.example` to `.env`
   - Fill in your Azure OpenAI credentials:
     ```
     AZURE_OPENAI_API_KEY=your_key
     AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
     AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
     ```
   - If not configured, the system will use mock/heuristic-based analysis

## Usage

### Start the Backend

```bash
cd backend
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### Start the Frontend

```bash
cd frontend
streamlit run app.py
```

The UI will be available at `http://localhost:8501`

## API Endpoints

### ETL Pipeline
- `POST /api/etl/process` - Upload and process data files

### Events
- `GET /api/events` - Get all events (with optional filters)
- `GET /api/events/{event_id}` - Get specific event details

### History Lookup
- `POST /api/history/lookup` - Find similar historical events

### Triage Scoring
- `POST /api/triage/score` - Get AI-powered triage score and recommendations

### Statistics
- `GET /api/stats` - Get system statistics

## Supported File Formats

### CSV Files
- **Sensor Readings**: Temperature, Vibration, Axis positions
- **Performance Metrics**: Various system metrics over time

### TXT Files
- **System Alerts**: Time-stamped alerts with severity levels
- **Error Logs**: Robot error codes (SRVO, TEMP, MOTN, etc.)
- **Maintenance Notes**: Maintenance history and actions

## Data Flow

1. **Upload**: User uploads a file through Streamlit UI
2. **ETL Processing**: FastAPI backend processes the file and extracts events
3. **Storage**: Events are stored in memory (use database in production)
4. **View**: User can browse and filter events
5. **Select**: User selects an event for analysis
6. **History Lookup**: System finds similar historical events
7. **Triage Scoring**: Azure AI analyzes the event and provides:
   - Priority level (CRITICAL, HIGH, MEDIUM, LOW)
   - Risk score (0-100)
   - Actionable recommendations
   - Detailed analysis

## Configuration

### Environment Variables

- `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint URL
- `AZURE_OPENAI_API_VERSION`: API version (default: 2024-02-15-preview)
- `AZURE_OPENAI_DEPLOYMENT_NAME`: Deployment name (default: gpt-4o)

## Project Structure

```
CSI_Hackathon/
├── backend/
│   ├── main.py                 # FastAPI application
│   └── services/
│       ├── etl_service.py      # ETL pipeline
│       ├── history_service.py  # History lookup
│       ├── triage_service.py   # Triage scoring
│       └── azure_ai_service.py # Azure AI integration
├── frontend/
│   └── app.py                  # Streamlit UI
├── Hackathon_Data/             # Sample data files
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## Development Notes

- The system works without Azure AI credentials (uses mock analysis)
- For production, replace in-memory storage with a database
- Add authentication/authorization for production use
- Implement proper error handling and logging
- Add unit tests and integration tests

## License

MIT License

>>>>>>> 5f187ce (Initial push)
