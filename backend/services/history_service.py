"""
History Service: Find similar events from historical data
"""

from typing import Dict, List, Any
import logging
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class HistoryService:
    """Service for finding similar historical events"""
    
    def __init__(self):
        self.similarity_threshold = 0.3  # Lowered threshold to find more matches
    
    async def find_similar_events(
        self,
        current_event: Dict[str, Any],
        all_events: List[Dict[str, Any]],
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find similar events from history based on:
        - Event type
        - Description similarity
        - Error codes
        - Severity levels
        - Temporal proximity
        """
        similar_events = []
        
        # Extract fields from current event (handle both normalized and original_event structures)
        current_type = current_event.get("event_type", "") or current_event.get("original_event", {}).get("event_type", "")
        current_desc = (current_event.get("description", "") or current_event.get("original_event", {}).get("description", "")).lower()
        current_error_code = current_event.get("error_code", "") or current_event.get("original_event", {}).get("error_code", "")
        current_severity = current_event.get("severity", "")
        current_event_id = current_event.get("event_id") or current_event.get("original_event", {}).get("event_id")
        current_record_id = current_event.get("record_id")
        
        logger.info(f"Looking for similar events. Current: type={current_type}, desc={current_desc[:50]}, events_store size={len(all_events)}")
        
        for event in all_events:
            # Skip the same event by comparing both event_id and record_id
            event_id = event.get("event_id") or event.get("original_event", {}).get("event_id")
            record_id = event.get("record_id")
            
            if (current_event_id and event_id == current_event_id) or (current_record_id and record_id == current_record_id):
                continue  # Skip the same event
            
            similarity_score = 0.0
            match_reasons = []
            
            # Extract event fields (handle both normalized and original_event structures)
            event_type = event.get("event_type", "") or event.get("original_event", {}).get("event_type", "")
            event_desc = (event.get("description", "") or event.get("original_event", {}).get("description", "")).lower()
            event_error_code = event.get("error_code", "") or event.get("original_event", {}).get("error_code", "")
            event_severity = event.get("severity", "")
            
            # Type match (40% weight)
            if event_type and current_type and event_type == current_type:
                similarity_score += 0.4
                match_reasons.append("same_type")
            
            # Description similarity (30% weight)
            if current_desc and event_desc:
                desc_similarity = SequenceMatcher(None, current_desc, event_desc).ratio()
                similarity_score += desc_similarity * 0.3
                if desc_similarity > 0.3:  # Lowered threshold
                    match_reasons.append(f"similar_description({desc_similarity:.2f})")
            
            # Error code match (20% weight)
            if current_error_code and event_error_code and event_error_code == current_error_code:
                similarity_score += 0.2
                match_reasons.append("same_error_code")
            
            # Severity match (10% weight)
            if current_severity and event_severity and event_severity == current_severity:
                similarity_score += 0.1
                match_reasons.append("same_severity")
            
            # Keyword matching bonus
            current_keywords = self._extract_keywords(current_desc)
            event_keywords = self._extract_keywords(event_desc)
            common_keywords = set(current_keywords) & set(event_keywords)
            if common_keywords:
                similarity_score += min(len(common_keywords) * 0.05, 0.2)
                match_reasons.append(f"common_keywords: {', '.join(common_keywords)}")
            
            if similarity_score >= self.similarity_threshold:
                event_copy = event.copy()
                event_copy["similarity_score"] = round(similarity_score, 3)
                event_copy["match_reasons"] = match_reasons
                similar_events.append(event_copy)
        
        # Sort by similarity score (descending)
        similar_events.sort(key=lambda x: x.get("similarity_score", 0), reverse=True)
        
        return similar_events[:limit]
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        # Common industrial robot keywords
        keywords = []
        important_terms = [
            "collision", "torque", "vibration", "temperature", "servo",
            "battery", "fence", "overtravel", "singularity", "joint",
            "motor", "axis", "sensor", "network", "calibrate", "belt",
            "wiring", "lubricate", "replace", "check", "inspect"
        ]
        
        text_lower = text.lower()
        for term in important_terms:
            if term in text_lower:
                keywords.append(term)
        
        return keywords
    
    async def get_event_statistics(
        self,
        event_type: str,
        all_events: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Get statistics for a specific event type"""
        type_events = [e for e in all_events if e.get("event_type") == event_type]
        
        if not type_events:
            return {
                "event_type": event_type,
                "count": 0,
                "frequency": "N/A"
            }
        
        # Calculate frequency
        timestamps = [e.get("timestamp") for e in type_events if e.get("timestamp")]
        
        return {
            "event_type": event_type,
            "count": len(type_events),
            "frequency": f"{len(type_events)} occurrences",
            "first_occurrence": min(timestamps) if timestamps else None,
            "last_occurrence": max(timestamps) if timestamps else None
        }

