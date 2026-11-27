# SHOTOKAN
**Strategic Hit-confirm Oracle for Tactics, Okizeme, Knockdowns And Neutral**

> *"Look at you, mashing on wake-up. I have confirmed every frame of your hesitation, insect."*

**New to Claude?** Start with [GETTING-STARTED.md](GETTING-STARTED.md): install the skills and capture scripts, record a replay, and get your first review.

SHOTOKAN is the SF6 Claude Coaching replay-review system. The name is a nod to SHODAN from System Shock.

Replay reviews for Street Fighter 6. Claude reads each game's REFramework capture (exact frame-by-frame game data), checks key moments against the video, and builds a dashboard showing what happened, why, and what to train next. Everything lives in `D:\SF6-Claude-Coaching`.

---

## 1. General features

### Input
- **Capture files (`.json`)**: recorded by `tools/capture_replay.lua` while a replay plays back in REFramework. Each one holds both players' state every frame: move, action state, HP, Drive, super, burnout, position, hitstun/blockstun and inputs, plus the game's own battle stats.
- **Videos (`.mp4`)**: the same replays recorded with OBS. They're used to check moments the data can't explain (intent, a read, a super cinematic) and to cut clips.
- **Replays folder**: `$SHOTOKAN_HOME/replays` (e.g. `D:\SF6-Claude-Coaching\replays`) is the default store; see [Paths](#paths). A review can also point at any other folder (e.g. `Juniper`).
- **Local or offline matches** save no names, ranks or round results. Sean gives the player names, and round winners come from HP: the first player to reach 0, or whoever had more HP on a timeout.

### Analysis
- `tools/shared_core_analyze.py` turns the captures into datasets:
  - every damaging hit or combo: damage, starter, hit kind, anti-air, situation, what the victim was doing;
  - burnouts and perfect parries;
  - Drive Parries;
  - Drive and super spending per round;
  - per-game stats and action timings;
  - every decision press (a new button, special, super or throw while the opponent isn't being hit or knocked down): its situation, the move, what the opponent was doing and the first outcome (landed, blocked, parried, whiffed, got hit);
  - corner time per round (`corner.json`, from `tools/corner_time.py`): seconds each player spent cornered, how many times they got cornered and the longest stretch. Cornered = within 1.5 of the wall (|posX| 7.65) with the opponent on the inner side, live play only (`fight_st` 4). A zoner who parks in the corner by choice counts too.
  - whiff punishes (`whiffs.json`, from `tools/shared_core_whiffs.py`): every whiffed ground normal or throw, its recovery window (wiki startup + active, frame_data `frames`), the distance (posX, centre to centre; round start is 3.0 apart) and whether the other player punished it. A chance needs 15+ frames of recovery, the punisher free and in reach (frame_data `reach_vs_move`, measured with `tools/whiff_reach.py`).
- **Victim states in hit rows:** `DRD_` (e.g. `5060_DRD_STD_L_START`) means the victim was already in hit reaction (a split combo or a reset), not in Drive Rush (`Drive Rush`) or blocking (`GRD_`). A `HOLD` state, sometimes only a number such as `_966`, is the being-grabbed animation: read the move just before it.
- **Damage** is the permanent life a hit takes. When a hit lands while the victim has white (recoverable) health, the white health it cashes in counts too (e.g. after Arjun's blocked pressure or a Drive Reversal). Hit rows also record `recoverable` (white health the combo added) and `white_cashed`.
- **Hit kinds**:
  - **Clean hit** is the default.
  - **Counter hit**: the first hit does 1.2× its base damage.
  - **Punish counter**: a counter hit with 2 more frames of hitstun.
  - **Throw** and **reversal** are their own kinds.
- **Drive Rush types are decided by cost**:
  - **Raw drive rush** (1 bar): from neutral, or Drive Parry > Drive Rush, even inside a blockstring.
  - **Combo drive rush cancel** (3 bars): in a combo.
  - **Pressure drive rush cancel** (3 bars): in a blockstring.
  - **Whiff drive rush cancel** (3 bars): off a whiffed button.
- **Drive economy**:
  - **Spent**: Drive Rush, Drive Rush cancel, Parry, Drive Impact, OD, and Drive Reversal / other.
  - **Out**: lost blocking, and lost getting hit.
  - **In**: gained landing hits, gained when attacks are blocked, and regained from parried hits.

### History database
- `history\sf6.db` (SQLite) keeps every reviewed set, game, hit, event, resource row, parry and review doc.
- It's used to:
  - compare a player with their own history (e.g. "shog tonight vs his history");
  - compare players with each other (`tools/full_review_decision_presses.py`: where they press, with which buttons, and what it leads to);
  - make predictions before a set;
  - score player spectra against everyone reviewed so far.
- **Blind predictions:** `tools/shared_core_blind_manifest.py` gives the pre-set facts without anything that leaks the result (round results, later games' MR, the number of games); `shared_core_db.py history` gathers history only from sets before the one predicted; `shared_core_db.py predict` stores the prediction before the analyzer runs, refuses once the set is ingested, and ingest links and grades it (`predictions` table).
- `shared_core_db.py ingest` also computes the set's ten spectra and adds its replays to the behaviour cache first (`--no-spectra` skips it). `tools/spectra_backfill.py` fills sets that have none. Spectra are scored against everyone except you: `tools/spectra_calibrate.py DB` recalibrates the cut points from every other player (each weighted equally, less below 10 games) and re-scores all sets; `tools/player_baseline.py` (run by ingest) compares each of your sets with your own previous 7 days; `tools/character_baselines.py DB` prints the per-character baselines without you.
- **Review date, notable players, excluded sets** (2026-11-26):
  - `sets.reviewed_at` is when a set was first reviewed, kept on re-ingest; SHOTOKAN Web sorts its latest sets by it.
  - `shared_core_db.py flag DB NAME|CFN [FLAG] [--note ...] [--remove]` marks a notable / pro player (`player_flags`, default flag `notable`); `flags DB` lists them. Other flags in use: `azfgc` (a local group) and country codes `jp`, `kr`, `no`, `gb`, `us`, which the site shows as flag badges.
  - Ingest stores corner time in `corner_time` (per round and player) and adds `active_frames`, `cornered_frames`, `cornering_frames` and `cornered_entries` to `set_stats` / `game_stats` (frames / 60 = seconds). `tools/corner_time.py --backfill DB [--set KEY]` fills older sets from their captures; `tools/corner_time.py CAPTURE...` prints it.
  - `shared_core_db.py exclude DB SETKEY [REASON] [--remove]` keeps a set in the database but leaves it out of prediction history and the published site (reason `1v1me` for betting matches that open with a ~30 s warm-up). META `excluded` does the same at ingest.
- `tools/full_review_fireball_drive_rush.py DB --player NAME --ranked-only` measures fireball Drive Rush per character and player: damage either way in the next 30 frames, Drive cost, the mixup after a blocked button, and round win rates, with raw Drive Rush for comparison.
- When the analyzer's counting changes, `tools/rescore_damage.py` re-scores damage in an existing database from the captures without re-ingesting, `lethal_backfill.py` / `game_stats_backfill.py` apply older rule changes, and `relabel_moves.py DB OLD_ANALYZER.py MOVES_DIR` brings stored move labels up to date after the analyzer learns new move names (it compares the old and new analyzer on each character's move export); `relabel_resolve.py` settles the labels it reports as ambiguous from the captures.

### Review levels
| Level | What you get |
|---|---|
| **Quick** | Data-only: datasets, KPIs, computed player reads. No story writing. |
| **Full** | Everything in Quick, plus the Story of the Set, habits, gameplans, fixes, a training routine and findings by skill. The reviewer can override computed spectra (the card says so). |
| **Tournament** | Everything in Full, with every key exchange checked on video. It's written from **both** players' sides and adds a decision audit ("could you have guessed better?"), how each player adapted, what to say between games, rematch prep and a longer training plan. |

### Prediction before review
- Before any capture or video is opened, Claude writes a prediction for each set: each player's gameplan, the winner and score with a confidence, the path to victory, and key factors to watch.
- After the review, each prediction is graded right or wrong, with what it missed and why.
- Predictions are stored in the database so their accuracy can be tracked over time.

### Dashboards
- Each review becomes a **Data artifact** (e.g. *Jon-dashboard*, *obi1-dashboard*), plus a **standalone HTML copy** with `data/*.json` and `*.csv` on D:.
- **Overview tab**:
  - sets, games and rounds won;
  - anti-airs, counter hits and burnouts;
  - patterns common to all sets;
  - where damage taken came from;
  - gameplan review;
  - a set-by-set table;
  - Drive economy over time;
  - what to work on next.
- **Set review tab**: pick a set to see:
  - damage by situation and by what the player was doing;
  - KPI tiles and hits by kind;
  - Drive and super spending, Drive economy and Drive Parry tables;
  - player reads, habits, gameplans and the prediction card;
  - the tournament section, when there is one;
  - the Story of the Set (set overview with top 3 highs and lows, then game cards);
  - punishes, fixes and drills, a training routine, findings by skill, and every hit.
- **Players tab** (when asked): a quick profile of each player, covering archetype, summary, strengths, leaks and how to beat them.
- Total damage dealt isn't tracked as a score. Damage only appears as a *share* (where it came from) or per hit.

### Terms used everywhere
- **Round**: one life bar.
- **Game**: one replay, made of 2-3 rounds.
- **Set**: a group of games between the same two players. The formats are:
  - **FT2** (best of 3);
  - **FT3** (best of 5);
  - **FT5** (best of 9).
- **@** is the round timer (e.g. "G2 R1 @61").
- **Ranks**: below Master, players get the league name only (e.g. "Platinum"). Master players with no MR are "MR unknown".

---

## 2. What I look for in replays

**Every game, both players:**
1. **Where damage came from.**
   - By situation: neutral, pressure, oki, punish, defense.
   - By what the victim was doing: pressing in pressure or on wake-up, pressing at mid range, walking in, teching a throw, blocking and getting opened up, jumping, getting jumped in on, offense beaten by a reversal, Drive Rush or Impact checked, an unsafe move punished, or unclear / super.
2. **Neutral:**
   - who controls the space, and at what range;
   - whiff punishes;
   - pokes that get counter-poked;
   - Drive Rush checks;
   - jumps, and whether they're anti-aired.
3. **Offense:**
   - frame traps vs staggers, and whether the gap matches the defender's timing;
   - throw/strike/shimmy structure, and whether they throw before shimmying;
   - Drive Rush cancels: true or gapped, and whether they're confirmed;
   - oki after each knockdown.
4. **Defense:**
   - what each player does after blocking and on wake-up: block, button, throw tech, jump, parry, reversal, Drive Reversal;
   - how fast they do it (reversal timing or delayed);
   - whether the choice fits the six modifiers.
5. **Resources:**
   - Drive spent and how it was spent, burnouts, super use and super left unspent at round end;
   - parry net (regained − cost), and what happened after each parry;
   - whether a combo's Drive or super bought enough (damage, knockdown, corner).
6. **Counter hits and punish counters**: what got counter-hit, and whether it was a habit.
7. **Punishes**: what was punished, with what, and the missed punishes ("none (missed)").
8. **Adaptation**: what changed between rounds and games, with each change tagged New, Improved or Regressed and where it first appeared.
9. **Turning points**: the exchange that decided each game.
10. **Economy of buttons**: each player's share of the decision presses, who starts the exchanges, damage per decision press against the opponent's, and who won the Drive war (pressure cancels, Drive lost blocking, burnouts).

**How it's reported:**
- Every claim cites game, round and timer.
- Each finding is High, Medium or Low confidence. Low-confidence notes are collapsed.
- Fixes are ranked, each with a drill.
- The training routine is split Primary 50%, Secondary 25%, Free play 25%.

---

## 3. What I look for in player profiles

### Archetype (from E.X. Dojo)
- **Aggressive**:
  - lots of neutral Drive Rush, Drive Impact and jumping;
  - presses after blocking or on wake-up, mashes throw tech, reversals often;
  - high Drive use and burnouts;
  - rarely throws a blocking opponent.
- **Defensive**:
  - walks back and holds down-back;
  - presses few buttons in neutral, blocks long strings, delay-techs;
  - low Drive use.
- **Fundamentalist**:
  - pokes and fireballs, plays to whiff punish;
  - uses little Drive Rush, Impact or Parry;
  - struggles when the opponent uses system mechanics.
- **Balanced**:
  - changes pace with resources and score;
  - punishes consistently and mixes strike and throw;
  - adapts after being shown something.
- Most players have a **lean** (e.g. "Balanced, leans aggressive").
- **Confidence**:
  - **High**: several clear signs across at least two rounds.
  - **Medium**: mixed signs or only one game.
  - **Low**: a short or one-sided set.

### The ten spectra
Each player gets a 1-5 score on ten axes. 1 is the left end and 5 the right end, and neither end is "good" by itself. Scores are **percentile strata** against every player-set in the database: 1 = bottom 20%, 2 = 20-40%, 3 = 40-60% (middle), 4 = 60-80%, 5 = top 20%. In Full and Tournament reviews the reviewer can override a computed score; the card then says "Reviewer's call (computed X/5)".

| Spectrum | 1 (left) ↔ 5 (right) | What's measured |
|---|---|---|
| **Temperament (defense)** | Impulsive ↔ Mindful | How often their first action after blocking or on wake-up is a button, special, jump or parry on reversal timing (0-2 frames). Impulsive players act at once; mindful players wait and block. |
| **Temperament (offense)** | Impulsive ↔ Mindful | How often they press again within 3 frames of being free after their attack is blocked. |
| **Adaptability** | Inelastic ↔ Elastic | Whether the opponent's best weapon in the first half of the set (the move that did the most damage, 2,500+) still worked in the second half: damage per round after vs before. |
| **Risk tolerance** | Low ↔ High | Wake-up reversals, Drive Impacts, Drive Reversals, raw Drive Rushes, supers and forward jumps per round. |
| **Initiative** | Reactive ↔ Proactive | Forward movement in neutral, and how many neutral exchanges they start. |
| **Composure** | Steady ↔ Tilts | How much more they act after taking a 2,000+ combo or losing a round. |
| **Variety** | Scripted ↔ Mixed | How spread out their after-block and wake-up choices are. Scripted players do the same thing every time. |
| **Resource use** | Conservative ↔ Spendthrift | Drive, super and burnouts per round. |
| **Cash-in** | Speculative ↔ Cashes in | Share of the Drive and super spent that went into combos that landed. |
| **Space** | Gives ground ↔ Takes ground | Share of live time cornering the opponent minus share cornered (corner time). The set winner scores higher about 3 times in 4. |

How to read a profile:
- **Extremes (1 or 5) are exploitable habits.** For example:
  - a 1 on Defense temperament (Impulsive) loses to frame traps and staggers;
  - a 1 on Variety (Scripted) loses to a single hard read;
  - a 5 on Resource use (Spendthrift) leads to burnouts, which are close to checkmate in the corner.
- **The middle (3) is flexible but readable once you know their tendency.**
- **The axes combine.** "Impulsive + Inelastic + Tilts" is the classic player to stay patient against and let them burn out. "Mindful + Elastic + Mixed" is the hardest to read: play your fundamentals and don't gamble.
- Profiles also note how the player **adapted** during the set, their **strengths and leaks** (habits tagged Strength / Leak / Pattern), and **how to beat them**.

### Player comparison over time
When a player has history in the database, the dashboard compares this set with their history per game: throws, damage dealt and taken, supers, pressing after blocking, burnouts and so on. This flags whether a performance was typical or an outlier (for example, a different setting or the opponent forcing a change).

---

## Repository layout

| Path | What it is |
|---|---|
| `tools/shared_core_analyze.py` | Turns REFramework capture files into review datasets (hits, events, parries, resources, timings). |
| `tools/shared_core_db.py`, `rank.py`, `spectra.py`, `behavior.py`, `beh_cache.py` | The history database (SQLite) and the player spectra and behaviour stats. `shared_core_db.py` commands: `ingest`, `predict`, `history`, `mr`, `odds`, `flag` / `flags` (notable players), `exclude` (sets left out of stats), `sql`. |
| `tools/spectra_calibrate.py` | Recalibrate the spectra cut points from every player except you (each weighted equally, less below 10 games), store them in sf6.db and re-score every set. |
| `tools/player_baseline.py` | Your set against your own previous 7 days (`player_baseline` table); ingest runs it. |
| `tools/character_baselines.py` | Per-character baselines (jumps, Drive Rush, Drive Parry, throws per round) without you, for sf6-character-notes. |
| `tools/spectra_backfill.py`, `rescore_damage.py`, `lethal_backfill.py`, `game_stats_backfill.py`, `relabel_moves.py`, `relabel_resolve.py` | Bring an existing database up to date after a rule change: spectra, damage (white health), lethal burnouts, per-game stats, move names. |
| `tools/shared_core_blind_manifest.py` | Pre-set facts for a blind prediction (first game's header only). |
| `tools/full_review_decision_presses.py` | Compare players' decision presses: per round by situation, outcome rates, top moves per situation. |
| `tools/whiff_reach.py` | Measures each character's button reach from the captures (90th percentile contact distance) into `frame_data/`, for the whiff-punish step. |
| `tools/archetype_calibrate.py` | Calibrates the generated archetype reads from the pool (without you) and rewrites every Quick set's read; `--dry` prints the split first. |
| `tools/corner_time.py` | Corner time per round from a capture (also run by the analyzer); `--backfill` fills `corner_time` and the stats for sets already in the database. |
| `tools/full_review_fireball_drive_rush.py` | Fireball Drive Rush value per character and player (damage both ways, Drive cost, mixup after a blocked button, round win rates). |
| `tools/quick_review_reads.py`, `overview_from_db.py`, `profiles_from_db.py`, `sf6db_export.py`, `ranked_build.py` | Build dashboard datasets, overviews and player profiles from the database. The quick-dashboard they fed is retired ([archive](docs/archive/quick-dashboard.md)); `quick_review_reads.py --write-reads` is still run after a Quick review to write its reads and habits to the database. |
| `tools/standalone.py`, `standalone_head.html`, `standalone_shim.js`, `summary_md.py`, `check_page.py` | Offline HTML copies of dashboards, summaries and page checks. |
| `tools/drive_contact.py`, `drive_measure.py` | Drive gauge measurement helpers. |
| `tools/base_damage.json`, `tools/enums.json` | Base damage per move and the game enums the analyzer reads. |
| `batch/` | `batch_record.py` drives OBS to record replays by ID (see `batch/README.md`). |
| `skills/` | The Claude skills the reviews run on (see `skills/README.md`). Coaching-lens skills live in the gitignored `skills/local/`. |

The in-game scripts (`capture_replay.lua`, `export_moves.lua`, `batch_replays.lua`) live in the separate REFramework mods repo, [shotokan-sf6/mods](https://github.com/shotokan-sf6/mods). That repo also ships move names for the full roster in `data/sf6_moves/`; point the analyzer at them with `SF6_MOVES=<path to data/sf6_moves>` so hits and habits use move names instead of action IDs.

Not in this repo, on purpose: the history database, capture files, replays and videos, and the review dashboards. They hold match data about real players.

### Paths
No script has a machine-specific path in its code. They read environment variables, or `tools/.env` (copy `tools/.env.example`; it's gitignored). `tools/paths.py` resolves them:

| Variable | What it points at | Default |
|---|---|---|
| `SHOTOKAN_HOME` | The coaching folder (replays, history, reviews) | The folder above `tools/` |
| `SHOTOKAN_REPLAYS` | Capture files and videos | `$SHOTOKAN_HOME/replays` |
| `SHOTOKAN_DB` | The history database | `$SHOTOKAN_HOME/history/sf6.db` |
| `SHOTOKAN_CAPTURE_DIRS` | Extra folders to search for captures (`;`-separated on Windows) | none |
| `SHOTOKAN_RANKED_DIR` | `ranked_build.py`'s working folder | `$SHOTOKAN_HOME/ranked` |
| `SF6_MOVES` | Move-name files (`data/sf6_moves` from the mods repo) | none (action IDs instead of names) |

### Player
The player in focus (you) is set once, not in code. `tools/paths.py` reads `SHOTOKAN_PLAYER` / `SHOTOKAN_CFN_ID` from the environment or `.env`, else `$SHOTOKAN_HOME/shotokan.json`:

```json
{"player_name": ".shog", "other_names": ["shog"], "cfn_id": "1307078698", "main_character": "Cammy", "control": "Classic"}
```

`player_name` is your in-game name; `other_names` lists names you've used before (full_review_decision_presses.py counts them as you); `cfn_id` is your Buckler short ID. The Claude plugin's setup skill writes this file. Tools that need a player (`shared_core_db.py history`, `profiles_from_db.py`, `quick_review_reads.py`, `overview_from_db.py`, `ranked_build.py`, `spectra_backfill.py`, `full_review_decision_presses.py`) use it when you don't pass one, and stop with a clear message when neither is set. `batch/buckler_replays.py` uses `cfn_id` when no CFN ID is given. Reviewing someone else: pass their name (`--player`, `--me`) as before.

Captures are found by replay ID or file name in those folders, as `.json` or `.json.gz`, so a capture path stored in the database on another machine still resolves. The batch recorder reads the same `SHOTOKAN_HOME` / `SHOTOKAN_REPLAYS` from `batch/.env` (`REPLAYS_DIR` still works). Paths in the docs and skills, like `D:\SF6-Claude-Coaching`, are examples.
