# Claude skills

The Claude skills SHOTOKAN reviews run on. A skill is a folder with a `SKILL.md`: instructions Claude loads when a task matches its description.

## In this folder
| Skill | What it does |
|---|---|
| [sf6-replay-analysis](sf6-replay-analysis/SKILL.md) | The review method: reading REFramework captures (and video), the analyzer, frame data, habits, the history database, review levels, logging. Loads the other skills. |
| [sf6-review-dashboard](sf6-review-dashboard/SKILL.md) | Dashboard format: datasets, page sections, the Story of the Set, local and standalone copies. |
| [replay-review-prediction](replay-review-prediction/SKILL.md) | Predict each set before reviewing it, then grade the prediction. |
| [sf6-drive-efficiency](sf6-drive-efficiency/SKILL.md) | Value of Drive and super spending on offense and defense. |
| [sf6-coach-shog](sf6-coach-shog/SKILL.md) | Coach .shog's own rules and theories: 2MK hit-confirm limits, judging wake-up options, when taking a throw is correct, read vs react and reaction frames, conditioning, risk vs skill gap, Plant and Harvest and the M. Bison Scissor Kicks theory (both credited to PortaJon, Arizona FGC), the Economy of Buttons (James Chen and PortaJon). |
| [sf6-footsies-handbook-maj](sf6-footsies-handbook-maj/SKILL.md) | Maj's *Street Fighter Footsies Handbook* (sonichurricane.com): Elements 1-35, Rules 1-5, the projectile and avoiding-footsies supplements and the epilogue, paraphrased with SF6 translations. A lens the review loads. |
| [sf6-fgc-glossary](sf6-fgc-glossary/SKILL.md) | FGC and Street Fighter vocabulary from Infil's *Fighting Game Glossary* (glossary.infil.net), paraphrased and grouped, so reviews use terms consistently. |
| [sf6-coach-juzzy-tips](sf6-coach-juzzy-tips/SKILL.md) | Lessons from Juzzy's *Juzz the Tip* videos (YouTube @juzz87): neutral skips before footsies, pressing with intention, meter and cash-outs, plus frames, overextending, autopilot, the don't-whiff drill. Shared with permission. |
| [sf6-coach-juzzy-sessions](sf6-coach-juzzy-sessions/SKILL.md) | Recurring themes from Juzzy's *Sit Down and Shut Up* coaching sessions and set reviews: play grounded, don't give up space, corner control, shimmy punishes and interactions to kill, block more, Drive discipline. Shared with permission. |

## Personalize them
Every copy here, and in `skills/local/`, has the author's details replaced with placeholders. Fill them in with your own before installing:

| Placeholder | Replace with | Example |
|---|---|---|
| `{{PLAYER_NAME}}` | Your name (the player being coached) | `Alex` |
| `{{PLAYER_CFN}}` | Your CFN name | `.alexfgc` |
| `{{PLAYER_CFN_ID}}` | Your CFN short ID (Buckler profile number) | `1234567890` |
| `{{COACHING_DIR}}` | The folder holding your replays, history database and reviews | `D:\SF6-Claude-Coaching` |
| `{{VIDEOS_DIR}}` | Where OBS saves recordings | `C:\Users\alex\Videos` |

Links to private dashboards and sheets read "your artifact link": replace them with your own, or delete those lines.

**PowerShell** (from the repo folder; copies the personalized skills to `skills-personal\`):
```powershell
$map = @{ '{{PLAYER_NAME}}'='Alex'; '{{PLAYER_CFN}}'='.alexfgc'; '{{PLAYER_CFN_ID}}'='1234567890'; '{{COACHING_DIR}}'='D:\SF6-Claude-Coaching'; '{{VIDEOS_DIR}}'='C:\Users\alex\Videos' }
Get-ChildItem skills -Recurse -Filter SKILL.md | ForEach-Object {
  $out = $_.FullName.Replace((Resolve-Path skills).Path, (Join-Path (Get-Location) 'skills-personal'))
  New-Item -ItemType Directory -Force (Split-Path $out) | Out-Null
  $t = Get-Content $_.FullName -Raw; foreach ($k in $map.Keys) { $t = $t.Replace($k, $map[$k]) }
  Set-Content $out $t -NoNewline -Encoding utf8 }
```
**bash:**
```bash
mkdir -p skills-personal && cp -r skills/. skills-personal/ && find skills-personal -name SKILL.md -exec sed -i \
  -e 's/{{PLAYER_NAME}}/Alex/g' -e 's/{{PLAYER_CFN}}/.alexfgc/g' -e 's/{{PLAYER_CFN_ID}}/1234567890/g' \
  -e 's#{{COACHING_DIR}}#D:\\SF6-Claude-Coaching#g' -e 's#{{VIDEOS_DIR}}#C:\\Users\\alex\\Videos#g' {} +
```
`skills-personal/` is gitignored, so your details stay out of the repo.

## Private coaching notes
`sf6-coach-doctaafrikan` (notes from private coaching sessions) is kept local and gitignored. Without it the review still runs.

## Coaching lenses (`skills/local/`, not in the repo)
The review method also loads coaching "lens" skills: paraphrased summaries of E.X. Dojo seminars. They stay out of the public repo for now (`skills/local/` is in `.gitignore`). The list of what each one covers is in `SKILLS.md` (also local only).

If you have them, put each in `skills/local/<name>/SKILL.md`. Without them the core skills still run; findings just won't be tagged with those lenses.

## Installing
- **Claude.ai / desktop app:** turn on **Code execution and file creation** ("Create and edit files") in **Settings → Capabilities**, then **Customize → Skills → + → + Create skill → Upload a skill**, one zip per skill folder. Step-by-step in [GETTING-STARTED.md](../GETTING-STARTED.md#3-add-the-skills-to-claude-once).
- **Claude Code:** copy the folders into `~/.claude/skills/` (or a project's `.claude/skills/`).
