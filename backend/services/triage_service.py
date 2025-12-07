"""
Triage Service: Score and prioritize events
"""

from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class TriageService:
    """Service for triage scoring and prioritization"""
    
    def __init__(self, azure_ai_service):
        self.azure_ai_service = azure_ai_service
    
    async def score_event(
        self,
        event: Dict[str, Any],
        similar_events: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Score an event for triage
        Returns: score (0-100), priority, recommendation, analysis
        """
        logger.info(f"Scoring event: {event.get('event_id')}")
        
        # Use Azure AI for intelligent analysis
        ai_result = await self.azure_ai_service.analyze_event(
            event,
            similar_events,
            prompt_template="triage"
        )
        
        # Get AI score, but validate against event severity
        ai_score = ai_result.get("risk_score", 50)
        severity = str(event.get("severity", "")).lower().strip()
        recurrence = event.get("recurrence_count", 0) or 0
        
        # Log for debugging
        logger.info(f"Scoring event - severity: '{severity}', recurrence: {recurrence}, AI score: {ai_score}")
        
        # Override AI score if it's too low for critical/high severity events
        # This ensures critical events always get appropriate scores
        if severity == "critical":
            # Critical events should be at least 80, regardless of AI score
            base_score = max(ai_score, 80)
            # Massive recurrence (like 967) indicates chronic critical issue
            if recurrence > 100:
                base_score = 95  # Near maximum for chronic critical issues
                logger.info(f"Critical event with {recurrence} recurrences -> setting score to 95")
            elif recurrence > 50:
                base_score = min(base_score + 10, 100)
            elif recurrence > 10:
                base_score = min(base_score + 5, 100)
            logger.info(f"Critical event - base_score after override: {base_score}")
        elif severity == "high":
            # High severity should be at least 60
            base_score = max(ai_score, 60)
            if recurrence > 100:
                base_score = min(base_score + 15, 100)
            elif recurrence > 50:
                base_score = min(base_score + 10, 100)
            elif recurrence > 10:
                base_score = min(base_score + 5, 100)
        else:
            # For medium/low, use AI score but still boost for high recurrence
            base_score = ai_score
            if recurrence > 100:
                base_score = min(base_score + 20, 100)
            elif recurrence > 50:
                base_score = min(base_score + 15, 100)
            elif recurrence > 10:
                base_score = min(base_score + 10, 100)
        
        # Adjust based on similar events
        if similar_events:
            avg_similarity = sum(e.get("similarity_score", 0) for e in similar_events[:5]) / min(len(similar_events), 5)
            if avg_similarity > 0.8:
                base_score += 10  # Boost if very similar events exist
        
        # Normalize score
        final_score = min(max(base_score, 0), 100)
        
        # Determine priority - override AI if severity demands it
        ai_priority = ai_result.get("priority", "").upper()
        if severity == "critical":
            priority = "CRITICAL"  # Always CRITICAL for critical severity
        elif severity == "high":
            priority = "HIGH" if ai_priority != "CRITICAL" else ai_priority
        else:
            priority = ai_priority if ai_priority else self._score_to_priority(final_score)
        
        return {
            "score": round(final_score, 2),
            "priority": priority,
            "recommendation": ai_result.get("recommendation", "Monitor the situation"),
            "analysis": ai_result.get("analysis", "Event analyzed"),
            "maintenance_report": ai_result.get("maintenance_report", {}),
            "ai_metadata": {
                "token_usage": ai_result.get("token_usage", {}),
                "ai_available": self.azure_ai_service.is_available()
            }
        }
    
    def _score_to_priority(self, score: float) -> str:
        """Convert numeric score to priority level"""
        if score >= 80:
            return "CRITICAL"
        elif score >= 60:
            return "HIGH"
        elif score >= 40:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _calculate_heuristic_score(self, event: Dict[str, Any]) -> float:
        """Calculate score using heuristics (fallback)"""
        score = 50.0  # Base score
        
        # Severity weighting
        severity = event.get("severity", "").upper()
        if severity == "CRITICAL":
            score += 40
        elif severity == "ALERT":
            score += 25
        elif severity == "WARN":
            score += 15
        elif severity == "NOTICE" or severity == "INFO":
            score -= 10
        
        # Error code weighting
        error_code = event.get("error_code", "")
        if "SRVO" in error_code:
            score += 15
        if "TEMP" in error_code:
            score += 10
        if "MOTN" in error_code:
            score += 5
        
        # Event type weighting
        event_type = event.get("event_type", "")
        if event_type == "error_log":
            score += 10
        elif event_type == "system_alert":
            score += 5
        
        return min(max(score, 0), 100)

