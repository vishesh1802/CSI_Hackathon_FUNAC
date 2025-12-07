"""
Streamlit Frontend for FANUC FirstResponder
- Upload data files
- View processed events
- Select events for triage analysis
- Advanced features: PDF reports, heatmaps, trend analysis, exports
"""

import streamlit as st
import requests
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple
import io
from collections import Counter
import base64
import hashlib

# Try to import Plotly, but handle gracefully if not available
PLOTLY_AVAILABLE = False
try:
    import plotly.express as px
    import plotly.graph_objects as go
    # Test if Plotly actually works by trying to create a simple figure
    try:
        test_fig = px.bar(x=[1, 2], y=[1, 2])
        PLOTLY_AVAILABLE = True
    except Exception:
        # Plotly imported but broken (missing modules)
        PLOTLY_AVAILABLE = False
        px = None
        go = None
except ImportError:
    PLOTLY_AVAILABLE = False
    px = None
    go = None

# Configuration
API_BASE_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="FANUC FirstResponder",
    page_icon="🤖",
    layout="wide"
)

# Initialize dark mode in session state
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# Custom CSS with dark mode support
def get_css():
    if st.session_state.dark_mode:
        return """
        <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #4fc3f7;
            text-align: center;
            margin-bottom: 2rem;
        }
        .event-card {
            border: 1px solid #444;
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem 0;
            background-color: #2d2d2d;
        }
        .stApp {
            background-color: #1e1e1e;
        }
        .priority-critical { color: #ff5252; font-weight: bold; }
        .priority-high { color: #ffab40; font-weight: bold; }
        .priority-medium { color: #ffee58; font-weight: bold; }
        .priority-low { color: #69f0ae; font-weight: bold; }
        .metric-card {
            background: linear-gradient(135deg, #2d2d2d 0%, #3d3d3d 100%);
            border-radius: 10px;
            padding: 15px;
            margin: 5px;
            border: 1px solid #444;
        }
        .heatmap-cell { border-radius: 5px; padding: 10px; text-align: center; }
        </style>
        """
    else:
        return """
        <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 2rem;
        }
        .event-card {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem 0;
            background-color: #f9f9f9;
        }
        .priority-critical { color: #d32f2f; font-weight: bold; }
        .priority-high { color: #f57c00; font-weight: bold; }
        .priority-medium { color: #fbc02d; font-weight: bold; }
        .priority-low { color: #388e3c; font-weight: bold; }
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
            padding: 15px;
            margin: 5px;
            color: white;
        }
        .heatmap-cell { border-radius: 5px; padding: 10px; text-align: center; }
        </style>
        """

st.markdown(get_css(), unsafe_allow_html=True)

# Plotly availability helper
def plotly_enabled() -> bool:
    return bool(PLOTLY_AVAILABLE and px is not None and go is not None)

# ============ ADVANCED FEATURE FUNCTIONS ============

def estimate_downtime_cost(events: List[Dict]) -> Dict[str, Any]:
    """Estimate downtime and cost impact based on events"""
    # Cost estimates per severity (in USD per hour of downtime)
    HOURLY_COST = 500  # Average production line cost per hour
    DOWNTIME_HOURS = {
        "critical": 4.0,  # Critical issues take ~4 hours to fix
        "high": 2.0,      # High severity ~2 hours
        "med": 1.0,       # Medium ~1 hour
        "low": 0.25       # Low ~15 minutes
    }
    
    total_downtime = 0
    total_cost = 0
    by_severity = {"critical": 0, "high": 0, "med": 0, "low": 0}
    
    for event in events:
        severity = event.get("severity", "low")
        downtime = DOWNTIME_HOURS.get(severity, 0.25)
        total_downtime += downtime
        total_cost += downtime * HOURLY_COST
        by_severity[severity] = by_severity.get(severity, 0) + 1
    
    return {
        "total_downtime_hours": round(total_downtime, 1),
        "total_cost_usd": round(total_cost, 2),
        "hourly_rate": HOURLY_COST,
        "events_by_severity": by_severity,
        "avg_downtime_per_event": round(total_downtime / max(len(events), 1), 2)
    }

def analyze_trends(events: List[Dict]) -> Dict[str, Any]:
    """Analyze trends over time"""
    if not events:
        return {"trend": "no_data", "change_percent": 0}
    
    # Parse timestamps and group by day
    daily_counts = {}
    severity_over_time = []
    
    for event in events:
        ts = event.get("timestamp", "")
        try:
            dt = pd.to_datetime(ts)
            day = dt.strftime("%Y-%m-%d")
            daily_counts[day] = daily_counts.get(day, 0) + 1
            severity_over_time.append({
                "date": dt,
                "severity": event.get("severity", "low"),
                "score": {"critical": 4, "high": 3, "med": 2, "low": 1}.get(event.get("severity", "low"), 1)
            })
        except:
            continue
    
    if len(daily_counts) < 2:
        return {"trend": "insufficient_data", "change_percent": 0, "daily_counts": daily_counts}
    
    # Calculate trend (comparing first half vs second half)
    sorted_days = sorted(daily_counts.keys())
    mid = len(sorted_days) // 2
    first_half_avg = sum(daily_counts[d] for d in sorted_days[:mid]) / max(mid, 1)
    second_half_avg = sum(daily_counts[d] for d in sorted_days[mid:]) / max(len(sorted_days) - mid, 1)
    
    if first_half_avg == 0:
        change_percent = 100 if second_half_avg > 0 else 0
    else:
        change_percent = ((second_half_avg - first_half_avg) / first_half_avg) * 100
    
    if change_percent > 10:
        trend = "increasing"
    elif change_percent < -10:
        trend = "decreasing"
    else:
        trend = "stable"
    
    return {
        "trend": trend,
        "change_percent": round(change_percent, 1),
        "daily_counts": daily_counts,
        "first_half_avg": round(first_half_avg, 2),
        "second_half_avg": round(second_half_avg, 2),
        "severity_timeline": severity_over_time
    }

def get_joint_heatmap_data(events: List[Dict]) -> Dict[str, Dict]:
    """Get data for joint risk heatmap"""
    joints = ["J1", "J2", "J3", "J4", "J5", "J6", "UNKNOWN"]
    severities = ["critical", "high", "med", "low"]
    
    heatmap = {joint: {sev: 0 for sev in severities} for joint in joints}
    joint_totals = {joint: 0 for joint in joints}
    
    for event in events:
        joint = event.get("joint", "UNKNOWN")
        if joint not in joints:
            joint = "UNKNOWN"
        severity = event.get("severity", "low")
        if severity not in severities:
            severity = "low"
        heatmap[joint][severity] += 1
        joint_totals[joint] += 1
    
    # Calculate risk score per joint (weighted by severity)
    weights = {"critical": 4, "high": 3, "med": 2, "low": 1}
    risk_scores = {}
    for joint in joints:
        score = sum(heatmap[joint][sev] * weights[sev] for sev in severities)
        risk_scores[joint] = score
    
    return {
        "heatmap": heatmap,
        "totals": joint_totals,
        "risk_scores": risk_scores,
        "highest_risk_joint": max(risk_scores, key=risk_scores.get) if risk_scores else "N/A"
    }

