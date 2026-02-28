# Beta Launch Checklist

**Target**: Dev-AID public beta announcement
**Status**: Pre-launch

---

## Pre-Launch

- [ ] Enable GitHub Discussions on the repo
- [ ] Verify README badges render correctly
- [ ] Record 60-second demo video (see DEMO-SCRIPT.md)
- [ ] Test setup wizard on clean macOS and Ubuntu installs
- [ ] Verify all 3 orchestration modes work with live API keys
- [ ] Create GitHub Release v1.6.0-beta with changelog

## Launch Day

### Hacker News (Show HN)

Post template:

```
Title: Show HN: Dev-AID – Open-source multi-AI orchestrator for coding assistants

Dev-AID routes your coding tasks to the best AI model automatically.
Instead of manually switching between Claude, GPT, and Gemini, it
classifies your task (code gen, security audit, massive context analysis)
and picks the optimal model.

Three modes:
- Solo: single model, your choice
- Ensemble: automatic routing by task type
- Challenger: primary model generates, secondary reviews

It's a CLI tool that integrates with Claude Code, Cursor, and Windsurf
via slash commands. All API keys stay local — no SaaS backend.

1300+ tests, 89% coverage, pre-commit quality hooks.

GitHub: https://github.com/[owner]/Dev-AID
```

- [ ] Post to Hacker News
- [ ] Monitor and respond to comments for first 2 hours

### Reddit

Post to r/ClaudeAI, r/ChatGPTPro, r/LocalLLaMA:

```
Title: I built an open-source tool that routes coding tasks to the best AI model automatically

I got tired of manually switching between Claude, GPT, and Gemini depending
on the task. So I built Dev-AID — it classifies your request and routes to
the optimal model.

Key features:
- Ensemble mode: auto-routes by task type (Gemini for massive context, Claude for code, GPT for docs)
- Challenger mode: one model generates, another reviews
- Works with Claude Code, Cursor, Windsurf
- Local models supported (Ollama, LM Studio)
- All keys stay on your machine

Looking for beta testers! Link in comments.
```

- [ ] Post to r/ClaudeAI
- [ ] Post to r/ChatGPTPro
- [ ] Post to r/LocalLLaMA

### Other

- [ ] Tweet/post announcement with demo GIF
- [ ] Update README "Getting Started" section if needed

## Post-Launch (Week 1)

- [ ] Triage beta feedback issues
- [ ] Respond to all beta waitlist submissions within 48 hours
- [ ] Track GitHub stars and engagement metrics
- [ ] Fix any critical bugs reported by beta users
- [ ] Write follow-up blog post with learnings

---

## Success Metrics

| Metric | Target |
|--------|--------|
| GitHub stars (week 1) | 50+ |
| Beta waitlist signups | 20+ |
| Critical bugs reported | < 3 |
| Setup success rate | > 80% |
