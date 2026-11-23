# TODO

Ideas and planned work for SHOTOKAN (the replay-review tooling and skills). Newest additions at the top of each section.

## Analysis depth
- [ ] **Button sequencing:** define it, with Cammy-specific examples (Sean to explain the concept).
- [ ] **Structured gameplay:** better definition of offensive structure, and analysis of it in reviews (defaults, checkpoints, what follows each initiator).
- [ ] **Matchup-specific punishes:** know what is and isn't punishable per matchup (e.g. Cammy can't always punish Blanka Ball), so reviews don't flag a "missed punish" that wasn't there.
- [ ] **Missed whiff punishes:** find whiff-punish openings that went unused; possibly simulate other buttons to see which would have counter-hit.

## Beyond the guideline skills
- [ ] Look past the skills set by Sean or built from YouTube guides. Once sequence / structure analysis works better, track meta ideas long term: game plans, offensive structure and the sequences players use.

## Long-term tracking and prediction
- [x] Store long-term data for both players in every reviewed set (the reviewed player and the opponent). Every reviewed set is ingested, whoever it's for.
- [ ] Export trends to character-specific data (a store or skill) and by MR range, to compare what works at different levels of competition.
- [ ] Score the advice: when review notes highlight something as a strength for the set winner, bump that advice's points; when they highlight something as a weakness for the set loser, bump that too.
- [ ] Make matchups predictive before review from this data: "Cammy wins if..." per character matchup, and per player profile type (archetype and spectra).

## Pro replays
- [ ] Review pro vs pro replays and track them the same way long term.
- [ ] Test whether player traits plus the character matchup can predict pro match results.

## Already noted
- [ ] Predictions: start from the MR gap and grade each key factor as data (blind winner picks are 72%, about the same as the higher-MR player's 76%).
- [ ] Name the internal moves still shown as IDs for Zangief, Marisa, Ingrid and Yasmine; confirm Arjun's Divine Pillar (`03`) and Cruel Shoulder (`623P`) names.
- [ ] Measure conditioning: how players condition each other over a set.
- [ ] Winner weighting for the Economy of Buttons.
- [ ] Correct the hand-written burnout counts in older review docs (cadii, Grozznuy) for the lethal-burnout rule.
- [ ] Stick-figure viewer: character looks for characters beyond Cammy and Akuma.
