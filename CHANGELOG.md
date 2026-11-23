# Changelog

Notable changes to the SHOTOKAN review tooling and skills, newest first. Every push adds its changes here.

## 2026-11-22
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
