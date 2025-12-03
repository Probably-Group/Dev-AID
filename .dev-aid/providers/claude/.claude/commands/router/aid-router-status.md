---
name: aid-router-status
description: Show current routing configuration, recent activity, and cost breakdown
tags: [routing, status, monitoring, costs]
---

# 📊 Router Status & Monitoring

Display current routing configuration, recent activity, and cost analytics.

## 🎯 Usage

```bash
# Show full status
/aid-router-status

# Show only costs
/aid-router-status --costs

# Show recent routing decisions
/aid-router-status --history

# Show configuration only
/aid-router-status --config
```

## 📋 Output Format

### Full Status Report

```markdown
# 🚀 Dev-AID Router Status

## ⚙️ Current Configuration

**Mode:** {current_mode}
**Status:** {enabled/disabled}
**Config File:** `.dev-aid/config/routing.json`

### Challenger Mode
- **Enabled:** {yes/no}
- **Primary Model:** {claude-sonnet}
- **Challenger Model:** {gemini-flash}
- **Auto-refine:** {HIGH, CRITICAL}
- **Review Triggers:** {auth, crypto, password, token}

### Ensemble Mode
- **Enabled:** {yes/no}
- **Routing Strategy:** {semantic/rule-based}
- **Task Routes:**
  - Massive Context → {gemini-flash}
  - Code Generation → {claude-sonnet}
  - Security Audit → {claude-sonnet}
  - Documentation → {gpt-4o}

### Fallback Chain
1. {claude-sonnet}
2. {gpt-4o}
3. {gemini-flash}

---

## 💰 Cost Analytics

### Today ({date})
- **Total:** ${total_today:.4f}
- **Requests:** {count}
- **Average:** ${avg_per_request:.4f}

### By Model
| Model | Calls | Cost | Avg/Call |
|-------|-------|------|----------|
| claude-sonnet | {calls} | ${cost:.4f} | ${avg:.4f} |
| gemini-flash | {calls} | ${cost:.4f} | ${avg:.4f} |
| gpt-4o | {calls} | ${cost:.4f} | ${avg:.4f} |

### Last 7 Days
```
Day         | Cost    | Requests
------------|---------|----------
2025-11-27  | $2.47   | 23
2025-11-26  | $3.12   | 31
2025-11-25  | $1.85   | 18
...
```

**Budget Status:** {under/over} budget
- Daily Limit: ${daily_limit:.2f}
- Used Today: ${used_today:.4f}
- Remaining: ${remaining:.4f}

---

## 📝 Recent Activity

### Last 10 Routing Decisions

```
Time       | Mode       | Model         | Request                    | Cost
-----------|------------|---------------|----------------------------|-------
14:23:15   | CHALLENGER | claude-sonnet | Implement OAuth2 auth      | $0.083
14:15:42   | ENSEMBLE   | gemini-flash  | Analyze codebase           | $0.012
14:02:18   | SOLO       | claude-sonnet | Fix bug in auth.ts         | $0.045
...
```

---

## 🔧 Quick Actions

To change configuration:
```bash
# Enable challenger mode
/aid-router-enable challenger

# Disable all routing
/aid-router-disable

# Reconfigure
vim .dev-aid/config/routing.json
```

To view logs:
```bash
# Full routing log
tail -f .dev-aid/logs/routing.log

# Cost log
cat .dev-aid/logs/costs.json

# Filter by model
grep "gemini-flash" .dev-aid/logs/routing.log
```

---

## 📊 Model Performance

### Average Latency
- **claude-sonnet:** {avg_latency}ms
- **gemini-flash:** {avg_latency}ms
- **gpt-4o:** {avg_latency}ms

### Success Rate (Last 24h)
- **claude-sonnet:** {success_rate}%
- **gemini-flash:** {success_rate}%
- **gpt-4o:** {success_rate}%

### Most Used Models
1. {model_name}: {usage_count} calls ({percentage}%)
2. {model_name}: {usage_count} calls ({percentage}%)
3. {model_name}: {usage_count} calls ({percentage}%)
```

## 🚀 Implementation

### Step 1: Read Configuration

```python
import json
from datetime import datetime, timedelta

def read_routing_config():
    """Read current routing configuration"""
    with open('.dev-aid/config/routing.json') as f:
        return json.load(f)

config = read_routing_config()
```

