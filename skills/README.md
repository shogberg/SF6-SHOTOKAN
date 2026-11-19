# Claude skills

The Claude skills SHOTOKAN reviews run on. A skill is a folder with a `SKILL.md`: instructions Claude loads when a task matches its description.

## In this folder
| Skill | What it does |
|---|---|
| [sf6-replay-analysis](sf6-replay-analysis/SKILL.md) | The review method: reading REFramework captures (and video), the analyzer, frame data, habits, the history database, review levels, logging. Loads the other skills. |
| [sf6-review-dashboard](sf6-review-dashboard/SKILL.md) | Dashboard format: datasets, page sections, the Story of the Set, local and standalone copies. |
| [replay-review-prediction](replay-review-prediction/SKILL.md) | Predict each set before reviewing it, then grade the prediction. |
| [sf6-drive-efficiency](sf6-drive-efficiency/SKILL.md) | Value of Drive and super spending on offense and defense. |
| [sf6-coach-doctaafrikan](sf6-coach-doctaafrikan/SKILL.md) | Notes from two coaching sessions with DoctaAfrikan (E.X. Dojo): categorizing opponents, Venn-diagram answers, default offense that gathers info, Cammy as a "scam artist", structured training. Shared with permission. |

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
rsync -a skills/ skills-personal/ && find skills-personal -name SKILL.md -exec sed -i \
  -e 's/{{PLAYER_NAME}}/Alex/g' -e 's/{{PLAYER_CFN}}/.alexfgc/g' -e 's/{{PLAYER_CFN_ID}}/1234567890/g' \
  -e 's#{{COACHING_DIR}}#D:\\SF6-Claude-Coaching#g' -e 's#{{VIDEOS_DIR}}#C:\\Users\\alex\\Videos#g' {} +
```
`skills-personal/` is gitignored, so your details stay out of the repo.

## Coaching lenses (`skills/local/`, not in the repo)
The review method also loads coaching "lens" skills: paraphrased summaries of E.X. Dojo seminars, Maj's Street Fighter Footsies Handbook and Infil's Fighting Game Glossary. They stay out of the public repo for now (`skills/local/` is in `.gitignore`). The list of what each one covers is in `SKILLS.md` (also local only).

If you have them, put each in `skills/local/<name>/SKILL.md`. Without them the core skills still run; findings just won't be tagged with those lenses.

## Installing
- **Claude.ai / desktop app:** Settings → Capabilities → Skills → upload each skill folder (zipped).
- **Claude Code:** copy the folders into `~/.claude/skills/` (or a project's `.claude/skills/`).
