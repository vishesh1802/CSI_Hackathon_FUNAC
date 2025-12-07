"""
Schema Service: Enforces hackathon-required schema structure
Based on Minimum Base Schema from hackathon guide
"""

import uuid
from typing import Dict, Any, Optional
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)


class SchemaService:
    """Service for enforcing standardized schema according to hackathon requirements"""
    
    # Error code to standardized name mapping
    ERROR_CODE_MAP = {
        "SRVO-160": "Torque limit reached",
        "SRVO-161": "Torque limit reached",
        "SRVO-005": "Torque limit reached",
        "SRVO-050": "Torque limit reached",
        "SRVO-062": "Torque limit reached",
        "SRVO-324": "Collision detected",
        "TEMP-100": "Temperature anomaly",
        "MOTN-019": "Motion error",
        "INTP-105": "Interpreter error",
        "PROG-048": "Program error"
    }
    
    # Collision type detection keywords
    COLLISION_KEYWORDS = {
        "hard_impact": ["collision", "crash", "impact", "strike"],
        "soft_collision": ["contact", "touch", "brush"],
        "emergency_stop": ["e-stop", "emergency", "estop", "emergency stop"]
    }
    
    def __init__(self):
        self.confidence_flags = ["high", "medium", "inferred"]
    
    def normalize_event(self, raw_event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize event to hackathon schema:
        - record_id (UUID/Int)
        - timestamp (ISO 8601)
        - joint (string, standardized)
        - collision_type (enum)
        - force_value (float in Newtons)
        - severity (enum: low/med/high/critical)
        - recommended_action (text, AI-generated)
        - confidence_flag (high/medium/inferred)
        - recurrence_count (int)
        """
        normalized = {
            "record_id": self._generate_record_id(),
            "timestamp": self._normalize_timestamp(raw_event.get("timestamp")),
            "joint": self._extract_joint(raw_event),
            "collision_type": self._detect_collision_type(raw_event),
            "force_value": self._extract_force_value(raw_event),
            "severity": self._calculate_severity(raw_event),
            "status": self._normalize_status(raw_event.get("status")),
            "recommended_action": "",  # Will be populated by AI agent
            "confidence_flag": self._determine_confidence(raw_event),
            "recurrence_count": 0,  # Will be calculated during deduplication
            "notes": self._generate_notes(raw_event),
            # Preserve important fields for display
            "event_type": raw_event.get("event_type", "unknown"),
            "event_id": raw_event.get("event_id"),
            "description": raw_event.get("description", "No description"),
            "error_code": raw_event.get("error_code"),
            # Preserve original data
            "original_event": raw_event
        }
        
        return normalized
    
    def _generate_record_id(self) -> str:
        """Generate unique record ID (UUID format)"""
        return str(uuid.uuid4())
    
    def _normalize_timestamp(self, timestamp: Any) -> str:
        """
        Normalize timestamp to ISO 8601 format
        Handles various formats and missing timestamps
        """
        if timestamp is None:
            return datetime.now().isoformat()
        
        timestamp_str = str(timestamp).strip()
        
        # Remove brackets if present [09:18:37]
        if timestamp_str.startswith('[') and timestamp_str.endswith(']'):
            timestamp_str = timestamp_str[1:-1]
        
        # Try to parse common formats
        formats = [
            "%Y-%m-%d %H:%M:%S",      # 2025-11-17 09:59:45
            "%Y-%m-%dT%H:%M:%S",       # 2025-11-17T09:59:45
            "%Y-%m-%dT%H:%M:%S.%f",    # 2025-11-17T09:59:45.123456
            "%Y/%m/%d %H:%M:%S",       # 2025/11/17 09:59:45
            "%Y/%m/%d %H:%M",          # 2025/11/17 09:59
            "%Y-%m-%d",                # 2025-11-17
            "%Y/%m/%d",                # 2025/11/17
            "%H:%M:%S",                 # 09:18:37
            "%H:%M",                    # 09:18
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(timestamp_str, fmt)
                # If only time provided, use today's date
                if fmt.startswith("%H"):
                    today = datetime.now()
                    dt = dt.replace(year=today.year, month=today.month, day=today.day)
                # If only date provided, use midnight
                elif fmt in ["%Y-%m-%d", "%Y/%m/%d"]:
                    dt = dt.replace(hour=0, minute=0, second=0)
                return dt.isoformat()
            except ValueError:
                continue
        
        # Try to extract date and time separately if format is mixed
        # Handle cases like "2025-11-17" (date only) or "[09:18:37]" (time only)
        date_match = re.search(r'(\d{4}[-/]\d{2}[-/]\d{2})', timestamp_str)
        time_match = re.search(r'(\d{2}:\d{2}:\d{2}|\d{2}:\d{2})', timestamp_str)
        
        if date_match and time_match:
            try:
                date_str = date_match.group(1).replace('/', '-')
                time_str = time_match.group(1)
                combined = f"{date_str} {time_str}"
                dt = datetime.strptime(combined, "%Y-%m-%d %H:%M:%S")
                return dt.isoformat()
            except:
                pass
        elif date_match:
            try:
                date_str = date_match.group(1).replace('/', '-')
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                dt = dt.replace(hour=0, minute=0, second=0)
                return dt.isoformat()
            except:
                pass
        elif time_match:
            try:
                time_str = time_match.group(1)
                today = datetime.now()
                if len(time_str) == 8:  # HH:MM:SS
                    dt = datetime.strptime(time_str, "%H:%M:%S")
                else:  # HH:MM
                    dt = datetime.strptime(time_str, "%H:%M")
                dt = dt.replace(year=today.year, month=today.month, day=today.day)
                return dt.isoformat()
            except:
                pass
        
        # If all parsing fails, use current time and mark as inferred
        logger.warning(f"Could not parse timestamp: {timestamp_str}, using current time")
        return datetime.now().isoformat()
    
    def _extract_joint(self, event: Dict[str, Any]) -> str:
        """
        Extract and standardize joint identifier
        Maps: J1, J2, J3, J4, J5, J6, axis1, axis2, etc.
        """
        description = str(event.get("description", "")).upper()
        data = event.get("data", {})
        
        # Check for explicit joint mentions
        joint_patterns = [
            (r"J([1-6])", "J{}"),
            (r"AXIS\s*([1-6])", "J{}"),
            (r"JOINT\s*([1-6])", "J{}")
        ]
        
        for pattern, template in joint_patterns:
            match = re.search(pattern, description)
            if match:
                joint_num = match.group(1)
                return template.format(joint_num)
        
        # Check data fields
        for key in ["axis1", "axis2", "axis3", "axis4", "axis5", "axis6"]:
            if key in data and data[key] is not None:
                axis_num = key.replace("axis", "")
                return f"J{axis_num}"
        # Check generic Axis column (numeric 1-6)
        axis_val = data.get("Axis") or data.get("axis")
        try:
            if axis_val is not None:
                axis_int = int(axis_val)
                if 1 <= axis_int <= 6:
                    return f"J{axis_int}"
        except (ValueError, TypeError):
            pass
        
        return "UNKNOWN"
    
    def _detect_collision_type(self, event: Dict[str, Any]) -> str:
        """
        Detect collision type from event data
        Returns: hard_impact, soft_collision, emergency_stop, or None
        """
        description = str(event.get("description", "")).lower()
        error_code = str(event.get("error_code", "")).upper()
        
        # Check for collision keywords
        for collision_type, keywords in self.COLLISION_KEYWORDS.items():
            for keyword in keywords:
                if keyword in description or keyword in error_code:
                    return collision_type
        
        # Additional error-code-based inference
        if "SRVO-324" in error_code:
            return "hard_impact"
        if "SRVO" in error_code and "COLLISION" in description.upper():
            return "hard_impact"
        if "E-STOP" in description.upper() or "EMERGENCY" in description.upper():
            return "emergency_stop"
        
        return None
    
    def _extract_force_value(self, event: Dict[str, Any]) -> Optional[float]:
        """
        Extract force value in Newtons
        Validates range: 0-10,000N acceptable
        """
        data = event.get("data", {})
        description = str(event.get("description", "")).lower()
        
        # Check data fields
        for key in ["force", "force_value", "torque", "vibration"]:
            if key in data and data[key] is not None:
                try:
                    force = float(data[key])
                    # Convert vibration (g) to approximate force if needed
                    if key == "vibration" and force > 0:
                        # Rough conversion: high vibration ~ higher force
                        force = force * 100  # Approximate conversion
                    if 0 <= force <= 10000:
                        return round(force, 2)
                except (ValueError, TypeError):
                    continue
        
        # Try to extract from description
        force_match = re.search(r'(\d+(?:\.\d+)?)\s*[Nn]', description)
        if force_match:
            force = float(force_match.group(1))
            if 0 <= force <= 10000:
                return round(force, 2)
        
        return None
    
    def _calculate_severity(self, event: Dict[str, Any]) -> str:
        """
        Calculate severity based on force value and other indicators
        Formula: low < 300N, med 300-600N, high/critical > 600N
        """
        force_value = self._extract_force_value(event)
        severity_raw = str(event.get("severity", "")).upper()
        
        # Use force-based calculation
        if force_value is not None:
            if force_value < 300:
                return "low"
            elif force_value < 600:
                return "med"
            else:
                return "high" if force_value < 800 else "critical"
        
        # Fallback to raw severity
        if "CRITICAL" in severity_raw:
            return "critical"
        elif "HIGH" in severity_raw or "ALERT" in severity_raw:
            return "high"
        elif "MEDIUM" in severity_raw or "MED" in severity_raw or "WARN" in severity_raw:
            return "med"
        elif "LOW" in severity_raw or "NOTICE" in severity_raw or "INFO" in severity_raw:
            return "low"
        
        # Default based on error type
        error_code = event.get("error_code", "")
        if "SRVO" in error_code or "COLLISION" in str(event.get("description", "")).upper():
            return "med"
        
        return "low"
    
    def _determine_confidence(self, event: Dict[str, Any]) -> str:
        """
        Determine confidence flag: high, medium, or inferred
        """
        has_timestamp = event.get("timestamp") is not None
        has_joint = self._extract_joint(event) != "UNKNOWN"
        has_force = self._extract_force_value(event) is not None
        has_error_code = event.get("error_code") is not None
        
        score = sum([has_timestamp, has_joint, has_force, has_error_code])
        
        if score >= 3:
            return "high"
        elif score >= 2:
            return "medium"
        else:
            return "inferred"
    
    def _normalize_status(self, status: Any) -> str:
        """
        Normalize maintenance status
        Allowed: pending_inspection, under_repair, resolved
        Defaults to pending_inspection
        """
        allowed = {"pending_inspection", "under_repair", "resolved"}
        if not status:
            return "pending_inspection"
        status_norm = str(status).strip().lower().replace(" ", "_")
        return status_norm if status_norm in allowed else "pending_inspection"
    
    def _generate_notes(self, event: Dict[str, Any]) -> str:
        """Generate notes about data quality and assumptions"""
        notes = []
        
        if not event.get("timestamp"):
            notes.append("Timestamp inferred from sequence")
        
        joint = self._extract_joint(event)
        if joint == "UNKNOWN":
            notes.append("Joint identifier not found, may need manual review")
        
        if not self._extract_force_value(event):
            notes.append("Force value not available, severity calculated from other indicators")
        
        return "; ".join(notes) if notes else ""
    
    def standardize_error_code(self, error_code: str) -> str:
        """Standardize error code to canonical name"""
        if not error_code:
            return ""
        
        return self.ERROR_CODE_MAP.get(error_code, error_code)
    
    def validate_schema(self, normalized_event: Dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Validate normalized event against schema
        Returns: (is_valid, list_of_errors)
        """
        errors = []
        required_fields = ["record_id", "timestamp", "joint", "severity", "status"]
        
        for field in required_fields:
            if field not in normalized_event or not normalized_event[field]:
                errors.append(f"Missing required field: {field}")
        
        # Validate timestamp format (ISO 8601)
        try:
            datetime.fromisoformat(normalized_event["timestamp"].replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            errors.append("Invalid timestamp format (must be ISO 8601)")
        
        # Validate severity enum
        valid_severities = ["low", "med", "high", "critical"]
        if normalized_event.get("severity") not in valid_severities:
            errors.append(f"Invalid severity: must be one of {valid_severities}")
        
        # Validate status enum
        valid_status = ["pending_inspection", "under_repair", "resolved"]
        if normalized_event.get("status") not in valid_status:
            errors.append(f"Invalid status: must be one of {valid_status}")
        
        # Validate force value range
        force = normalized_event.get("force_value")
        if force is not None and (force < 0 or force > 10000):
            errors.append(f"Force value out of range: {force}N (must be 0-10,000N)")
        
        return (len(errors) == 0, errors)

