#!/usr/bin/env python3
"""
Automated scheduler for Stingray monitoring
Runs scans on schedule and when HackRF is detected
"""

import os
import json
import time
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

SCHEDULE_FILE = os.path.expanduser('~/Library/Application Support/EpiRay/schedule.json')
LAST_RUN_FILE = os.path.expanduser('~/Library/Application Support/EpiRay/last_run.json')

def ensure_dirs():
    """Ensure config directories exist"""
    os.makedirs(os.path.dirname(SCHEDULE_FILE), exist_ok=True)

def load_schedule():
    """Load schedule configuration"""
    ensure_dirs()
    if os.path.exists(SCHEDULE_FILE):
        with open(SCHEDULE_FILE, 'r') as f:
            return json.load(f)
    return {
        'enabled': False,
        'daily_time': '20:00',  # 8 PM default
        'duration_minutes': 60,
        'interval_seconds': 120
    }

def save_schedule(schedule):
    """Save schedule configuration"""
    ensure_dirs()
    with open(SCHEDULE_FILE, 'w') as f:
        json.dump(schedule, f, indent=2)

def load_last_run():
    """Load last run timestamp"""
    if os.path.exists(LAST_RUN_FILE):
        with open(LAST_RUN_FILE, 'r') as f:
            data = json.load(f)
            return datetime.fromisoformat(data['timestamp'])
    return None

def save_last_run():
    """Save current timestamp as last run"""
    ensure_dirs()
    with open(LAST_RUN_FILE, 'w') as f:
        json.dump({'timestamp': datetime.now().isoformat()}, f)

def is_hackrf_available():
    """Check if HackRF is connected and not in use"""
    try:
        result = subprocess.run(
            ['hackrf_info'],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except:
        return False

def kill_hackrf_processes():
    """Kill any running HackRF processes"""
    try:
        subprocess.run(['killall', 'hackrf_sweep'], stderr=subprocess.DEVNULL)
        subprocess.run(['killall', 'hackrf_info'], stderr=subprocess.DEVNULL)
        time.sleep(1)
    except:
        pass

def run_monitoring(duration_minutes, interval_seconds):
    """Run monitoring scan"""
    print(f"Starting monitoring: {duration_minutes} min, {interval_seconds}s intervals")
    
    # Kill any existing HackRF processes
    kill_hackrf_processes()
    
    # Wait a bit for device to be ready
    time.sleep(2)
    
    # Run the tracking script
    try:
        subprocess.run(
            ['./track-movement.sh', str(duration_minutes), str(interval_seconds)],
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        save_last_run()
        print("Monitoring complete!")
        return True
    except Exception as e:
        print(f"Error running monitoring: {e}")
        return False

def should_run_now(schedule):
    """Check if we should run now based on schedule"""
    if not schedule['enabled']:
        return False
    
    # Parse scheduled time
    hour, minute = map(int, schedule['daily_time'].split(':'))
    now = datetime.now()
    scheduled_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    # Check if we're within 5 minutes of scheduled time
    time_diff = abs((now - scheduled_time).total_seconds())
    if time_diff <= 300:  # Within 5 minutes
        # Check if we already ran today
        last_run = load_last_run()
        if last_run is None or last_run.date() < now.date():
            return True
    
    return False

def check_and_run():
    """Check if we should run and execute if needed"""
    schedule = load_schedule()
    
    if should_run_now(schedule):
        if is_hackrf_available():
            print("Running scheduled monitoring...")
            run_monitoring(schedule['duration_minutes'], schedule['interval_seconds'])
        else:
            print("HackRF not available, will retry...")
    
def daemon_loop():
    """Main daemon loop"""
    print("Scheduler daemon started")
    
    while True:
        try:
            check_and_run()
            time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\nScheduler stopped")
            break
        except Exception as e:
            print(f"Error in daemon loop: {e}")
            time.sleep(60)

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'daemon':
        daemon_loop()
    else:
        # One-time check
        check_and_run()
