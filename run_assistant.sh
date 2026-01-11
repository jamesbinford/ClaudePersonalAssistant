#!/bin/bash
# ClaudePersonalAssistant - Daily reminder script
# Runs the personal assistant to check Notion tasks and Dex contacts

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
LOG_FILE="$LOG_DIR/assistant_$(date +%Y-%m-%d).log"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Change to project directory
cd "$SCRIPT_DIR"

echo "========================================" >> "$LOG_FILE"
echo "Running ClaudePersonalAssistant at $(date)" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# Ensure Mailpit is running
if ! docker ps --filter "name=mailpit" --format "{{.Names}}" | grep -q mailpit; then
    echo "Starting Mailpit..." >> "$LOG_FILE"
    docker compose up -d >> "$LOG_FILE" 2>&1
    sleep 2
fi

# Run the assistant
/home/james/.local/bin/uv run python main.py >> "$LOG_FILE" 2>&1

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "Assistant completed successfully at $(date)" >> "$LOG_FILE"
else
    echo "Assistant failed with exit code $EXIT_CODE at $(date)" >> "$LOG_FILE"
fi

echo "" >> "$LOG_FILE"

# Clean up old logs (keep last 30 days)
find "$LOG_DIR" -name "assistant_*.log" -mtime +30 -delete 2>/dev/null || true

exit $EXIT_CODE