### Step 2: Read Cost Data

```python
def read_cost_data():
    """Read cost tracking data"""
    try:
        with open('.dev-aid/logs/costs.json') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

costs = read_cost_data()
```

### Step 3: Parse Routing Logs

```python
import re

def parse_routing_log(limit=10):
    """Parse recent routing decisions from log"""
    decisions = []

    try:
        with open('.dev-aid/logs/routing.log') as f:
            lines = f.readlines()

        # Get last N lines
        for line in lines[-limit:]:
            # Parse log format:
            # 2025-11-27 14:23:15 [CHALLENGER] Request: "..." | Model: claude-sonnet | Cost: $0.083
            match = re.search(
                r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[(\w+)\] .* Model: ([\w-]+) .* Cost: \$(\d+\.\d+)',
                line
            )
            if match:
                decisions.append({
                    "time": match.group(1),
                    "mode": match.group(2),
                    "model": match.group(3),
                    "cost": float(match.group(4))
                })
    except FileNotFoundError:
        pass

    return decisions
```

### Step 4: Calculate Analytics

```python
def calculate_today_stats(costs):
    """Calculate today's cost statistics"""
    today = datetime.now().strftime("%Y-%m-%d")

    if today not in costs:
        return {
            "total": 0.0,
            "count": 0,
            "by_model": {}
        }

    day_data = costs[today]
    total = day_data.get("total", 0.0)
    by_model = day_data.get("by_model", {})

    # Calculate total requests
    count = sum(model["calls"] for model in by_model.values())

    # Calculate average
    avg = total / count if count > 0 else 0.0

    return {
        "total": total,
        "count": count,
        "average": avg,
        "by_model": by_model
    }

def calculate_weekly_stats(costs):
    """Calculate last 7 days statistics"""
    weekly = []

    for i in range(7):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        day_data = costs.get(date, {})
        total = day_data.get("total", 0.0)
        by_model = day_data.get("by_model", {})
        count = sum(model["calls"] for model in by_model.values())

        weekly.append({
            "date": date,
            "cost": total,
            "requests": count
        })

    return weekly

def check_budget_status(costs, config):
    """Check if under/over budget"""
    daily_limit = config.get("cost_limit_per_day", 100.0)
    today_stats = calculate_today_stats(costs)
    used = today_stats["total"]
    remaining = daily_limit - used

    return {
        "daily_limit": daily_limit,
        "used_today": used,
        "remaining": remaining,
        "status": "under" if remaining > 0 else "over"
    }
```

### Step 5: Format Output

```python
def format_status_report(config, costs, recent_decisions):
    """Format complete status report"""

    # Current configuration
    mode = config.get("default_mode", "solo")
    challenger_config = config.get("modes", {}).get("challenger", {})
    ensemble_config = config.get("modes", {}).get("ensemble", {})

    # Cost analytics
    today_stats = calculate_today_stats(costs)
    weekly_stats = calculate_weekly_stats(costs)
    budget_status = check_budget_status(costs, config)

    # Build report
    report = f"""
# 🚀 Dev-AID Router Status

## ⚙️ Current Configuration

**Mode:** {mode.upper()}
**Status:** ENABLED
**Config File:** `.dev-aid/config/routing.json`

### Challenger Mode
- **Enabled:** {"Yes" if challenger_config.get("enabled") else "No"}
- **Primary Model:** {challenger_config.get("primary_model", "claude-sonnet")}
- **Challenger Model:** {challenger_config.get("challenger_model", "gemini-flash")}
- **Auto-refine:** {", ".join(challenger_config.get("auto_refine_on", ["HIGH", "CRITICAL"]))}
- **Review Triggers:** {", ".join(challenger_config.get("review_triggers", []))}

### Ensemble Mode
- **Enabled:** {"Yes" if ensemble_config.get("enabled") else "No"}
- **Routing Strategy:** {ensemble_config.get("routing_strategy", "semantic")}

### Fallback Chain
{chr(10).join(f"{i+1}. {model}" for i, model in enumerate(config.get("fallback_chain", [])))}

---

## 💰 Cost Analytics

### Today ({datetime.now().strftime("%Y-%m-%d")})
- **Total:** ${today_stats["total"]:.4f}
- **Requests:** {today_stats["count"]}
- **Average:** ${today_stats["average"]:.4f}

### By Model
| Model | Calls | Cost | Avg/Call |
|-------|-------|------|----------|
"""

    for model, stats in today_stats["by_model"].items():
        avg = stats["cost"] / stats["calls"] if stats["calls"] > 0 else 0
        report += f"| {model} | {stats['calls']} | ${stats['cost']:.4f} | ${avg:.4f} |\n"

    report += f"""
### Last 7 Days
```
Day         | Cost    | Requests
------------|---------|----------
"""
    for day in weekly_stats:
        report += f"{day['date']}  | ${day['cost']:.2f}   | {day['requests']}\n"

    report += f"""```

**Budget Status:** {budget_status["status"].upper()} budget
- Daily Limit: ${budget_status["daily_limit"]:.2f}
- Used Today: ${budget_status["used_today"]:.4f}
- Remaining: ${budget_status["remaining"]:.4f}

---

## 📝 Recent Activity

### Last {len(recent_decisions)} Routing Decisions

```
Time       | Mode       | Model         | Cost
-----------|------------|---------------|-------
"""

    for decision in reversed(recent_decisions):
        time_only = decision["time"].split()[1]
        report += f"{time_only}   | {decision['mode']:<10} | {decision['model']:<13} | ${decision['cost']:.4f}\n"

    report += """```

---

## 🔧 Quick Actions

To change configuration:
```bash
# Enable challenger mode
/aid-router-enable challenger

