# Hackathon Part I: Build Your Code Scanner

**Focus:** DPI workflow + Active Partner + Feedback Loop + Encoding Priority
**Goal:** Build a working code scanner CLI from scratch — and build the infrastructure to make your agent effective on it

---

## This Is a Pressure Test

This hackathon is intentionally ambitious. The goal is NOT to test your coding skills — it's to test your ability to **leverage your coding agent to ship fast**.

**Expected experience:**
- First 10 minutes: Mild panic ("This is a lot!")
- Minutes 10-30: Finding rhythm ("OK, let the agent handle this")
- Rest of hackathon: Flow state ("This is actually working")

**If you're feeling overwhelmed, that's the point.** The solution isn't working harder — it's applying DPI. Design before building. Plan before implementing. Let the agent iterate while you steer.

---

## Overview

Use your coding agent to build a code scanner that:

1. Walks through any codebase and extracts metrics
2. Analyzes code quality (complexity, duplicates, or smells)
3. Generates reports (JSON + a human-readable format)

**Success = functional scanner + 2-3 analysis features working + infrastructure artifacts created**

You choose the language and tech stack. The agent does the heavy lifting. You steer, verify, and encode.

**What you'll produce:**
- A working CLI tool
- Ground rules for the project
- At least one custom command encoding a workflow from the build
- A feedback loop where the agent validates its own work

---

## Safety Net

**Git: commit early, commit often.** This hackathon moves fast.

- `git init` if starting fresh
- `git add . && git commit -m "message"` after each working milestone
- `git checkout -b experiment` before trying something risky
- `git stash` or `git checkout .` to reset if things break

**Suggested commit points:**
- After basic scanner works
- After each analysis feature
- After report generation works
- Before any major refactor

**Claude Code users:** `/rewind` lets you roll back to any previous prompt — conversation-level checkpoints alongside git's code-level checkpoints. Use both.

**Model strategy:** Consider Opus for design and planning prompts, Sonnet for implementation. The hackathon is long enough for this to matter.

---

## Your Tasks

### Step 1: Bootstrap Your Scanner (~15 min)

Prompt your agent to generate a basic scanner. Specify your preferred language and output format. Apply the DPI workflow: design the interface first, then let the agent implement.

<details>
<summary><strong>Starter Prompt</strong></summary>

```
Create a [Python/Node/Go] code scanner with:
- CLI that accepts a directory path
- Recursive file traversal (skip .git, node_modules, __pycache__)
- Count files by extension and total lines of code
- Output JSON summary: {totalFiles, totalLines, languages: {...}}
- Handle errors gracefully

Make it production-ready with proper structure.
```

</details>

**Before moving on:**
- Did the agent ask clarifying questions, or did it just build? (Compliance Bias check)
- What prompts worked well? What did you have to clarify or retry?

**Commit your work:** `git add . && git commit -m "Basic scanner working"`

---

### Step 2: Add Core Analysis (~45 min)

Choose 2-3 analysis features to add to your scanner.

**Quick approach:** Pick features that interest you and prompt directly.

**DPI approach:** Ask the agent to compare options with trade-offs, then choose. "What are 3 ways to add complexity analysis? Compare trade-offs."

**Alignment check:** Before the agent writes code, ask "Tell me what you're going to build" to catch misunderstandings early.

<details>
<summary><strong>Complexity Analysis Prompt</strong></summary>

```
Extend my scanner to calculate cyclomatic complexity for functions.
Use existing tools or implement a simple version.
Flag functions with complexity > 10.
Add to JSON output.
```

</details>

<details>
<summary><strong>Duplication Detection Prompt</strong></summary>

```
Add code duplication detection to my scanner.
Find duplicate blocks (exact or similar).
Calculate duplication percentage per file.
Show top 5 offenders.
```

</details>

<details>
<summary><strong>Security Scanning Prompt</strong></summary>

```
Add basic security scanning:
- Detect hardcoded secrets (API keys, passwords) using regex
- Flag dangerous functions (eval, exec, etc.)
- Output as security_issues array in JSON
```

</details>

<details>
<summary><strong>Code Smell Detection Prompt</strong></summary>

