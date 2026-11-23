# Getting started: your first SF6 replay review with Claude

This guide is for someone who has never used Claude. By the end you'll have recorded a Street Fighter 6 replay, handed it to Claude, and got back a review: what happened in each game, your habits and the opponent's, what cost you rounds, and drills to fix it.

**How it works, in one paragraph.** Claude is an AI assistant you talk to in a chat. A *skill* is a set of written instructions you add to your Claude account that teaches it a specific job. **sf6-replay-analysis** is the skill that teaches Claude to review SF6 replays the SHOTOKAN way. Once it's installed, you don't call it by name: you ask for a replay review in normal words, and Claude picks the skill up by itself.

---

## 1. What you need

| | Why |
|---|---|
| A **Claude account** ([claude.ai](https://claude.ai)) | Where the reviews happen. A paid plan gives you more room for long reviews, but you can start on Free. |
| The **Claude desktop app** (recommended) | It can be given access to a folder on your PC, so Claude can read your capture files and videos directly instead of you uploading them. Capture files are large (10-40 MB each). |
| **Street Fighter 6** on PC (Steam) + **[REFramework](https://github.com/praydog/REFramework)** | REFramework runs the capture script inside the game. |
| The **SHOTOKAN capture scripts** from [shotokan-sf6/mods](https://github.com/shotokan-sf6/mods) | They record every frame of a replay to a file Claude can read exactly. |
| **OBS** (optional) | A video of the replay lets Claude check key moments by eye. Reviews work from capture files alone. |

## 2. Set up the capture scripts (once)
1. Install REFramework for SF6 (follow its instructions; it adds a `reframework` folder next to the game).
2. From the mods repo, copy `autorun\*.lua` into `Street Fighter 6\reframework\autorun\`, and the `data\sf6_moves` folder into `Street Fighter 6\reframework\data\`.
3. Start the game. Press **Insert** to open the REFramework menu: you should see a **Replay Capture** window.

## 3. Add the skills to Claude (once)
1. **Personalize them.** The skills in this repo use placeholders like `{{PLAYER_NAME}}` and `{{PLAYER_CFN}}`. Fill them in with your own name, CFN name and folders using the snippet in [skills/README.md](skills/README.md#personalize-them). That gives you a `skills-personal` folder.
2. **Turn on file tools.** In Claude, go to **Settings → Capabilities** and make sure **Code execution and file creation** is on. In the newer settings layout it's called **Create and edit files**. Skills need it.
3. **Zip each skill folder.** Each skill is a folder with a `SKILL.md` inside (e.g. `skills-personal\sf6-replay-analysis\`). On Windows, right-click the folder → **Send to → Compressed (zipped) folder**. Make one zip per skill.
4. **Upload them.** In Claude, go to **Customize → Skills**, click **+**, then **+ Create skill → Upload a skill**, and choose the zip. Repeat for each skill.

Upload at least these:
- `sf6-replay-analysis`: the review itself;
- `sf6-review-dashboard`: the dashboard it builds;
- `replay-review-prediction`: predicts each set before reviewing it, then grades the prediction;
- `sf6-drive-efficiency`: Drive and super spending;
- `sf6-coach-shog`: coach .shog's rules and theories, used as a lens;
- `sf6-coach-coosco`: Coosco's replay-breakdown lessons, used as a lens;
- `sf6-character-notes`: per-character baselines, so habits are judged against what's normal for the character;
- `sf6-coach-juzzy-tips` and `sf6-coach-juzzy-sessions`: Juzzy's coaching lessons, also used as lenses.

If you have the coaching-lens skills (`skills/local/`, not in the public repo), upload those too. Without them the review still works, it just leans on fewer coaching frameworks.

Skills you upload stay private to your account.

## 4. Record a replay
1. In SF6, open a replay (Fighting Pass / CFN → Replays) and play it. If you use OBS, record it at the same time.
2. When the replay ends, the capture script saves `<ReplayID>.json` in `Street Fighter 6\reframework\data\`.
3. Move the `.json` (and the video, named `<ReplayID>.mp4`) to your coaching folder, e.g. `D:\SF6-Claude-Coaching\replays\`.

For a **set** (all the games against one opponent), record every game in it. Local matches work too: leave the capture script running while you play, and it saves each match when it ends.

To record many replays without clicking through menus, see the batch recorder in [batch/README.md](batch/README.md). It can also pull a player's last 100 replay IDs from Buckler by CFN ID (`batch/buckler_replays.py`, using your own Buckler login), so you don't have to copy IDs by hand.

## 5. Ask for a review
Open a new chat. If you're in the desktop app, give Claude access to your coaching folder when it asks (or attach the files to the message). Then just ask, in your own words. Some examples:

> Review my replays in D:\SF6-Claude-Coaching\replays: A7LWJNR6U and PCJFRDBW3. It's an FT2 ranked set, I'm .mycfn (Cammy). Quick review.

> Full review of the 3 games in D:\SF6-Claude-Coaching\local-night, local matches, no CFN names: I'm "alex" (Ken), my opponent is "sam" (Juri). Predict the set first.

> Treat these as a tournament set and review it from both my side and my opponent's.

Things that help Claude get it right:
- **Which games make up a set**, and the format (FT2 = first to 2 games, FT3 = first to 3).
- **Which player is you.** For local matches with no CFN names, give each player a name and character.
- **The review level you want:** Quick, Full or Tournament (see "Choosing a review level" below). If you don't say, Claude asks or picks Full.
- Claude writes a **prediction** before every review (winner, score and each player's gameplan, from your history and the matchup), then grades it afterwards. You don't need to ask.

A review takes a while: Claude reads every frame, runs the analysis, and builds the dashboard. You can leave the chat open and come back.

### Choosing a review level
The three levels use the same game data. They differ in how much Claude writes and checks by hand.

| | **Quick** | **Full** | **Tournament** |
|---|---|---|---|
| **In one line** | The numbers, computed straight from the capture | Quick + a coach's written review | Full + a match-by-match audit from both players' sides |
| **Damage breakdown, hit kinds, counter hits, anti-airs, burnouts, punishes** | ✓ | ✓ | ✓ |
| **Drive and super spending, Drive economy, every hit** | ✓ | ✓ | ✓ |
| **Player reads** (archetype and the eight spectra) | Computed from the data | Computed, then checked; Claude can overrule a score and says why | Same as Full, for both players in depth |
| **Habits** | Auto-detected from the stats (top damage starters, burnouts, what you press after blocking) | Written up, with when they happened and a fix for each | Same as Full |
| **Story of the set** (what worked, what cost games, what changed game to game) | – | ✓ | ✓ |
| **Gameplans** (each player's plan and how they adjusted) | – | ✓ | ✓ |
| **Fixes with drills, training routine** | – | ✓ | ✓, plus a longer training plan |
| **Findings by coaching skill** (E.X. Dojo, Maj, etc.) | – | ✓ | ✓ |
| **Key moments checked on video** | – | Some | Every key exchange |
| **Decision audit** ("could you have guessed better?" at each big guess) | – | – | ✓ |
| **Both players' perspectives** (a review written for your opponent too) | – | – | ✓ |
| **Between-games advice and rematch prep** | – | – | ✓ |
| **Time** | Fastest | Longer | Longest |

**Which to pick:**
- **Quick:** a batch of ranked sets, or when you just want the numbers. Quick reviews still feed your history, so patterns across many sets show up in your player profile.
- **Full:** a set you want to learn from: a loss you don't understand, a new matchup, a rival.
- **Tournament:** an important set (a tournament, a long FT3/FT5 against one player), or when you want to coach both sides. It works best with video of every game.

A **prediction** goes with every level: Claude writes its call before looking at the games, then grades itself in the review.

You can start small and go deeper later: "do a Full review of set 3" turns an existing Quick review into a Full one.

## 6. What you get back
- **A dashboard** (an interactive page in the chat) with Overview, Set review, Coach lenses and About SHOTOKAN tabs:
  - where your damage came from;
  - counter hits, anti-airs, burnouts and punishes (a burnout spent on a combo that kills, e.g. everything into a Level 3 for the round, doesn't count);
  - Drive and super spending;
  - player reads on eight spectra (e.g. Impulsive vs Mindful, Inelastic vs Elastic);
  - habits for both players;
  - the story of each game;
  - fixes with drills, and a training routine.
- **A short summary in the chat:** the result, the biggest highs and lows, and the top fixes.
- **Local copies** in your coaching folder (an offline HTML version and the data files), if Claude has access to it.
- **History:** every reviewed set goes into a local database (`history\sf6.db`), including sets you review for other players, so later reviews can compare you, and your opponents, with past sets. After a review, the capture files are stored gzipped (`<ReplayID>.json.gz`, about 40x smaller).

## 7. Keep going
Just keep chatting. For example:
- "Why did I lose round 2 of game 3?"
- "Show me every time I got anti-aired."
- "Add the next set to the same dashboard."
- "Compare tonight with my sets from last week."
- "Make the fixes into a 30-minute training plan."

If something looks wrong ("that wasn't a counter hit"), say so. Claude checks the data or the video and corrects it.

## Tips and troubleshooting
| Problem | What to do |
|---|---|
| Claude doesn't seem to use the skill | Mention "replay review" or "SF6 replay" in your message, and check the skill is switched on in **Customize → Skills**. |
| No capture file appeared | Make sure the Replay Capture window is open in REFramework and that you watched the replay to the end. |
| Files too big to attach | Use the desktop app and give Claude access to the folder instead of attaching them. |
| Only have a video, no capture | Reviews still work from video, but are slower and less exact (Claude reads the screen instead of the game data). |
| Confidence says "Low" | A 2-0 set gives little to go on. Reads firm up as more sets are reviewed. |

## See your history on the web (optional)
[shotokan-sf6/web](https://github.com/shotokan-sf6/web) turns your review history into a searchable site: a Players page with each player's overview, set lists and set details, head to head, **What winning players do** (the winner and loser of each set compared stat by stat), Observations (dated notes on what wins and what the model learned) and an About page. It runs locally with one Docker command, or on your own server; publishing a new snapshot after each batch of reviews keeps it current.
