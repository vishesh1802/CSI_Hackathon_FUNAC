"""
Azure AI Foundry Service: Integration with Azure OpenAI
- GPT model deployment
- Prompt templates
- Token monitoring
"""

import os
import logging
import re
from typing import Dict, List, Any
from openai import AzureOpenAI
import json
import hashlib
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class AzureAIService:
    """Service for interacting with Azure AI Foundry (Azure OpenAI)"""
    
    def __init__(self):
        # Configuration from environment variables
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
        
        # Initialize Azure OpenAI client if credentials are available
        self.client = None
        if self.api_key and self.endpoint:
            try:
                self.client = AzureOpenAI(
                    api_key=self.api_key,
                    api_version=self.api_version,
                    azure_endpoint=self.endpoint
                )
                logger.info("Azure OpenAI client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Azure OpenAI client: {str(e)}")
        else:
            logger.warning("Azure OpenAI credentials not found. Using mock mode.")
        
        # Response cache: key -> cached response
        # Cache key is hash of event_id + description + severity
        self.response_cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
    
    def is_available(self) -> bool:
        """Check if Azure AI service is available"""
        return self.client is not None
    
    def _generate_cache_key(self, event: Dict[str, Any]) -> str:
        """Generate cache key from event characteristics"""
        # Use event_id, description, severity, error_code for cache key
        key_data = {
            "event_id": event.get("event_id", ""),
            "description": event.get("description", "")[:100],  # First 100 chars
            "severity": event.get("severity", ""),
            "error_code": event.get("error_code", ""),
            "joint": event.get("joint", "")
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total * 100) if total > 0 else 0
        return {
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate": round(hit_rate, 2),
            "cache_size": len(self.response_cache)
        }
    
    async def analyze_event(
        self,
        event: Dict[str, Any],
        similar_events: List[Dict[str, Any]] = None,
        prompt_template: str = "default"
    ) -> Dict[str, Any]:
        """
        Analyze event using GPT model
        Returns: analysis, priority, recommendation, score
        Uses caching to avoid duplicate AI calls
        """
        if not self.is_available():
            return self._mock_analysis(event, similar_events)
        
        # Initialize cache_key for potential caching
        cache_key = None
        
        # Check cache first (only for triage template to avoid caching different contexts)
        if prompt_template == "triage":
            cache_key = self._generate_cache_key(event)
            if cache_key in self.response_cache:
                logger.info(f"Cache HIT for event {event.get('event_id')}")
                self.cache_hits += 1
                cached_response = self.response_cache[cache_key].copy()
                cached_response["cached"] = True
                return cached_response
            
            logger.info(f"Cache MISS for event {event.get('event_id')} - calling AI")
            self.cache_misses += 1
        
        try:
            prompt = self._build_prompt(event, similar_events, prompt_template)
            
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            # Extract response
            analysis_text = response.choices[0].message.content
            
            # Parse structured response
            result = self._parse_ai_response(analysis_text, event)
            
            # Token usage tracking
            usage = response.usage
            logger.info(f"Token usage - Prompt: {usage.prompt_tokens}, Completion: {usage.completion_tokens}, Total: {usage.total_tokens}")
            
            result["token_usage"] = {
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens
            }
            
            result["cached"] = False
            
            # Cache the result (only for triage template, limit cache size to prevent memory issues)
            if prompt_template == "triage" and cache_key:
                if len(self.response_cache) < 1000:  # Max 1000 cached responses
                    self.response_cache[cache_key] = result.copy()
                else:
                    # Remove oldest entry (simple FIFO)
                    oldest_key = next(iter(self.response_cache))
                    del self.response_cache[oldest_key]
                    self.response_cache[cache_key] = result.copy()
            
            return result
        
        except Exception as e:
            logger.error(f"Error calling Azure OpenAI: {str(e)}")
            # Fallback to mock analysis
            return self._mock_analysis(event, similar_events)
    
    def _build_prompt(
        self,
        event: Dict[str, Any],
        similar_events: List[Dict[str, Any]] = None,
        template: str = "default"
    ) -> str:
        """Build prompt from template"""
        
        if template == "triage":
            return self._build_triage_prompt(event, similar_events)
        else:
            return self._build_default_prompt(event, similar_events)
    
    def _build_default_prompt(
        self,
        event: Dict[str, Any],
        similar_events: List[Dict[str, Any]] = None
    ) -> str:
        """Build default analysis prompt"""
        prompt = f"""Analyze the following industrial robot event and provide:
1. Priority level (CRITICAL, HIGH, MEDIUM, LOW)
2. Risk assessment (0-100 score)
3. Recommended action
4. Brief analysis

Event Details:
- Type: {event.get('event_type', 'Unknown')}
- Timestamp: {event.get('timestamp', 'Unknown')}
- Description: {event.get('description', 'No description')}
"""
        
        if event.get('error_code'):
            prompt += f"- Error Code: {event.get('error_code')}\n"
        
        if event.get('severity'):
            prompt += f"- Severity: {event.get('severity')}\n"
        
        if event.get('data'):
            prompt += f"- Data: {json.dumps(event.get('data'), indent=2)}\n"
        
        if similar_events:
            prompt += f"\nSimilar Historical Events ({len(similar_events)} found):\n"
            for i, similar in enumerate(similar_events[:3], 1):
                prompt += f"{i}. {similar.get('description', 'N/A')} (Similarity: {similar.get('similarity_score', 0):.2f})\n"
        
        prompt += "\nProvide your analysis in JSON format:\n"
        prompt += '{"priority": "CRITICAL|HIGH|MEDIUM|LOW", "risk_score": 0-100, "recommendation": "action to take", "analysis": "brief explanation"}'
        
        return prompt
    
    def _build_triage_prompt(
        self,
        event: Dict[str, Any],
        similar_events: List[Dict[str, Any]] = None
    ) -> str:
        """
        Build triage prompt with 5-section output format required by hackathon:
        1. Diagnose cause
        2. Step-by-step inspection procedure
        3. Required maintenance actions
        4. Safety clearance procedure
        5. Return-to-service conditions
        """
        event_type = event.get('event_type', 'unknown')
        original_event = event.get('original_event', {})
        event_data = original_event.get('data', {}) or event.get('data', {})
        
        # Enhanced prompt with few-shot example for better structured output
        prompt = f"""You are an expert FANUC industrial robot maintenance technician with 20+ years of experience. Analyze the following FANUC robot event and provide a comprehensive maintenance recommendation.

EVENT TYPE: {event_type.upper()}

FANUC ROBOT EVENT DETAILS:
- Joint: {event.get('joint', 'Unknown')} (J1=Base, J2=Shoulder, J3=Elbow, J4=Wrist Roll, J5=Wrist Pitch, J6=Wrist Yaw)
- Force Value: {event.get('force_value', 'N/A')}N
- Severity: {event.get('severity', 'Unknown')}
- Collision Type: {event.get('collision_type', 'N/A')}
- Timestamp: {event.get('timestamp', 'Unknown')}
- Description: {event.get('description', 'No description')}
"""
        
        # Add event-specific data based on type
        if event_type == 'performance_metric' and event_data:
            prompt += f"\nPERFORMANCE METRICS:\n"
            for key, value in event_data.items():
                prompt += f"- {key}: {value}\n"
            prompt += "\nNOTE: Performance metrics indicate system health. Analyze these values against FANUC specifications.\n"
        elif event_type == 'sensor_reading' and event_data:
            prompt += f"\nSENSOR READINGS:\n"
            if 'temperature' in event_data:
                prompt += f"- Temperature: {event_data.get('temperature')}°C\n"
            if 'vibration' in event_data:
                prompt += f"- Vibration: {event_data.get('vibration')}g\n"
            if 'axis1' in event_data or 'axis2' in event_data:
                prompt += f"- Joint Angles: "
                axes = []
                for i in range(1, 7):
                    axis_val = event_data.get(f'axis{i}') or event_data.get(f'Axis{i}_deg')
                    if axis_val is not None:
                        axes.append(f"J{i}={axis_val}°")
                prompt += ", ".join(axes) + "\n"
        
        if event.get('error_code'):
            # Map FANUC error code to description
            error_code = event.get('error_code')
            from services.schema_service import SchemaService
            schema_svc = SchemaService()
            error_desc = schema_svc.standardize_error_code(error_code)
            prompt += f"\nFANUC Error Code: {error_code} ({error_desc})\n"
        
        if event.get('recurrence_count', 0) > 0:
            prompt += f"\nRECURRENCE WARNING: This event has occurred {event.get('recurrence_count')} times in the last 24 hours. This suggests a chronic issue requiring immediate attention.\n"
        
        if event.get('notes'):
            prompt += f"\nDATA QUALITY NOTES: {event.get('notes')}\n"
        
        if similar_events:
            prompt += f"\nSIMILAR HISTORICAL EVENTS ({len(similar_events)} found):\n"
            for i, similar in enumerate(similar_events[:3], 1):
                prompt += f"{i}. {similar.get('description', 'N/A')} (Similarity: {similar.get('similarity_score', 0):.2%})\n"
        
        # Adjust prompt based on event type
        if event_type == 'performance_metric':
            prompt += """
CONTEXT: This is a performance monitoring event. Focus on:
- Analyzing metric values against FANUC operational specifications
- Identifying degradation trends or anomalies
- Preventive maintenance recommendations
- Performance optimization opportunities

REQUIRED OUTPUT FORMAT (provide all 5 sections):

1. DIAGNOSE CAUSE:
   [Analyze the performance metrics and identify potential root causes: wear, calibration drift, environmental factors, or system degradation]

2. STEP-BY-STEP INSPECTION PROCEDURE:
   [List specific diagnostic checks: review performance logs, inspect joints, verify sensor calibration, check environmental conditions]

3. REQUIRED MAINTENANCE ACTIONS:
   [Specify preventive or corrective actions: lubrication, calibration, component replacement, or system optimization]

4. SAFETY CLEARANCE PROCEDURE:
   [What must be verified before continuing operations or performing maintenance]

5. RETURN-TO-SERVICE CONDITIONS:
   [Criteria for confirming the robot is operating within acceptable performance parameters]

Provide your response in clear, technician-focused language. Use controlled vocabulary and be specific."""
        else:
            prompt += """
EXAMPLE OUTPUT FORMAT (follow this structure exactly):

For a collision event on J3 with force 645N:
1. DIAGNOSE CAUSE:
   Excessive force detected on J3 (Elbow joint) indicates potential mechanical binding or obstruction. The 645N reading exceeds normal operating parameters, suggesting possible wear in the joint mechanism or external interference.

2. STEP-BY-STEP INSPECTION PROCEDURE:
   1. Power down robot and lock out/tag out per safety procedures
   2. Visually inspect J3 joint for visible damage or obstructions
   3. Check joint lubrication levels and condition
   4. Manually rotate J3 through full range of motion to detect binding
   5. Inspect cables and hoses for pinching or damage
   6. Verify joint encoder readings match physical position

3. REQUIRED MAINTENANCE ACTIONS:
   - Replace J3 joint bearings if excessive play detected
   - Re-lubricate joint with FANUC-approved grease
   - Replace damaged cables if found
   - Calibrate joint encoder if misalignment detected

4. SAFETY CLEARANCE PROCEDURE:
   - Verify all safety interlocks are functional
   - Test emergency stop system
   - Confirm work area is clear
   - Check that all guards are in place

5. RETURN-TO-SERVICE CONDITIONS:
   - Joint moves smoothly through full range
   - Force readings within normal parameters (<300N)
   - No error codes present
   - Successful test cycle completed

RISK_SCORE: 75
PRIORITY: HIGH

---

REQUIRED OUTPUT FORMAT (provide all 5 sections for the current event):

1. DIAGNOSE CAUSE:
   [Explain the root cause based on force level, joint location, frequency, error patterns, and event characteristics. Be specific and technical.]

2. STEP-BY-STEP INSPECTION PROCEDURE:
   [List specific checks the technician should perform, in order. Number each step.]

3. REQUIRED MAINTENANCE ACTIONS:
   [Specify exact repairs, replacements, or adjustments needed. Include part numbers if applicable, torque specifications, and required tools.]

4. SAFETY CLEARANCE PROCEDURE:
   [What must be verified before restarting the robot. Include lockout verification, safety system checks, and test procedures.]

5. RETURN-TO-SERVICE CONDITIONS:
   [Specific criteria for putting robot back online. Include test movements, verification steps, and monitoring requirements.]

CRITICAL: At the END of your response, provide these values on separate lines:
RISK_SCORE: [number 0-100]
PRIORITY: [CRITICAL or HIGH or MEDIUM or LOW]

Provide your response in clear, technician-focused language. Use controlled vocabulary and be specific. Each section should be comprehensive and actionable."""
        
        return prompt
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for the AI"""
        return """You are an expert FANUC industrial robot maintenance and diagnostics system. 
