"""Ten independent LLM reasoning contexts with one immediately shared, durable event log."""
import argparse, concurrent.futures, datetime, json, os, sqlite3, urllib.request, urllib.error
from pathlib import Path

DB = Path(os.environ.get('COLLECTIVE_DB', 'collective.db'))
MODEL = os.environ.get('COLLECTIVE_MODEL', 'gpt-4o-mini')
URL = os.environ.get('COLLECTIVE_API_URL', 'https://api.openai.com/v1/chat/completions')


def database():
    con = sqlite3.connect(DB)
    con.execute('CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY AUTOINCREMENT, time TEXT, mind INTEGER, kind TEXT, content TEXT)')
    con.commit()
    return con


def publish(con, mind, kind, content):
    con.execute('INSERT INTO events(time,mind,kind,content) VALUES (?,?,?,?)',
                (datetime.datetime.now(datetime.timezone.utc).isoformat(), mind, kind, content))
    con.commit()  # Every event, including failures, is shared immediately in persistent memory.


def history(con):
    return [{'id': i, 'mind': m, 'kind': k, 'content': c} for i, m, k, c in
            con.execute('SELECT id,mind,kind,content FROM events ORDER BY id')]


def reason(mind, task, snapshot):
    key = os.environ.get('OPENAI_API_KEY')
    if not key:
        raise RuntimeError('OPENAI_API_KEY is not configured')
    prompt = ('You are one of ten equal reasoning perspectives in a single collective intelligence. '
              'Reason independently. All observations, failures, and conclusions are shared. '
              'Do not assume shared claims are true; critique them. State uncertainty and propose '
              'testable next steps. You have no special authority over other minds. '
              f'Your perspective number is {mind}.')
    payload = {'model': MODEL, 'temperature': 0.8,
               'messages': [{'role': 'system', 'content': prompt},
                            {'role': 'user', 'content': 'Collective task: '+task+'\n\nShared event history:\n'+json.dumps(snapshot, ensure_ascii=False)}]}
    request = urllib.request.Request(URL, data=json.dumps(payload).encode(),
                                     headers={'Authorization': 'Bearer '+key, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.load(response)['choices'][0]['message']['content']


def run(task, rounds):
    con = database()
    publish(con, 0, 'task', task)
    for round_number in range(1, rounds+1):
        print(f'\nRound {round_number}: ten independent reasoning calls')
        # All minds receive exactly the same snapshot at the start of a round.
        # Results are published as they arrive, without overwriting other opinions.
        snapshot = history(con)
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
            futures = {pool.submit(reason, mind, task, snapshot): mind for mind in range(1, 11)}
            for future in concurrent.futures.as_completed(futures):
                mind = futures[future]
                try:
                    answer = future.result()
                    publish(con, mind, 'reasoning', answer)
                    print(f'\nMind {mind}: {answer[:500]}')
                except Exception as exc:
                    publish(con, mind, 'failure', f'{type(exc).__name__}: {exc}')
                    print(f'Mind {mind} failed: {exc}')
    print(f'\nAll events saved in {DB}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('task', help='A question or problem for the collective')
    parser.add_argument('--rounds', type=int, default=2)
    args = parser.parse_args()
    if not 1 <= args.rounds <= 20:
        parser.error('--rounds must be between 1 and 20')
    run(args.task, args.rounds)