def export_to_csv(events: List[Dict]) -> str:
    """Export events to CSV format"""
    if not events:
        return ""
    
    df = pd.DataFrame(events)
    # Select and order important columns
    columns = ["event_id", "timestamp", "event_type", "severity", "joint", 
               "force_value", "description", "recurrence_count", "triage_score", "priority"]
    available_cols = [c for c in columns if c in df.columns]
    df = df[available_cols]
    
    return df.to_csv(index=False)

def generate_pdf_report(event: Dict, triage_result: Dict) -> str:
    """Generate HTML report that can be printed as PDF"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    event_id = event.get("event_id", "Unknown")
    severity = event.get("severity", "Unknown")
    score = triage_result.get("triage_score", 0)
    priority = triage_result.get("priority", "Unknown")
    
    maintenance_report = triage_result.get("maintenance_report", {})
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>FANUC FirstResponder - Triage Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; color: #333; }}
            .header {{ background: linear-gradient(135deg, #1f77b4 0%, #2e86ab 100%); 
                      color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
            .header h1 {{ margin: 0; }}
            .section {{ background: #f9f9f9; padding: 15px; margin: 10px 0; border-radius: 8px; 
                       border-left: 4px solid #1f77b4; }}
            .section h3 {{ color: #1f77b4; margin-top: 0; }}
            .metric {{ display: inline-block; background: #e3f2fd; padding: 10px 20px; 
                      margin: 5px; border-radius: 5px; }}
            .critical {{ color: #d32f2f; }}
            .high {{ color: #f57c00; }}
            .medium {{ color: #fbc02d; }}
            .low {{ color: #388e3c; }}
            table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background: #1f77b4; color: white; }}
            .footer {{ text-align: center; margin-top: 30px; color: #888; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🤖 FANUC FirstResponder</h1>
            <p>Maintenance Triage Report</p>
        </div>
        
        <div class="section">
            <h3>📋 Event Summary</h3>
            <table>
                <tr><th>Field</th><th>Value</th></tr>
                <tr><td>Event ID</td><td>{event_id}</td></tr>
                <tr><td>Timestamp</td><td>{event.get('timestamp', 'N/A')}</td></tr>
                <tr><td>Event Type</td><td>{event.get('event_type', 'N/A')}</td></tr>
                <tr><td>Severity</td><td class="{severity}">{severity.upper()}</td></tr>
                <tr><td>Joint</td><td>{event.get('joint', 'N/A')}</td></tr>
                <tr><td>Force Value</td><td>{event.get('force_value', 'N/A')}N</td></tr>
                <tr><td>Recurrence Count</td><td>{event.get('recurrence_count', 0)}</td></tr>
            </table>
        </div>
        
        <div class="section">
            <h3>🎯 Triage Results</h3>
            <div class="metric"><strong>Score:</strong> {score}/100</div>
            <div class="metric"><strong>Priority:</strong> <span class="{priority.lower()}">{priority}</span></div>
        </div>
        
        <div class="section">
            <h3>1. 🔍 Diagnose Cause</h3>
            <p>{maintenance_report.get('diagnose_cause', 'N/A')}</p>
        </div>
        
        <div class="section">
            <h3>2. 📝 Inspection Procedure</h3>
            <p>{maintenance_report.get('inspection_procedure', 'N/A')}</p>
        </div>
        
        <div class="section">
            <h3>3. 🔧 Required Maintenance</h3>
            <p>{maintenance_report.get('maintenance_actions', 'N/A')}</p>
        </div>
        
        <div class="section">
            <h3>4. ⚠️ Safety Clearance</h3>
            <p>{maintenance_report.get('safety_clearance', 'N/A')}</p>
        </div>
        
        <div class="section">
            <h3>5. ✅ Return-to-Service</h3>
            <p>{maintenance_report.get('return_to_service', 'N/A')}</p>
        </div>
        
        <div class="footer">
            <p>Generated by FANUC FirstResponder | {timestamp}</p>
            <p>This report is for maintenance reference only. Always follow official FANUC procedures.</p>
        </div>
    </body>
    </html>
    """
    return html

def get_download_link(content: str, filename: str, link_text: str, mime_type: str = "text/plain") -> str:
    """Generate a download link for content"""
    b64 = base64.b64encode(content.encode()).decode()
    return f'<a href="data:{mime_type};base64,{b64}" download="{filename}">{link_text}</a>'

# ============ END ADVANCED FEATURES ============


def check_api_connection() -> bool:
    """Check if API is available"""
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        if response.status_code == 200:
            return True
        return False
    except requests.exceptions.ConnectionError:
        return False
    except requests.exceptions.Timeout:
        return False
    except Exception as e:
        # Log other errors but don't crash
        return False


def upload_file(file) -> Dict[str, Any]:
    """Upload file to API"""
    try:
        files = {"file": (file.name, file.getvalue(), file.type)}
        data = {"file_type": "auto"}
        response = requests.post(
            f"{API_BASE_URL}/api/etl/process",
            files=files,
            data=data,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error uploading file: {str(e)}")
        return None


def get_events(limit: int = 100) -> Tuple[List[Dict[str, Any]], int]:
    """Get all events from API
    Returns: (events_list, total_count)
    """
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/events",
            params={"limit": limit},
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        events = data.get("events", [])
        total = data.get("total", len(events))
        return events, total
    except Exception as e:
        st.error(f"Error fetching events: {str(e)}")
        return [], 0


def get_event_details(event_id: str) -> Dict[str, Any]:
    """Get specific event details"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/events/{event_id}",
            timeout=5
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching event: {str(e)}")
        return None


def lookup_history(event: Dict[str, Any]) -> Dict[str, Any]:
    """Lookup similar historical events"""
    try:
        # Extract event data - handle both normalized and original_event structures
        if "original_event" in event:
            # If event has original_event nested, use that
            original = event.get("original_event", {})
            event_id = original.get("event_id") or event.get("event_id", "unknown")
            event_type = original.get("event_type") or event.get("event_type", "unknown")
            timestamp = original.get("timestamp") or event.get("timestamp", "")
            description = original.get("description") or event.get("description", "")
            raw_data = original.get("data") or event.get("raw_data") or {}
        else:
            # Use event directly
            event_id = event.get("event_id", "unknown")
            event_type = event.get("event_type", "unknown")
            timestamp = event.get("timestamp", "")
            description = event.get("description", "")
            raw_data = event.get("raw_data") or event.get("data") or {}
        
        # Build request payload matching EventRequest model
        request_payload = {
            "event_id": str(event_id),
            "event_type": str(event_type),
            "timestamp": str(timestamp),
            "description": str(description),
            "raw_data": raw_data
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/history/lookup",
            json=request_payload,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error looking up history: {str(e)}")
        return None


def score_triage(event: Dict[str, Any]) -> Dict[str, Any]:
    """Get triage score for event"""
    try:
        # Extract event data - handle both normalized and original_event structures
        if "original_event" in event:
            # If event has original_event nested, use that
            original = event.get("original_event", {})
            event_id = original.get("event_id") or event.get("event_id", "unknown")
            event_type = original.get("event_type") or event.get("event_type", "unknown")
            timestamp = original.get("timestamp") or event.get("timestamp", "")
            description = original.get("description") or event.get("description", "")
            raw_data = original.get("data") or event.get("raw_data") or {}
        else:
            # Use event directly
            event_id = event.get("event_id", "unknown")
            event_type = event.get("event_type", "unknown")
            timestamp = event.get("timestamp", "")
            description = event.get("description", "")
            raw_data = event.get("raw_data") or event.get("data") or {}
        
        # Build request payload matching EventRequest model
        request_payload = {
            "event_id": str(event_id),
            "event_type": str(event_type),
            "timestamp": str(timestamp),
            "description": str(description),
            "raw_data": raw_data
        }
        
        # Increased timeout for AI processing (Azure OpenAI can take 30-60 seconds)
        response = requests.post(
            f"{API_BASE_URL}/api/triage/score",
            json=request_payload,
            timeout=60  # Increased from 15 to 60 seconds
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        st.error("⏱️ Request timed out. The AI analysis is taking longer than expected. Please try again.")
        return None
    except requests.exceptions.ConnectionError:
        st.error("🔌 Cannot connect to backend. Please ensure the server is running.")
        return None
    except Exception as e:
        st.error(f"Error scoring triage: {str(e)}")
        return None


def get_stats() -> Dict[str, Any]:
    """Get system statistics"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/stats", timeout=5)
        response.raise_for_status()
        return response.json()
    except:
        return {}


