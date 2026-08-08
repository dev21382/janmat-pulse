from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_analyzer = SentimentIntensityAnalyzer()


def score_text(text: str) -> float:
    """Returns VADER compound sentiment score in [-1, 1]."""
    return _analyzer.polarity_scores(text)["compound"]
