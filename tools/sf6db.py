"""SF6 review history database (SQLite).

One file (D:\\SF6-Claude-Coaching\\history\\sf6.db) holding every reviewed set: players (CFN ID + names),
sets, games, the analyzer's hits / events / timings, per-set stats, player reads, habits and matchup notes.

  python sf6db.py init  DB
  python sf6db.py ingest DB ANALYZER_OUTDIR META.json      # one set; META describes it (see ingest_set)
  python sf6db.py sql   DB "SELECT ..."                   # ad-hoc query, prints rows

Re-ingesting a set replaces it (same set_key), so a set can be re-analysed without duplicates.
"""
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import rank as RANK
import json, os, sqlite3, sys, datetime, collections as C

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS players (
  player_id INTEGER PRIMARY KEY, cfn_id TEXT UNIQUE, name TEXT NOT NULL, first_seen TEXT, last_seen TEXT);
CREATE TABLE IF NOT EXISTS player_names (
  player_id INTEGER REFERENCES players, name TEXT, first_seen TEXT, last_seen TEXT, PRIMARY KEY (player_id, name));
CREATE TABLE IF NOT EXISTS sets (
  set_key TEXT PRIMARY KEY, played_date TEXT, ranked INTEGER, format TEXT, review TEXT,
  focus_player_id INTEGER REFERENCES players, opp_player_id INTEGER REFERENCES players,
  focus_char TEXT, opp_char TEXT, focus_games INTEGER, opp_games INTEGER, winner_player_id INTEGER REFERENCES players,
  focus_mr_start INTEGER, games_missing INTEGER DEFAULT 0, note TEXT, dashboard TEXT, analyzer TEXT, ingested_at TEXT);
CREATE TABLE IF NOT EXISTS games (
  replay_id TEXT PRIMARY KEY, set_key TEXT REFERENCES sets ON DELETE CASCADE, game_no INTEGER, played_time TEXT,
  p1_player_id INTEGER REFERENCES players, p2_player_id INTEGER REFERENCES players, p1_char TEXT, p2_char TEXT,
  p1_control INTEGER, p2_control INTEGER, p1_mr INTEGER, p2_mr INTEGER,
  winner_player_id INTEGER REFERENCES players, round_score TEXT, round_winners TEXT, capture_file TEXT,
  p1_lp INTEGER, p2_lp INTEGER, p1_rank TEXT, p2_rank TEXT);   -- rank: league below Master, '<MR> MR' or 'MR unknown' at Master (rank.py)
CREATE TABLE IF NOT EXISTS hits (
  hit_id INTEGER PRIMARY KEY, set_key TEXT REFERENCES sets ON DELETE CASCADE, replay_id TEXT, round INTEGER, round_timer INTEGER,
  attacker_id INTEGER, victim_id INTEGER, attacker_char TEXT, victim_char TEXT, damage INTEGER, starter TEXT, hits_in_combo INTEGER,
  hit_kind TEXT, anti_air INTEGER, situation TEXT, lens TEXT, victim_state TEXT, victim_move TEXT, note TEXT,
  drive_spent REAL, super_spent REAL, drive_gained REAL, drive_damage REAL, knockdown TEXT, kd_adv INTEGER, corner_dist REAL, victim_drive_after REAL);
CREATE TABLE IF NOT EXISTS events (
  event_id INTEGER PRIMARY KEY, set_key TEXT REFERENCES sets ON DELETE CASCADE, replay_id TEXT, round INTEGER, round_timer INTEGER,
  player_id INTEGER, type TEXT, note TEXT);
CREATE TABLE IF NOT EXISTS timings (
  timing_id INTEGER PRIMARY KEY, set_key TEXT REFERENCES sets ON DELETE CASCADE, replay_id TEXT, round INTEGER, round_timer INTEGER,
  player_id INTEGER, event TEXT, action TEXT, frames_until INTEGER);
CREATE TABLE IF NOT EXISTS resources (            -- Drive / super spent per player per round, by category (bars; 1 bar = 10,000)
  set_key TEXT REFERENCES sets ON DELETE CASCADE, replay_id TEXT, round INTEGER, player_id INTEGER,
  drive_rush REAL, drive_parry REAL, drive_impact REAL, drive_reversal REAL, od_specials REAL, drive_other REAL, drive_total REAL,
  super_bars REAL, supers TEXT, burnouts INTEGER, drive_end REAL, super_end REAL,
  gain_hit REAL, gain_block REAL, parry_regain REAL, loss_block REAL, loss_hit REAL, loss_hit_drive_impact REAL, loss_hit_punish_counter REAL,
  drive_rush_cancel REAL,                         -- part of drive_rush spent on combo / pressure cancels (the rest is raw)
  PRIMARY KEY (replay_id, round, player_id));
