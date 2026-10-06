# AI Usage Log

Course policy: any use of AI (for ideas, text, code or anything else) must be cited in your
README, saying **which tool**, **what it was used for**, and **how you used the output**.
Keep this log as you go, then copy the summary into your README.

> 📖 **Book:** "Record where you used AI and how you verified it", [§13.2.10](https://www.swebook.org/chapters/13-ai-across-the-lifecycle/index.html#13210-the-team-project-appendix-a).

## Summary (paste into README)
- **Tool:** Codex (Personal, model: GPT-5.6 Sol low 
- **Used for:** Test-first implementation of the tasks in specs/001-movie-listings/tasks.md, one task at a time
- **How I used the output:** I read every diff and ran the test suite myself before committing each task. I wrote the commit messages, decided when a change was in scope, and applied the migration to my dev database when the page broke.

## Log
| Date | Feature / task | What I asked Codex | What I kept, changed or rejected |
| 2026-10-06 | 001 movie listings, T1–T15 | Implement each task from tasks.md test-first, one at a time | Kept all generated code; verified each diff and test run myself |
