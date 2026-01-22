# Core Implementation Patterns

## 1. Landing Page Copy Structure

### Above the Fold

```html
<!-- Hero Section Pattern -->
<section class="hero">
  <h1>[Primary Headline - Promise/Benefit]</h1>
  <p class="subheadline">[Supporting detail or how it works]</p>
  <a class="cta-primary">[Action + Value]</a>
  <p class="trust-element">[Social proof snippet]</p>
</section>
```

**Example**:
```html
<h1>Build Websites 10x Faster</h1>
<p class="subheadline">AI-powered design tools that turn your ideas into production-ready code.</p>
<a class="cta-primary">Start Building Free</a>
<p class="trust-element">Join 50,000+ developers shipping faster</p>
```

### Problem-Agitation-Solution (PAS)

```markdown
## [Problem Statement - What's broken?]
[1-2 sentences describing the pain point your audience faces]

## [Agitation - Why it matters]
[Dig into the consequences of not solving this problem]

## [Solution - How you fix it]
[Introduce your product/service as the answer]
```

**Example**:
```markdown
## Spending hours on repetitive tasks?
Most teams waste 40% of their week on work that could be automated.

## Every hour lost is money down the drain
While you're doing busywork, competitors are shipping features and closing deals.

## Automate the boring stuff
Our platform handles the repetitive work so your team can focus on growth.
```

---

## 2. Product Description Patterns

### Feature-Benefit-Proof (FBP)

```markdown
**[Feature Name]**
[One sentence describing what it does]
[One sentence explaining why that matters to the user]
[Proof point: stat, testimonial, or example]
```

**Example**:
```markdown
**Real-Time Collaboration**
Work together with your team on the same document simultaneously.
No more version conflicts or waiting for files - ship faster together.
"Cut our review cycles from 3 days to 3 hours." - Sarah, Design Lead at Acme
```

### The "So What?" Test

For every feature, ask "So what?" until you reach an emotional benefit:

```
Feature: 256-bit encryption
So what? → Your data is secure
So what? → Hackers can't access your info
So what? → You can sleep at night knowing your business is protected
```

Use the final answer in your copy:
> "256-bit encryption means you can sleep at night knowing your business data is protected."

---

## 3. Email Copy Patterns

### Subject Line Formulas

```
[Number] + [Timeframe]: "3 ideas for your Monday"
Question: "Quick question about [topic]"
Curiosity Gap: "The mistake 90% of [audience] make"
Personal: "Thought of you when I saw this"
Urgency: "[First Name], ending tonight"
```

### Email Body Structure

```markdown
[Opening Hook - 1 sentence, personal or intriguing]

[Problem/Context - Why are you writing?]

[Value - What's in it for them?]

[Single CTA - One clear action]

[Sign-off]
```

**Example**:
```markdown
Hey [Name],

Noticed you downloaded our guide last week - hope it was helpful!

Quick question: what's your biggest challenge with [topic] right now?

I ask because we just published a case study showing how [Company] solved [specific problem] and saw [specific result].

Want me to send it over?

[Name]
```

---

## 4. About Page Patterns

### The Story Arc

```markdown
## Our Story

**The Beginning** (Where we started)
[Founder story, origin, initial problem we faced]

**The Turning Point** (What changed)
[Insight, breakthrough, decision to build the solution]

**The Mission** (Where we're going)
[Vision, purpose, what drives us today]
```

### Values Section

```markdown
## What We Believe

### [Value 1: Single Word]
[1-2 sentence explanation of what this means in practice]

### [Value 2: Single Word]
[1-2 sentence explanation]

### [Value 3: Single Word]
[1-2 sentence explanation]
```

**Example**:
```markdown
### Transparency
We share our metrics, our roadmap, and our reasoning publicly. No black boxes.

### Simplicity
We ruthlessly cut complexity. If it's not essential, it's out.

### Speed
We ship fast and iterate. Done is better than perfect.
```

---

## 5. Testimonial Patterns

### The STAR Format

```markdown
**Situation**: What was the context/problem?
**Task**: What did they need to accomplish?
**Action**: How did our product/service help?
**Result**: What measurable outcome did they achieve?
```

