# SHOTOKAN
**Strategic Hit-confirm Oracle for Tactics, Okizeme, Knockdowns And Neutral**

> *"Look at you, mashing on wake-up. I have confirmed every frame of your hesitation, insect."*

SHOTOKAN is the SF6 Claude Coaching replay-review system. The name is a nod to SHODAN from System Shock.

Replay reviews for Street Fighter 6. Claude reads each game's REFramework capture (exact frame-by-frame game data), checks key moments against the video, and builds a dashboard showing what happened, why, and what to train next. Everything lives in `D:\SF6-Claude-Coaching`.

---

## 1. General features

### Input
- **Capture files (`.json`)**: recorded by `tools/capture_replay.lua` while a replay plays back in REFramework. Each one holds both players' state every frame: move, action state, HP, Drive, super, burnout, position, hitstun/blockstun and inputs, plus the game's own battle stats.
- **Videos (`.mp4`)**: the same replays recorded with OBS. They're used to check moments the data can't explain (intent, a read, a super cinematic) and to cut clips.
- **Replays folder**: `D:\SF6-Claude-Coaching\replays` is the default store. A review can also point at any other folder (e.g. `Juniper`).
- **Local or offline matches** save no names, ranks or round results. Sean gives the player names, and round winners come from HP: the first player to reach 0, or whoever had more HP on a timeout.

### Analysis
- `tools/analyze_capture.py` turns the captures into datasets:
  - every damaging hit or combo: damage, starter, hit kind, anti-air, situation, what the victim was doing;
  - burnouts and perfect parries;
  - Drive Parries;
  - Drive and super spending per round;
  - per-game stats and action timings.
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
  - make predictions before a set;
  - score player spectra against everyone reviewed so far.

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

## 2. What each skill provides

Every review loads the skills below. Each one is a lens: a set of questions to ask of the replay, and the vocabulary used for findings. Findings are tagged with the skill that produced them (see "Findings by skill" on any dashboard).