def display_event_card(event: Dict[str, Any], show_select: bool = True, index: int = None):
    """Display event in a card format"""
    event_id = event.get("event_id", "N/A")
    record_id = event.get("record_id")  # Use record_id if available (UUID, always unique)
    event_type = event.get("event_type", "unknown")
    timestamp = event.get("timestamp", "N/A")
    description = event.get("description", "No description")
    priority = event.get("priority", "MEDIUM")
    
    priority_class = f"priority-{priority.lower()}"
    
    # Generate unique key for button
    if record_id:
        unique_key = f"select_{record_id}"
    elif event_id and event_id != "N/A":
        unique_key = f"select_{event_id}"
    elif index is not None:
        unique_key = f"select_idx_{index}"
    else:
        # Last resort: use hash of event data
        import hashlib
        event_str = str(event.get("timestamp", "")) + str(event.get("description", ""))
        unique_key = f"select_{hashlib.md5(event_str.encode()).hexdigest()[:8]}"
    
    with st.container():
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.markdown(f"**{event_type.upper()}** - {description[:100]}")
            st.caption(f"ID: {event_id} | Time: {timestamp}")
        
        with col2:
            st.markdown(f'<span class="{priority_class}">{priority}</span>', unsafe_allow_html=True)
        
        with col3:
            if show_select:
                if st.button("Select", key=unique_key):
                    # Store the full event in session state
                    st.session_state.selected_event = event.copy()
                    # Also store a flag to show it was just selected
                    st.session_state.event_just_selected = True
                    st.success(f"✅ Event selected! Go to 'Triage Analysis' page to view details.")
                    st.rerun()