# Disable all routing
/aid-router-disable

# Reconfigure manually
vim .dev-aid/config/routing.json
```

To view logs:
```bash
# Full routing log
tail -f .dev-aid/logs/routing.log

# Cost log
cat .dev-aid/logs/costs.json
```
"""

    return report
```

### Step 6: Execute and Display

```python
# Read all data
config = read_routing_config()
costs = read_cost_data()
recent_decisions = parse_routing_log(limit=10)

# Format report
report = format_status_report(config, costs, recent_decisions)

# Display to user
print(report)
```

## 📊 Example Output

```
# 🚀 Dev-AID Router Status

## ⚙️ Current Configuration

**Mode:** SOLO
**Status:** ENABLED
**Config File:** `.dev-aid/config/routing.json`

### Challenger Mode
- **Enabled:** Yes
- **Primary Model:** claude-sonnet
- **Challenger Model:** gemini-flash
- **Auto-refine:** HIGH, CRITICAL
- **Review Triggers:** auth, crypto, password, token, oauth, jwt

### Ensemble Mode
- **Enabled:** No
- **Routing Strategy:** semantic

### Fallback Chain
1. claude-sonnet
2. gpt-4o
3. gemini-flash

---

## 💰 Cost Analytics

### Today (2025-11-27)
- **Total:** $2.47
- **Requests:** 23
- **Average:** $0.1074

### By Model
| Model | Calls | Cost | Avg/Call |
|-------|-------|------|----------|
| claude-sonnet | 18 | $1.85 | $0.1028 |
| gemini-flash | 3 | $0.42 | $0.1400 |
| gpt-4o | 2 | $0.20 | $0.1000 |

### Last 7 Days
```
Day         | Cost    | Requests
------------|---------|----------
2025-11-27  | $2.47   | 23
2025-11-26  | $3.12   | 31
2025-11-25  | $1.85   | 18
2025-11-24  | $2.94   | 27
2025-11-23  | $0.00   | 0
2025-11-22  | $1.56   | 14
2025-11-21  | $2.88   | 25
```

**Budget Status:** UNDER budget
- Daily Limit: $100.00
- Used Today: $2.4700
- Remaining: $97.5300

---

## 📝 Recent Activity

### Last 10 Routing Decisions

```
Time       | Mode       | Model         | Cost
-----------|------------|---------------|-------
14:23:15   | CHALLENGER | claude-sonnet | $0.0830
14:15:42   | ENSEMBLE   | gemini-flash  | $0.0120
14:02:18   | SOLO       | claude-sonnet | $0.0450
13:45:33   | SOLO       | claude-sonnet | $0.0380
13:22:11   | CHALLENGER | claude-sonnet | $0.0950
```
```

---

**Now display the router status above!**

1. Read routing configuration
2. Read cost data
3. Parse routing logs
4. Calculate analytics
5. Format and display report
