# Quick Start Guide

## Prerequisites

- Python 3.8 or higher
- pip package manager

## Installation

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Azure AI (Optional)**
   - Copy `config.env.example` to `.env`
   - Add your Azure OpenAI credentials
   - If you don't have Azure OpenAI, the system will work with mock analysis

## Running the System

### Option 1: Using Shell Scripts (Recommended)

**Terminal 1 - Start Backend:**
```bash
./start_backend.sh
```

**Terminal 2 - Start Frontend:**
```bash
./start_frontend.sh
```

### Option 2: Manual Start

**Terminal 1 - Start Backend:**
```bash
cd backend
uvicorn main:app --reload
```

**Terminal 2 - Start Frontend:**
```bash
cd frontend
streamlit run app.py
```

## Access the Application

- **Frontend UI**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Usage Workflow

1. **Upload Data**
   - Go to "Upload" page
   - Select a CSV or TXT file from `Hackathon_Data/` folder
   - Click "Process File"
   - Events will be extracted and stored

2. **View Events**
   - Go to "View Events" page
   - Browse processed events
   - Filter by type if needed
   - Click "Select" on any event

3. **Triage Analysis**
   - Go to "Triage Analysis" page
   - Selected event will be shown
   - Click "Lookup History" to find similar events
   - Click "Score Triage" to get AI-powered analysis
   - View priority, recommendations, and detailed analysis

## Sample Data

The `Hackathon_Data/` folder contains sample files:
- `sensor_readings.csv` - Sensor data
- `system_alerts.txt` - System alerts
- `error_logs.txt` - Error logs
- `performance_metrics.csv` - Performance data
- `maintenance_notes.txt` - Maintenance history

## Troubleshooting

### Backend won't start
- Check if port 8000 is available
- Ensure all dependencies are installed
- Check for Python version compatibility

### Frontend can't connect to backend
- Ensure backend is running on port 8000
- Check API_BASE_URL in `frontend/app.py`
- Verify CORS settings in backend

### Azure AI not working
- Check `.env` file has correct credentials
- Verify Azure OpenAI deployment name
- System will fallback to mock analysis if Azure AI is unavailable

## Next Steps

- Add your own data files
- Configure Azure AI Foundry for intelligent analysis
- Customize prompt templates in `backend/services/azure_ai_service.py`
- Extend ETL service for additional file formats

