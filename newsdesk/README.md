# newsdesk: Phase 1 of the AI news-trading plan

newsdesk reads the news for a watchlist of 40 stocks (20 US, 20 euro-area) a few
times a day. Two AI analysts each give a view on every stock with fresh
headlines: long, short or no trade, how many sessions the move should last
(1 to 5), and how confident they are (1 to 5). By default they are Claude
Haiku 5.5, through Anthropic's API, and a free model running on your own PC
through Ollama. Both see exactly the same news and are scored separately, so the
scorecard shows whether the free model is good enough. Every call is
time-stamped when it is made and scored automatically once the prices are in.

It places no orders and connects to no broker. Phase 1 exists to answer one
question with real, forward-looking data before any money is at risk:
**do the AI's calls beat simply holding the index, after costs?**

## How a call is scored

The rules are strict on purpose, so the result can be trusted:

- **Entry** is the open of the first trading session that starts *after* the
  call was logged. A call made at 15:00 Helsinki time on a Helsinki stock enters
  at the next morning's open. The jump that happens when the news first comes
  out is never counted, because by the time you had read it, that jump was gone.
- **Exit** is the close of the last session in the call's horizon. Horizon 1
  means in at the open, out at the close of the same session.
- **Costs** are subtracted from every call. With the defaults below that is
  0.30% per round trip on US stocks and 0.40% on euro stocks, plus a stock
  borrowing fee on shorts. Edit `config.yaml` to match your real Interactive
  Brokers fees.
- **Benchmark.** Each call is compared with the index over the same days: SPY
  for US stocks, the iShares STOXX Europe 600 ETF (EXSA.DE) for euro stocks.
- **Only fresh news.** Only headlines published in the last 24 hours are
  analysed, and Claude only sees them as they arrive. A back-test on old news
  would let the model use what it already knows about how those stories ended.
- **The log is append-only.** A call is never edited after it is written.

## Gate 1

`python -m newsdesk report` prints the scorecard, with a result for each
analyst. An analyst passes Gate 1 when both of these hold:

1. At least 400 calls with confidence 3 or higher have been scored.
2. On average those calls beat holding the index over the same days, after
   costs, with a t-stat above 2.

The scorecard also shows a baseline: buy every stock that had a call and ignore
the AI's direction. The AI only adds value if it beats that.

If no analyst passes, the trading idea stops there. You still have a news-brief tool.

## Setup

