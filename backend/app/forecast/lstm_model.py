import torch
import torch.nn as nn


class SentimentLSTM(nn.Module):
    """Tiny univariate LSTM forecaster: window of past daily sentiment -> next day."""

    def __init__(self, hidden_size: int = 16, num_layers: int = 1):
        super().__init__()
        self.lstm = nn.LSTM(input_size=1, hidden_size=hidden_size, num_layers=num_layers, batch_first=True)
        self.head = nn.Linear(hidden_size, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (batch, seq_len, 1)
        out, _ = self.lstm(x)
        last = out[:, -1, :]
        return self.head(last)
