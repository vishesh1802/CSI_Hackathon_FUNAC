# 🚀 How to Run the Industrial Robot Event Triage System

## Quick Start Guide

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Set Up Azure AI Credentials (Optional but Recommended)

Create a `.env` file in the project root:

```bash
cp config.env.example .env
```

Edit `.env` and add your Azure OpenAI credentials:
```
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.cognitiveservices.azure.com
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-2
AZURE_OPENAI_API_VERSION=2024-12-01-preview
```

**Note:** If you don't set up Azure AI, the system will use mock analysis (still works, but less intelligent).

### Step 3: Start the Backend Server

**Option A: Using the start script (Recommended)**
```bash
./start_backend.sh
```

**Option B: Manual start**
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend will start on: **http://localhost:8000**
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/

### Step 4: Start the Frontend (in a NEW terminal)

**Option A: Using the start script**
```bash
./start_frontend.sh
```

**Option B: Manual start**
```bash
streamlit run frontend/app.py
```

The frontend will open automatically in your browser at: **http://localhost:8501**

## 🎯 Using the System

### Option 1: Batch Process All Datasets (Recommended)

1. **Start both backend and frontend** (see steps above)
2. **In the frontend**, go to the **"Upload"** page
3. **Click "🔄 Process All Datasets"** button
4. **Wait 2-5 minutes** for processing
5. **View results** in "View Events" page

This will:
- ✅ Process all 7 files in `Hackathon_Data` folder
- ✅ Clean and normalize all events
- ✅ Generate AI recommendations
- ✅ Show summary metrics

### Option 2: Process Individual Files

1. **Go to "Upload"** page
2. **Click "Choose a file"** or drag and drop a file
3. **Click "Process File"** button
4. **View results** in the preview or "View Events" page

### Option 3: Use Command Line Script

For full batch processing with all recommendations:

```bash
python scripts/batch_process_all_datasets.py
```

This will:
- Process all datasets
- Generate recommendations for ALL events (not just first 50)
- Export results to `batch_processing_results/` folder
- Create JSON and CSV exports

## 📊 Viewing Results

### View All Events
- Go to **"View Events"** page
- See all processed events in a table
- Filter by event type
- Click **"Select"** on any event for detailed analysis

### Triage Analysis
- Go to **"Triage Analysis"** page
- Select an event (from "View Events" or quick select)
- Click **"🔍 Lookup History"** to find similar events
- Click **"📊 Score Triage"** to get AI-powered recommendations

## 🔧 Troubleshooting

### Backend won't start
- Check if port 8000 is already in use: `lsof -ti:8000`
- Kill existing process: `kill -9 <PID>`
- Try a different port: `uvicorn main:app --reload --port 8001`

### Frontend can't connect to backend
- Make sure backend is running on http://localhost:8000
- Check backend logs for errors
- Try refreshing the browser (hard refresh: Cmd+Shift+R)

### No events showing
- Make sure you've processed files (batch or individual)
- Check "View Events" page and click "🔄 Refresh Events"
- Check backend logs for processing errors

### Azure AI not working
- Verify credentials in `.env` file
- Check Azure Portal to ensure deployment is active
- System will fall back to mock analysis if Azure AI unavailable

## 📁 File Structure

```
CSI_Hackathon/
├── backend/              # FastAPI backend
│   ├── main.py          # API endpoints
│   └── services/        # Business logic
├── frontend/            # Streamlit frontend
│   └── app.py           # UI application
├── Hackathon_Data/      # Input datasets
├── scripts/             # Utility scripts
│   ├── clean_dataset.py
│   └── batch_process_all_datasets.py
└── .env                 # Environment variables (create this)
```

## 🎯 Quick Commands Reference

```bash
# Start backend
./start_backend.sh

# Start frontend (in new terminal)
./start_frontend.sh

# Batch process all datasets (command line)
python scripts/batch_process_all_datasets.py

# Clean datasets
python scripts/clean_dataset.py

# Test Azure connection
python test_azure_connection.py
```

## ✅ Success Checklist

- [ ] Backend running on http://localhost:8000
- [ ] Frontend running on http://localhost:8501
- [ ] Azure AI credentials configured (optional)
- [ ] Datasets in `Hackathon_Data` folder
- [ ] Can see "Upload" page in frontend
- [ ] Can process files successfully

## 🆘 Need Help?

- Check backend logs for errors
- Check frontend browser console (F12)
- Verify all dependencies installed: `pip install -r requirements.txt`
- Ensure Python 3.8+ is installed

