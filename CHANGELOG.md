# Changelog

Notable changes to the SHOTOKAN review tooling and skills, newest first. Every push adds its changes here.

## 2026-11-23
- No machine-specific paths in code: new `tools/paths.py` reads `SHOTOKAN_HOME`, `SHOTOKAN_REPLAYS`, `SHOTOKAN_DB`, `SHOTOKAN_CAPTURE_DIRS` and `SHOTOKAN_RANKED_DIR` from the environment or `tools/.env` (see `tools/.env.example`), with defaults relative to the coaching folder. `beh_cache.py`, `ranked_build.py`, `lethal_backfill.py`, `spectra_backfill.py` and `decision_presses.py` use it (captures are found by replay ID as `.json` or `.json.gz`; `decision_presses.py`'s DB now defaults to `SHOTOKAN_DB`). `batch_record.py` takes `SHOTOKAN_HOME` / `SHOTOKAN_REPLAYS` (`REPLAYS_DIR` still works) and no longer defaults to a D: path. README: new Paths section.
- Docs: sf6-meta-description.md "What the data says" rewritten for 122 compared sets (archetypes, what separates winners and what doesn't, decision presses, button economy, prediction accuracy vs the higher-MR baseline) and the winner profile corrected (Initiative even, Resource use 3.9 vs 2.2, Drive Reversal about 2x in losers, wake-up damage not wake-up blocking, Arjun's white health). README: white-health damage, decision presses, spectra at ingest, backfill and rescore tools, Economy of buttons. GETTING-STARTED and TODO updated; skill copies (sf6-replay-analysis, sf6-coach-shog) match the live skills.
- Decision presses: a throw now counts as landed when the opponent is held, not only when its damage arrives inside the ~70-frame window. Long throws (Juri's) were all counted as whiffs before.
- Spectra on every ingest: `sf6db.py ingest` now computes the eight player spectra for the set it just ingested (spectra table, and attached to the review's hand-written archetypes), adding the set's replays to `beh_cache.json` first so Composure, Initiative, Resource use and Temperament (offense) aren't left blank. `--no-spectra` skips it. New `tools/spectra_backfill.py DB [SET_KEY ...]` fills sets that have none (until now only the batch ingest scripts computed spectra, so a plain ingest left them empty).
- Decision presses in detail: analyze_capture.py now returns each decision press with its situation (air button, vs a jump, wake-up, after blocking, own pressure, oki, after a hit, or neutral close / mid / far), the move, what the opponent was doing, and the first outcome within about 70 frames (landed, blocked, parried, whiffed, got hit, whiff punished). New `tools/decision_presses.py DB --player NAME[,ALIAS] [--char C]` compares players: presses per round by situation, outcome rates, and the top moves per situation with how often each landed or got them hit (throw presses on wake-up or after blocking are reported as throw techs).
- Damage now counts white (recoverable) health. A hit's damage is permanent life lost: the drop in `hp_recoverable_cap` over the combo, including any white health the hit cashed in; a hit that only adds white health (Arjun's Indomitable Defense counter, Drive Reversal) counts 0. New hit fields `recoverable` (white health the combo added) and `white_cashed` (white health it wiped out), also stored in sf6db.py's `hits` table. On a C.Viper set, lost rounds that didn't add up to a full life bar went from 10 of 23 to 2; the old count ran about 5% low.
- Damage is read from the frame before the first hit (some moves leave the victim in a damage state with no hitstun, so the old lookback read HP after the hit), runs on while the victim is still being hit or held (cinematic supers log their last hits late), and never reaches back into the previous combo on the same victim (no more double counting).
- Command grabs whose hits land long after the Throw stat (Arjun's Ghastly Interrogation, about 145 frames) are no longer counted twice, and are tagged as throws.
- Arjun's moves are named: Arm of Justice (+ follow-up), Breathing Ring / Breathing Shockwave, Indomitable Defense (stance, counter) and Moral Breakdown, Divine Pillar, Cruel Shoulder and Justice Beyond, Ghastly Interrogation, SA1 Howling Destruction, SA2 Instant Oblivion, SA3 Yaksha's Order. Divine Pillar (`03`) and Cruel Shoulder (`623P`) are inferred from how the moves behave. Hits from a pillar or ring set up earlier are credited to that move instead of Arjun's walk or jump.
- `tools/rescore_damage.py`: re-scores damage in an existing history database from the captures, without re-ingesting (reads, habits, review docs and press counts are kept), and recomputes the damage-based set_stats and game_stats.

## 2026-11-22
- sf6db.py: new `game_stats` table, the same metrics as `set_stats` per game with the character played, written on every ingest. `tools/game_stats_backfill.py` fills it for sets ingested earlier (from the stored hits, events and timings; press counts need a re-ingest).
- Moved to the shotokan-sf6 organization (was shogberg/SF6-SHOTOKAN): links to shotokan-sf6/mods and shotokan-sf6/web.
- batch/buckler_replays.py: pull a player's last 100 replay IDs from Buckler by CFN ID, for batch_record.py --file (BUCKLER_COOKIE in .env).
- GETTING-STARTED.md: Buckler pulls, predictions on every review, lethal burnouts, every reviewed set in the database, gzipped captures, the dashboard tabs and the new web pages.
- sf6-meta-description.md: data findings from 69 compared sets (winner vs loser): Resource use revised to 4, Initiative to 3, throws, counter hits and punish counters, wake-up blocking, Drive Reversal, burnouts and anti-airs as weaker signals, archetype win rates, and the measures still to fix.
- TODO.md: planned work (button sequencing, offensive structure, matchup-specific punishes, missed whiff punishes, long-term tracking and prediction, pro replays).
- Burnouts: a burnout that starts inside the player's own combo that kills (the opponent stays in hitstun until their HP hits 0) is logged as a `lethal burnout` and no longer counts as a burnout in counts, tiles, spectra or advice. `tools/lethal_backfill.py` relabels burnouts already in a history database.

## 2026-11-21
- Skills: added `sf6-coach-coosco` (Coosco's replay-breakdown lessons) and `sf6-character-notes` (per-character baselines and notes).
- Skills: added `sf6-coach-shog` (coach .shog's rules and theories). `sf6-coach-doctaafrikan` is now kept local and gitignored.
- Elasticity (Adaptability spectrum): only a losing plan counts as inelastic. Reusing a punished move counts when the player lost that game or was behind in the set, weighted 1.5x if the move kept getting punished. In a won game, a reused move only counts at 3,500+ damage. Keeping a winning plan scores 3/5, "Kept a winning plan".
- Lenses: "Pressed after turn ended" is split out of "Unsafe move punished" (a new press after the attacker's blockstring ended, rather than a blocked move that was unsafe).
- Lenses renamed: "Counter-hit at mid range", "Whiff punished", "Challenging pressure" and "Challenging okizeme". Damage taken per lens is now stored as raw damage as well as a share.
- Button economy: the analyzer writes `presses.json` with total presses and decision presses (presses while the opponent isn't busy getting hit or knocked down).
- Throw techs: defensive throw presses are labelled "Throw tech attempt", kept apart from offensive throws.
- Reversals: reversal hits (an invincible special or super out of blockstun) are tagged as their own hit kind.

## 2026-11-20
- The wip dashboard is renamed quick-dashboard.
- Raw Drive Rush counts at half weight in the risk spectrum, and is a leak only when it gets checked and the player doesn't adjust.
- Quick reviews: generated text is character-aware.

## 2026-11-19
- sf6db ingest: reads and habits default to the review's archetypes and habits.
- batch: documented the working replay navigation.
- Skills added: Coach Juzzy (tips and sessions), Maj's Footsies Handbook and the FGC glossary.
- GETTING-STARTED guide for first-time Claude users, including Quick vs Full vs Tournament reviews.
- Skills use placeholders for personal details.
- First release: review tooling (analyzer, history database, dashboard builders) and the SHOTOKAN Claude skills.
