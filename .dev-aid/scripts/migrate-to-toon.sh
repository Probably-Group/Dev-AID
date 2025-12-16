#!/bin/bash
# Migrate JSON configs to TOON format
# Part of Dev-AID TOON Integration (v1.3.0)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$HOME/.dev-aid/config"
ORCHESTRATION_DIR="$(dirname "$SCRIPT_DIR")/orchestration"

echo "🔄 Dev-AID Config Migration: JSON → TOON"
echo "======================================="
echo

# Check if config directory exists
if [ ! -d "$CONFIG_DIR" ]; then
    echo "❌ Config directory not found: $CONFIG_DIR"
    echo "   Please run Dev-AID installation first."
    exit 1
fi

# Check if Python venv exists
VENV_PATH="$ORCHESTRATION_DIR/venv"
if [ ! -d "$VENV_PATH" ]; then
    VENV_PATH="$ORCHESTRATION_DIR/.venv"
    if [ ! -d "$VENV_PATH" ]; then
        echo "❌ Python virtual environment not found"
        echo "   Please run setup first."
        exit 1
    fi
fi

# Activate venv
echo "📦 Activating Python environment..."
source "$VENV_PATH/bin/activate"

# Check if TOON module is available
python -c "from toon import encode, decode" 2>/dev/null || {
    echo "❌ TOON module not found"
    echo "   Please install dependencies: cd $ORCHESTRATION_DIR && pip install -r requirements.txt"
    exit 1
}

echo "✅ TOON module ready"
echo

# Create backup directory
BACKUP_DIR="$CONFIG_DIR/backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
echo "💾 Creating backups in: $BACKUP_DIR"

# Function to convert JSON to TOON
convert_config() {
    local json_file="$1"
    local base_name=$(basename "$json_file" .json)
    local toon_file="$CONFIG_DIR/${base_name}.toon"

    if [ ! -f "$json_file" ]; then
        echo "⏭️  Skipping $base_name.json (not found)"
        return
    fi

    echo "🔄 Converting $base_name.json → $base_name.toon..."

    # Backup original
    cp "$json_file" "$BACKUP_DIR/"

    # Convert using Python
    python3 <<EOF
import json
import sys
sys.path.insert(0, '$ORCHESTRATION_DIR')
from toon import encode

with open('$json_file', 'r') as f:
    data = json.load(f)

toon_output = encode(data)

with open('$toon_file', 'w') as f:
    f.write(toon_output)

print(f"   ✓ Created: $base_name.toon")
EOF

    if [ $? -eq 0 ]; then
        echo "   ✅ $base_name.json → $base_name.toon (backup saved)"
    else
        echo "   ❌ Failed to convert $base_name.json"
        return 1
    fi
}

# Convert config files
echo "🔄 Converting configuration files..."
echo

convert_config "$CONFIG_DIR/models.json"
convert_config "$CONFIG_DIR/routing.json"
convert_config "$CONFIG_DIR/orchestration.json"

echo
echo "✅ Migration complete!"
echo
echo "📋 Summary:"
echo "   • Backups saved to: $BACKUP_DIR"
echo "   • TOON files created in: $CONFIG_DIR"
echo "   • Original JSON files preserved"
echo
echo "💡 Config loader will automatically use TOON files when available"
echo "   To revert: rm $CONFIG_DIR/*.toon"
echo
echo "📊 Token savings: ~40-60% on config-heavy prompts"
echo

# Show file sizes
echo "📏 File size comparison:"
for json_file in "$CONFIG_DIR"/models.json "$CONFIG_DIR"/routing.json "$CONFIG_DIR"/orchestration.json; do
    if [ -f "$json_file" ]; then
        base_name=$(basename "$json_file" .json)
        toon_file="$CONFIG_DIR/${base_name}.toon"
        if [ -f "$toon_file" ]; then
            json_size=$(wc -c < "$json_file" | tr -d ' ')
            toon_size=$(wc -c < "$toon_file" | tr -d ' ')
            savings=$((100 - (toon_size * 100 / json_size)))
            echo "   $base_name: ${json_size}B (JSON) → ${toon_size}B (TOON) | ${savings}% smaller"
        fi
    fi
done

echo
echo "✨ Done! Your Dev-AID is now using TOON format for better token efficiency."