CREATE TABLE IF NOT EXISTS parries (              -- each Drive Parry: cost, hits parried, Drive regained, perfect, what happened next
  set_key TEXT REFERENCES sets ON DELETE CASCADE, replay_id TEXT, round INTEGER, round_timer INTEGER, player_id INTEGER,
  frames INTEGER, drive_before REAL, cost REAL, hits_parried INTEGER, regained REAL, net REAL, perfect INTEGER, next TEXT);
CREATE TABLE IF NOT EXISTS set_stats (            -- long format: one row per set, player and metric, for trends
  set_key TEXT REFERENCES sets ON DELETE CASCADE, player_id INTEGER, metric TEXT, value REAL, PRIMARY KEY (set_key, player_id, metric));
CREATE TABLE IF NOT EXISTS reads (
  set_key TEXT REFERENCES sets ON DELETE CASCADE, player_id INTEGER, character TEXT, archetype TEXT, lean TEXT, confidence TEXT,
  evidence TEXT, counter_note TEXT, risk_tolerance TEXT, temperament TEXT, source TEXT, PRIMARY KEY (set_key, player_id));
CREATE TABLE IF NOT EXISTS habits (
  habit_row INTEGER PRIMARY KEY, set_key TEXT REFERENCES sets ON DELETE CASCADE, player_id INTEGER, kind TEXT, area TEXT, habit TEXT,
  seen TEXT, times INTEGER, fix TEXT, confidence TEXT, source TEXT);
CREATE TABLE IF NOT EXISTS matchup_notes (        -- scope 'character' (my_char vs opp_char) or 'player' (me vs opp_player)
  note_id INTEGER PRIMARY KEY, scope TEXT, my_char TEXT, opp_char TEXT, opp_player_id INTEGER, kind TEXT, note TEXT,
  seen_in TEXT, status TEXT, created TEXT, updated TEXT);
CREATE TABLE IF NOT EXISTS usage (            -- move usage per game and player, from the analyzer report
  set_key TEXT REFERENCES sets ON DELETE CASCADE, replay_id TEXT, player_id INTEGER, move TEXT, n INTEGER,
  PRIMARY KEY (replay_id, player_id, move));
CREATE TABLE IF NOT EXISTS review_docs (      -- hand-written Full-review content per set and dashboard dataset (kept across re-ingests)
  set_key TEXT, dataset TEXT, rows TEXT, updated TEXT, PRIMARY KEY (set_key, dataset));
CREATE TABLE IF NOT EXISTS dashboard_sets (   -- stable "Set N" numbering per dashboard
  dashboard TEXT, set_key TEXT, set_no INTEGER, PRIMARY KEY (dashboard, set_key));
CREATE INDEX IF NOT EXISTS ix_hits_set ON hits(set_key); CREATE INDEX IF NOT EXISTS ix_hits_victim ON hits(victim_id, lens);
CREATE INDEX IF NOT EXISTS ix_sets_opp ON sets(opp_player_id); CREATE INDEX IF NOT EXISTS ix_sets_chars ON sets(focus_char, opp_char);
CREATE INDEX IF NOT EXISTS ix_stats_metric ON set_stats(metric, player_id);

-- views: who you play and which matchups
CREATE VIEW IF NOT EXISTS v_sets AS
  SELECT s.set_key, s.played_date, s.played_date || ' ' || COALESCE((SELECT MIN(played_time) FROM games g WHERE g.set_key = s.set_key), '') AS played_at, s.ranked, s.review, f.name AS focus, s.focus_char, o.name AS opponent, o.cfn_id AS opp_cfn_id, s.opp_char,
         s.focus_games || '-' || s.opp_games AS score, CASE WHEN s.winner_player_id = s.focus_player_id THEN 'W' ELSE 'L' END AS result,
         s.focus_mr_start, s.games_missing, s.note
  FROM sets s JOIN players f ON f.player_id = s.focus_player_id JOIN players o ON o.player_id = s.opp_player_id;
