# Set 6 — Exploring the ARIMA Model

## What ARIMA Is

**ARIMA** = **AutoRegressive Integrated Moving Average**. It's a classical statistical technique for analyzing and **forecasting time-series data** — i.e. one numerical value evolving over time (daily sales, monthly rainfall, stock close).

It is especially useful when the data shows **trends** or **seasonality** over time.

It combines three components, denoted **ARIMA(p, d, q)**:

| Letter | Stands for | Parameter | Intuition |
|--------|------------|-----------|-----------|
| **AR** | AutoRegression       | `p` | Today's value depends on the previous `p` values |
| **I**  | Integration          | `d` | Difference the series `d` times to make it stationary |
| **MA** | Moving Average       | `q` | Today's value depends on the previous `q` forecast errors |

### Why each piece?

- **AR (p)** — captures momentum / inertia. If yesterday and the day before were both high, today is likely high too.
- **I (d)** — most real series **trend** (mean keeps drifting). You can't fit constant-parameter models to trending data. Solution: take differences (`y_t − y_{t-1}`) until the trend goes away — that's what `d` controls.
- **MA (q)** — captures the lingering effect of past shocks/errors. A sudden spike yesterday may partially still affect today.

After fitting in the differenced space, the model undoes the differencing to give forecasts in original units.

---

## Choosing `(p, d, q)`

1. **`d`** — Apply the **ADF test** (Augmented Dickey-Fuller). p < 0.05 ⇒ series is stationary, stop. Otherwise increment `d` and difference again.
2. **`p`** — Examine the **PACF** (Partial AutoCorrelation Function) plot. The lag at which it "cuts off" suggests `p`.
3. **`q`** — Examine the **ACF** (AutoCorrelation Function) plot. The lag at which it "cuts off" suggests `q`.

A common safe starting point for textbook problems is **ARIMA(1, 1, 1)**.

---

## Minimal Python Program (Exam-Ready)

```python
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA

# Step 1: Load dataset (sales.csv in the same folder)
data = pd.read_csv("sales.csv")

# Step 2: Select the column to forecast
series = data['Sales']

# Step 3: Plot the original data
plt.plot(series)
plt.title("Original Data")
plt.show()

# Step 4: Fit the ARIMA model
model = ARIMA(series, order=(1, 1, 1))
model_fit = model.fit()

# Step 5: Forecast the next 5 values
forecast = model_fit.forecast(steps=5)
print("Forecasted Values:")
print(forecast)

# Step 6: Plot forecast alongside the history
plt.plot(series, label='Original')
plt.plot(range(len(series), len(series) + 5), forecast, label='Forecast')
plt.legend()
plt.show()
```

---

## How Each Step Works

### Step 1 — Load the data
`pd.read_csv` reads the file into a `DataFrame`. The CSV is assumed to have at least one numerical column (here `Sales`) — possibly also a date column, but ARIMA itself just needs the values in chronological order.

### Step 2 — Select the series
ARIMA is **univariate** — it forecasts one column. We pull out `data['Sales']` as a pandas `Series` indexed by row order.

### Step 3 — Visualize
Always plot first. Eyeballing tells you:
- Is there a trend? (suggests `d ≥ 1`)
- Is there seasonality? (would need **SARIMA** instead)
- Any obvious outliers?

### Step 4 — Fit the model
`ARIMA(series, order=(1,1,1))` constructs the model with `p=1, d=1, q=1`. Calling `.fit()` runs **Maximum Likelihood Estimation** to find the AR coefficients φ, MA coefficients θ, and the noise variance that best match the data.

### Step 5 — Forecast
`model_fit.forecast(steps=5)` projects 5 time steps beyond the last observation. Internally:
- It applies the fitted AR/MA equations in the differenced space.
- Then **undoes the differencing** (the "I" part) to give predictions in the original scale.

### Step 6 — Plot
We append the forecast onto the original timeline at indices `[len(series), len(series)+5)`. This makes the join between history and forecast visible.

---

## Quick Comparison

| Model | When to use |
|-------|-------------|
| **AR(p)**     | Series strongly depends on its own recent past |
| **MA(q)**     | Series shocked by random noise |
| **ARMA(p,q)** | Already stationary, mix of the two |
| **ARIMA(p,d,q)** | Trending (non-stationary) series |
| **SARIMA**    | + seasonal pattern (weekly, yearly, etc.) |

---

## Things to Remember

- ARIMA's three letters: **AR(p)** for the past values, **I(d)** for differencing, **MA(q)** for past errors.
- **Stationarity is the precondition.** Mean and variance must not drift over time. That's why `d` exists.
- Diagnose with: **ADF test → d**, **PACF → p**, **ACF → q**.
- After fitting, the **residuals should look like white noise** (no pattern, mean ≈ 0). That's how you confirm the model captured the signal.
- ARIMA needs an **evenly-spaced univariate** series. No missing time stamps; one value per period.
- For seasonality, jump to **SARIMA(p,d,q)(P,D,Q,s)** where `s` is the season length (e.g. 12 for monthly data with yearly cycle).
