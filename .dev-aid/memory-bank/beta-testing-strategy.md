# Dev-AID Beta Testing Strategy (Snowball Effect)

*Created: 2026-02-10*

## Current Plan Assessment (LinkedIn + X + GitHub username)

The friction is high: someone sees the post, has to comment their username publicly, then wait for... what? An email? A repo invite? Each step loses people. And there's zero incentive for them to share it further.

## Snowball Mechanics

The core problem: **why would a beta tester tell their friends?** You need a mechanism where sharing is either required or naturally rewarding.

**Waitlist with priority queue.** Set up a simple landing page (even a GitHub Pages site on the Dev-AID repo). "Join the beta" form collects GitHub username + email. After signup, they get a unique referral link. Each referral bumps them up the queue. "You're #47. Share your link to move up." This is the classic viral waitlist pattern (Superhuman, Linear, etc.). Tools like [Waitlist.ing](https://waitlist.ing) or [LaunchList](https://launchlist.net) do this out of the box for free/cheap.

**GitHub star as social proof trigger.** Require starring the repo to join. Stars are public -- their followers see it in their GitHub feed. This is passive snowball. "Star the repo + fill the form" is a common open-source beta pattern.

**"Beta Tester" badge.** People love visible status. Promise contributors a badge in the README, a `beta-tester` label on their GitHub profile (via a team invite to a `Probably-Group/beta-testers` team), or a role in Discord. Social currency drives sharing.

## Better Recruitment Channels (Beyond LinkedIn/X)

| Channel | Why | How |
|---------|-----|-----|
| **Reddit** (`r/programming`, `r/devtools`, `r/ChatGPTCoding`, `r/ClaudeAI`, `r/LocalLLaMA`) | High-intent devs, discussion-driven | "Show HN"-style post, not an ad. Show the problem you solve. |
| **Hacker News** (Show HN) | Massive reach if it catches, dev-heavy audience | "Show HN: Dev-AID -- memory bank + multi-model routing for AI coding assistants" |
| **Dev.to / Hashnode** | Write a post about the *problem*, not the tool. "How I stopped repeating context to Claude every session" | Soft CTA at the end: "We're opening beta" |
| **Discord communities** | Claude Code Discord, Cursor community, AI coding discords | Genuine participation first, then share when relevant |
| **GitHub Discussions on popular repos** | Where your target users already hang out | Only if genuinely relevant (don't spam) |
| **Twitter/X threads** | Not just "join our beta" -- show a compelling demo | Screen recording of Dev-AID in action: before/after comparison. Threads get more reach than single posts. |

The LinkedIn/X post alone won't snowball. A **demo video or GIF** will. Show a 30-second clip: "Session 1: Claude doesn't know my patterns. Session 2 with Dev-AID: Claude writes code matching my conventions from the first prompt." Visual proof spreads.

## Communication During Beta

**Open the Discord -- but make it the reward.** Don't keep it invite-only as a restriction. Make it invite-only as *exclusivity*. "Beta testers get access to our Discord." This makes the Discord access itself part of the value. Auto-send a Discord invite link when someone is accepted to the beta.

For structured feedback, use **GitHub Discussions** (not Issues):

| Channel | Purpose |
|---------|---------|
| **GitHub Discussions -> Q&A** | Setup problems, "how do I..." |
| **GitHub Discussions -> Ideas** | Feature requests, suggestions |
| **GitHub Discussions -> Show & Tell** | Testers sharing their setups (this is gold for social proof) |
| **GitHub Issues** | Actual bugs only |
| **Discord** | Real-time chat, quick questions, community feel |

GitHub Discussions is already built into your repo -- you just need to enable it. It's searchable, threaded, and doesn't require another account.

## Suggested Beta Flow

```
1. User sees post/thread/article
   |
   v
2. Lands on page: "Join Dev-AID Beta"
   - Star the repo
   - Enter GitHub username + email
   - Get referral link + queue position
   |
   v
3. Accepted (in waves, e.g. 20/week)
   - Added to Probably-Group/beta-testers team (badge)
   - Discord invite link
   - Onboarding email with setup guide + feedback expectations
   |
   v
4. During beta
   - Discord for chat
   - GitHub Discussions for structured feedback
   - GitHub Issues for bugs
   - Weekly "What did you try this week?" thread (keeps engagement)
   |
   v
5. Tester shares experience
   - "Show & Tell" in Discussions
   - Their own social posts (encourage with: "Tag us and we'll repost")
   - Referral link bumps their friends up the queue
```

## What Actually Causes Snowball

Three things:

1. **A demo that makes people say "I need this."** Invest time in a 60-second screen recording showing the pain -> solution. This single asset drives everything.

2. **Making sharing the path of least resistance.** Referral link + queue position. People will post it themselves.

3. **Letting beta testers feel like insiders, not guinea pigs.** "Beta tester" badge, Discord access, "your feedback shaped this feature" callouts in changelogs. People evangelize things they feel ownership over.

The LinkedIn/X post is fine as *one* channel, but without a landing page, referral mechanic, and a compelling demo -- it's just a post that gets a few likes and dies in the algorithm.
