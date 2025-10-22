#!/bin/bash
# Manage the EpiRay scheduler daemon

PLIST="$HOME/Library/LaunchAgents/com.epiray.scheduler.plist"

case "$1" in
    start)
        echo "Starting EpiRay scheduler..."
        launchctl load "$PLIST"
        echo "✅ Scheduler started"
        echo "Logs: ~/Library/Logs/EpiRay/scheduler.log"
        ;;
    stop)
        echo "Stopping EpiRay scheduler..."
        launchctl unload "$PLIST"
        echo "✅ Scheduler stopped"
        ;;
    restart)
        echo "Restarting EpiRay scheduler..."
        launchctl unload "$PLIST" 2>/dev/null
        sleep 1
        launchctl load "$PLIST"
        echo "✅ Scheduler restarted"
        ;;
    status)
        if launchctl list | grep -q com.epiray.scheduler; then
            echo "✅ Scheduler is RUNNING"
            echo ""
            echo "Recent log entries:"
            tail -n 20 ~/Library/Logs/EpiRay/scheduler.log 2>/dev/null || echo "No logs yet"
        else
            echo "❌ Scheduler is NOT running"
        fi
        ;;
    logs)
        echo "=== Scheduler Logs ==="
        tail -f ~/Library/Logs/EpiRay/scheduler.log
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the scheduler daemon"
        echo "  stop    - Stop the scheduler daemon"
        echo "  restart - Restart the scheduler daemon"
        echo "  status  - Check if scheduler is running"
        echo "  logs    - View scheduler logs (live)"
        exit 1
        ;;
esac
