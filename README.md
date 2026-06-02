# Electronics Industry Reddit Monitor

A tool that monitors Reddit for discussions about electronics components, procurement, supply chain, and hardware engineering. Designed for industry professionals who need to track emerging trends, component shortages, and community sentiment across relevant subreddits.

## What it does

- Discovers relevant subreddits for electronics, procurement, and hardware engineering topics
- Monitors recent posts and discussions matching configurable keywords
- Filters content by date range so you only see recent activity
- Exports matched posts to JSON for downstream analysis or reporting

## Use case

Electronics buyers, hardware engineers, and supply chain analysts use this to:
- Track component shortage signals early (e.g. MLCC, semiconductor lead times)
- Monitor discussions about specific parts, distributors, or manufacturers
- Stay current on community sentiment around supply chain disruptions
- Research how engineers approach component selection and sourcing

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Create a Reddit app

1. Go to https://www.reddit.com/prefs/apps
2. Click **create another app**
3. Select **script** as the app type
4. Set redirect URI to `http://localhost:8080`
5. Copy your **client ID** (below the app name) and **client secret**

### 3. Configure

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

### 4. Run

```bash
python monitor.py
```

Results are saved to `output/results_YYYY-MM-DD.json`.

## Configuration

Edit `.env` to control:

| Variable | Default | Description |
|----------|---------|-------------|
| `DAYS_BACK` | `7` | How many days back to search |
| `KEYWORDS` | *(see .env.example)* | Comma-separated keywords to track |
| `SUBREDDITS` | *(see .env.example)* | Subreddits to monitor |
| `MIN_SCORE` | `1` | Minimum post score to include |

## Rate limits

This app uses Reddit's official OAuth API and respects the 100 requests/minute rate limit. It adds delays between requests to stay well within limits.

## License

MIT
