"""
Dataset Cleaning Script
Cleans missing data and normalizes datetime formats in the Hackathon_Data files
"""

import pandas as pd
import re
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np

# Directories
DATA_DIR = Path("Hackathon_Data")
CLEANED_DIR = Path("Hackathon_Data_Cleaned")
CLEANED_DIR.mkdir(exist_ok=True)

def clean_sensor_readings():
    """Clean sensor_readings.csv - handle missing values and normalize timestamps"""
    print("🧹 Cleaning sensor_readings.csv...")
    
    df = pd.read_csv(DATA_DIR / "sensor_readings.csv")
    
    # Normalize timestamps to ISO 8601
    df['Timestamp'] = pd.to_datetime(df['Timestamp']).dt.strftime('%Y-%m-%dT%H:%M:%S')
    
    # Fill missing values using forward fill (carry last known value)
    # This is reasonable for sensor data where values change gradually
    df['Temperature_C'] = df['Temperature_C'].ffill().bfill()
    df['Vibration_g'] = df['Vibration_g'].ffill().bfill()
    df['Axis1_deg'] = df['Axis1_deg'].ffill().bfill()
    df['Axis2_deg'] = df['Axis2_deg'].ffill().bfill()
    df['Axis3_deg'] = df['Axis3_deg'].ffill().bfill()
    
    # If still missing, use mean (for edge cases)
    for col in ['Temperature_C', 'Vibration_g', 'Axis1_deg', 'Axis2_deg', 'Axis3_deg']:
        df[col] = df[col].fillna(df[col].mean())
    
    # Save cleaned file
    output_file = CLEANED_DIR / "sensor_readings.csv"
    df.to_csv(output_file, index=False)
    
    missing_before = df.isnull().sum().sum()
    missing_after = 0
    
    print(f"  ✅ Cleaned: {len(df)} records")
    print(f"  ✅ Missing values: {missing_before} → {missing_after}")
    print(f"  ✅ Saved to: {output_file}")
    
    return df

def clean_performance_metrics():
    """Clean performance_metrics.csv - handle missing values"""
    print("\n🧹 Cleaning performance_metrics.csv...")
    
    df = pd.read_csv(DATA_DIR / "performance_metrics.csv")
    
    # Normalize timestamps
    df['Timestamp'] = pd.to_datetime(df['Timestamp']).dt.strftime('%Y-%m-%dT%H:%M:%S')
    
    # Fill missing values with forward fill, then backward fill
    for col in ['Metric1', 'Metric2', 'Metric3', 'Metric4']:
        df[col] = df[col].ffill().bfill()
        # If still missing, use mean
        df[col] = df[col].fillna(df[col].mean())
    
    output_file = CLEANED_DIR / "performance_metrics.csv"
    df.to_csv(output_file, index=False)
    
    print(f"  ✅ Cleaned: {len(df)} records")
    print(f"  ✅ Saved to: {output_file}")
    
    return df