```
Add code smell detection:
- Long functions (> 50 lines)
- Deep nesting (> 4 levels)
- Long parameter lists (> 5 params)
- Add to JSON with severity ratings
```

</details>

**Before moving on:**
- Which features integrated smoothly vs. required iteration?
- Did you need to provide more context for certain features?
- Did you hit a point where the agent needed a fresh session? (Context Degradation signal)

**Commit your work:** `git add . && git commit -m "Added analysis features"`

---

### Step 3: Generate Reports (~30 min)

Add human-readable output formats to your scanner.

<details>
<summary><strong>HTML Report Prompt</strong></summary>

```
Create an HTML report generator for my scanner.
Include:
- Summary dashboard (total files, lines, quality score)
- File-by-file breakdown table
- 2-3 charts (language distribution, complexity)
- Professional styling

Use the JSON output from my scanner as input.
```

</details>

<details>
<summary><strong>Quality Score Prompt</strong></summary>

```
Add a quality scoring system (0-100) to my scanner:
- Weight complexity (30%), duplication (25%), code smells (25%), docs (20%)
- Output a letter grade (A/B/C/D/F)
- Include in both JSON and HTML reports
```

</details>

**Before moving on:**
- How did the agent handle UI/visualization generation?
- What manual adjustments were needed?

**Commit your work:** `git add . && git commit -m "Report generation working"`

---

## Patterns to Practice

**Design Document** *(from DPI)*
Before prompting for implementation, sketch the interface: what does the CLI accept, what does the JSON output look like, what features are in scope? Even a 2-minute `DESIGN.md` saves 20 minutes of re-prompting.

**Active Partner** *(from DPI)*
The agent defaults to silent compliance. Push back: "What are the trade-offs?" "What would you do differently?" "Push back if something seems wrong."

**Feedback Loop** *(from Evolve Loop)*
Set up a cycle where the agent validates its own output: implement a feature → run the scanner on a real codebase → read the output → fix issues → re-run. The agent should be iterating, not you.

**Encoding Priority** *(from Evolve Loop)*
As you work, notice what you're repeating. A prompt you've typed three times should become a rule. A multi-step workflow should become a command. Encode as you go — don't save it all for the end.

---

## Obstacles to Watch

**Compliance Bias** — The agent says "Sure thing!" even when confused. If it agrees instantly without asking questions, that's a signal. Force alignment: "Tell me what you're going to build before you build it."

**Context Degradation** — After many exchanges, the agent loses track of earlier decisions. Watch for contradictions or repeated mistakes. When you see it: start a fresh session with a summary of where you are.

**Silent Misalignment** — The agent builds confidently in the wrong direction. Confidence does not equal correctness. Run the scanner on real code frequently — real output catches misalignment faster than reading generated code.

---

## Definition of Done

**Core (required):**
- [ ] Functional scanner (walks a codebase, extracts metrics)
- [ ] 2-3 analysis features working
- [ ] JSON + one human-readable report format
- [ ] Ground rules file created (`CLAUDE.md` or `.cursor/rules/`) with at least 2-3 meaningful rules
- [ ] At least one custom command encoding a workflow from the build
- [ ] Feedback Loop applied: agent validates its work against scanner output (implement → scan → fix → rescan)

