# Set 6 — Sales Prediction Using ARIMA

## What ARIMA Is

**ARIMA(p, d, q)** — a classical model for forecasting time-series data (like daily/monthly sales).

| Letter | Meaning | Parameter | What it does |
|--------|---------|-----------|-------------|
| **AR** | AutoRegression | `p` | Uses the last `p` values to predict the next |
| **I**  | Integration    | `d` | Differences the series `d` times to remove trend |
| **MA** | Moving Average | `q` | Uses the last `q` forecast errors to correct predictions |

**Why these three?**
- Real sales data has **trends** (mean keeps rising/falling) → `d` removes the trend by differencing.
- Today's sales are influenced by recent past → `AR` captures that.
- Random shocks (sudden spike) linger → `MA` captures that.

A safe default for exam: **ARIMA(1, 1, 1)**

---

## Sales Prediction Program

### Input Data — `sales.csv`

```
Month,Sales
1,200
2,220
3,210
4,240
5,260
6,250
7,280
8,300
9,290
10,320
11,340
12,330
```

### Python Code

```python
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA

# Load the sales data
data = pd.read_csv("sales.csv")
series = data['Sales']

# Plot original data
plt.plot(series)
plt.title("Sales Data")
plt.xlabel("Month")
plt.ylabel("Sales")
plt.show()

# Fit ARIMA model
model = ARIMA(series, order=(1, 1, 1))
model_fit = model.fit()

# Forecast next 5 months
forecast = model_fit.forecast(steps=5)
print("Forecasted Sales for next 5 months:")
print(forecast)

# Plot original + forecast
plt.plot(series, label='Original')
plt.plot(range(len(series), len(series) + 5), forecast, label='Forecast', color='red')
plt.legend()
plt.title("Sales Prediction using ARIMA")
plt.show()
```

### Run It

```bash
python sales_arima.py
```

---

## How Each Step Works

**Load data** — `pd.read_csv` reads the CSV into a DataFrame. We extract the `Sales` column as a Series (values in time order).

**Plot original** — always visualize first to check for trend (if the line goes up/down, you need `d=1`).

**Fit model** — `ARIMA(series, order=(1,1,1))` builds the model. `.fit()` finds the best AR and MA coefficients using Maximum Likelihood Estimation.

**Forecast** — `model_fit.forecast(steps=5)` predicts the next 5 values. Internally: applies fitted AR/MA equations in the differenced space, then undoes the differencing to give predictions in original sales units.

**Plot forecast** — append the 5 forecasted points after the last observed index so you can visually see where history ends and prediction begins.

---

## Things to Remember

- ARIMA needs the data to be **stationary** (stable mean and variance). The `d` parameter achieves this by differencing: `y_t - y_{t-1}`.
- `order=(p, d, q)` — common exam default is `(1, 1, 1)`.
- ARIMA is **univariate** — it forecasts one column at a time.
- After fitting, check: residuals should look like **white noise** (random, no pattern). If they show a pattern, the model didn't capture everything.
- Choosing parameters: `d` → ADF test | `p` → PACF plot | `q` → ACF plot.
- For data with seasonal patterns (e.g. December always spikes), use **SARIMA** instead.