CREATE VIEW IF NOT EXISTS v_player_matchups AS
  SELECT focus, opponent, opp_cfn_id, COUNT(*) AS sets, SUM(result = 'W') AS sets_won, SUM(result = 'L') AS sets_lost,
         GROUP_CONCAT(DISTINCT opp_char) AS their_chars, GROUP_CONCAT(DISTINCT focus_char) AS my_chars, MAX(played_date) AS last_played
  FROM v_sets GROUP BY focus, opponent;
CREATE VIEW IF NOT EXISTS v_char_matchups AS
  SELECT focus, focus_char, opp_char, COUNT(*) AS sets, SUM(result = 'W') AS sets_won, SUM(result = 'L') AS sets_lost,
         COUNT(DISTINCT opponent) AS opponents, MAX(played_date) AS last_played
  FROM v_sets GROUP BY focus, focus_char, opp_char;
"""

DR_TYPES = ('raw drive rush', 'pressure drive rush cancel', 'combo drive rush cancel', 'whiff drive rush cancel')


def connect(db):
    con = sqlite3.connect(db)
    con.execute('PRAGMA foreign_keys = ON')
    con.executescript(SCHEMA)
    for t, cols in (('games', 'p1_lp INTEGER, p2_lp INTEGER, p1_rank TEXT, p2_rank TEXT'), ('hits', 'drive_spent REAL, super_spent REAL, drive_gained REAL, drive_damage REAL, knockdown TEXT, kd_adv INTEGER, corner_dist REAL, victim_drive_after REAL'),
                    ('resources', 'gain_hit REAL, gain_block REAL, parry_regain REAL, loss_block REAL, loss_hit REAL, loss_hit_drive_impact REAL, loss_hit_punish_counter REAL, drive_rush_cancel REAL')):
        have = {r[1] for r in con.execute(f'PRAGMA table_info({t})')}
        for c_ in cols.split(', '):
            if c_.split()[0] not in have: con.execute(f'ALTER TABLE {t} ADD COLUMN {c_}')   # older databases
    return con


def player(con, name, cfn_id=None, seen=None):
    """Find or create a player: by CFN ID when known, else by current name. Records name changes."""
    cur = con.cursor()
    row = None
    if cfn_id:
        row = cur.execute('SELECT player_id, name FROM players WHERE cfn_id = ?', (cfn_id,)).fetchone()
        if not row:  # a player first stored by name only, now seen with an ID
            row = cur.execute('SELECT player_id, name FROM players WHERE name = ? AND cfn_id IS NULL', (name,)).fetchone()
            if row: cur.execute('UPDATE players SET cfn_id = ? WHERE player_id = ?', (cfn_id, row[0]))
    if not row:
        row = cur.execute('SELECT player_id, name FROM players WHERE name = ? ORDER BY cfn_id IS NULL LIMIT 1', (name,)).fetchone()
    if not row:
        cur.execute('INSERT INTO players (cfn_id, name, first_seen, last_seen) VALUES (?, ?, ?, ?)', (cfn_id, name, seen, seen))
        pid = cur.lastrowid
    else:
        pid = row[0]
        if seen:
            cur.execute('UPDATE players SET name = ?, last_seen = MAX(COALESCE(last_seen, ?), ?), first_seen = MIN(COALESCE(first_seen, ?), ?) WHERE player_id = ?',
                        (name, seen, seen, seen, seen, pid))
    cur.execute('INSERT OR IGNORE INTO player_names (player_id, name, first_seen, last_seen) VALUES (?, ?, ?, ?)', (pid, name, seen, seen))
    if seen:
        cur.execute('UPDATE player_names SET last_seen = MAX(COALESCE(last_seen, ?), ?), first_seen = MIN(COALESCE(first_seen, ?), ?) WHERE player_id = ? AND name = ?',
                    (seen, seen, seen, seen, pid, name))
    return pid


def set_stats(hits, events, timings, games, pids, presses=None):
    """Per-player metrics for trend tracking (ints and shares)."""
    out = {}
    for name, pid in pids.items():
        mine = [h for h in hits if h['attacker'] == name]; took = [h for h in hits if h['victim'] == name]
        taken = sum(h['damage'] for h in took) or 0
        m = dict(games=len(games), damage_dealt=sum(h['damage'] for h in mine), damage_taken=taken,
                 counter_hits=sum(h['hit_kind'] == 'counter hit' for h in mine), punish_counters=sum(h['hit_kind'] == 'punish counter' for h in mine),
                 throws=sum(h['hit_kind'] == 'throw' for h in mine), anti_airs=sum(bool(h['anti_air']) for h in mine),
                 burnouts=sum(e['player'] == name and e['type'] == 'burnout' for e in events),
                 throw_techs=sum(e['player'] == name and e['type'] == 'throw tech' for e in events),
                 perfect_parries=sum(e['player'] == name and e['type'] == 'perfect parry' for e in events),
                 drive_reversals=sum(e['player'] == name and e['type'] == 'drive reversal' for e in events))
        if presses:   # button economy (Theory #4): all presses and decision presses (opponent not being hit / knocked down)
            pr = [x for x in presses if x['player'] == name]
            m['presses'] = sum(x['presses'] for x in pr); m['decision_presses'] = sum(x['decision_presses'] for x in pr); m['press_rounds'] = len(pr)
        for t in DR_TYPES:
            m[t.replace(' ', '_')] = sum(e['player'] == name and e['type'] == t for e in events)
        for ev in ('after block', 'wake-up'):
            ts = [t for t in timings if t['player'] == name and t['event'] == ev]
            k = ev.replace(' ', '_').replace('-', '_')
            m[f'{k}_n'] = len(ts)
            m[f'{k}_attack'] = sum(t['action'].split(':')[0] in ('atck', 'special', 'super') for t in ts)
            m[f'{k}_attack_f0'] = sum(t['action'].split(':')[0] in ('atck', 'special', 'super') and (t['frames_until'] or 0) <= 1 for t in ts)
            m[f'{k}_hold'] = sum(t['action'].startswith('nothing') for t in ts)
            m[f'{k}_jump'] = sum(t['action'].startswith('jump') for t in ts)
            m[f'{k}_parry'] = sum(t['action'].startswith('parry') for t in ts)
        lens = C.Counter()
        sit = C.Counter()
        for h in took:
            lens[h['lens'] or 'Unclear / super'] += h['damage']; sit[h['situation']] += h['damage']
        for k, v in lens.items(): m['taken_share: ' + k] = round(v / taken, 4) if taken else 0
        for k, v in sit.items(): m['taken_situation_share: ' + k] = round(v / taken, 4) if taken else 0
        out[pid] = m
    return out


def resource_row(k, r, names):
    b = r['drive_bars']
    return (k, r['game_id'], r['round'], names[r['player']], b.get('Drive Rush'), b.get('Drive Parry'), b.get('Drive Impact'), b.get('Drive Reversal'),
            b.get('OD specials'), b.get('other'), r['drive_total_bars'], r['super_bars'], json.dumps(r['supers']), r['burnouts'],
            round((r['drive_end'] or 0) / 10000, 2), round((r['super_end'] or 0) / 10000, 2),
            r.get('gain_hit'), r.get('gain_block'), r.get('parry_regain'), r.get('loss_block'), r.get('loss_hit'), r.get('loss_hit_drive_impact'), r.get('loss_hit_punish_counter'), r.get('drive_rush_cancel_bars'))


def ingest_set(con, outdir, meta):
    """meta: set_key, focus (name), played_date, ranked, review ('Full'/'Quick'), format, note, dashboard,
    games_missing, game_times [..], focus_mr [..] (per game, optional), reads [rows], habits [rows] (default: review_docs archetypes / habits), source (reads/habits origin),
    review_docs {dataset: rows} (hand-written Full-review content, kept across re-ingests), dash {"dashboard": "quick-dashboard", "set_no": N} (stable Set N)."""
    L = lambda n: json.load(open(os.path.join(outdir, n + '.json')))
    hits, events, timings, games = L('hits'), L('events'), L('timings'), L('games')
    presses = L('presses') if os.path.exists(os.path.join(outdir, 'presses.json')) else None
    infos = {}
    for n, g in enumerate(games):
        infos[g['game_id']] = load_info(meta['captures_local'][g['game_id']])
        for s_ in ('p1', 'p2'):   # names typed in Move Export for ids the game doesn't name (char_names.json)
            c_ = infos[g['game_id']].get(s_ + '_char') or ''
            if c_.startswith('char_') and c_[5:] in (meta.get('char_names') or {}):
                infos[g['game_id']][s_ + '_char'] = meta['char_names'][c_[5:]]
        for s_, c_ in (meta.get('override') or {}).get(g['game_id'], {}).items():   # stale labels in pre-v3.1 captures
            infos[g['game_id']][s_ + '_char'] = c_
        if meta.get('game_numbers'): g['game_no'] = meta['game_numbers'][n]          # e.g. a game missing from the set
    k = meta['set_key']
    cur = con.cursor()
    cur.execute('DELETE FROM sets WHERE set_key = ?', (k,))
    seen = meta.get('played_date')
    names = {}
    for g in games:
        i = infos[g['game_id']]
        for s in ('p1', 'p2'):
            names[i[s + '_name']] = player(con, i[s + '_name'], i.get(s + '_cfn_id'), seen)
    focus = meta['focus']; opp = next(n for n in names if n != focus)
    i0 = infos[games[0]['game_id']]
    fs = 'p1' if i0['p1_name'] == focus else 'p2'; os_ = 'p2' if fs == 'p1' else 'p1'
    fg = sum(g['winner'] == focus for g in games) + meta.get('extra_focus_wins', 0)
    og = len(games) - sum(g['winner'] == focus for g in games) + meta.get('extra_opp_wins', 0)
    winner = names[focus] if fg > og else names[opp]
    cur.execute('INSERT INTO sets VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                (k, seen, meta.get('ranked'), meta.get('format', 'FT2'), meta.get('review'), names[focus], names[opp],
                 meta.get('focus_char') or i0[fs + '_char'], meta.get('opp_char') or i0[os_ + '_char'], fg, og, winner,
                 (meta.get('focus_mr') or [None])[0] or None, meta.get('games_missing', 0), meta.get('note'), meta.get('dashboard'),
                 meta.get('analyzer', 'analyze_capture.py'), datetime.datetime.now().isoformat(timespec='seconds')))
    for n, g in enumerate(games):
        i = infos[g['game_id']]
        fm = (meta.get('focus_mr') or [None] * len(games))[n] if n < len(meta.get('focus_mr') or []) else None
        p1mr = i.get('p1_mr') or (fm if fs == 'p1' else None); p2mr = i.get('p2_mr') or (fm if fs == 'p2' else None)
        lp1, lp2 = i.get('p1_lp'), i.get('p2_lp')
        cur.execute('INSERT OR REPLACE INTO games VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                    (g['game_id'], k, g['game_no'], (meta.get('game_times') or [None] * 9)[n] if meta.get('game_times') else None,
                     names[i['p1_name']], names[i['p2_name']], i['p1_char'], i['p2_char'], i.get('p1_control'), i.get('p2_control'),
                     p1mr or None, p2mr or None, names[g['winner']], g['round_score'], g['round_winners'], meta['captures'][g['game_id']],
                     lp1, lp2, RANK.label(lp1, p1mr), RANK.label(lp2, p2mr)))
    charof = {}
    for g in games:
        i = infos[g['game_id']]
        for s in ('p1', 'p2'): charof[(g['game_id'], i[s + '_name'])] = i[s + '_char']
    cur.executemany('INSERT INTO hits (set_key, replay_id, round, round_timer, attacker_id, victim_id, attacker_char, victim_char, damage, starter, hits_in_combo, hit_kind, anti_air, situation, lens, victim_state, victim_move, note, drive_spent, super_spent, drive_gained, drive_damage, knockdown, kd_adv, corner_dist, victim_drive_after) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                    [(k, h['game_id'], h['round'], h['round_timer'], names[h['attacker']], names[h['victim']], charof.get((h['game_id'], h['attacker'])),
                      charof.get((h['game_id'], h['victim'])), h['damage'], h['starter'], h.get('hits_in_combo'), h['hit_kind'], int(bool(h.get('anti_air'))),
                      h.get('situation'), h.get('lens'), h.get('victim_state'), h.get('victim_move'), h.get('note'),
                      h.get('drive_spent'), h.get('super_spent'), h.get('drive_gained'), h.get('drive_damage'), h.get('knockdown'), h.get('kd_adv'), h.get('corner_dist'), h.get('victim_drive_after')) for h in hits])
    cur.executemany('INSERT INTO events (set_key, replay_id, round, round_timer, player_id, type, note) VALUES (?,?,?,?,?,?,?)',
                    [(k, e['game_id'], e['round'], e.get('round_timer'), names[e['player']], e['type'], e.get('note')) for e in events])
    cur.executemany('INSERT INTO timings (set_key, replay_id, round, round_timer, player_id, event, action, frames_until) VALUES (?,?,?,?,?,?,?,?)',
                    [(k, t['game_id'], t['round'], t['round_timer'], names[t['player']], t['event'], t['action'], t['frames_until']) for t in timings])
    if os.path.exists(f'{outdir}/resources.json'):
        cur.execute('DELETE FROM resources WHERE set_key=?', (k,))
        cur.executemany('INSERT OR REPLACE INTO resources VALUES (' + ','.join('?' * 24) + ')', [resource_row(k, r, names) for r in L('resources')])
    cur.execute('DELETE FROM parries WHERE set_key=?', (k,))
    if os.path.exists(f'{outdir}/parries.json'):
        cur.executemany('INSERT INTO parries VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)', [(k, x['game_id'], x['round'], x['round_timer'], names[x['player']], x['frames'], x['drive_before'], x['cost'],
                                                                                x['hits_parried'], x['regained'], x['net'], int(bool(x['perfect'])), x['next']) for x in L('parries')])
    for pid, m in set_stats(hits, events, timings, games, names, presses).items():
        cur.executemany('INSERT INTO set_stats VALUES (?,?,?,?)', [(k, pid, a, b) for a, b in m.items()])
    rep = os.path.join(outdir, 'report.md')
    if os.path.exists(rep):
        import ast, re
        gi = -1
        for line in open(rep, encoding='utf-8'):
            if line.startswith('# Game'): gi += 1
            m = re.match(r'\s+usage (.+?): (\[.*\])$', line)
            if m and 0 <= gi < len(games) and m.group(1) in names:
                cur.executemany('INSERT OR REPLACE INTO usage VALUES (?,?,?,?,?)',
                                [(k, games[gi]['game_id'], names[m.group(1)], mv, n) for mv, n in ast.literal_eval(m.group(2))])
    for ds, rows in (meta.get('review_docs') or {}).items():
        cur.execute('INSERT OR REPLACE INTO review_docs VALUES (?,?,?,?)', (k, ds, json.dumps(rows, ensure_ascii=False), datetime.datetime.now().isoformat(timespec='seconds')))
    if meta.get('dash'):   # {"dashboard": name, "set_no": N or None (next free)}
        d = meta['dash']; have = cur.execute('SELECT set_no FROM dashboard_sets WHERE dashboard=? AND set_key=?', (d['dashboard'], k)).fetchone()
        if not have:
            no = d.get('set_no') or (cur.execute('SELECT COALESCE(MAX(set_no),0)+1 FROM dashboard_sets WHERE dashboard=?', (d['dashboard'],)).fetchone()[0])
            cur.execute('INSERT INTO dashboard_sets VALUES (?,?,?)', (d['dashboard'], k, no))
    src = meta.get('source')
    # A Full review's hand-written archetypes / habits live in review_docs; use them when META has no
    # separate reads / habits, so the reads and habits tables (and SHOTOKAN-WEB) always get them.
    docs = meta.get('review_docs') or {}
    if not meta.get('reads') and docs.get('archetypes'): meta['reads'] = docs['archetypes']
    if not meta.get('habits') and docs.get('habits'): meta['habits'] = docs['habits']
    for r in meta.get('reads', []):
        if r['player'] not in names: continue
        cur.execute('INSERT OR REPLACE INTO reads VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                    (k, names[r['player']], r.get('character'), r.get('archetype'), r.get('lean'), r.get('confidence'), r.get('evidence'),
                     r.get('counter_note'), r.get('doc_risk_tolerance'), r.get('doc_temperament'), src))
    cur.executemany('INSERT INTO habits (set_key, player_id, kind, area, habit, seen, times, fix, confidence, source) VALUES (?,?,?,?,?,?,?,?,?,?)',
                    [(k, names[h['player']], h.get('kind'), h.get('area'), h.get('habit'), h.get('seen'), h.get('times'), h.get('fix'), h.get('confidence'), src)
                     for h in meta.get('habits', []) if h['player'] in names])
    con.commit()
    return k


def load_info(path):
    """Just the capture's info block (plain or .gz)."""
    if path.endswith('.gz'):
        import gzip
        with gzip.open(path, 'rt', encoding='utf-8') as f: return json.load(f)['info']
    return json.load(open(path, encoding='utf-8'))['info']


if __name__ == '__main__':
    cmd, db = sys.argv[1], sys.argv[2]
    con = connect(db)
    if cmd == 'ingest':
        print('ingested', ingest_set(con, sys.argv[3], json.load(open(sys.argv[4]))))
    elif cmd == 'sql':
        cur = con.execute(sys.argv[3]); print(' | '.join(d[0] for d in cur.description))
        for r in cur.fetchall(): print(' | '.join('' if v is None else str(v) for v in r))
    elif cmd == 'init':
        print('ok')
