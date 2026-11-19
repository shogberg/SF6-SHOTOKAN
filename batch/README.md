# Batch replay recording

Records SF6 replays by replay ID with no clicking: `batch_replays.lua` (inside SF6) searches and plays
each replay, `capture_replay.lua` saves the frame capture, and `batch_record.py` drives OBS and files
the results as `<ID>.mp4` + `<ID>.json` in `D:\SF6-Claude-Coaching\replays`.

## Setup (once)
1. Copy `batch_replays.lua` (from the REFramework mods repo) into `Street Fighter 6\reframework\autorun\` (next to `capture_replay.lua`).
2. OBS: Tools > WebSocket Server Settings > Enable WebSocket server (port 4455, authentication on).
3. `pip install obsws-python python-dotenv`
4. Copy `.env.example` to `.env` and fill it in (OBS password and your SF6 `reframework\data` path).

## First run: calibrate
The menu key sequences are a first guess and need a check on your setup.
1. Start SF6 and go to Fighting Pass/CFN > Replays.
2. `python batch_record.py --probe`, then navigate by hand to Search by Replay ID, a result, the info
   screen, a replay and End Replay. The screen names it prints (also in `reframework\data\sf6_batch\flows.json`)
   show what the script sees.
3. Try one replay without OBS: `python batch_record.py --no-obs A7LWJNR6U` and watch it.
   If a step goes wrong, put a fixed sequence in `reframework\data\sf6_batch\config.json`, e.g.
   `{"to_search": [["Escape",3],["",30],["S",3],["",15],["F",3],["",30],["Return",3],["",30]]}`
   (each step is [key, frames held]; "" waits). Reload scripts in REFramework after editing.

## Use
    python batch_record.py ID1 ID2 ID3
    python batch_record.py --file ids.txt
Already-recorded IDs are skipped; a failed ID is retried once, then skipped. Progress is in `batch_record.log`.
Stop at any time with Ctrl+C, or the Stop button under "Batch replays" in the REFramework menu.
