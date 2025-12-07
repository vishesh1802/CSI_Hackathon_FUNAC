# How Severity is Measured

## Overview
Severity is calculated using a **force-based formula** with intelligent fallbacks when force values are not available. The system uses a multi-tier approach to ensure accurate severity classification.

## Primary Method: Force-Based Calculation

Severity is primarily determined by **force values** (in Newtons) measured from collision events:

| Force Value | Severity Level | Description |
|------------|----------------|-------------|
| **< 300N** | `low` | Normal operation, minor impacts |
| **300-600N** | `med` | Moderate collision, requires attention |
| **600-800N** | `high` | Significant collision, immediate action needed |
| **> 800N** | `critical` | Severe collision, emergency response required |

### Formula (from `schema_service.py`):
```python
if force_value < 300:
    return "low"
elif force_value < 600:
    return "med"
else:
    return "high" if force_value < 800 else "critical"
```

## Fallback Methods

When force values are **not available**, the system uses these fallbacks in order:

### 1. Raw Severity Parsing
If the event already has a severity field, it's parsed and standardized:
- `"CRITICAL"` → `critical`
- `"HIGH"` or `"ALERT"` → `high`
- `"MEDIUM"`, `"MED"`, or `"WARN"` → `med`
- `"LOW"`, `"NOTICE"`, or `"INFO"` → `low`

### 2. Error Code Analysis
If no explicit severity is found, error codes are analyzed:
- `SRVO` errors (servo/torque issues) → `med`
- Events with `"COLLISION"` in description → `med`

### 3. Default
If none of the above apply → `low` (safest default)

## Example Scenarios

### Scenario 1: Force Value Available
```
Event: Collision on J3
Force: 645N
Severity: "high" (645N is between 600-800N)
```

### Scenario 2: No Force Value, Raw Severity Present
```
Event: System Alert
Raw Severity: "CRITICAL"
Severity: "critical" (parsed from raw)
```

### Scenario 3: No Force, No Raw Severity, Error Code Present
```
Event: SRVO-160 error
Error Code: "SRVO-160"
Severity: "med" (SRVO errors default to medium)
```

### Scenario 4: Minimal Data
```
Event: Generic log entry
No force, no severity, no error code
Severity: "low" (safe default)
```

## How Severity Affects Triage Scoring

Severity is a **key factor** in triage scoring:

1. **Critical Severity**:
   - Minimum triage score: **80/100**
   - If recurrence > 100: Score boosted to **95/100**
   - Priority always set to **CRITICAL**

2. **High Severity**:
   - Minimum triage score: **60/100**
   - Recurrence boosts score further
   - Priority set to **HIGH** (unless AI suggests CRITICAL)

3. **Medium/Low Severity**:
   - Uses AI-generated score
   - Recurrence can boost score significantly
   - Priority determined by AI or score thresholds

## Force Value Extraction

Force values are extracted from:
1. **Data fields**: `force`, `force_value`, `torque`, `vibration`
2. **Description text**: Patterns like "645N" or "645 N"
3. **Vibration conversion**: High vibration readings converted to approximate force

**Valid Range**: 0-10,000N (outliers are flagged in `notes` field)

## Confidence Flag

The system also tracks **confidence** in severity calculation:

- **`high`**: Has timestamp, joint, force value, and error code (3+ fields)
- **`medium`**: Has 2 of the key fields
- **`inferred`**: Missing critical data, assumptions made

## Summary

**Severity Measurement Priority:**
1. ✅ **Force value** (if available) - Most accurate
2. ✅ **Raw severity parsing** - If present in data
3. ✅ **Error code analysis** - For known error patterns
4. ✅ **Safe default** - `low` if nothing else available

This multi-tier approach ensures that severity is **always calculated**, even with incomplete data, while prioritizing the most accurate method (force-based) when available.

