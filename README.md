# 📊 Commodity Price Explorer
### What Drives Gold & Oil? — Macro Factor Analysis Dashboard

**ACC102 Mini Assignment | Track 4 – Interactive Data Analysis Tool**  
**Dataset period:** January 2022 – April 2026 | **Data source:** Yahoo Finance (accessed April 2026)

---

## Overview

This is an interactive Streamlit dashboard that analyses the relationship between commodity prices (Gold and WTI Crude Oil) and key macroeconomic drivers (US Dollar Index and 10-Year Treasury Yield).

**Analytical question:** How do macroeconomic factors — particularly the US Dollar and interest rates — drive commodity price movements, and what can investors learn from these relationships over the 2022–2026 period?

**Target audience:** Individual investors and economics/finance students who want to explore commodity market dynamics without relying on expensive financial terminals.

---

## Features

| Tab | Description |
|-----|-------------|
| 📈 **Price Trends** | Normalised or raw price chart for all four assets. Click any data point to see a full snapshot of that day's values. Major macro events (e.g. Fed rate hikes, Russia-Ukraine war) are annotated directly on the chart. |
| 🔗 **Correlations** | Rolling Pearson correlation between any two selected assets, with an adjustable time window. Also includes a full correlation heatmap. |
| 📊 **Volatility** | Annualised rolling volatility for Gold and Oil, with a summary statistics table. |
| 🔍 **Scatter Analysis** | Scatter plot of any asset vs. any macro driver, colour-coded by year, with an OLS regression line and R²/p-value output. |
| 💰 **Return Calculator** | Enter a buy-in date, sell date, and investment amount to calculate total return, P&L, annualised return, and view the price chart for the holding period. Automatically highlights macro events that occurred during the holding window. Clicking a point on the Price Trends chart auto-fills the buy-in date here. |

**Sidebar controls** let you filter by date range, toggle individual assets and drivers, switch between normalised and raw prices, and adjust rolling window lengths.

---

## Data

| Asset | Ticker | Description |
|-------|--------|-------------|
| Gold | `GC=F` | Gold Futures (USD per troy ounce) |
| WTI Crude Oil | `CL=F` | WTI Crude Oil Futures (USD per barrel) |
| US Dollar Index | `DX-Y.NYB` | DXY — measures USD against a basket of currencies |
| 10Y Treasury Yield | `^TNX` | US 10-Year Government Bond Yield (%) |

Data was downloaded using `yfinance` and saved as `commodity_data.csv`. The CSV covers trading days from January 2022 to April 2026. Forward-fill (`ffill`) is applied to handle non-trading days.

---

## Installation & Setup

### Requirements

- Python 3.8 or above
- The following Python packages:

```
streamlit
pandas
numpy
plotly
scipy
yfinance
```

Install all dependencies with:

```bash
pip install streamlit pandas numpy plotly scipy yfinance
```

### File Structure

Make sure both files are in the **same folder**:

```
acc102quan/
├── app.py
└── commodity_data.csv
```

### Running the App

Open a terminal, navigate to the project folder, and run:

```bash
cd ~/Desktop/acc102quan
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

> **Note:** If the port is already in use, Streamlit will automatically select another port (e.g. 8502).

---

## How to Use

1. **Adjust the date range** in the sidebar to focus on a specific period (e.g. the 2022 rate-hike cycle).
2. **Toggle assets and drivers** on/off to simplify or expand the charts.
3. **Click any point** on the Price Trends chart to see all four asset values on that date. If the date is near a major macro event, an explanation will appear automatically.
4. **Switch to Return Calculator** — the clicked date is auto-filled as the buy-in date. Enter a sell date and investment amount to see your hypothetical P&L.
5. **Use the Scatter tab** to run OLS regression between any asset and macro driver, with statistical output (slope, R², p-value).

---

## Macro Events Annotated

The following events are marked on the Price Trends chart:

| Date | Event |
|------|-------|
| 2022-02-24 | 🔴 Russia invades Ukraine |
| 2022-03-16 | 📈 Fed first rate hike |
| 2022-06-15 | 📈 Fed +75bps hike |
| 2023-03-10 | 🏦 SVB bank collapse |
| 2023-07-26 | 📈 Fed final rate hike (5.5%) |
| 2024-09-18 | 📉 Fed first rate cut |
| 2025-01-20 | 🇺🇸 Trump inauguration |

---

## Academic Information

- **Module:** ACC102 — Introduction to Data Analytics
- **Track:** Track 4 — Interactive Data Analysis Tool
- **Institution:** Xi'an Jiaotong-Liverpool University (XJTLU)
- **Submission deadline:** 27 April 2026

---

## Limitations

- Data is sourced from Yahoo Finance via `yfinance`, which may have occasional gaps or inaccuracies for futures contracts.
- The OLS regression in the Scatter tab assumes a linear relationship and does not account for lagged effects or confounding variables.
- The Return Calculator assumes frictionless trading (no transaction costs, taxes, or slippage).
- Futures contract rollovers may introduce minor price discontinuities in the Gold and Oil series.
