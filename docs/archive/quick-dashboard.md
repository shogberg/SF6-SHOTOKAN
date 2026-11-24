# Archive: the quick-dashboard (retired 2026-11-24)

The quick-dashboard was a Claude Data artifact that showed every reviewed set, built from `sf6.db`. It was last refreshed on 2026-11-18 with 16 sets, and was retired as a review step on 2026-11-24: reviews now end at the database, and the web site ([shotokan-sf6/web](https://github.com/shotokan-sf6/web)) is where the data is shown. This page keeps how it was built, in case it comes back.

## Where it lives
- Artifact: https://claude.ai/artifact/7cVsKUW5nXJPdvrtrRCo4f (slug `358ba778-1928-4b51-a1b0-e2ad6b3a9864`). It still opens; its data stops at 2026-11-18.
- Page format: the `sf6-review-dashboard` skill (sections, CSS `page-css.html`, script `helpers.js`).

## How it was built
1. Ingest each set with `dash: {"dashboard": "quick-dashboard"}` in META. That gives the set a stable "Set N" in the `dashboard_sets` table (sets ingested later still get one if `dash` is passed).
2. For a Full review, pass the hand-written `review_docs` in META. These are still used: they are the review's record in the database.
3. Build the datasets from the database:
   - `tools/quick_review_reads.py DB OUTDIR --write-reads`: the Set review datasets (sets, games, hits, events, timings, resources, parries, archetypes, habits, story, story_games, punish, findings, fixes, training, set_gameplan, prediction, tournament). Quick reviews are regenerated and their reads and habits written back to the database (this part is still run for Quick reviews).
   - `tools/overview_from_db.py DB OUTDIR` (after the step above; reads OUTDIR/stats.json and sets.json): the Overview datasets (ov_sets, overview, gameplan, ov_training).
   - `tools/profiles_from_db.py DB OUT.json`: the `players` dataset (one profile per player from Quick reviews).
4. Upload each changed JSON to the artifact with `upload_asset`, then update that dataset's document in the artifact's database (`datasets/<id>`: `source.url` and `updated`).
5. It ran before the Replay Tracker sheet export, since step 3 can change Player Reads.

## Datasets it declared
archetypes, events, findings, fixes, gameplan, games, habits, hits, ov_sets, ov_training, overview, parries, players, prediction, punish, resources, set_gameplan, sets, story, story_games, tournament, training.

## The skill text it replaced (sf6-replay-analysis, section 0)
- **quick-dashboard** (https://claude.ai/artifact/7cVsKUW5nXJPdvrtrRCo4f, slug 358ba778-1928-4b51-a1b0-e2ad6b3a9864) is built from the database too. Ingest with `dash: {"dashboard": "quick-dashboard"}` in META (gives the set the next stable "Set N"), and for a **Full** review also pass `review_docs` (the hand-written story, story_games, habits, archetypes, fixes, training, findings, punish and sets rows, plus `set_gameplan`: each player's gameplan, mid-set adjustments, what worked, and how each should adjust, shown in the dashboard's Gameplan section; and `prediction` when replay-review-prediction was used), which are kept across re-ingests. Then run `tools\quick_review_reads.py DB OUTDIR --write-reads` (Set review datasets; Quick reviews are regenerated and their reads/habits written back to the DB) and `tools\overview_from_db.py DB OUTDIR` (Overview: ov_sets, overview, gameplan, ov_training, every number computed from the DB). Upload each changed JSON with upload_asset and update that dataset's `source.url` and `updated`. Run the quick-dashboard step before the sheet export, since it can change Player Reads.