You need Python 3.10 or newer, an Anthropic API key from
[console.anthropic.com](https://console.anthropic.com), and Ollama for the local
model.

**1. newsdesk**

```bash
cd newsdesk
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python -m pytest                   # 18 tests, no network needed
```

Set the API key. On Windows, run this once and then open a new terminal:
`setx ANTHROPIC_API_KEY "sk-ant-..."`. On Linux or macOS, use
`export ANTHROPIC_API_KEY=sk-ant-...`.

**2. The local model**

Install Ollama from [ollama.com](https://ollama.com). On Windows it runs in the
background and starts with the computer. Then download the model:

```bash
ollama pull qwen3:8b
ollama run qwen3:8b "Say hello"    # check that it works, then type /bye
```

With 6 GB of graphics memory, as on an RTX 3060 laptop, `qwen3:8b` only just
fits. Ollama puts the overflow in normal memory, which works but is slower. If a
call takes more than about a minute, switch to `qwen3:4b`: run
`ollama pull qwen3:4b` and change `model:` under the `local` analyst in
`config.yaml`. Newer models appear in the [Ollama library](https://ollama.com/library)
all the time; any model that fits your memory will work. Give each new model
its own analyst `name` so its record stays separate.

**3. First run**

```bash
python -m newsdesk --only NOKIA.HE,AAPL run   # two stocks, both analysts
python -m newsdesk brief                      # read what they said
```

If one analyst fails, for example because Ollama is not running, the other
carries on and the error is printed. That analyst picks up the unread news on
the next run, as long as the news is still within 24 hours old.

## Daily use

| Command | What it does |
|---|---|
| `python -m newsdesk run` | Fetch news, ask Claude, score finished calls. This is the scheduled job. |
| `python -m newsdesk brief --hours 24` | Today's calls in readable form. |
| `python -m newsdesk report --out reports/scorecard.md` | The scorecard and Gate 1 check. |
| `python -m newsdesk fetch` | News only, no AI and no cost. |
| `python -m newsdesk score` | Score calls only. |
| `python -m newsdesk --analyst local run` | Run only the named analyst(s). |

Run `run` three times on weekdays. Suggested times in Finland are 08:30, before
Helsinki opens at 10:00; 15:00, before New York opens at 16:30; and 22:30,
after New York closes. On Linux or macOS, add this with `crontab -e`:

```
30 8,15 * * 1-5  cd /path/to/newsdesk && .venv/bin/python -m newsdesk run >> data/run.log 2>&1
30 22   * * 1-5  cd /path/to/newsdesk && .venv/bin/python -m newsdesk run >> data/run.log 2>&1
```

On Windows, use Task Scheduler to run `.venv\Scripts\python.exe -m newsdesk run`
in the `newsdesk` folder at the same times. The computer has to be on at those
times. A small always-on machine works too, such as a Raspberry Pi or a cheap
cloud server.

Everything is stored in `data/newsdesk.db`, a SQLite file. Back it up, because
it is the evidence.

## Cost

An analyst is only called for a stock when it has new headlines. With 40 stocks
and three runs a day, expect roughly 50 to 100 calls a day per analyst. Rough
costs:

| Analyst model | Per call | Per month (about 1,500 to 2,000 calls) |
|---|---|---|
| Local model through Ollama | Free | Electricity only |
| `claude-haiku-5-5` (default) | under $0.001 | ~$1–2 |
| `claude-sonnet-5-5` | ~$0.01 | ~$15–25 |
| `claude-opus-5-5` (most capable) | ~$0.02–0.03 | ~$35–60 |

These are estimates; your Anthropic Console shows actual usage. The news and
price data are free.

On a 6 GB graphics card, the local model takes roughly 10 to 60 seconds a call,
so one run of 20 to 40 calls takes about 5 to 30 minutes. That is fine with
runs hours apart. Setting `think: true` lets the model reason before it answers,
which may give better calls but makes each one several times slower.

To try a stronger Claude model, add a third analyst with its own name, for
example `claude-sonnet`, rather than changing the model of an existing one.
That keeps each model's record separate.

## Files

| File | Purpose |
|---|---|
| `watchlist.yaml` | The stocks. Euro stocks avoid currency fees on a euro account. |
| `config.yaml` | Analysts and models, costs, horizon rules, Gate 1 thresholds, exchange hours. |
| `newsdesk/news.py` | Google News RSS and Yahoo Finance headlines, de-duplicated. |
| `newsdesk/analyst.py` | The prompt, and the Claude and Ollama calls, with a fixed JSON answer format. |
| `newsdesk/prices.py` | Daily prices (Yahoo Finance) and the entry and exit session rules. |
| `newsdesk/scoring.py` | Returns, costs and benchmark comparison. |
| `newsdesk/report.py` | Scorecard and daily brief. |

## Limits

- Yahoo Finance and Google News are free, unofficial sources meant for
  personal use. They can change format or rate-limit without notice. If a
  source fails, the run continues with the others and logs a warning. Check
  each site's terms before using them for anything other than personal research.
- Daily prices only. Entry at the next open is deliberately conservative.
  Phase 2 uses Interactive Brokers' own prices.
- Calls that overlap in time are not independent, so treat the t-stat as a
  floor, not proof.

## Next: Phase 2 (only after Gate 1 passes)

While Phase 1 runs, open an Interactive Brokers account and enable its paper
trading account. In Phase 2, newsdesk sends orders to that paper account through
the IBKR API, long and short, with position-size and daily-loss limits. That
tests real fills with no money at risk.

This is a research tool, not financial advice.
