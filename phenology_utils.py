# phenology_utils.py

import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter


def smooth_and_plot_ndvi(
    csv_path,
    window_length=7,
    polyorder=2,
    figsize=(10, 4)
):
    """
    Load NDVI CSV, apply Savitzky–Golay smoothing and plot.

    Parameters
    ----------
    csv_path : str
        Path to NDVI CSV file.
    window_length : int
        Must be odd. Controls smoothing strength.
    polyorder : int
        Polynomial degree for smoothing.
    figsize : tuple
        Figure size for plot.
    """

    # Load data
    df = pd.read_csv(csv_path)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")

    ndvi = df["band_unnamed"].values

    # Safety check
    if window_length % 2 == 0:
        raise ValueError("window_length must be odd.")

    if window_length >= len(ndvi):
        raise ValueError("window_length must be smaller than number of data points.")

    # Apply smoothing
    ndvi_smooth = savgol_filter(ndvi, window_length, polyorder)

    #write values in the df
    df["ndvi_smooth"] = ndvi_smooth
    
    df.to_csv(csv_path.replace(".csv", "_smoothed.csv"), index=False)
    # Plot
    plt.figure(figsize=figsize)

    plt.plot(df["date"], ndvi, "o-", alpha=0.4, label="Original NDVI")
    plt.plot(df["date"], ndvi_smooth, "-", linewidth=2, label="Smoothed NDVI")

    plt.ylabel("NDVI")
    plt.ylim(-1, 1)
    plt.title("NDVI Time Series (Savitzky–Golay Smoothed)")
    plt.legend()

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    return df, ndvi_smooth