Your role is to analyze FANUC robot events, errors, and alerts to determine priority, assess risk, 
and provide actionable recommendations for robot technicians. Consider:
- FANUC robot-specific error codes (SRVO, TEMP, MOTN, INTP, PROG)
- Robot joint-specific issues (J1-J6: base, shoulder, elbow, wrist)
- Safety implications for industrial robots
- Production line impact
- Historical patterns
- Severity indicators
- Maintenance history

Always provide clear, actionable recommendations specific to FANUC robot maintenance procedures."""
    
    def _parse_ai_response(self, response_text: str, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse AI response into structured format with 5-section output
        """
        # Extract 5 sections from response
        sections = {
            "diagnose_cause": "",
            "inspection_procedure": "",
            "maintenance_actions": "",
            "safety_clearance": "",
            "return_to_service": ""
        }
        
        # Try to parse structured sections
        section_patterns = {
            "diagnose_cause": r"(?:1\.\s*)?DIAGNOSE CAUSE:?\s*\n(.*?)(?=\n\s*(?:2\.|STEP-BY-STEP|REQUIRED|SAFETY|RETURN))",
            "inspection_procedure": r"(?:2\.\s*)?STEP-BY-STEP INSPECTION(?: PROCEDURE)?:?\s*\n(.*?)(?=\n\s*(?:3\.|REQUIRED|SAFETY|RETURN))",
            "maintenance_actions": r"(?:3\.\s*)?REQUIRED MAINTENANCE(?: ACTIONS)?:?\s*\n(.*?)(?=\n\s*(?:4\.|SAFETY|RETURN))",
            "safety_clearance": r"(?:4\.\s*)?SAFETY CLEARANCE(?: PROCEDURE)?:?\s*\n(.*?)(?=\n\s*(?:5\.|RETURN))",
            "return_to_service": r"(?:5\.\s*)?RETURN-TO-SERVICE(?: CONDITIONS)?:?\s*\n(.*?)(?=\n\s*$)"
        }
        
        for section_key, pattern in section_patterns.items():
            match = re.search(pattern, response_text, re.IGNORECASE | re.DOTALL | re.MULTILINE)
            if match:
                sections[section_key] = match.group(1).strip()
        
        # If sections not found, try alternative parsing
        if not any(sections.values()):
            # Try numbered list format
            lines = response_text.split('\n')
            current_section = None
            for line in lines:
                line_upper = line.upper()
                if 'DIAGNOSE' in line_upper or 'CAUSE' in line_upper:
                    current_section = "diagnose_cause"
                elif 'INSPECTION' in line_upper:
                    current_section = "inspection_procedure"
                elif 'MAINTENANCE' in line_upper:
                    current_section = "maintenance_actions"
                elif 'SAFETY' in line_upper:
                    current_section = "safety_clearance"
                elif 'RETURN' in line_upper or 'SERVICE' in line_upper:
                    current_section = "return_to_service"
                elif current_section and line.strip():
                    sections[current_section] += line.strip() + "\n"
        
        # Try to extract risk_score and priority from AI response
        risk_score = None
        priority = None
        
        # Look for RISK_SCORE: number pattern
        risk_match = re.search(r'RISK_SCORE[:\s]+(\d+)', response_text, re.IGNORECASE)
        if risk_match:
            try:
                risk_score = int(risk_match.group(1))
                risk_score = max(0, min(100, risk_score))  # Clamp to 0-100
            except:
                pass
        
        # Look for PRIORITY: level pattern
        priority_match = re.search(r'PRIORITY[:\s]+(CRITICAL|HIGH|MEDIUM|LOW)', response_text, re.IGNORECASE)
        if priority_match:
            priority = priority_match.group(1).upper()
        
        # Fallback: Determine priority and risk_score from severity and content if not found
        # Also validate AI score - if AI gives low score to critical event, override it
        severity = event.get("severity", "").lower()
        force_value = event.get("force_value") or 0
        recurrence = event.get("recurrence_count", 0)
        
        # Calculate base score from severity and force
        if severity == "critical" or force_value > 800:
            base_priority = "CRITICAL"
            base_score = 90
        elif severity == "high" or force_value > 600:
            base_priority = "HIGH"
            base_score = 75
        elif severity == "med" or force_value > 300:
            base_priority = "MEDIUM"
            base_score = 50
        else:
            base_priority = "LOW"
            base_score = 30
        
        # Adjust for recurrence (chronic issues are more urgent)
        # Massive recurrence indicates systemic problem
        if recurrence > 100:
            base_score += 25  # Major boost for chronic issues
        elif recurrence > 50:
            base_score += 20
        elif recurrence > 10:
            base_score += 15
        elif recurrence > 5:
            base_score += 10
        elif recurrence > 1:
            base_score += 5
        
        # Use fallback if AI didn't provide score, OR if AI score is too low for severity
        if risk_score is None or priority is None:
            # Use calculated values
            if risk_score is None:
                risk_score = base_score
            if priority is None:
                priority = base_priority
        elif severity == "critical" and risk_score < 80:
            # Override low AI scores for critical events
            logger.warning(f"AI returned low score {risk_score} for critical event, overriding to {base_score}")
            risk_score = max(base_score, risk_score)
            priority = "CRITICAL"
        elif severity == "high" and risk_score < 60:
            # Override low AI scores for high severity events
            logger.warning(f"AI returned low score {risk_score} for high severity event, overriding to {base_score}")
            risk_score = max(base_score, risk_score)
            if priority != "CRITICAL":
                priority = "HIGH"
            
            # Adjust for error codes
            error_code = str(event.get("error_code", "")).upper()
            if "SRVO" in error_code and "COLLISION" in error_code:
                base_score += 20
            elif "SRVO" in error_code:
                base_score += 15
            elif "TEMP" in error_code:
                base_score += 10
            
            # Adjust for collision type
            collision_type = str(event.get("collision_type", "")).upper()
            if "HARD_IMPACT" in collision_type:
                base_score += 25
            elif "EMERGENCY_STOP" in collision_type:
                base_score += 20
            
            # Clamp score
            base_score = max(0, min(100, base_score))
            
            # Use calculated values if AI didn't provide them
            if risk_score is None:
                risk_score = base_score
            if priority is None:
                priority = base_priority
        
        # Build comprehensive recommendation from sections
        recommendation = ""
        if sections["diagnose_cause"]:
            recommendation += f"Diagnosis: {sections['diagnose_cause'][:200]}...\n\n"
        if sections["maintenance_actions"]:
            recommendation += f"Actions: {sections['maintenance_actions'][:200]}"
        
        if not recommendation:
            recommendation = "Review event details and follow standard maintenance procedures"
        
        result = {
            "priority": priority,
            "risk_score": risk_score,
            "recommendation": recommendation.strip(),
            "analysis": response_text,
            "maintenance_report": {
                "diagnose_cause": sections["diagnose_cause"] or "Analysis pending",
                "inspection_procedure": sections["inspection_procedure"] or "Standard inspection required",
                "maintenance_actions": sections["maintenance_actions"] or "Review event details",
                "safety_clearance": sections["safety_clearance"] or "Verify all safety checks",
                "return_to_service": sections["return_to_service"] or "Meet all return-to-service criteria"
            }
        }
        
        return result
    
    def _mock_analysis(
        self,
        event: Dict[str, Any],
        similar_events: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Mock analysis when Azure AI is not available"""
        event_type = event.get("event_type", "")
        severity = event.get("severity", "")
        error_code = event.get("error_code", "")
        
        # Determine priority based on heuristics
        priority = "MEDIUM"
        risk_score = 50
        
        if severity == "CRITICAL" or "CRITICAL" in str(event.get("description", "")).upper():
            priority = "CRITICAL"
            risk_score = 90
        elif severity == "ALERT" or severity == "WARN":
            priority = "HIGH"
            risk_score = 70
        elif severity == "NOTICE" or severity == "INFO":
            priority = "LOW"
            risk_score = 30
        
        # Error code based scoring
        if error_code:
            if "SRVO" in error_code:
                risk_score += 10
            if "TEMP" in error_code:
                risk_score += 5
        
        # Similar events influence
        if similar_events:
            high_priority_similar = sum(1 for e in similar_events if e.get("severity") in ["CRITICAL", "ALERT"])
            if high_priority_similar > 0:
                risk_score += min(high_priority_similar * 5, 20)
        
        risk_score = min(risk_score, 100)
        
        recommendation = self._generate_mock_recommendation(priority, event_type, error_code)
        
        analysis = f"Event type: {event_type}. "
        if severity:
            analysis += f"Severity: {severity}. "
        if error_code:
            analysis += f"Error code: {error_code}. "
        analysis += f"Based on analysis, this event has {priority} priority with a risk score of {risk_score}."
        
        return {
            "priority": priority,
            "risk_score": risk_score,
            "recommendation": recommendation,
            "analysis": analysis,
            "token_usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "mode": "mock"
            }
        }
    
    def _generate_mock_recommendation(
        self,
        priority: str,
        event_type: str,
        error_code: str
    ) -> str:
        """Generate mock recommendation"""
        if priority == "CRITICAL":
            return "Immediate action required. Stop operations and investigate root cause."
        elif priority == "HIGH":
            return "Schedule maintenance soon. Monitor closely for escalation."
        elif priority == "MEDIUM":
            return "Review during next maintenance window. Continue monitoring."
        else:
            return "Log for tracking. No immediate action needed."
    
    def get_token_usage_stats(self) -> Dict[str, Any]:
        """Get token usage statistics (would track across calls in production)"""
        return {
            "total_tokens": 0,
            "total_calls": 0,
            "average_tokens_per_call": 0
        }