### Core
| Skill | Provides |
|---|---|
| **sf6-replay-analysis** | The review method: reading captures and HUD, logging moments by round and timer, frame-data checks (SuperCombo), both players' habits and fixes, the "chess or poker?" rule (a stock answer gets one fix; a read gets the options and what each one beats). |
| **sf6-review-dashboard** | Dashboard layout, dataset schemas, page code, and local and standalone copies. |
| **replay-review-prediction** | The pre-review prediction and its grading afterwards. |
| **sf6-drive-efficiency** | Value of Drive and super spending: resource routes vs meterless routes (damage, knockdown, position), and reversal / parry / Drive Reversal vs blocking on defense. |
| **sf6-fgc-glossary** | Consistent FGC vocabulary (Infil's glossary). |

### E.X. Dojo seminars
| Skill | Lens |
|---|---|
| **footsies-101** | Red/yellow/green threat zones, interceptive timing, the footsies triangle (poke > walk-in > whiff punish > poke), small vs big steps. |
| **spacing-traps** | Making a spacing whose response you can predict, and punishing it; learning from failed traps. |
| **using-pokes** | What makes a good poke; using pokes to pin timing and position and to gather data. |
| **air-footsies** / **how-to-jump** | When jumps are good (outside anti-air range, as whiff punishes, delayed or empty jumps) and how anti-airs get beaten. |
| **dps-and-divekicks** | Dive kick height and advantage, beating dive kicks, DP range discipline. |
| **dealing-with-drive-rush** | Drive Rush hot spots, checking with lights up close and mediums at range, parrying the fastest options. |
| **reactions** | Anticipation over raw reaction, mental stack, reacting to Drive Impact, 2MK~Drive Rush and jumps. |
| **jab-strings** / **stagger-pressure** | Frame traps and the four defensive timings (reversal, ~3f, ~6f safe delay, ~12f reactive); manual vs automatic staggers; checkpoints. |
| **improving-shimmy** / **delayed-throw-offense** | Throw until they answer it; shimmy only once they've teched; in-and-out shimmy, delay jab, delayed throws. |
| **drive-rush-blockstrings** | True vs gapped Drive Rush strings and the DP option select. |
| **hit-confirms** | Confirm before spending Drive; err late rather than dump meter on block. |
| **simple-gameplan** / **structuring-offense-defense** | A minimal plan per character; strike/throw and immediate/delayed structure; a primary defensive option as a message. |
| **the-defense-equation** | Judging defensive choices by risk/reward against the "take the throw" baseline and six modifiers (HP, Drive and super for both players, screen position, characters, round/set score); "could you have guessed better?" |
| **defense-offense-101** / **delay-option-selects** / **back-recovery** / **drive-reversal** / **drive-parry-mindgames** | Defensive tools and when each one is worth it. |
| **holistic-lens** | Reading position, health, Drive and super together to predict what the opponent wants. |
| **consistency** | Doing what the game wants, playing your win condition, removing volatile options. |
| **beating-unstable-players** | Making every mistake costly, limiting interactions, safe openers. |
| **matchups-gameplans** | Reading a character's kit to see its game plan, then adjusting per matchup. |
| **player-archetypes** | Aggressive / Defensive / Fundamentalist / Balanced, with signs, counters and a confidence. |

### Other coaches and texts
| Skill | Lens |
|---|---|
| **sf6-coach-doctaafrikan** | Opponent categories (risk tolerance × temperament), the two likely follow-ups and Venn-diagram answers, "don't fight the boogeyman", default offense that gathers info, Cammy as a "scam artist". |
| **sf6-footsies-handbook-maj** | Maj's Footsies Handbook (Elements 1-35, Rules 1-5) with SF6 translations: baiting pokes, corner footsies, baiting supers, when to jump, misdirection, committing fully. |

---

## 3. What I look for in replays

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

**How it's reported:**
- Every claim cites game, round and timer.
- Each finding is High, Medium or Low confidence. Low-confidence notes are collapsed.
- Fixes are ranked, each with a drill.
- The training routine is split Primary 50%, Secondary 25%, Free play 25%.

---

## 4. What I look for in player profiles

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

### The eight spectra
Each player gets a 1-5 score on eight axes. 1 is the left end and 5 the right end, and neither end is "good" by itself. Scores are **percentile strata** against every player-set in the database: 1 = bottom 20%, 2 = 20-40%, 3 = 40-60% (middle), 4 = 60-80%, 5 = top 20%. In Full and Tournament reviews the reviewer can override a computed score; the card then says "Reviewer's call (computed X/5)".

| Spectrum | 1 (left) ↔ 5 (right) | What's measured |
|---|---|---|
| **Temperament (defense)** | Impulsive ↔ Mindful | How often their first action after blocking or on wake-up is a button, special, jump or parry on reversal timing (0-2 frames). Impulsive players act at once; mindful players wait and block. |
| **Temperament (offense)** | Impulsive ↔ Mindful | How often they press again within 3 frames of being free after their attack is blocked. |
| **Adaptability** | Inelastic ↔ Elastic | Whether moves that got them counter-hit, punished or checked in earlier games (jabs aside) were used less later. Inelastic players keep doing it even when it hurts them; elastic players adjust. |
| **Risk tolerance** | Low ↔ High | Wake-up reversals, Drive Impacts, Drive Reversals, raw Drive Rushes, supers and forward jumps per round. |
| **Initiative** | Reactive ↔ Proactive | Forward movement in neutral, and how many neutral exchanges they start. |
| **Composure** | Steady ↔ Tilts | How much more they act after taking a 2,000+ combo or losing a round. |
| **Variety** | Scripted ↔ Mixed | How spread out their after-block and wake-up choices are. Scripted players do the same thing every time. |
| **Resource use** | Conservative ↔ Spendthrift | Drive, super and burnouts per round. |

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
| `tools/analyze_capture.py` | Turns REFramework capture files into review datasets (hits, events, parries, resources, timings). |
| `tools/sf6db.py`, `rank.py`, `spectra.py`, `behavior.py`, `beh_cache.py` | The history database (SQLite) and the player spectra and behaviour stats. |
| `tools/wip_from_db.py`, `overview_from_db.py`, `profiles_from_db.py`, `sf6db_export.py`, `ranked_build.py` | Build dashboard datasets, overviews and player profiles from the database. |
| `tools/standalone.py`, `standalone_head.html`, `standalone_shim.js`, `summary_md.py`, `check_page.py` | Offline HTML copies of dashboards, summaries and page checks. |
| `tools/drive_contact.py`, `drive_measure.py` | Drive gauge measurement helpers. |
| `tools/base_damage.json`, `tools/enums.json` | Base damage per move and the game enums the analyzer reads. |
| `batch/` | `batch_record.py` drives OBS to record replays by ID (see `batch/README.md`). |

The in-game scripts (`capture_replay.lua`, `export_moves.lua`, `batch_replays.lua`) live in the separate REFramework mods repo, [SF6-SHOTOKAN-mods](https://github.com/shogberg/SF6-SHOTOKAN-mods). That repo also ships move names for the full roster in `data/sf6_moves/`; point the analyzer at them with `SF6_MOVES=<path to data/sf6_moves>` so hits and habits use move names instead of action IDs.

Not in this repo, on purpose: the history database, capture files, replays and videos, and the review dashboards. They hold match data about real players. Some scripts still have the author's local paths (`D:\SF6-Claude-Coaching`, working folders) as defaults; change them for your setup.