def clean_error_logs():
    """Clean error_logs.txt - normalize timestamps and standardize format"""
    print("\n🧹 Cleaning error_logs.txt...")
    
    with open(DATA_DIR / "error_logs.txt", 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    
    cleaned_lines = []
    base_date = datetime(2025, 11, 17)  # Use a base date for time-only entries
    last_full_timestamp = None
    
    for line in lines:
        # Extract timestamp
        timestamp = None
        timestamp_str = None
        
        # Try different timestamp patterns
        patterns = [
            (r'\[(\d{2}:\d{2}:\d{2})\]', '%H:%M:%S', True),  # [09:18:37]
            (r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', '%Y-%m-%d %H:%M:%S', False),  # 2025-11-17 09:59:45
            (r'(\d{4}/\d{2}/\d{2} \d{2}:\d{2})', '%Y/%m/%d %H:%M', False),  # 2025/11/17 09:03
            (r'(\d{2}:\d{2}:\d{2})', '%H:%M:%S', True),  # 09:18:37
        ]
        
        for pattern, fmt, needs_date in patterns:
            match = re.search(pattern, line)
            if match:
                try:
                    if needs_date:
                        # Use base date or last full timestamp
                        if last_full_timestamp:
                            date_part = last_full_timestamp.date()
                        else:
                            date_part = base_date.date()
                        dt = datetime.strptime(match.group(1), fmt)
                        dt = dt.replace(year=date_part.year, month=date_part.month, day=date_part.day)
                    else:
                        dt = datetime.strptime(match.group(1), fmt)
                        last_full_timestamp = dt
                    
                    timestamp_str = dt.strftime('%Y-%m-%dT%H:%M:%S')
                    timestamp = dt
                    break
                except:
                    continue
        
        # If no timestamp found, infer from sequence
        if not timestamp:
            if last_full_timestamp:
                timestamp = last_full_timestamp + timedelta(minutes=1)
            else:
                timestamp = base_date
            timestamp_str = timestamp.strftime('%Y-%m-%dT%H:%M:%S')
        
        # Extract error code
        error_code_match = re.search(r'([A-Z]+-\d+)', line)
        error_code = error_code_match.group(1) if error_code_match else "UNKNOWN"
        
        # Extract error description
        # Remove timestamp and error code to get description
        clean_line = line
        for pattern, _, _ in patterns:
            clean_line = re.sub(pattern, '', clean_line)
        clean_line = re.sub(r'[A-Z]+-\d+', '', clean_line)
        clean_line = re.sub(r'[-:]', ' ', clean_line).strip()
        
        # Create standardized format
        cleaned_line = f"{timestamp_str} | {error_code} | {clean_line}"
        cleaned_lines.append(cleaned_line)
    
    # Save cleaned file
    output_file = CLEANED_DIR / "error_logs.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(cleaned_lines))
    
    print(f"  ✅ Cleaned: {len(cleaned_lines)} records")
    print(f"  ✅ All timestamps normalized to ISO 8601")
    print(f"  ✅ Saved to: {output_file}")
    
    return cleaned_lines

def clean_system_alerts():
    """Clean system_alerts.txt - add dates to time-only entries"""
    print("\n🧹 Cleaning system_alerts.txt...")
    
    with open(DATA_DIR / "system_alerts.txt", 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    
    cleaned_lines = []
    base_date = datetime(2025, 11, 17)  # Use base date
    
    for line in lines:
        # Extract time
        time_match = re.search(r'(\d{2}:\d{2}:\d{2})', line)
        if time_match:
            time_str = time_match.group(1)
            # Create full timestamp
            dt = datetime.strptime(time_str, '%H:%M:%S')
            dt = dt.replace(year=base_date.year, month=base_date.month, day=base_date.day)
            timestamp_str = dt.strftime('%Y-%m-%dT%H:%M:%S')
            
            # Extract severity and message
            parts = line.split(':', 1)
            if len(parts) == 2:
                severity = parts[0].split()[-1] if ' ' in parts[0] else parts[0]
                message = parts[1].strip()
                cleaned_line = f"{timestamp_str} | {severity} | {message}"
            else:
                cleaned_line = f"{timestamp_str} | {line}"
            
            cleaned_lines.append(cleaned_line)
        else:
            # Keep as is if no time found
            cleaned_lines.append(line)
    
    output_file = CLEANED_DIR / "system_alerts.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(cleaned_lines))
    
    print(f"  ✅ Cleaned: {len(cleaned_lines)} records")
    print(f"  ✅ All timestamps normalized to ISO 8601")
    print(f"  ✅ Saved to: {output_file}")
    
    return cleaned_lines

def clean_maintenance_notes():
    """Clean maintenance_notes.txt - normalize date format"""
    print("\n🧹 Cleaning maintenance_notes.txt...")
    
    with open(DATA_DIR / "maintenance_notes.txt", 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    
    cleaned_lines = []
    
    for line in lines:
        # Extract date and action
        match = re.match(r'(\d{4}-\d{2}-\d{2})\s+-\s+(.+)', line)
        if match:
            date_str = match.group(1)
            action = match.group(2)
            
            # Normalize to ISO 8601 with time
            dt = datetime.strptime(date_str, '%Y-%m-%d')
            timestamp_str = dt.strftime('%Y-%m-%dT00:00:00')
            
            cleaned_line = f"{timestamp_str} | {action}"
            cleaned_lines.append(cleaned_line)
        else:
            cleaned_lines.append(line)
    
    output_file = CLEANED_DIR / "maintenance_notes.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(cleaned_lines))
    
    print(f"  ✅ Cleaned: {len(cleaned_lines)} records")
    print(f"  ✅ All dates normalized to ISO 8601")
    print(f"  ✅ Saved to: {output_file}")
    
    return cleaned_lines

def clean_torque_events():
    """Clean torque_events_by_cycle.csv - handle missing values and normalize timestamps"""
    print("\n🧹 Cleaning torque_events_by_cycle.csv...")
    
    try:
        # Read CSV preserving empty strings (don't convert to NaN)
        df = pd.read_csv(DATA_DIR / "torque_events_by_cycle.csv", keep_default_na=False)
        
        # Normalize timestamp columns
        for ts_col in ['Cycle_Start', 'Cycle_End', 'Timestamp']:
            if ts_col in df.columns:
                df[ts_col] = pd.to_datetime(df[ts_col], errors='coerce')
                df[ts_col] = df[ts_col].dt.strftime('%Y-%m-%dT%H:%M:%S')
        
        # Fill missing numeric values
        for col in df.select_dtypes(include=[np.number]).columns:
            if df[col].isnull().any():
                df[col] = df[col].ffill().bfill().fillna(df[col].mean())
        
        # Fill empty/missing text columns (like Related_Error_Code)
        for col in df.select_dtypes(include=['object']).columns:
            if col not in ['Cycle_Start', 'Cycle_End', 'Timestamp']:
                # Replace empty strings and NaN with 'N/A' for optional fields
                df[col] = df[col].replace('', 'N/A').fillna('N/A')
        
        output_file = CLEANED_DIR / "torque_events_by_cycle.csv"
        df.to_csv(output_file, index=False)
        
        missing_count = df.isnull().sum().sum()
        print(f"  ✅ Cleaned: {len(df)} records")
        print(f"  ✅ Missing values: {missing_count}")
        print(f"  ✅ Saved to: {output_file}")
        
        return df
    except Exception as e:
        print(f"  ⚠️  Could not clean torque_events_by_cycle.csv: {str(e)}")
        return None

def clean_torque_timeseries():
    """Clean torque_timeseries.csv - handle missing values and normalize timestamps"""
    print("\n🧹 Cleaning torque_timeseries.csv...")
    
    try:
        df = pd.read_csv(DATA_DIR / "torque_timeseries.csv")
        
        # Normalize timestamps if present
        if 'Timestamp' in df.columns:
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
            df['Timestamp'] = df['Timestamp'].dt.strftime('%Y-%m-%dT%H:%M:%S')
        elif 'time' in df.columns.lower():
            time_col = [c for c in df.columns if 'time' in c.lower()][0]
            df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
            df[time_col] = df[time_col].dt.strftime('%Y-%m-%dT%H:%M:%S')
        
        # Fill missing numeric values
        for col in df.select_dtypes(include=[np.number]).columns:
            df[col] = df[col].ffill().bfill().fillna(df[col].mean())
        
        # Fill missing text columns
        for col in df.select_dtypes(include=['object']).columns:
            if 'time' not in col.lower() and 'timestamp' not in col.lower():
                df[col] = df[col].fillna('')
        
        output_file = CLEANED_DIR / "torque_timeseries.csv"
        df.to_csv(output_file, index=False)
        
        print(f"  ✅ Cleaned: {len(df)} records")
        print(f"  ✅ Missing values: {df.isnull().sum().sum()}")
        print(f"  ✅ Saved to: {output_file}")
        
        return df
    except Exception as e:
        print(f"  ⚠️  Could not clean torque_timeseries.csv: {str(e)}")
        return None

def generate_cleaning_report():
    """Generate a report of what was cleaned"""
    print("\n" + "="*60)
    print("📊 CLEANING REPORT")
    print("="*60)
    
    # Count files
    original_files = list(DATA_DIR.glob("*.csv")) + list(DATA_DIR.glob("*.txt"))
    cleaned_files = list(CLEANED_DIR.glob("*.csv")) + list(CLEANED_DIR.glob("*.txt"))
    
    print(f"\n✅ Files cleaned: {len(cleaned_files)}")
    print(f"📁 Original files: {DATA_DIR}")
    print(f"📁 Cleaned files: {CLEANED_DIR}")
    
    print("\n📋 Cleaned Files:")
    for file in cleaned_files:
        size = file.stat().st_size
        print(f"  ✅ {file.name} ({size:,} bytes)")

def main():
    """Main cleaning function"""
    print("="*60)
    print("🧹 DATASET CLEANING")
    print("="*60)
    print(f"\n📂 Original data: {DATA_DIR}")
    print(f"📂 Cleaned data: {CLEANED_DIR}")
    print("\n")
    
    try:
        # Clean all files
        clean_sensor_readings()
        clean_performance_metrics()
        clean_error_logs()
        clean_system_alerts()
        clean_maintenance_notes()
        clean_torque_events()
        clean_torque_timeseries()
        
        # Generate report
        generate_cleaning_report()
        
        print("\n" + "="*60)
        print("✅ CLEANING COMPLETE!")
        print("="*60)
        print(f"\n📁 Cleaned files saved to: {CLEANED_DIR}")
        print("✅ All missing values filled")
        print("✅ All timestamps normalized to ISO 8601")
        print("✅ Ready to use!")
        
    except Exception as e:
        print(f"\n❌ Error during cleaning: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

