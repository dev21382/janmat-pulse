CREATE TABLE IF NOT EXISTS opinion_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id TEXT NOT NULL,
    source TEXT NOT NULL,             -- 'reddit' | 'news'
    external_id TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT,
    created_utc INTEGER NOT NULL,     -- unix timestamp of the original post/article
    fetched_utc INTEGER NOT NULL,
    score REAL,                       -- reddit upvotes, null for news
    sentiment REAL,                   -- VADER compound score, -1..1
    UNIQUE(topic_id, source, external_id)
);

CREATE INDEX IF NOT EXISTS idx_items_topic_created ON opinion_items(topic_id, created_utc);

CREATE TABLE IF NOT EXISTS daily_sentiment (
    topic_id TEXT NOT NULL,
    day TEXT NOT NULL,               -- ISO date, UTC
    mean_sentiment REAL NOT NULL,
    item_count INTEGER NOT NULL,
    PRIMARY KEY (topic_id, day)
);

CREATE TABLE IF NOT EXISTS forecasts (
    topic_id TEXT NOT NULL,
    generated_utc INTEGER NOT NULL,
    horizon_day TEXT NOT NULL,       -- ISO date being forecast
    predicted_sentiment REAL NOT NULL,
    PRIMARY KEY (topic_id, generated_utc, horizon_day)
);
