# Claude skills

The Claude skills SHOTOKAN reviews run on. A skill is a folder with a `SKILL.md`: instructions Claude loads when a task matches its description.

## In this folder
| Skill | What it does |
|---|---|
| [sf6-replay-analysis](sf6-replay-analysis/SKILL.md) | The review method: reading REFramework captures (and video), the analyzer, frame data, habits, the history database, review levels, logging. Loads the other skills. |
| [sf6-review-dashboard](sf6-review-dashboard/SKILL.md) | Dashboard format: datasets, page sections, the Story of the Set, local and standalone copies. |
| [replay-review-prediction](replay-review-prediction/SKILL.md) | Predict each set before reviewing it, then grade the prediction. |
| [sf6-drive-efficiency](sf6-drive-efficiency/SKILL.md) | Value of Drive and super spending on offense and defense. |

Links to the author's private dashboards and sheets are replaced with placeholders. Point them at your own.

## Coaching lenses (`skills/local/`, not in the repo)
The review method also loads coaching "lens" skills: paraphrased summaries of E.X. Dojo seminars, Maj's Street Fighter Footsies Handbook, Infil's Fighting Game Glossary, and notes from private coaching. They stay out of the public repo for now (`skills/local/` is in `.gitignore`). The list of what each one covers is in `SKILLS.md` (also local only).

If you have them, put each in `skills/local/<name>/SKILL.md`. Without them the core skills still run; findings just won't be tagged with those lenses.

## Installing
- **Claude.ai / desktop app:** Settings → Capabilities → Skills → upload each skill folder (zipped).
- **Claude Code:** copy the folders into `~/.claude/skills/` (or a project's `.claude/skills/`).
