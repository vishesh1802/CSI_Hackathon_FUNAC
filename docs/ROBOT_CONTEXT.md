# Robot-Specific Context

## Robot Type: FANUC Industrial Robot

The system is designed specifically for **FANUC industrial robots**, as evidenced by:

### FANUC Error Codes in Dataset

| Error Code | Type | Description |
|------------|------|-------------|
| **SRVO-160** | Servo Error | Torque limit reached |
| **SRVO-161** | Servo Error | Torque limit reached |
| **SRVO-005** | Servo Error | Torque limit reached |
| **SRVO-050** | Servo Error | Torque limit reached |
| **SRVO-062** | Servo Error | Torque limit reached |
| **SRVO-324** | Servo Error | Collision detected |
| **TEMP-100** | Temperature Error | Singularity condition / Overtravel |
| **MOTN-019** | Motion Error | Fence open / Battery Zero Alarm |
| **INTP-105** | Interpreter Error | Run request failed / Collision detected |
| **PROG-048** | Program Error | Shift released / Collision detected |

### Robot Joints (J1-J6)

FANUC robots typically have 6 joints:
- **J1**: Base rotation
- **J2**: Shoulder
- **J3**: Elbow
- **J4**: Wrist roll
- **J5**: Wrist pitch
- **J6**: Wrist yaw

The system maps `axis1-6` → `J1-J6` automatically.

### Robot-Specific Data

1. **Sensor Readings**: Temperature, vibration, and joint angles (degrees)
2. **Error Logs**: FANUC-specific error codes and messages
3. **System Alerts**: Robot operational alerts (vibration, temperature, servo)
4. **Maintenance Notes**: Robot maintenance actions (belts, motors, calibration, lubrication)

## How the System Handles Robot Data

### 1. **FANUC Error Code Recognition**
The schema service maps FANUC error codes to standardized descriptions:
```python
ERROR_CODE_MAP = {
    "SRVO-160": "Torque limit reached",
    "SRVO-324": "Collision detected",
    "TEMP-100": "Temperature anomaly",
    # ... etc
}
```

### 2. **Joint Standardization**
All joint references are normalized to FANUC standard (J1-J6):
- `axis1` → `J1`
- `axis2` → `J2`
- etc.

### 3. **Robot-Specific Maintenance Actions**
The system recognizes robot maintenance terminology:
- Belt checking/replacement
- Motor replacement
- Joint calibration
- Lubrication
- Sensor cleaning
- Wiring inspection

### 4. **Force Value Validation**
Robot collision forces are validated:
- Range: 0-10,000N (typical for industrial robots)
- Severity based on force: <300N (low), 300-600N (med), >600N (high/critical)

## Robot-Specific Enhancements

### Current Implementation ✅
- ✅ FANUC error code mapping
- ✅ Joint standardization (J1-J6)
- ✅ Robot maintenance action recognition
- ✅ Force value validation for collisions
- ✅ Robot-specific severity calculation

### Potential Enhancements 🔮
1. **FANUC Error Code Database**: Expand error code meanings
2. **Joint-Specific Recommendations**: Different actions for different joints
3. **Robot Model Detection**: Identify specific FANUC model
4. **Payload Considerations**: Factor in robot payload for force calculations
5. **Safety Standards**: Include FANUC safety standards in recommendations

## Robot Maintenance Context

The AI agent generates maintenance recommendations specifically for:
- **Industrial robot technicians**
- **FANUC robot maintenance procedures**
- **Safety-critical operations**
- **Production line impact**

All recommendations follow robot maintenance best practices and safety protocols.

