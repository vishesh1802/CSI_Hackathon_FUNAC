"""
Clean and Convert Text Files to CSV
Converts error_logs.txt and system_alerts.txt to structured CSV files
"""

import pandas as pd
import re
from pathlib import Path
from datetime import datetime
import numpy as np

# Directories
DATA_DIR = Path("Hackathon_Data")
CLEANED_DIR = Path("Hackathon_Data_Cleaned")
CLEANED_DIR.mkdir(exist_ok=True)

def parse_error_logs():
    """Parse error_logs.txt and convert to CSV"""
    print("🧹 Cleaning error_logs.txt and converting to CSV...")
    
    with open(DATA_DIR / "error_logs.txt", 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    
    records = []
    
    for line in lines:
        record = {
            'timestamp': None,
            'error_code': None,
            'description': None,
            'raw_line': line
        }
        
        # Pattern 1: [HH:MM:SS] ERROR-CODE Description
        match = re.match(r'\[(\d{2}:\d{2}:\d{2})\]\s+([A-Z]+-\d+)\s+(.+)', line)
        if match:
            time_str = match.group(1)
            record['error_code'] = match.group(2)
            record['description'] = match.group(3)
            # Use today's date with the time
            today = datetime.now()
            try:
                time_obj = datetime.strptime(time_str, '%H:%M:%S').time()
                record['timestamp'] = datetime.combine(today.date(), time_obj).isoformat()
            except:
                record['timestamp'] = today.isoformat()
            records.append(record)
            continue
        
        # Pattern 2: YYYY-MM-DD HH:MM:SS - ERROR-CODE: Description
        match = re.match(r'(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})\s+-\s+([A-Z]+-\d+):\s+(.+)', line)
        if match:
            date_str = match.group(1)
            time_str = match.group(2)
            record['error_code'] = match.group(3)
            record['description'] = match.group(4)
            try:
                dt = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M:%S')
                record['timestamp'] = dt.isoformat()
            except:
                record['timestamp'] = datetime.now().isoformat()
            records.append(record)
            continue
        
        # Pattern 3: YYYY/MM/DD HH:MM ERROR-CODE - Description
        match = re.match(r'(\d{4}/\d{2}/\d{2})\s+(\d{2}:\d{2})\s+([A-Z]+-\d+)\s+-\s+(.+)', line)
        if match:
            date_str = match.group(1).replace('/', '-')
            time_str = match.group(2)
            record['error_code'] = match.group(3)
            record['description'] = match.group(4)
            try:
                dt = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M')
                record['timestamp'] = dt.isoformat()
            except:
                record['timestamp'] = datetime.now().isoformat()
            records.append(record)
            continue
        
        # Pattern 4: ERROR-CODE - Description
        match = re.match(r'([A-Z]+-\d+)\s+-\s+(.+)', line)
        if match:
            record['error_code'] = match.group(1)
            record['description'] = match.group(2)
            record['timestamp'] = datetime.now().isoformat()
            records.append(record)
            continue
        
        # Pattern 5: ERROR-CODE,Description
        match = re.match(r'([A-Z]+-\d+),?\s*(.+)', line)
        if match:
            record['error_code'] = match.group(1)
            record['description'] = match.group(2) if match.group(2) else 'No description'
            record['timestamp'] = datetime.now().isoformat()
            records.append(record)
            continue
        
        # If no pattern matches, try to extract error code
        error_match = re.search(r'([A-Z]+-\d+)', line)
        if error_match:
            record['error_code'] = error_match.group(1)
            record['description'] = line.replace(error_match.group(1), '').strip(' -:,')
            record['timestamp'] = datetime.now().isoformat()
            records.append(record)
        else:
            # Last resort: use entire line as description
            record['description'] = line
            record['timestamp'] = datetime.now().isoformat()
            records.append(record)
    
    # Create DataFrame
    df = pd.DataFrame(records)
    
    # Clean up: remove raw_line column for final output
    df_clean = df[['timestamp', 'error_code', 'description']].copy()
    
    # Fill missing values
    df_clean['error_code'] = df_clean['error_code'].fillna('UNKNOWN')
    df_clean['description'] = df_clean['description'].fillna('No description')
    df_clean['timestamp'] = df_clean['timestamp'].fillna(datetime.now().isoformat())
    
    # Save to CSV
    output_file = CLEANED_DIR / "error_logs.csv"
    df_clean.to_csv(output_file, index=False)
    
    print(f"  ✅ Parsed: {len(df_clean)} records")
    print(f"  ✅ Columns: timestamp, error_code, description")
    print(f"  ✅ Saved to: {output_file}")
    
    # Show sample
    print(f"\n  Sample records:")
    print(df_clean.head(5).to_string(index=False))
    
    return df_clean

def parse_system_alerts():
    """Parse system_alerts.txt and convert to CSV"""
    print("\n🧹 Cleaning system_alerts.txt and converting to CSV...")
    
    with open(DATA_DIR / "system_alerts.txt", 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    
    records = []
    
    for line in lines:
        record = {
            'timestamp': None,
            'severity': None,
            'message': None
        }
        
        # Pattern: HH:MM:SS SEVERITY: Message
        match = re.match(r'(\d{2}:\d{2}:\d{2})\s+([A-Z]+):\s+(.+)', line)
        if match:
            time_str = match.group(1)
            record['severity'] = match.group(2)
            record['message'] = match.group(3)
            
            # Use today's date with the time
            today = datetime.now()
            try:
                time_obj = datetime.strptime(time_str, '%H:%M:%S').time()
                record['timestamp'] = datetime.combine(today.date(), time_obj).isoformat()
            except:
                record['timestamp'] = today.isoformat()
        else:
            # Try alternative pattern without colon
            match = re.match(r'(\d{2}:\d{2}:\d{2})\s+([A-Z]+)\s+(.+)', line)
            if match:
                time_str = match.group(1)
                record['severity'] = match.group(2)
                record['message'] = match.group(3)
                
                today = datetime.now()
                try:
                    time_obj = datetime.strptime(time_str, '%H:%M:%S').time()
                    record['timestamp'] = datetime.combine(today.date(), time_obj).isoformat()
                except:
                    record['timestamp'] = today.isoformat()
            else:
                # Last resort: parse what we can
                parts = line.split(' ', 2)
                if len(parts) >= 3:
                    record['timestamp'] = datetime.now().isoformat()
                    record['severity'] = parts[1] if len(parts) > 1 else 'UNKNOWN'
                    record['message'] = parts[2] if len(parts) > 2 else line
                else:
                    record['timestamp'] = datetime.now().isoformat()
                    record['severity'] = 'UNKNOWN'
                    record['message'] = line
        
        records.append(record)
    
    # Create DataFrame
    df = pd.DataFrame(records)
    
    # Fill missing values
    df['timestamp'] = df['timestamp'].fillna(datetime.now().isoformat())
    df['severity'] = df['severity'].fillna('UNKNOWN')
    df['message'] = df['message'].fillna('No message')
    
    # Save to CSV
    output_file = CLEANED_DIR / "system_alerts.csv"
    df.to_csv(output_file, index=False)
    
    print(f"  ✅ Parsed: {len(df)} records")
    print(f"  ✅ Columns: timestamp, severity, message")
    print(f"  ✅ Saved to: {output_file}")
    
    # Show sample
    print(f"\n  Sample records:")
    print(df.head(5).to_string(index=False))
    
    # Show severity distribution
    print(f"\n  Severity distribution:")
    print(df['severity'].value_counts().to_string())
    
    return df

def main():
    """Main function to clean and convert text files"""
    print("=" * 60)
    print("📋 Cleaning Text Files and Converting to CSV")
    print("=" * 60)
    
    # Clean error_logs.txt
    error_df = parse_error_logs()
    
    # Clean system_alerts.txt
    alerts_df = parse_system_alerts()
    
    print("\n" + "=" * 60)
    print("✅ All text files cleaned and converted to CSV!")
    print("=" * 60)
    print(f"\n📁 Output directory: {CLEANED_DIR}")
    print(f"  - error_logs.csv ({len(error_df)} records)")
    print(f"  - system_alerts.csv ({len(alerts_df)} records)")

if __name__ == "__main__":
    main()

