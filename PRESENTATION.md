# 🤖 FANUC FirstResponder - Project Presentation

## Slide 1: Title Slide

**FANUC FirstResponder**
*Intelligent Robot Maintenance Diagnostic Assistant*

**Team:** [Your Team Name]  
**Hackathon:** CSI Hackathon | December 5-7, 2025  
**Date:** [Presentation Date]

---

## Slide 2: Problem Statement

### The Challenge

**Industrial robot maintenance teams face critical pain points:**

🔴 **Unstructured Data Chaos**
- Robot logs come in multiple formats (CSV, TXT, JSON)
- Inconsistent timestamps, missing values, varied error codes
- No standardized way to analyze events

🔴 **Reactive Maintenance**
- Technicians react to failures after they occur
- No intelligent prioritization of issues
- Chronic problems go unnoticed

🔴 **Expert Knowledge Gap**
- Maintenance decisions rely on experience
- No standardized diagnostic procedures
- Inconsistent recommendations across teams

### The Impact
- **Production Downtime**: Hours of lost productivity
- **Safety Risks**: Unaddressed critical issues
- **Cost Overruns**: Reactive repairs cost 3-5x more than preventive maintenance

---

## Slide 3: Our Solution

### FANUC FirstResponder

**An AI-powered third-party diagnostic assistant** that transforms unstructured robot data into actionable maintenance intelligence.

### Core Value Proposition

✅ **Data Structuring Pipeline**  
Transforms messy robot logs into clean, AI-consumable format

✅ **AI Maintenance Agent**  
Generates expert-level, standardized maintenance procedures

✅ **Intelligent Triage System**  
Prioritizes events by severity, recurrence, and risk

### Key Differentiator
**Better data hygiene = Better AI maintenance decisions**

---

