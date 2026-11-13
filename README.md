# Electronics Discussion Monitor for Reddit

A Python prototype that finds recent public Reddit submissions matching electronics-related keywords, including component shortages, procurement, PCB design, and component sourcing.

## Purpose and audience

- This project is intended solely for the developer’s personal, non-commercial use as a Reddit reader interested in electronics and hardware engineering.
- It helps locate recent discussions about components, PCB design, availability, and sourcing. Results link back to the original Reddit discussions.
- Exported data will remain on the developer’s computer. It will not be shared with coworkers, customers, websites, or AI services. The project is not intended for commercial market intelligence, customer reporting, advertising, or AI training.
- Earlier descriptions referring to industry professionals and market intelligence did not accurately reflect the intended use and are superseded by this description.
- The current implementation is a prototype. API approval and appropriate data-handling controls are required before deployment.

## Current functionality

- Reads up to 100 recent submissions per configured subreddit using PRAW and Reddit’s OAuth API.
- Filters submissions by age, minimum score, and keyword matches in their titles and text.
- Saves matching submissions to a local JSON file with links to the original Reddit discussions.
- Does not retrieve comment bodies, post content, send messages, vote, or perform moderation actions.
- Does not include AI analysis or model training.

## Access requirements

API access requires Reddit’s explicit approval for the intended use case before running the tool. Creating API credentials alone does not establish approval. Commercial use requires appropriate written authorization from Reddit.

## Current data handling

The prototype exports post IDs, subreddit names, titles, author usernames, scores, comment counts, permalinks, up to 2,000 characters of post text, matched keywords, and creation timestamps.

Files are saved locally as `output/results_YYYY-MM-DD.json`. The search lookback setting controls which posts are retrieved; it is not a retention or deletion setting.

Automatic expiry and synchronization with content deleted or removed on Reddit are not currently implemented. The intended audience, permitted downstream uses, retention period, and deletion process must be finalized before deployment.

## Scope

Subreddits and keywords are explicitly configured. Automatic subreddit discovery and sentiment analysis are not currently implemented.
