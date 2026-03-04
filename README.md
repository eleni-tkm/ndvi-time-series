# NDVI Time Series Extraction & Phenology Smoothing

This project extracts **monthly NDVI time series** from Sentinel-2 imagery using openEO (Copernicus Data Space) and applies **Savitzky–Golay smoothing** for phenological analysis.

The workflow consists of:

- Part A – NDVI extraction using openEO (`download-ndvi-timeSeries.py`) 
- Part B – NDVI smoothing and visualization (`phenology_utils.py`)  

---

# Project Structure
```
├── data/
│ └── one-plot.geojson --> Area Of Interest
├── Outputs/
│ └── timeseries-mean-monthly-ndvi.csv
| └── timeseries-mean-monthly-ndvi_smoothed.csv --> has an extra column with the NDVI smoothed values
├── phenology_utils.py
├── main_script.py # or Jupyter Notebook
└── README.m
```


---

# Part A – NDVI Extraction with openEO

This script:

- Connects to the Copernicus Data Space Ecosystem
- Loads Sentinel-2 Level-2A imagery
- Applies cloud masking using Scene Classification Layer (SCL)
- Applies water masking using NDWI threshold
- Computes NDVI
- Aggregates monthly median values
- Computes spatial mean over the Area of Interest (AOI)
- Downloads the results as a CSV file

## Data Source

- Collection: `SENTINEL2_L2A`
- Bands used:
  - B04 – Red
  - B08 – Near Infrared (NIR)
  - B03 – Green
  - SCL – Scene Classification Layer

## NDVI Formula

NDVI = (NIR - RED) / (NIR + RED)

## Masking Strategy

- Cloud masking using SCL classes: 3, 6, 8, 9, 10
- Water masking using NDWI > 0.3

## Output

The workflow generates:
- `Outputs/timeseries-mean-monthly-ndvi.csv`


With structure:

| date | band_unnamed |
|------|-------------|
| YYYY-MM-DD | NDVI value |

---

# Part B – NDVI Smoothing & Visualization

File: `phenology_utils.py`

Main function:
`smooth_and_plot_ndvi(csv_path, window_length=7, polyorder=2)`

## What the Function Does
- Loads the NDVI CSV
- Sorts values by date
- Applies Savitzky–Golay smoothing
- Saves a new file with suffix `_smoothed.csv`
- Adds a new column `ndvi_smooth` in the new file
- `_smoothed.csv` strusture:

| date | band_unnamed | ndvi_smooth |
|------|-------------|--------|
| YYYY-MM-DD | NDVI value | NDVI smoothed value |

  
- Plots:
  - Original NDVI values
  - Smoothed NDVI curve
 
## Example Usage
```
from phenology_utils import smooth_and_plot_ndvi

csv_file = "Outputs/timeseries-mean-monthly-ndvi.csv"

df, smoothed = smooth_and_plot_ndvi(
    csv_file,
    window_length=7,
    polyorder=2
)
```
## Smoothing Parameters
### window_length
- Defines the number of consecutive observations used in each local fit 
- Must be odd
- Must be smaller than number of observations
**Effect of window_length:**
  - Small window (e.g., 5)
      - Less smoothing
      - Preserves short-term variability
      - More sensitive to noise
  - Large window (e.g., 9)
      - Stronger smoothing
      - Reduces noise
      - It flatten peaks and seasonal extremes


### polyorder
- Degree of the polynomial fitted within each moving window
**Effect of polyorder:**
  - Lower order (e.g., 2)
      - Produces smoother curves
      - Good for general seasonal trends
  - Higher order (e.g., 3 or 4)
      - Allows more curvature
      - May follow noise if too high