## Slide 4: Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│              MAINTENANCE TEAM (Users)                    │
│  • Upload robot data files                               │
│  • View structured analysis                              │
│  • Get AI-powered recommendations                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│           FANUC FirstResponder System                   │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ ETL Pipeline │→ │   Schema     │→ │ Validation   │   │
│  │              │  │ Normalization│  │ & Dedupe     │   │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   History    │  │    Triage    │  │  Azure AI    │    │
│  │   Lookup     │  │   Scoring    │  │   Service    │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└───────────────────────┬──────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│         Azure AI Foundry (GPT-4o)                       │
│  • Intelligent event analysis                           │
│  • 5-section maintenance reports                        │
│  • FANUC-specific recommendations                       │
└─────────────────────────────────────────────────────────┘
```

### Technology Stack
- **Frontend**: Streamlit (Python web framework)
- **Backend**: FastAPI (async REST API)
- **AI**: Azure OpenAI GPT-4o
- **Data Processing**: Pandas, NumPy
- **Cloud**: Azure AI Foundry

---

## Slide 5: Key Features

### 1. Data Structuring Pipeline ✅

**Transforms unstructured data into clean format:**
- Handles multiple file formats (CSV, TXT)
- Normalizes timestamps to ISO 8601
- Standardizes FANUC error codes (SRVO, TEMP, MOTN)
- Maps joints to standard J1-J6 format
- Calculates severity from force values
- Tracks recurrence (chronic issues)

**Result**: 75%+ extraction accuracy

### 2. AI Maintenance Agent ✅

**Generates standardized 5-section reports:**
1. **Diagnose Cause**: Root cause analysis
2. **Inspection Procedure**: Step-by-step technician checklist
3. **Maintenance Actions**: Specific repairs needed
4. **Safety Clearance**: Pre-restart verification
5. **Return-to-Service**: Criteria for going live

**FANUC-Specific**: Understands robot error codes, joints, and maintenance procedures

### 3. Intelligent Triage System ✅

**Prioritizes events intelligently:**
- Risk score (0-100) based on severity, recurrence, force values
- Priority levels: CRITICAL, HIGH, MEDIUM, LOW
- Similar event lookup for context
- Visual dashboards and charts

---

## Slide 6: Demo Flow

### Live Demonstration

**Step 1: Upload Data** 📤
- Upload robot collision data files
- Supports CSV (sensor readings, metrics) and TXT (error logs, alerts)

**Step 2: Data Processing** ⚙️
- ETL pipeline extracts and normalizes events
- Schema service standardizes all fields
- Validation ensures 75%+ accuracy

**Step 3: View Events** 📋
- Browse processed events with filters
- See severity distribution, recurrence counts
- Statistics dashboard

**Step 4: Triage Analysis** 🎯
- Select an event for analysis
- AI generates maintenance report
- Get prioritized recommendations

**Step 5: AI Recommendations** 🤖
- 5-section structured output
- FANUC-specific maintenance procedures
- Risk score and priority

---

## Slide 7: Technical Highlights

### Data Quality Handling

**Robust error handling:**
- Missing timestamps → Inferred from context
- Missing joints → Marked as "UNKNOWN" with confidence flags
- Inconsistent formats → Normalized automatically
- NaN values → Handled gracefully (JSON-safe)

**Validation Metrics:**
- Field completeness tracking
- Extraction accuracy calculation
- Deduplication statistics

### AI Integration

**Azure OpenAI GPT-4o:**
- Few-shot examples for consistent output
- Response caching (1000 entries) for performance
- Token usage tracking
- Fallback to heuristic analysis if unavailable

**Prompt Engineering:**
- FANUC-specific context
- Structured output format enforcement
- Technician-focused language

### Performance Optimizations

- **Caching**: AI responses cached for identical events
- **Batch Processing**: Process all datasets at once
- **Fast Mode**: Skip AI for quick processing
- **Async Processing**: Non-blocking API calls

---

## Slide 8: Results & Validation

### Data Processing Results

**Dataset Statistics:**
- **Total Records Processed**: ~7,906 records
- **Files Processed**: 7 files (4 CSV, 3 TXT)
- **Events Extracted**: [Actual count from your system]
- **Missing Values**: 0% (all handled)
- **Timestamp Normalization**: 100% ISO 8601

### Validation Metrics

✅ **Extraction Accuracy**: 75%+ (meets hackathon requirement)  
✅ **Data Completeness**: High (missing values handled)  
✅ **Schema Compliance**: 100% (all events normalized)  
✅ **Deduplication**: Recurrence tracking enabled

### AI Performance

- **Response Time**: <5 seconds per event (cached: instant)
- **Cache Hit Rate**: [Your cache stats]
- **Token Usage**: Optimized with caching
- **Output Quality**: Consistent 5-section format

---

## Slide 9: Why Our Approach Wins

### 1. Schema-First Design ✅

**"Your schema = your power"**
- Defined early, enforced consistently
- Enables better AI reasoning
- Easier to extend and maintain

### 2. Better Data Hygiene ✅

**"Better data hygiene = Better AI decisions"**
- Handles missing values intelligently
- Normalizes inconsistent formats
- Tracks data quality with confidence flags

### 3. Production-Ready Architecture ✅

- Modular service design
- Scalable (can add database, caching)
- Azure cloud-native
- Security-ready (authentication hooks)

### 4. Real-World Applicable ✅

- Works with actual FANUC robot data formats
- Understands FANUC error codes and joints
- Generates actionable maintenance procedures
- Third-party tool (doesn't interfere with robot control)

---

## Slide 10: Future Enhancements

### Short-Term (Next Sprint)

🔮 **Real-Time Integration**
- Connect to FANUC Data Server
- Stream events in real-time
- Live monitoring dashboard

🔮 **Enhanced Analytics**
- Trend analysis over time
- Predictive maintenance alerts
- Cost estimation for repairs

### Long-Term (Production)

🔮 **Multi-Robot Support**
- Fleet-wide monitoring
- Cross-robot pattern detection
- Centralized maintenance scheduling

🔮 **Advanced AI**
- Fine-tuned models for FANUC robots
- Custom embeddings for similarity search
- Automated maintenance scheduling

🔮 **Enterprise Features**
- User authentication (Azure AD)
- Role-based access control
- Audit logging
- Integration with maintenance management systems

---

## Slide 11: Lessons Learned

### What Worked Well ✅

1. **Schema-First Approach**: Defining schema early prevented rework
2. **Incremental Development**: Built MVP first, then enhanced
3. **Azure AI Integration**: Smooth integration with Azure OpenAI
4. **Modular Design**: Easy to test and extend components

### Challenges Overcome 🛠️

1. **Data Quality Issues**: Handled missing values and inconsistent formats
2. **AI Output Consistency**: Used few-shot examples and structured prompts
3. **Performance**: Implemented caching for faster responses
4. **UI/UX**: Fixed event selection, triage scoring, and display issues

### Key Takeaways 💡

- **Better data beats fancy AI**: Data quality is foundational
- **Schema is power**: Good structure enables better decisions
- **Iterate quickly**: MVP mindset allowed rapid development
- **Test with real data**: Found issues early by processing actual datasets

---

## Slide 12: Conclusion

### FANUC FirstResponder Delivers

✅ **Complete Solution**
- Data structuring pipeline
- AI maintenance agent
- Working end-to-end demo

✅ **Production-Ready**
- Scalable architecture
- Azure cloud-native
- Security-ready

✅ **Real-World Value**
- Reduces maintenance downtime
- Improves safety through prioritization
- Standardizes maintenance procedures

### Thank You! 🙏

**Questions?**

---

## Appendix: Technical Details

### API Endpoints

- `POST /api/etl/process` - Upload and process files
- `GET /api/events` - List events (with filters)
- `POST /api/triage/score` - Get AI-powered triage analysis
- `POST /api/history/lookup` - Find similar events
- `GET /api/stats` - System statistics

### Data Schema

**Core Fields:**
- `record_id`: UUID
- `timestamp`: ISO 8601
- `joint`: J1-J6 (standardized)
- `collision_type`: hard_impact, soft_collision, emergency_stop
- `force_value`: 0-10,000N
- `severity`: low, med, high, critical
- `recurrence_count`: Deduplication tracking
- `confidence_flag`: Data quality indicator

### FANUC Error Codes Supported

- **SRVO**: Servo errors (torque limits, collisions)
- **TEMP**: Temperature anomalies
- **MOTN**: Motion errors (fence, battery)
- **INTP**: Interpreter errors
- **PROG**: Program errors

---

## Presentation Tips

### Demo Script (2 minutes)

1. **Introduction** (15 sec)
   - "FANUC FirstResponder is an AI-powered diagnostic assistant for robot maintenance"

2. **Upload Data** (20 sec)
   - Show file upload
   - Process a file
   - Show structured output

3. **View Events** (20 sec)
   - Show event list
   - Highlight severity distribution
   - Show statistics

4. **Triage Analysis** (30 sec)
   - Select a critical event
   - Show AI-generated report
   - Highlight 5-section format

5. **Conclusion** (15 sec)
   - "Complete solution: data structuring + AI agent + working demo"

### Key Points to Emphasize

✅ **Schema-first design** - Better structure = better decisions  
✅ **Data quality handling** - Robust error handling  
✅ **Production-ready** - Scalable, secure, cloud-native  
✅ **Real-world applicable** - Works with actual FANUC data

### Common Questions & Answers

**Q: How does this integrate with real robots?**  
A: Currently file-based (hackathon MVP). For production, add data collector service connecting to FANUC Data Server or Ethernet/IP.

**Q: What if Azure AI is unavailable?**  
A: System falls back to heuristic analysis based on severity, recurrence, and error codes.

**Q: How accurate is the AI?**  
A: Uses GPT-4o with few-shot examples for consistent output. Validation shows 75%+ extraction accuracy.

**Q: Can this scale?**  
A: Yes - designed for Azure cloud. Can add database, caching, and horizontal scaling.

---

## Presentation Checklist

- [ ] Practice demo flow (2 minutes)
- [ ] Prepare backup dataset (in case upload fails)
- [ ] Test all features work
- [ ] Prepare answers for likely questions
- [ ] Time yourself (stay under 5 minutes)
- [ ] Remove debug logging
- [ ] Ensure Azure AI credentials are configured
- [ ] Have statistics/metrics ready to show

---

**Good luck with your presentation! 🚀**

