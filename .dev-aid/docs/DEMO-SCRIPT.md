# Demo Recording Script

**Duration**: 60 seconds
**Tool**: [asciinema](https://asciinema.org/) or screen recording
**Resolution**: 1920x1080, dark terminal theme

---

## Script

### Scene 1: Setup (0-15s)

```bash
# Show the setup wizard
./setup-dev-aid.sh --wizard-only
```

Narration: "Dev-AID sets up in under a minute. The wizard detects your AI providers and configures routing."

Show: Provider detection, API key prompts, config generation.

### Scene 2: Challenger Mode (15-35s)

```bash
# Run challenger mode — two models, one reviews the other
cd .dev-aid/orchestration
venv/bin/python -m router.cli execute \
  "Implement a rate limiter for the API" \
  --mode challenger --verbose
```

Narration: "Challenger mode sends your request to a primary model, then a second model reviews the output for bugs and security issues."

Show: Primary response, challenger review, issue detection, final refined output.

### Scene 3: Memory Bank (35-50s)

```bash
# Show memory bank context
cat .dev-aid/memory-bank/activeContext.md | head -20
```

Narration: "The memory bank gives every AI assistant instant context about your project — no more repeating yourself."

Show: Active context with project state, key commands, environment setup.

### Scene 4: Cost Tracking (50-60s)

```bash
# Show cost dashboard
venv/bin/python -m router.cli status
```

Narration: "Track costs across all providers. Set budget limits. See which models you're using and how much you're spending."

Show: Daily costs, model breakdown, budget status.

---

## Recording Tips

1. **Pre-populate**: Have API keys configured before recording
2. **Use mock responses**: Set up test fixtures so demos are instant
3. **Clear terminal**: Start with a clean terminal, no history
4. **Font size**: 16pt minimum for readability
5. **Pause**: Brief pauses between scenes for editing cuts
6. **Terminal prompt**: Use a clean prompt like `$` without paths

## Post-Production

- Add captions/subtitles
- Add Dev-AID logo intro (2s)
- Export as GIF for README and MP4 for YouTube
- Upload GIF to repo as `.dev-aid/docs/assets/demo.gif`
