---
name: "replay-review-prediction"
description: "Before analyzing an SF6 set, predict both players' gameplans, the winner, score and path to victory, then grade the prediction after the review. Use when {{PLAYER_NAME}} asks for a prediction before a replay review."
---

# Replay review prediction

Runs inside sf6-replay-analysis (shared-core-review step 4). The prediction is written **before** any capture, report.md or video of the set is opened, so it is a real test of how well the database and the guideline skills model the players.

## 1. Gather only pre-set information (blind)
Always in this order: manifest, history, prediction stored, then the analyzer.
- **Pre-set facts:** `python tools\shared_core_blind_manifest.py <captures...> --out manifest.json` (first game's header only; withholds round results, later games' MR/LP, the number of games and frame data).
- **History:** `python tools\shared_core_db.py history DB --opp <name|CFN> --opp-char <char> --my-char <char> [--before <date>] [--exclude <IDs>]`, only from sets before the one predicted.
- **Baseline:** start from the MR gap (the higher-MR player won 70% of 133 sets in the author's data, recounted 2026-11-25); go against it only with direct evidence.
  - **MR odds:** for ranked sets where both players have an MR, the manifest's `mr_odds` gives each player's MR at stake (`win` / `loss`), game win chance and FT2 / FT3 chance (sfbuff's Elo, K=16: every game has 16 MR at stake, and the MR a player would lose is 16 x their game win chance, so +8 / -8 is 50% and +6 / -10 is 62.5%). `python tools\shared_core_db.py odds DB MY_MR OPP_MR` gives the same for any pair. Quote it in `inputs`.
  - **How far to trust it** (the author's sf6.db, 117 ranked sets, 2026-11-25): FT2 odds under 0.6 played like coin flips (the favourite won 42%), so a small MR edge alone is Low confidence; bigger gaps favoured the higher MR more than the formula says (0.65 expected, 0.84 won; 0.81 expected, 0.93 won). Recount on your own database as sets are added.
- From sf6.db (`{{COACHING_DIR}}\history\sf6.db`): earlier sets vs this opponent (`v_player_matchups`), the character matchup (`v_char_matchups`), {{PLAYER_NAME}}'s recent habits and player reads, and the opponent's reads/habits if any.
- MR of both players (from CFN or the replay info screen, not from the capture's results), format (FT2, FT3, ranked/casual) and characters.
- SuperCombo matchup and strategy pages for both characters, and the guideline skills (sf6-matchups-gameplans-exdojo, sf6-simple-gameplan-exdojo, sf6-player-archetypes-exdojo).
- Do not open the capture, the analyzer output or the video yet. If anything about the result was already seen, say so in the prediction.

## 2. Write the prediction (one per set)
For each set, write `prediction.json` with `written_at`, `replays` and `manifest`, then store it with `python tools\shared_core_db.py predict DB prediction.json` before running the analyzer (refused once the set is ingested; ingest links it and records the grade). The prediction covers:
- **Each player's gameplan:** how they want to win neutral, their main approach and defensive tools, the resources they lean on (Drive Rush, Drive Parry, stance, supers), and their likely archetype.
- **Winner and score** (e.g. {{PLAYER_NAME}} 3-1), with a confidence (High / Medium / Low) and the reason for it.
- **Path to victory** for the predicted winner, and the most likely way the other player wins games.
- **Key factors to watch:** 2-4 specific things that would decide it (e.g. "does {{PLAYER_NAME}} anti-air the jump-ins", "does he keep pressing into Jus Cool").
Show the prediction to {{PLAYER_NAME}} before starting the analysis.

## 3. Grade it after the review
Once the review is done, compare each part against what happened:
- Winner and score: right / wrong.
- Gameplans: which parts matched, which the players didn't do, and what they did instead.
- Key factors: which actually decided the set.
- One line on what the prediction missed and why (e.g. no earlier data on this opponent, MR overstated their level, didn't expect a mid-set adjustment).

## 4. Store and show it
- Store the prediction and the grade in the database through ingest: `review_docs` dataset `prediction` (one row per player: predicted plan, winner, score, confidence, path, and the graded outcome).
- On the dashboard, show it in the **Gameplan** section next to `set_gameplan` (each player's plan, mid-set adjustments, what worked, how each should adjust).
- Over several sets, note how often the predictions are right; if they keep missing in the same way, adjust how they are made.