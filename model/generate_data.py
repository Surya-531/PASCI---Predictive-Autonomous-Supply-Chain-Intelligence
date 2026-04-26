"""
PASCI – Data Generation Module
Generates a synthetic logistics dataset for training the delay prediction model.
"""

import pandas as pd
import numpy as np
import os

def generate_dataset(n_samples: int = 1000, save_path: str = "data/data.csv") -> pd.DataFrame:
    """
    Generate synthetic shipment data with delay labels.

    Features:
        distance    : int   – km between source and destination (50–500)
        traffic     : int   – 0=low, 1=medium, 2=high
        weather     : int   – 0=clear, 1=rain, 2=storm
    Label:
        delay       : int   – 0=on-time, 1=delayed
    """
    np.random.seed(42)

    distance = np.random.randint(50, 501, size=n_samples)
    traffic  = np.random.choice([0, 1, 2], size=n_samples)
    weather  = np.random.choice([0, 1, 2], size=n_samples)

    # Delay logic:
    #   – Always delayed if storm (weather=2)
    #   – Always delayed if high traffic (traffic=2)
    #   – 40 % chance if medium traffic + rain
    #   – Otherwise on-time
    delay = np.zeros(n_samples, dtype=int)
    for i in range(n_samples):
        if weather[i] == 2 or traffic[i] == 2:
            delay[i] = 1
        elif traffic[i] == 1 and weather[i] == 1:
            delay[i] = int(np.random.rand() < 0.4)
        else:
            delay[i] = 0

    df = pd.DataFrame({
        "distance": distance,
        "traffic":  traffic,
        "weather":  weather,
        "delay":    delay,
    })

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    df.to_csv(save_path, index=False)
    print(f"[generate_data] Dataset saved → {save_path}  ({n_samples} rows)")
    return df


if __name__ == "__main__":
    df = generate_dataset()
    print(df["delay"].value_counts())
