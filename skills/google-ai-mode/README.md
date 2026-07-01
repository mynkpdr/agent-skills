# Google AI Mode Skill

A Claude Code skill that queries Google's AI Mode search (`udm=50`) using a real, persistent Chrome browser, and returns the AI-generated answer as Markdown with numbered citations.

## Requirements

- Claude Code CLI, run locally — the web UI sandbox has no network access, which browser automation needs
- Python 3.8+
- Google Chrome (installed automatically on first run if not already present)

## Installation

Copy this folder into your Claude Code skills directory:

```bash
cp -r google-ai-mode ~/.claude/skills/google-ai-mode
```

On first use, `scripts/run.py` automatically creates an isolated `.venv`, installs the dependencies in `requirements.txt`, and installs Chrome if it's missing.

## Usage

```bash
python scripts/run.py search.py --query "Your search query"
```

| Flag | Description |
|------|-------------|
| `--query <text>` | Search query (required) |
| `--show-browser` | Run with a visible browser window (needed to solve a CAPTCHA) |
| `--save` | Save the result to the cache folder instead of the current directory |
| `--debug` | Write a detailed log to the cache folder |
| `--json` | Also save the raw result as JSON |
| `--output <path>` | Save to a specific file path |

Example:

```bash
python scripts/run.py search.py --query "React hooks best practices 2026 (useState, useEffect, custom hooks). Include code examples." --save --debug
```

See `SKILL.md` for query-optimization guidance and the full CLI/exit-code reference.

## How It Works

1. Launches a persistent Chrome profile (reused across runs, not recreated each time — this is what avoids repeat CAPTCHAs)
2. Navigates to `google.com/search?udm=50&hl=en&q=...`
3. Waits for Google's AI Overview to finish generating
4. Extracts the answer and its citations via injected JavaScript
5. Converts the HTML to Markdown and appends a numbered source list

## First-Run CAPTCHA

Google may show a CAPTCHA the first time a fresh browser profile queries it. Re-run with `--show-browser`, solve it once, and the persistent profile keeps future searches CAPTCHA-free.

## Data Storage

The skill's code and Python environment live in this folder. Everything else — browser profile, saved results, debug logs — lives outside it, in a per-OS cache directory, so it survives skill updates/reinstalls and is never at risk of being committed to git:

```
~/.cache/google-ai-mode-skill/            (macOS: ~/Library/Caches/google-ai-mode-skill/, Windows: %LOCALAPPDATA%\google-ai-mode-skill\)
├── chrome_profile/   Persistent browser profile (cookies, session)
├── results/          Saved search results (--save)
└── logs/             Debug logs (--debug)
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Repeated CAPTCHAs | Re-run with `--show-browser`, solve it, space out searches |
| Browser won't launch / acting up | Delete `~/.cache/google-ai-mode-skill/chrome_profile` and retry |
| Dependency errors | Delete `.venv` in this folder, then run again |
| No AI overview found | Rephrase the query with more specificity (see `SKILL.md`'s query template) |
| Wrong response language | Google can still localize by IP/region despite the `hl=en` parameter; try again later or from a different network |
| "AI Mode not available" | Google AI Mode isn't available in your account's region |

## Limitations

- Local Claude Code only — the web UI sandbox can't reach the network for browser automation
- First query on a fresh profile may need a manual CAPTCHA solve
- Automating a real browser against Google Search, with anti-detection measures, sits in a gray area of Google's Terms of Service — this is unsupported scraping, not an official API. Use reasonable query frequency, and verify important claims via the cited sources rather than treating the answer as ground truth.