**Bonus (pick any):**
- [ ] Quality scoring system (0-100, letter grade)
- [ ] 3+ chart visualizations
- [ ] Unit tests for critical paths
- [ ] Model strategy applied (Opus for planning, Sonnet for implementation)
- [ ] `DESIGN.md` with architecture decisions documented
- [ ] Use **Worktrees** to run Parallel Implementations in isolated branches
- [ ] Use **Subagents** to spawn parallel specialists for independent tasks or phases (ask Claude about it)
- [ ] Use **Agent Teams** to coordinate multiple agents via a shared task list (ask Claude to search its latest docs - it's an experimental feature)


---

## Track What Works (and What Doesn't)

Keep a mental or written log as you build:

| Worked Well | Needed Iteration | Failed/Abandoned |
|---|---|---|
| e.g., "File traversal prompt worked first try" | e.g., "Complexity calc needed 3 attempts" | e.g., "Gave up on X, did Y instead" |

**Notice the patterns:**
- When did DPI (designing before implementing) save time?
- When did a fresh session beat continuing a long one?
- When did the Feedback Loop catch something you missed?
- What did you encode as a rule? What should you have encoded earlier?

---

## Milestones

**Milestone 1: Basic Scanner Works (~15 min)**
- Can scan any directory
- Outputs valid JSON
- Handles errors

**Milestone 2: Analysis Added (~45 min)**
- At least 2 analysis features working
- Enhanced JSON output
- Tested on real codebase

**Milestone 3: Reports Generated (~30 min)**
- Human-readable format (HTML or Markdown)
- Includes visualizations
- Looks presentable

**Milestone 4: Infrastructure Created (~remaining time)**
- Ground rules file with 2-3 rules
- Custom command for a workflow
- Feedback loop running

**Reach Milestones 2 and 4 minimum. Milestone 3 is excellent.**

---

## If You're Stuck

<details>
<summary><strong>10 minutes in, nothing working?</strong></summary>

```
I'm trying to build a code scanner in [LANGUAGE].
I need it to: traverse directories, count lines, detect file types.
Generate a complete working starter with CLI interface.
Keep it simple — I'll enhance it later.
```

</details>

<details>
<summary><strong>Analysis feature not integrating?</strong></summary>

```
I have a scanner that outputs JSON. I want to add [FEATURE].
Here's my current JSON output: [PASTE]
Generate code that adds [FEATURE] data to this structure.
```

</details>

<details>
<summary><strong>Report generation broken?</strong></summary>

```
Generate a standalone HTML file that:
- Reads my scanner's JSON output
- Displays a dashboard with [METRICS]
- Uses CDN libraries for visualizations
- Looks professional
Complete single-file solution.
```

</details>

<details>
<summary><strong>Don't know what rules to create?</strong></summary>

Ask the agent:

```
Review our conversation. What ground rules would have
prevented our correction cycles? Suggest 2-3 rules I should
save to [CLAUDE.md / .cursor/rules/].
```

</details>

<details>
<summary><strong>Don't know what to encode as a command?</strong></summary>

Look for a multi-step workflow you've done more than once. Common examples:
- "Run the scanner on this directory, then open the HTML report"
- "Run tests, then run the scanner, then compare quality scores"
- "Validate the scanner's JSON output against the expected schema"

</details>

---

## Detailed Requirements (Reference Only)

Use these to validate your implementation, not to build from scratch.

### Core Capabilities Checklist

- [ ] File system traversal with ignore patterns
- [ ] Multi-language detection (3+ languages)
- [ ] Basic metrics: LOC, comments, blanks
- [ ] Function/class counting
- [ ] 3+ advanced analysis features
- [ ] 2+ report formats (JSON + HTML/Markdown/CSV)
- [ ] Quality scoring (0-100)
- [ ] Visualization (2+ charts/graphs)
- [ ] Unit tests for critical paths

<details>
<summary><strong>Expected JSON Schema</strong></summary>

```json
{
  "scanId": "unique-identifier",
  "timestamp": "ISO-8601-timestamp",
  "repository": {
    "path": "/path/to/repo",
    "totalFiles": 0,
    "totalLines": 0,
    "languages": {}
  },
  "files": [
    {
      "path": "relative/path/to/file",
      "language": "detected-language",
      "metrics": {
        "loc": 0,
        "comments": 0,
        "complexity": 0
      }
    }
  ],
  "qualityScore": 85,
  "grade": "B"
}
```

</details>

---

## Part I Checkpoint

Before moving to Part II, you should have:

- **Core scanner working** — Can scan a codebase and extract metrics
- **Analysis features** — At least 2-3 features implemented
- **Reports** — At least JSON + one human-readable format
- **Infrastructure** — Ground rules + custom command + feedback loop

**Don't have all of this?** That's OK. Move to Part II anyway and build something creative with what you have. The infrastructure DoD items can be completed during Part II.

**Before Part II, ensure you have:**
- A clean git commit of your working Part I code
- Your scanner's JSON output format documented or understood
- Notes on what prompts and workflows worked well

**Context tip:** Part II is a good time for a fresh agent session. Summarize your Part I scanner in 2-3 sentences rather than pasting everything.

