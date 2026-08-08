"""Topic definitions shared by ingestion, sentiment and forecast modules.

Each topic maps to search keywords used against Reddit search and Google News
RSS search, plus a display label and the section hue reused from the
portfolio's design language (kept for brand continuity across the two
projects).
"""

TOPICS = {
    "economy_jobs": {
        "label": "Economy & Jobs",
        "query": "India economy unemployment jobs GDP",
        "hue": "#e0a455",
    },
    "agriculture": {
        "label": "Farmers & Agriculture",
        "query": "India farmers MSP agriculture policy",
        "hue": "#79cf9a",
    },
    "healthcare": {
        "label": "Healthcare",
        "query": "India healthcare Ayushman Bharat hospitals",
        "hue": "#56c8d0",
    },
    "education": {
        "label": "Education",
        "query": "India education policy NEP schools universities",
        "hue": "#8fc7f0",
    },
    "women_safety": {
        "label": "Women Safety & Welfare",
        "query": "India women safety welfare scheme",
        "hue": "#b58ae8",
    },
    "governance": {
        "label": "Governance & Corruption",
        "query": "India governance corruption policy reform",
        "hue": "#e0768f",
    },
}


def topic_ids():
    return list(TOPICS.keys())


def topic_meta(topic_id: str):
    return TOPICS.get(topic_id)