def main():
    """Main application"""
    st.markdown('<div class="main-header">🤖 FANUC FirstResponder</div>', unsafe_allow_html=True)
    
    # Check API connection
    if not check_api_connection():
        st.error("⚠️ Cannot connect to API backend. Please ensure the FastAPI server is running on http://localhost:8000")
        st.info("Start the backend with: `cd backend && uvicorn main:app --reload`")
        return
    
    # Initialize session state
    if "selected_event" not in st.session_state:
        st.session_state.selected_event = None
    if "events" not in st.session_state:
        st.session_state.events = []
    
    # Sidebar
    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Select Page",
            ["Upload", "View Events", "Triage Analysis", "📊 Analytics Dashboard"],
            key="page_selector"
        )
        
        st.divider()
        
        # Statistics
        stats = get_stats()
        if stats:
            st.header("Statistics")
            st.metric("Total Events", stats.get("total_events", 0))
            
            if stats.get("by_type"):
                st.subheader("By Type")
                for event_type, count in stats.get("by_type", {}).items():
                    st.text(f"{event_type}: {count}")
        
        # Quick stats visualization in sidebar
        if st.session_state.events:
            st.divider()
            st.subheader("📊 Quick Stats")
            # Normalize events list (some APIs might return nested lists)
            events_flat = st.session_state.events
            if events_flat and isinstance(events_flat[0], list):
                tmp = []
                for item in events_flat:
                    if isinstance(item, list):
                        tmp.extend(item)
                    else:
                        tmp.append(item)
                events_flat = tmp
            # Filter only dict events
            events_flat = [e for e in events_flat if isinstance(e, dict)]
            total = len(events_flat)
            if total > 0:
                # Severity breakdown
                severity_breakdown = Counter([e.get("severity", "unknown") for e in events_flat])
                if severity_breakdown:
                    plotly_ok = PLOTLY_AVAILABLE and px is not None
                    if plotly_ok:
                        try:
                            fig_sidebar = px.pie(
                                values=list(severity_breakdown.values()),
                                names=[s.upper() for s in severity_breakdown.keys()],
                                title="Severity Overview",
                                height=200
                            )
                            st.plotly_chart(fig_sidebar, use_container_width=True)
                        except Exception:
                            plotly_ok = False
                    if not plotly_ok:
                        # Fallback: Text summary
                        for sev, count in severity_breakdown.items():
                            st.write(f"**{sev.upper()}**: {count}")
        
        # Advanced Settings
        st.divider()
        st.subheader("⚙️ Settings")
        
        # Dark Mode Toggle
        dark_mode = st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode, key="dark_mode_toggle")
        if dark_mode != st.session_state.dark_mode:
            st.session_state.dark_mode = dark_mode
            st.rerun()
        
        # Auto-refresh toggle
        if "auto_refresh" not in st.session_state:
            st.session_state.auto_refresh = False
        
        auto_refresh = st.toggle("🔄 Auto-refresh (30s)", value=st.session_state.auto_refresh, key="auto_refresh_toggle")
        if auto_refresh != st.session_state.auto_refresh:
            st.session_state.auto_refresh = auto_refresh
        
        # Cost settings
        st.divider()
        st.subheader("💰 Cost Settings")
        hourly_cost = st.number_input("Hourly Cost ($)", value=500, min_value=0, max_value=10000, step=50, key="hourly_cost_input")
    
    # Main content based on selected page
    if page == "Upload":
        st.header("📤 Upload Data Files")
        st.markdown("Upload sensor readings, error logs, alerts, or performance metrics")
        
        # Batch processing option
        st.divider()
        st.subheader("🚀 Batch Process All Datasets")
        st.markdown("Process all datasets in `Hackathon_Data` folder at once, clean them, and generate recommendations")
        
        # Option to skip AI recommendations for faster processing (default to True for speed)
        skip_ai = st.checkbox("⚡ Fast Mode: Skip AI recommendations (processes in ~1 minute)", 
                              value=True,  # Default to fast mode
                              help="✅ RECOMMENDED: Enable this to process all files quickly without AI analysis. You can still get AI recommendations for individual events later using 'Score Triage'.")
        
        st.info("💡 **Tip:** Use Fast Mode for quick processing, then get AI recommendations for specific events in 'Triage Analysis' page.")
        
        if st.button("🔄 Process All Datasets", type="primary", use_container_width=True):
            processing_msg = "Processing all datasets (with AI recommendations)..." if not skip_ai else "Processing all datasets (fast mode, no AI)..."
            estimated_time = "10-15 minutes" if not skip_ai else "1-2 minutes"
            with st.spinner(f"{processing_msg} Estimated time: {estimated_time}"):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/api/batch/process-all",
                        json={"skip_ai_recommendations": skip_ai},
                        timeout=1200 if not skip_ai else 300  # 20 minutes with AI, 5 minutes without (increased buffer)
                    )
                    response.raise_for_status()
                    result = response.json()
                    
                    # Check if there was an error
                    if result.get("status") == "error":
                        st.error(f"❌ {result.get('message', 'Batch processing failed')}")
                    else:
                        if result.get("skip_ai"):
                            st.success(f"✅ {result.get('message', 'Batch processing completed!')}")
                            st.info("💡 Tip: Use 'Score Triage' on individual events to get AI-powered recommendations.")
                        else:
                            st.success(f"✅ {result.get('message', 'Batch processing completed!')}")
                    
                    # Show summary
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Files Processed", result.get("files_processed", 0))
                    with col2:
                        st.metric("Total Events", result.get("total_events", 0))
                    with col3:
                        ai_count = result.get("events_with_ai_recommendations", 0)
                        if result.get("skip_ai"):
                            st.metric("AI Recommendations", "Skipped (Fast Mode)")
                        else:
                            st.metric("With AI Recommendations", ai_count)
                    
                    # Show file details
                    if result.get("files"):
                        with st.expander("📋 File Processing Details"):
                            files_df = pd.DataFrame(result["files"])
                            st.dataframe(files_df, use_container_width=True)
                            
                            # Show any errors
                            error_files = [f for f in result["files"] if f.get("status") == "error"]
                            if error_files:
                                st.warning(f"⚠️ {len(error_files)} file(s) had errors during processing")
                                for err_file in error_files:
                                    st.text(f"  - {err_file.get('filename')}: {err_file.get('error', 'Unknown error')}")
                    
                    # Refresh events
                    if result.get("total_events", 0) > 0:
                        st.session_state.events = get_events(limit=1000)
                        st.info("🔄 Events list refreshed! Go to 'View Events' to see all processed events.")
                    
                except requests.exceptions.Timeout:
                    if skip_ai:
                        st.error("⏱️ Batch processing timed out even in Fast Mode. This might indicate a backend issue.")
                        st.info("🔧 **Troubleshooting:**\n1. Check if backend is running\n2. Restart backend: `./start_backend.sh`\n3. Check backend logs for errors\n4. Try processing files individually")
                    else:
                        st.error("⏱️ Batch processing timed out. The AI recommendations take a long time.")
                        st.info("💡 **Solution:** Enable 'Fast Mode' checkbox above for quick processing (~1 minute), then use 'Score Triage' for individual AI recommendations.")
                except requests.exceptions.HTTPError as e:
                    st.error(f"HTTP Error: {str(e)}")
                    try:
                        error_detail = response.json()
                        st.json(error_detail)
                    except:
                        pass
                except Exception as e:
                    st.error(f"Error in batch processing: {str(e)}")
        
        st.divider()
        st.subheader("📁 Individual File Upload")
        
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["csv", "txt"],
            help="Supported formats: CSV (sensor data, metrics), TXT (alerts, errors, maintenance notes)"
        )
        
        if uploaded_file is not None:
            st.info(f"📄 File: {uploaded_file.name} ({uploaded_file.size} bytes)")
            
            if st.button("Process File", type="primary"):
                with st.spinner("Processing file..."):
                    result = upload_file(uploaded_file)
                    
                    if result:
                        st.success(f"✅ Processed {result.get('events_processed', 0)} events")
                        
                        # Show preview
                        if result.get("events"):
                            st.subheader("Preview of Processed Events")
                            events_list = result["events"][:10]
                            
                            # Flatten nested original_event for better display
                            flattened_events = []
                            for event in events_list:
                                flat_event = event.copy()
                                # Convert original_event dict to string for display
                                if "original_event" in flat_event and isinstance(flat_event["original_event"], dict):
                                    flat_event["original_event"] = str(flat_event["original_event"])[:100] + "..." if len(str(flat_event["original_event"])) > 100 else str(flat_event["original_event"])
                                flattened_events.append(flat_event)
                            
                            preview_df = pd.DataFrame(flattened_events)
                            st.dataframe(preview_df, use_container_width=True)
                            
                            # Also show summary
                            st.info(f"📊 Showing {len(events_list)} of {result.get('events_processed', 0)} processed events")
                            
                            # Refresh events list
                            events_list, total_count = get_events()
                            st.session_state.events = events_list
                            st.session_state.total_events_count = total_count
    
    elif page == "View Events":
        st.header("📋 View Events")
        
        # Normalize events list (flatten nested lists, keep only dicts)
        events_flat = st.session_state.events
        if events_flat and isinstance(events_flat[0], list):
            tmp = []
            for item in events_flat:
                if isinstance(item, list):
                    tmp.extend(item)
                else:
                    tmp.append(item)
            events_flat = tmp
        events_flat = [e for e in events_flat if isinstance(e, dict)]
        st.session_state.events = events_flat
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            event_type_filter = st.selectbox(
                "Filter by Type",
                ["All"] + list(set(e.get("event_type") for e in events_flat if isinstance(e, dict) and e.get("event_type"))),
                key="type_filter"
            )
        with col2:
            # Initialize last_limit if not set
            if 'last_limit' not in st.session_state:
                st.session_state.last_limit = 100
            
            def reload_events():
                """Callback to reload events when limit changes"""
                events_list, total_count = get_events(limit=st.session_state.max_events_limit)
                st.session_state.events = events_list
                st.session_state.total_events_count = total_count
                st.session_state.last_limit = st.session_state.max_events_limit
            
            limit = st.number_input(
                "Max Events", 
                min_value=10, 
                max_value=1000, 
                value=st.session_state.get('last_limit', 100), 
                step=10, 
                key="max_events_limit",
                on_change=reload_events
            )
        with col3:
            if st.button("🔄 Refresh Events"):
                events_list, total_count = get_events(limit=limit)
                st.session_state.events = events_list
                st.session_state.total_events_count = total_count
                st.session_state.last_limit = limit
                st.rerun()
        
        # Load events if not loaded or if limit changed
        if not st.session_state.events or st.session_state.get('last_limit', limit) != limit:
            with st.spinner("Loading events..."):
                events_list, total_count = get_events(limit=limit)
                st.session_state.events = events_list
                st.session_state.total_events_count = total_count
                st.session_state.last_limit = limit
        
        # Filter events
        filtered_events = st.session_state.events
        if event_type_filter != "All":
            filtered_events = [e for e in filtered_events if e.get("event_type") == event_type_filter]
        
        # Sort by severity (optional)
        sort_col1, _, _ = st.columns(3)
        with sort_col1:
            sort_choice = st.selectbox(
                "Sort by",
                ["None", "Severity (Critical→Low)", "Severity (Low→Critical)"],
                key="sort_events_by"
            )
        if sort_choice != "None":
            severity_rank = {
                "critical": 4,
                "high": 3,
                "med": 2,
                "medium": 2,
                "low": 1,
                "unknown": 0,
                None: 0,
                "": 0
            }
            reverse = sort_choice == "Severity (Critical→Low)"
            filtered_events = sorted(
                filtered_events,
                key=lambda e: severity_rank.get(str(e.get("severity", "")).lower(), 0),
                reverse=reverse
            )
        
        # Get actual total (not filtered count)
        actual_total = st.session_state.get('total_events_count', len(filtered_events))
        
        # Statistics visualization
        if filtered_events:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Events", actual_total, delta=f"{len(filtered_events)} shown")
            with col2:
                critical_count = len([e for e in filtered_events if e.get("severity") == "critical"])
                st.metric("Critical", critical_count, delta=None)
            with col3:
                high_count = len([e for e in filtered_events if e.get("severity") == "high"])
                st.metric("High", high_count, delta=None)
            with col4:
                avg_recurrence = sum([e.get("recurrence_count", 0) for e in filtered_events]) / len(filtered_events) if filtered_events else 0
                st.metric("Avg Recurrence", f"{avg_recurrence:.1f}", delta=None)
            
            # Interactive Visualizations
            if len(filtered_events) > 0:
                severity_counts = {}
                for event in filtered_events:
                    sev = event.get("severity", "unknown")
                    severity_counts[sev] = severity_counts.get(sev, 0) + 1
                
                with st.expander("📊 Visualizations", expanded=True):
                    tab1, tab2, tab3, tab4 = st.tabs(["Severity Distribution", "Event Types", "Timeline", "Triage Scores"])
                    
                    # Tab 1: Severity Distribution
                    with tab1:
                        if severity_counts:
                            if PLOTLY_AVAILABLE:
                                # Create pie chart
                                fig_severity = px.pie(
                                    values=list(severity_counts.values()),
                                    names=[s.upper() for s in severity_counts.keys()],
                                    title="Events by Severity",
                                    color_discrete_map={
                                        'CRITICAL': '#FF0000',
                                        'HIGH': '#FF8800',
                                        'MED': '#FFAA00',
                                        'MEDIUM': '#FFAA00',
                                        'LOW': '#00AA00',
                                        'UNKNOWN': '#888888'
                                    }
                                )
                                fig_severity.update_traces(textposition='inside', textinfo='percent+label')
                                st.plotly_chart(fig_severity, use_container_width=True)
                                
                                # Also show bar chart
                                fig_severity_bar = px.bar(
                                    x=[s.upper() for s in severity_counts.keys()],
                                    y=list(severity_counts.values()),
                                    title="Severity Count",
                                    labels={'x': 'Severity', 'y': 'Count'},
                                    color=[s.upper() for s in severity_counts.keys()],
                                    color_discrete_map={
                                        'CRITICAL': '#FF0000',
                                        'HIGH': '#FF8800',
                                        'MED': '#FFAA00',
                                        'MEDIUM': '#FFAA00',
                                        'LOW': '#00AA00',
                                        'UNKNOWN': '#888888'
                                    }
                                )
                                st.plotly_chart(fig_severity_bar, use_container_width=True)
                            else:
                                # Fallback: Text-based visualization
                                st.markdown("**Severity Distribution**")
                                st.info("💡 Install Plotly for interactive charts: `pip install plotly==5.18.0`")
                                for severity, count in sorted(severity_counts.items(), key=lambda x: x[1], reverse=True):
                                    percentage = (count / len(filtered_events)) * 100
                                    bar_length = int(percentage / 2)
                                    st.markdown(f"**{severity.upper()}**: `{'█' * bar_length}{'░' * (50 - bar_length)}` {count} ({percentage:.1f}%)")
                    
                    # Tab 2: Event Types
                    with tab2:
                        event_type_counts = {}
                        for event in filtered_events:
                            etype = event.get("event_type", "unknown")
                            event_type_counts[etype] = event_type_counts.get(etype, 0) + 1
                        
                        if event_type_counts:
                            if PLOTLY_AVAILABLE:
                                fig_types = px.bar(
                                    x=list(event_type_counts.keys()),
                                    y=list(event_type_counts.values()),
                                    title="Events by Type",
                                    labels={'x': 'Event Type', 'y': 'Count'},
                                    color=list(event_type_counts.values()),
                                    color_continuous_scale='Viridis'
                                )
                                fig_types.update_xaxes(tickangle=-45)
                                st.plotly_chart(fig_types, use_container_width=True)
                            else:
                                # Fallback: Text-based
                                st.markdown("**Events by Type**")
                                for etype, count in sorted(event_type_counts.items(), key=lambda x: x[1], reverse=True):
                                    percentage = (count / len(filtered_events)) * 100
                                    st.write(f"**{etype}**: {count} ({percentage:.1f}%)")
                    
                    # Tab 3: Timeline
                    with tab3:
                        # Extract timestamps and create timeline
                        timeline_data = []
                        for event in filtered_events:
                            ts = event.get("timestamp", "")
                            if ts:
                                try:
                                    # Parse ISO 8601 timestamp
                                    dt = pd.to_datetime(ts)
                                    timeline_data.append({
                                        'timestamp': dt,
                                        'severity': event.get("severity", "unknown"),
                                        'event_type': event.get("event_type", "unknown")
                                    })
                                except:
                                    pass
                        
                        if timeline_data:
                            df_timeline = pd.DataFrame(timeline_data)
                            df_timeline = df_timeline.sort_values('timestamp')
                            
                            if PLOTLY_AVAILABLE:
                                # Create timeline scatter plot
                                fig_timeline = px.scatter(
                                    df_timeline,
                                    x='timestamp',
                                    y='severity',
                                    color='severity',
                                    size=[10]*len(df_timeline),
                                    title="Event Timeline",
                                    labels={'timestamp': 'Time', 'severity': 'Severity'},
                                    color_discrete_map={
                                        'critical': '#FF0000',
                                        'high': '#FF8800',
                                        'med': '#FFAA00',
                                        'medium': '#FFAA00',
                                        'low': '#00AA00'
                                    }
                                )
                                fig_timeline.update_layout(height=400)
                                st.plotly_chart(fig_timeline, use_container_width=True)
                            else:
                                # Fallback: Show timeline as table
                                st.markdown("**Event Timeline**")
                                st.dataframe(df_timeline[['timestamp', 'severity', 'event_type']].head(20), use_container_width=True)
                        else:
                            st.info("No valid timestamps found for timeline visualization")
                    
                    # Tab 4: Triage Scores
                    with tab4:
                        scores = []
                        for event in filtered_events:
                            score = event.get("triage_score")
                            if score is not None:
                                scores.append(score)
                        
                        if scores:
                            plotly_ok = plotly_enabled()
                            if plotly_ok:
                                try:
                                    fig_scores = px.histogram(
                                        x=scores,
                                        nbins=20,
                                        title="Triage Score Distribution",
                                        labels={'x': 'Triage Score', 'y': 'Count'},
                                        color_discrete_sequence=['#1f77b4']
                                    )
                                    fig_scores.add_vline(x=80, line_dash="dash", line_color="red", annotation_text="Critical Threshold")
                                    fig_scores.add_vline(x=60, line_dash="dash", line_color="orange", annotation_text="High Threshold")
                                    st.plotly_chart(fig_scores, use_container_width=True)
                                except Exception:
                                    plotly_ok = False
                            if not plotly_ok:
                                # Fallback: Show score distribution as text
                                st.markdown("**Triage Score Distribution**")
                                score_ranges = {'0-20': 0, '21-40': 0, '41-60': 0, '61-80': 0, '81-100': 0}
                                for score_val in scores:
                                    if score_val <= 20:
                                        score_ranges['0-20'] += 1
                                    elif score_val <= 40:
                                        score_ranges['21-40'] += 1
                                    elif score_val <= 60:
                                        score_ranges['41-60'] += 1
                                    elif score_val <= 80:
                                        score_ranges['61-80'] += 1
                                    else:
                                        score_ranges['81-100'] += 1
                                
                                for range_name, count in score_ranges.items():
                                    if count > 0:
                                        bar_length = int((count / len(scores)) * 50)
                                        st.markdown(f"**{range_name}**: `{'█' * bar_length}{'░' * (50 - bar_length)}` {count}")
                            
                            # Score statistics
                            col_a, col_b, col_c = st.columns(3)
                            with col_a:
                                st.metric("Average Score", f"{sum(scores)/len(scores):.1f}")
                            with col_b:
                                st.metric("Min Score", f"{min(scores):.1f}")
                            with col_c:
                                st.metric("Max Score", f"{max(scores):.1f}")
                        else:
                            st.info("No triage scores available. Score some events first!")
        
        st.info(f"Showing {len(filtered_events)} events")
        
        # Display events
        if filtered_events:
            for idx, event in enumerate(filtered_events):
                display_event_card(event, show_select=True, index=idx)
        else:
            st.info("No events found. Upload some data files first!")
    
    elif page == "Triage Analysis":
        st.header("🎯 Triage Analysis")
        
        # Event selection
        if st.session_state.selected_event:
            event = st.session_state.selected_event
            # Get event_id from either top level or original_event
            event_id = event.get('event_id') or event.get('original_event', {}).get('event_id') or event.get('record_id', 'Unknown')
            st.success(f"✅ Selected Event: {event_id}")
            
            # Clear the "just selected" flag
            if st.session_state.get('event_just_selected', False):
                st.session_state.event_just_selected = False
            
            # Display event details
            with st.expander("Event Details", expanded=True):
                st.json(event)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔍 Lookup History", type="primary"):
                    with st.spinner("Finding similar events..."):
                        history_result = lookup_history(event)
                        if history_result:
                            st.subheader("Similar Historical Events")
                            similar_count = history_result.get("similar_events_count", 0)
                            st.metric("Similar Events Found", similar_count)
                            
                            similar_events = history_result.get("similar_events", [])
                            if similar_events:
                                for similar in similar_events[:5]:
                                    with st.container():
                                        st.markdown(f"**{similar.get('description', 'N/A')}**")
                                        st.caption(f"Similarity: {similar.get('similarity_score', 0):.2%} | Type: {similar.get('event_type')}")
                                        st.divider()
            
            with col2:
                if st.button("📊 Score Triage", type="primary"):
                    with st.spinner("Analyzing event with AI..."):
                        triage_result = score_triage(event)
                        if triage_result:
                            st.subheader("Triage Results")
                            
                            # Score visualization with charts
                            score = triage_result.get("triage_score", 0)
                            priority = triage_result.get("priority", "MEDIUM")
                            
                            col_a, col_b, col_c = st.columns(3)
                            with col_a:
                                st.metric("Triage Score", f"{score:.1f}/100")
                            with col_b:
                                priority_class = f"priority-{priority.lower()}"
                                st.markdown(f'<span class="{priority_class}" style="font-size: 1.5rem;">{priority}</span>', unsafe_allow_html=True)
                            with col_c:
                                # Show cache indicator if cached
                                if triage_result.get("cached"):
                                    st.info("⚡ Cached Response")
                            
                            # Progress bar for score with color coding
                            if score >= 80:
                                st.progress(score / 100)
                                st.caption("🔴 Critical Priority")
                            elif score >= 60:
                                st.progress(score / 100)
                                st.caption("🟠 High Priority")
                            elif score >= 40:
                                st.progress(score / 100)
                                st.caption("🟡 Medium Priority")
                            else:
                                st.progress(score / 100)
                                st.caption("🟢 Low Priority")
                            
                            # Score breakdown visualization
                            with st.expander("📊 Score Breakdown & Visualizations", expanded=False):
                                tab1, tab2, tab3 = st.tabs(["Score Analysis", "Event Details", "Comparison"])
                                
                                with tab1:
                                    if PLOTLY_AVAILABLE:
                                        # Score gauge chart
                                        fig_gauge = go.Figure(go.Indicator(
                                            mode="gauge+number+delta",
                                            value=score,
                                            domain={'x': [0, 1], 'y': [0, 1]},
                                            title={'text': "Triage Score"},
                                            delta={'reference': 50},
                                            gauge={
                                                'axis': {'range': [None, 100]},
                                                'bar': {'color': "darkblue"},
                                                'steps': [
                                                    {'range': [0, 40], 'color': "lightgray"},
                                                    {'range': [40, 60], 'color': "yellow"},
                                                    {'range': [60, 80], 'color': "orange"},
                                                    {'range': [80, 100], 'color': "red"}
                                                ],
                                                'threshold': {
                                                    'line': {'color': "red", 'width': 4},
                                                    'thickness': 0.75,
                                                    'value': 80
                                                }
                                            }
                                        ))
                                        fig_gauge.update_layout(height=300)
                                        st.plotly_chart(fig_gauge, use_container_width=True)
                                        
                                        # Score breakdown factors
                                        event = st.session_state.selected_event
                                        factors = {
                                            'Base Score': score * 0.4,
                                            'Severity': 20 if event.get('severity') == 'critical' else 10 if event.get('severity') == 'high' else 5,
                                            'Recurrence': min(event.get('recurrence_count', 0) * 0.1, 30),
                                            'Force Value': min((event.get('force_value') or 0) / 50, 20)
                                        }
                                        
                                        fig_factors = px.bar(
                                            x=list(factors.keys()),
                                            y=list(factors.values()),
                                            title="Score Contribution Factors",
                                            labels={'x': 'Factor', 'y': 'Points'},
                                            color=list(factors.values()),
                                            color_continuous_scale='RdYlGn_r'
                                        )
                                        st.plotly_chart(fig_factors, use_container_width=True)
                                    else:
                                        # Fallback: Text-based score breakdown
                                        st.markdown(f"**Triage Score: {score:.1f}/100**")
                                        event = st.session_state.selected_event
                                        st.write(f"Severity: **{event.get('severity', 'N/A')}**")
                                        st.write(f"Recurrence: **{event.get('recurrence_count', 0)}** times")
                                        if event.get('force_value'):
                                            st.write(f"Force: **{event.get('force_value')}N**")
                                
                                with tab2:
                                    event = st.session_state.selected_event
                                    
                                    # Event characteristics visualization
                                    characteristics = {
                                        'Severity': event.get('severity', 'N/A'),
                                        'Recurrence': event.get('recurrence_count', 0),
                                        'Joint': event.get('joint', 'N/A'),
                                        'Force': event.get('force_value') or 0
                                    }
                                    
                                    st.markdown("**Event Characteristics**")
                                    for key, value in characteristics.items():
                                        st.write(f"{key}: **{value}**")
                                    
                                    # Force value visualization if available
                                    if event.get('force_value'):
                                        force = event.get('force_value')
                                        plotly_ok = plotly_enabled()
                                        if plotly_ok:
                                            try:
                                                fig_force = go.Figure(go.Indicator(
                                                    mode="gauge+number",
                                                    value=force,
                                                    domain={'x': [0, 1], 'y': [0, 1]},
                                                    title={'text': "Force Value (N)"},
                                                    gauge={
                                                        'axis': {'range': [None, 10000]},
                                                        'bar': {'color': "darkgreen"},
                                                        'steps': [
                                                            {'range': [0, 300], 'color': "lightgreen"},
                                                            {'range': [300, 600], 'color': "yellow"},
                                                            {'range': [600, 10000], 'color': "red"}
                                                        ],
                                                        'threshold': {
                                                            'line': {'color': "red", 'width': 4},
                                                            'thickness': 0.75,
                                                            'value': 600
                                                        }
                                                    }
                                                ))
                                                fig_force.update_layout(height=300)
                                                st.plotly_chart(fig_force, use_container_width=True)
                                            except Exception:
                                                plotly_ok = False
                                        if not plotly_ok:
                                            st.metric("Force Value", f"{force}N")
                                
                                with tab3:
                                    # Compare with similar events
                                    similar_events = triage_result.get("similar_events", [])
                                    if similar_events:
                                        similar_scores = [e.get('triage_score', 0) for e in similar_events[:5] if e.get('triage_score')]
                                        if similar_scores:
                                            if PLOTLY_AVAILABLE:
                                                fig_compare = px.box(
                                                    y=[score] + similar_scores,
                                                    title="Score Comparison with Similar Events",
                                                    labels={'y': 'Triage Score'},
                                                    points='all'
                                                )
                                                fig_compare.add_hline(y=score, line_dash="dash", line_color="blue", annotation_text="Current Event")
                                                st.plotly_chart(fig_compare, use_container_width=True)
                                            else:
                                                # Fallback: Text comparison
                                                st.markdown(f"**Current Event Score: {score:.1f}**")
                                                st.markdown("**Similar Events Scores:**")
                                                for i, s in enumerate(similar_scores, 1):
                                                    st.write(f"{i}. {s:.1f}")
                                        else:
                                            st.info("Similar events don't have scores yet")
                                    else:
                                        st.info("No similar events found for comparison")
                            
                            # Recommendation
                            st.subheader("Recommendation")
                            st.info(triage_result.get("recommendation", "No recommendation available"))
                            
                            # Analysis
                            st.subheader("AI Analysis")
                            st.write(triage_result.get("analysis", "No analysis available"))
                            
                            # Token usage (if available)
                            ai_metadata = triage_result.get("ai_metadata", {})
                            token_usage = ai_metadata.get("token_usage", {})
                            if token_usage:
                                with st.expander("Token Usage"):
                                    st.json(token_usage)
                            
                            # Similar events from triage
                            similar_events = triage_result.get("similar_events", [])
                            if similar_events:
                                st.subheader("Related Events")
                                for similar in similar_events:
                                    st.caption(f"{similar.get('description', 'N/A')} (Similarity: {similar.get('similarity_score', 0):.2%})")
                            
                            # Export options
                            st.divider()
                            st.subheader("📥 Export Report")
                            col_exp1, col_exp2 = st.columns(2)
                            with col_exp1:
                                # PDF Report
                                pdf_html = generate_pdf_report(event, triage_result)
                                st.markdown(
                                    get_download_link(pdf_html, "triage_report.html", "📄 Download HTML Report", "text/html"),
                                    unsafe_allow_html=True
                                )
                                st.caption("Open in browser and Print to PDF")
                            with col_exp2:
                                # JSON Export
                                report_json = json.dumps({
                                    "event": event,
                                    "triage_result": triage_result,
                                    "generated_at": datetime.now().isoformat()
                                }, indent=2, default=str)
                                st.markdown(
                                    get_download_link(report_json, "triage_report.json", "📋 Download JSON", "application/json"),
                                    unsafe_allow_html=True
                                )
        else:
            st.info("👆 Please select an event from the 'View Events' page to perform triage analysis")
            
            # Quick event selection
            st.subheader("Or select from recent events:")
            recent_events, _ = get_events(limit=10)
            if recent_events:
                for idx, event in enumerate(recent_events[:5]):
                    event_id = event.get('event_id') or f"event_{idx}"
                    if st.button(f"Select: {event.get('description', 'N/A')[:50]}", key=f"quick_select_{event_id}_{idx}"):
                        st.session_state.selected_event = event
                        st.rerun()
    
    # ============ ANALYTICS DASHBOARD ============
    elif page == "📊 Analytics Dashboard":
        st.header("📊 Analytics Dashboard")
        st.markdown("Advanced analytics, trends, and insights from your robot data")
        
        # Get all events for analysis
        all_events, total = get_events(limit=1000)
        
        if not all_events:
            st.warning("No events available. Upload some data first!")
        else:
            # Key Metrics Row
            st.subheader("📈 Key Metrics")
            col1, col2, col3 = st.columns(3)
            
            # Cost estimation
            cost_data = estimate_downtime_cost(all_events)
            trend_data = analyze_trends(all_events)
            
            with col1:
                st.metric(
                    "Total Events",
                    total,
                    delta=f"{len(all_events)} analyzed"
                )
            with col2:
                st.metric(
                    "Est. Downtime",
                    f"{cost_data['total_downtime_hours']}h",
                    delta=f"${cost_data['total_cost_usd']:,.0f} impact"
                )
            with col3:
                trend_emoji = "📈" if trend_data['trend'] == 'increasing' else "📉" if trend_data['trend'] == 'decreasing' else "➡️"
                st.metric(
                    "Trend",
                    f"{trend_emoji} {trend_data['trend'].title()}",
                    delta=f"{trend_data['change_percent']:+.1f}%"
                )
            
            st.divider()
            
            # Tabs for different analytics (heatmap removed due to sparse joint data)
            tab1, tab2, tab3, tab4 = st.tabs([
                "📈 Trend Analysis", 
                "💰 Cost Impact",
                "🔍 Advanced Filters",
                "📥 Export Data"
            ])
            
            with tab1:
                st.subheader("📈 Trend Analysis")
                st.markdown("Track how issues are changing over time")
                
                # Trend summary
                trend_color = "red" if trend_data['trend'] == 'increasing' else "green" if trend_data['trend'] == 'decreasing' else "gray"
                st.markdown(f"""
                <div style="background-color: {trend_color}; color: white; padding: 20px; border-radius: 10px; text-align: center;">
                    <h2>Issues are {trend_data['trend'].upper()}</h2>
                    <p>Change: {trend_data['change_percent']:+.1f}%</p>
                    <p>First half avg: {trend_data.get('first_half_avg', 'N/A')} events/day</p>
                    <p>Second half avg: {trend_data.get('second_half_avg', 'N/A')} events/day</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Daily counts chart
                if trend_data.get('daily_counts'):
                    st.subheader("Events per Day")
                    daily_df = pd.DataFrame([
                        {"Date": date, "Events": count}
                        for date, count in sorted(trend_data['daily_counts'].items())
                    ])
                    st.bar_chart(daily_df.set_index("Date"))
                
                # Severity over time
                st.subheader("Severity Breakdown Over Time")
                severity_counts = Counter([e.get("severity", "unknown") for e in all_events])
                for sev, count in sorted(severity_counts.items(), key=lambda x: {"critical": 0, "high": 1, "med": 2, "low": 3}.get(x[0], 4)):
                    pct = (count / len(all_events)) * 100
                    st.write(f"**{sev.upper()}**: {count} ({pct:.1f}%)")
            
            with tab2:
                st.subheader("💰 Cost & Impact Analysis")
                st.markdown("Estimated downtime and cost impact based on event severity")
                
                # Cost summary
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Estimated Downtime", f"{cost_data['total_downtime_hours']} hours")
                with col2:
                    st.metric("Total Cost Impact", f"${cost_data['total_cost_usd']:,.2f}")
                with col3:
                    st.metric("Avg per Event", f"{cost_data['avg_downtime_per_event']}h")
                
                # Cost breakdown by severity
                st.subheader("Cost Breakdown by Severity")
                severity_costs = {
                    "Critical": cost_data['events_by_severity'].get('critical', 0) * 4 * 500,
                    "High": cost_data['events_by_severity'].get('high', 0) * 2 * 500,
                    "Medium": cost_data['events_by_severity'].get('med', 0) * 1 * 500,
                    "Low": cost_data['events_by_severity'].get('low', 0) * 0.25 * 500
                }
                
                for severity, cost in severity_costs.items():
                    count = cost_data['events_by_severity'].get(severity.lower() if severity != "Medium" else "med", 0)
                    st.write(f"**{severity}**: {count} events → **${cost:,.2f}**")
                
                # ROI calculation
                st.subheader("💡 Potential Savings")
                st.info(f"""
                **If you prevent just 10% of critical issues:**
                - Downtime saved: ~{cost_data['events_by_severity'].get('critical', 0) * 0.1 * 4:.1f} hours
                - Cost saved: ~${cost_data['events_by_severity'].get('critical', 0) * 0.1 * 4 * 500:,.0f}
                
                **Predictive maintenance can reduce unplanned downtime by 30-50%!**
                """)
            
            with tab3:
                st.subheader("🔍 Advanced Filtering")
                st.markdown("Filter events by multiple criteria")
                
                # Filter options
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # Severity filter
                    severity_options = ["All"] + list(set(e.get("severity", "unknown") for e in all_events))
                    selected_severity = st.selectbox("Severity", severity_options, key="filter_severity")
                
                with col2:
                    # Joint filter
                    joint_options = ["All"] + list(set(e.get("joint", "UNKNOWN") for e in all_events))
                    selected_joint = st.selectbox("Joint", joint_options, key="filter_joint")
                
                with col3:
                    # Event type filter
                    type_options = ["All"] + list(set(e.get("event_type", "unknown") for e in all_events))
                    selected_type = st.selectbox("Event Type", type_options, key="filter_type")
                
                # Date range filter
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input("From Date", value=datetime.now() - timedelta(days=30), key="filter_start_date")
                with col2:
                    end_date = st.date_input("To Date", value=datetime.now(), key="filter_end_date")
                
                # Apply filters
                filtered = all_events.copy()
                if selected_severity != "All":
                    filtered = [e for e in filtered if e.get("severity") == selected_severity]
                if selected_joint != "All":
                    filtered = [e for e in filtered if e.get("joint") == selected_joint]
                if selected_type != "All":
                    filtered = [e for e in filtered if e.get("event_type") == selected_type]
                
                st.metric("Filtered Results", len(filtered), delta=f"of {len(all_events)} total")
                
                # Show filtered results
                if filtered:
                    st.dataframe(
                        pd.DataFrame(filtered)[['event_id', 'timestamp', 'event_type', 'severity', 'joint', 'description']].head(50),
                        use_container_width=True
                    )
            
            with tab4:
                st.subheader("📥 Export Data")
                st.markdown("Download your data in various formats")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("### CSV Export")
                    csv_data = export_to_csv(all_events)
                    if csv_data:
                        st.markdown(
                            get_download_link(csv_data, "events_export.csv", "📊 Download CSV", "text/csv"),
                            unsafe_allow_html=True
                        )
                    st.caption(f"{len(all_events)} events")
                
                with col2:
                    st.markdown("### JSON Export")
                    json_data = json.dumps(all_events, indent=2, default=str)
                    st.markdown(
                        get_download_link(json_data, "events_export.json", "📋 Download JSON", "application/json"),
                        unsafe_allow_html=True
                    )
                    st.caption("Full event data")
                
                with col3:
                    st.markdown("### Analytics Report")
                    report_data = {
                        "generated_at": datetime.now().isoformat(),
                        "total_events": len(all_events),
                        "cost_analysis": cost_data,
                        "trend_analysis": {k: v for k, v in trend_data.items() if k != 'severity_timeline'}
                    }
                    st.markdown(
                        get_download_link(json.dumps(report_data, indent=2), "analytics_report.json", "📈 Download Report", "application/json"),
                        unsafe_allow_html=True
                    )
                    st.caption("Summary analytics")
    
    # Auto-refresh logic
    if st.session_state.get("auto_refresh", False):
        import time
        time.sleep(30)
        st.rerun()


if __name__ == "__main__":
    main()