### Testimonial Template

```markdown
"[Specific result or transformation achieved].

Before [product], we [describe previous pain point].
Now, [describe new positive state].

[Product] has been [emotional adjective] for our [team/business/life]."

— [Full Name], [Title], [Company]
```

**Example**:
```markdown
"We cut our deployment time from 2 hours to 15 minutes.

Before DevOps Pro, we dreaded release days. The team would stay late,
things would break, and we'd spend weekends firefighting.

Now, deploys are a non-event. The team actually looks forward to shipping.

DevOps Pro has been transformative for our engineering culture."

— Maria Chen, VP Engineering, TechCorp
```

---

## 6. CTA Placement Patterns

### The Rule of Three

Place CTAs at three strategic points:
1. **Above the fold** - For ready-to-convert visitors
2. **Mid-page** - After presenting key benefits
3. **Bottom of page** - After full persuasion sequence

### CTA Variations by Intent

```markdown
High Intent (Ready to buy):
- "Start Free Trial"
- "Get Started Now"
- "Buy Now"

Medium Intent (Interested, needs more):
- "See How It Works"
- "View Demo"
- "Compare Plans"

Low Intent (Just exploring):
- "Learn More"
- "Download Guide"
- "Join Newsletter"
```

### Button Copy Formula

```
[Action Verb] + [Your/My] + [Desired Outcome]

Examples:
- "Start My Free Trial"
- "Get Your Custom Report"
- "Claim My Discount"
- "Download Your Guide"
```

---

## 7. Pricing Page Copy

### Plan Naming

```markdown
❌ Basic, Pro, Enterprise (generic)
✅ Starter, Growth, Scale (aspirational)
✅ Individual, Team, Organization (audience-based)
```

### Feature List Copy

```markdown
❌ "10GB storage" (feature)
✅ "10GB storage - enough for 10,000 documents" (feature + context)

❌ "Priority support" (vague)
✅ "Priority support - 2-hour response time guaranteed" (specific)
```

### Pricing Page CTA Hierarchy

```markdown
Free/Low Tier: "Get Started Free"
Recommended Tier: "Start [Plan Name] Trial" (highlight this)
Enterprise: "Contact Sales" or "Talk to Us"
```

---

## 8. Error & Empty State Copy

### Error Message Pattern

```markdown
[What happened] + [Why it matters/next step]

❌ "Error 404"
✅ "Page not found. It might have moved - try searching or go home."

❌ "Invalid input"
✅ "Please enter a valid email address (e.g., you@example.com)"
```

### Empty State Pattern

```markdown
[Acknowledge the empty state] + [Guide to first action]

❌ "No items"
✅ "No projects yet. Create your first project to get started."

❌ "Empty inbox"
✅ "All caught up! You've processed all your messages."
```

---

## 9. Microcopy Patterns

### Form Labels

```markdown
❌ "Name" (ambiguous)
✅ "Full name" or "First name" (specific)

❌ "Email" (bare)
✅ "Work email" (for B2B) or "Email address" (complete)
```

### Placeholder Text

```markdown
❌ "Enter text here" (useless)
✅ "e.g., john@company.com" (example)
✅ "Search for products..." (contextual)
```

### Helper Text

```markdown
Password: "At least 8 characters with one number"
File upload: "PDF or DOC, max 10MB"
Search: "Try searching by name, email, or company"
```

---

## 10. Trust-Building Copy

### Security & Privacy

```markdown
"Your data is encrypted with bank-level security (256-bit SSL)"
"We never share your information with third parties"
"SOC 2 Type II certified"
"GDPR compliant"
```

### Social Proof Elements

```markdown
Customer count: "Trusted by 10,000+ teams worldwide"
Logo wall: "Companies like [Brand], [Brand], and [Brand] trust us"
Ratings: "4.9/5 stars from 500+ reviews on G2"
Media mentions: "Featured in TechCrunch, Forbes, and Wired"
```

### Risk Reversal

```markdown
"30-day money-back guarantee - no questions asked"
"Cancel anytime - no long-term contracts"
"Free trial - no credit card required"
"If you're not satisfied, we'll refund your last 3 months"
```
