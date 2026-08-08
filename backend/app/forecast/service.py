"""Trains a tiny per-topic LSTM on the real accumulated daily sentiment series
and forecasts the next few days. Retrained from scratch on every call, which
is cheap (a few hundred steps over at most a few dozen points on CPU takes a
fraction of a second) rather than persisted as a checkpoint.

With too little history for a sequence model to mean anything (fewer than
MIN_LSTM_POINTS days), falls back to a simple linear-trend extrapolation and
labels the result "naive" rather than pretending an LSTM was involved. This
is an honest reflection of a cold-started system: forecast quality genuinely
improves the longer the deployed instance runs and accrues real days of data.
"""
import datetime as dt
import logging

import numpy as np
import torch
import torch.nn as nn

from app.db.database import cursor
from app.forecast.lstm_model import SentimentLSTM
from app.sentiment.aggregate import get_daily_series

log = logging.getLogger("forecast.service")

MIN_LSTM_POINTS = 8
WINDOW = 5
HORIZON_DAYS = 3
EPOCHS = 200


def _naive_forecast(values: list[float], horizon: int) -> list[float]:
    if len(values) == 1:
        return [values[0]] * horizon
    x = np.arange(len(values))
    slope, intercept = np.polyfit(x, values, 1)
    preds = []
    for h in range(1, horizon + 1):
        pred = slope * (len(values) - 1 + h) + intercept
        preds.append(float(np.clip(pred, -1.0, 1.0)))
    return preds


def _build_windows(series: np.ndarray, window: int):
    xs, ys = [], []
    for i in range(len(series) - window):
        xs.append(series[i : i + window])
        ys.append(series[i + window])
    return np.array(xs), np.array(ys)


def _lstm_forecast(values: list[float], horizon: int) -> list[float]:
    arr = np.array(values, dtype=np.float32)
    mean, std = arr.mean(), arr.std() if arr.std() > 1e-6 else 1.0
    norm = (arr - mean) / std

    window = min(WINDOW, len(norm) - 2)
    xs, ys = _build_windows(norm, window)
    x_t = torch.tensor(xs, dtype=torch.float32).unsqueeze(-1)  # (n, window, 1)
    y_t = torch.tensor(ys, dtype=torch.float32).unsqueeze(-1)  # (n, 1)

    model = SentimentLSTM()
    opt = torch.optim.Adam(model.parameters(), lr=0.01)
    loss_fn = nn.MSELoss()

    model.train()
    for _ in range(EPOCHS):
        opt.zero_grad()
        pred = model(x_t)
        loss = loss_fn(pred, y_t)
        loss.backward()
        opt.step()

    model.eval()
    window_vals = list(norm[-window:])
    preds_norm = []
    with torch.no_grad():
        for _ in range(horizon):
            inp = torch.tensor(window_vals[-window:], dtype=torch.float32).view(1, window, 1)
            next_val = model(inp).item()
            preds_norm.append(next_val)
            window_vals.append(next_val)

    return [float(np.clip(p * std + mean, -1.0, 1.0)) for p in preds_norm]


def forecast_topic(topic_id: str, horizon: int = HORIZON_DAYS) -> dict:
    series = get_daily_series(topic_id)
    values = [row["mean_sentiment"] for row in series]

    if len(values) < 2:
        return {"topic_id": topic_id, "method": "insufficient_data", "history": series, "forecast": []}

    method = "lstm" if len(values) >= MIN_LSTM_POINTS else "naive_trend"
    try:
        preds = _lstm_forecast(values, horizon) if method == "lstm" else _naive_forecast(values, horizon)
    except Exception as exc:
        log.warning("lstm forecast failed topic=%s err=%s, falling back to naive", topic_id, exc)
        method = "naive_trend"
        preds = _naive_forecast(values, horizon)

    last_day = dt.date.fromisoformat(series[-1]["day"])
    forecast_days = [(last_day + dt.timedelta(days=i + 1)).isoformat() for i in range(horizon)]

    now = int(dt.datetime.now(dt.timezone.utc).timestamp())
    with cursor() as cur:
        for day, val in zip(forecast_days, preds):
            cur.execute(
                """INSERT INTO forecasts (topic_id, generated_utc, horizon_day, predicted_sentiment)
                   VALUES (?, ?, ?, ?)""",
                (topic_id, now, day, val),
            )

    return {
        "topic_id": topic_id,
        "method": method,
        "points_used": len(values),
        "history": series,
        "forecast": [{"day": d, "predicted_sentiment": v} for d, v in zip(forecast_days, preds)],
    }
