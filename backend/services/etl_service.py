"""
ETL Service: Extract, Transform, Load data from various file formats
"""

import pandas as pd
import re
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ETLService:
    """Service for processing and transforming industrial robot data"""
    
    def __init__(self):
        # Data directory relative to project root
        project_root = Path(__file__).parent.parent.parent
        self.data_dir = project_root / "Hackathon_Data"
    
    async def process_file(self, file_path: Path, file_type: str = "auto") -> Dict[str, Any]:
        """
        Process uploaded file and extract events
        """
        file_type = file_type.lower()
        
        if file_type == "auto":
            file_type = self._detect_file_type(file_path)
        
        logger.info(f"Processing {file_type} file: {file_path}")
        
        if file_type == "csv":
            return await self._process_csv(file_path)
        elif file_type == "txt":
            return await self._process_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    def _detect_file_type(self, file_path: Path) -> str:
        """Auto-detect file type from extension"""
        ext = file_path.suffix.lower()
        if ext == ".csv":
            return "csv"
        elif ext == ".txt":
            return "txt"
        else:
            return "txt"  # Default
    
    async def _process_csv(self, file_path: Path) -> Dict[str, Any]:
        """Process CSV files (sensor readings, performance metrics)"""
        events = []
        metadata = {}
        
        try:
            df = pd.read_csv(file_path)
            metadata["columns"] = list(df.columns)
            metadata["row_count"] = len(df)
            
            # Check if it's sensor readings
            if "Temperature_C" in df.columns or "Vibration_g" in df.columns:
                events = self._extract_sensor_events(df)
            # Check if it's performance metrics
            elif "Metric1" in df.columns or "Metric2" in df.columns:
                events = self._extract_performance_events(df)
            else:
                # Generic CSV processing
                events = self._extract_generic_events(df)
        
        except Exception as e:
            logger.error(f"Error processing CSV: {str(e)}")
            raise
        
        return {
            "events": events,
            "metadata": metadata
        }
    
    async def _process_txt(self, file_path: Path) -> Dict[str, Any]:
        """Process TXT files (alerts, error logs, maintenance notes)"""
        events = []
        metadata = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
            
            metadata["line_count"] = len(lines)
            
            if not lines:
                logger.warning(f"No content found in file: {file_path}")
                return {
                    "events": [],
                    "metadata": metadata
                }
            
            # Check file content to determine type
            content = "".join(lines[:10])  # First 10 lines
            logger.info(f"File content preview (first 10 lines): {content[:200]}")
            
            if "ALERT" in content or "WARN" in content or "CRITICAL" in content:
                logger.info("Detected as system alerts file")
                events = self._extract_alert_events(lines)
            elif "SRVO" in content or "TEMP" in content or "MOTN" in content:
                logger.info("Detected as error logs file")
                events = self._extract_error_events(lines)
            elif "Checked" in content or "Replaced" in content or "Calibrated" in content or "Lubricated" in content or "Inspected" in content:
                logger.info("Detected as maintenance notes file")
                events = self._extract_maintenance_events(lines)
            else:
                logger.info("Detected as generic text file")
                events = self._extract_generic_txt_events(lines)
            
            logger.info(f"Extracted {len(events)} events from {file_path}")
        
        except Exception as e:
            logger.error(f"Error processing TXT: {str(e)}", exc_info=True)
            raise
        
        return {
            "events": events,
            "metadata": metadata
        }
    
    def _extract_sensor_events(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Extract events from sensor readings"""
        events = []
        
        for idx, row in df.iterrows():
            event = {
                "event_id": f"sensor_{idx}_{int(datetime.now().timestamp())}",
                "event_type": "sensor_reading",
                "timestamp": str(row.get("Timestamp", datetime.now())),
                "data": {
                    "temperature": row.get("Temperature_C"),
                    "vibration": row.get("Vibration_g"),
                    "axis1": row.get("Axis1_deg"),
                    "axis2": row.get("Axis2_deg"),
                    "axis3": row.get("Axis3_deg")
                },
                "description": self._generate_sensor_description(row)
            }
            events.append(event)
        
        return events
    
    def _extract_performance_events(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Extract events from performance metrics"""
        events = []
        
        for idx, row in df.iterrows():
            event = {
                "event_id": f"perf_{idx}_{int(datetime.now().timestamp())}",
                "event_type": "performance_metric",
                "timestamp": str(row.get("Timestamp", datetime.now())),
                "data": {
                    "metric1": row.get("Metric1"),
                    "metric2": row.get("Metric2"),
                    "metric3": row.get("Metric3"),
                    "metric4": row.get("Metric4")
                },
                "description": f"Performance metrics recorded at {row.get('Timestamp')}"
            }
            events.append(event)
        
        return events
    
    def _extract_alert_events(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract events from system alerts"""
        events = []
        
        for idx, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Parse alert format: "10:03:00 NOTICE: Vibration spike"
            match = re.match(r'(\d{2}:\d{2}:\d{2})\s+(\w+):\s+(.+)', line)
            if match:
                time_str, severity, message = match.groups()
                event = {
                    "event_id": f"alert_{idx}_{int(datetime.now().timestamp())}",
                    "event_type": "system_alert",
                    "timestamp": time_str,
                    "severity": severity,
                    "description": message,
                    "data": {
                        "severity": severity,
                        "message": message
                    }
                }
                events.append(event)
        
        return events
    
    def _extract_error_events(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract events from error logs"""
        events = []
        
        for idx, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Parse various error log formats
            error_code_match = re.search(r'([A-Z]+-\d+)', line)
            error_type_match = re.search(r'(Collision|Torque|Singularity|Overtravel|E-stop|Battery|Fence|Joint|Shift|Run request)', line, re.IGNORECASE)
            timestamp_match = re.search(r'(\d{4}[-/]\d{2}[-/]\d{2}|\d{2}:\d{2}:\d{2}|\[\d{2}:\d{2}:\d{2}\])', line)
            
            event = {
                "event_id": f"error_{idx}_{int(datetime.now().timestamp())}",
                "event_type": "error_log",
                "timestamp": timestamp_match.group(1) if timestamp_match else str(datetime.now()),
                "error_code": error_code_match.group(1) if error_code_match else "UNKNOWN",
                "description": line,
                "data": {
                    "error_code": error_code_match.group(1) if error_code_match else None,
                    "error_type": error_type_match.group(1) if error_type_match else None,
                    "raw_line": line
                }
            }
            events.append(event)
        
        return events
    
    def _extract_maintenance_events(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract events from maintenance notes"""
        events = []
        
        for idx, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Parse maintenance format: "2025-11-17 - Checked belts on axis 6."
            match = re.match(r'(\d{4}-\d{2}-\d{2})\s+-\s+(.+)', line)
            if match:
                date_str, action = match.groups()
                event = {
                    "event_id": f"maint_{idx}_{int(datetime.now().timestamp())}",
                    "event_type": "maintenance",
                    "timestamp": date_str,
                    "description": action,
                    "data": {
                        "action": action
                    }
                }
                events.append(event)
        
        return events
    
    def _extract_generic_events(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Extract generic events from CSV"""
        events = []
        
        for idx, row in df.iterrows():
            # Try to extract meaningful description from row data
            description_parts = []
            
            # Look for common fields that might contain descriptions
            for col in ['description', 'Description', 'DESCRIPTION', 'message', 'Message', 'error', 'Error']:
                if col in row and pd.notna(row[col]) and str(row[col]).strip():
                    description_parts.append(str(row[col]).strip())
                    break
            
            # If no description field, try to build from key fields
            if not description_parts:
                key_fields = []
                for col in df.columns:
                    if col.lower() not in ['timestamp', 'time', 'date', 'id', 'index']:
                        val = row.get(col)
                        if pd.notna(val) and str(val).strip():
                            key_fields.append(f"{col}: {val}")
                            if len(key_fields) >= 3:  # Limit to 3 fields
                                break
                if key_fields:
                    description_parts.append(" | ".join(key_fields))
            
            # Fallback description
            if not description_parts:
                description_parts.append(f"Data event from row {idx}")
            
            description = description_parts[0][:200]  # Limit length
            
            # Try to extract timestamp from common column names
            timestamp = str(datetime.now())
            for ts_col in ['timestamp', 'Timestamp', 'TIMESTAMP', 'time', 'Time', 'date', 'Date']:
                if ts_col in row and pd.notna(row[ts_col]):
                    try:
                        timestamp = str(row[ts_col])
                        break
                    except:
                        pass
            
            event = {
                "event_id": f"generic_{idx}_{int(datetime.now().timestamp())}",
                "event_type": "generic",
                "timestamp": timestamp,
                "data": row.to_dict(),
                "description": description
            }
            events.append(event)
        
        return events
    
    def _extract_generic_txt_events(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract generic events from TXT"""
        events = []
        
        for idx, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            event = {
                "event_id": f"txt_{idx}_{int(datetime.now().timestamp())}",
                "event_type": "text_event",
                "timestamp": str(datetime.now()),
                "description": line,
                "data": {"content": line}
            }
            events.append(event)
        
        return events
    
    def _generate_sensor_description(self, row: pd.Series) -> str:
        """Generate human-readable description from sensor data"""
        parts = []
        
        if pd.notna(row.get("Temperature_C")):
            temp = row.get("Temperature_C")
            if temp > 40:
                parts.append(f"High temperature: {temp}°C")
            elif temp < 20:
                parts.append(f"Low temperature: {temp}°C")
        
        if pd.notna(row.get("Vibration_g")):
            vib = row.get("Vibration_g")
            if vib > 0.2:
                parts.append(f"High vibration: {vib}g")
        
        if parts:
            return "; ".join(parts)
        return "Sensor reading recorded"

