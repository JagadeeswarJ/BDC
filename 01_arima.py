import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA

# Step 1: Load dataset (make sure file is in same folder)
data = pd.read_csv("sales.csv")

# Step 2: Select column (change 'Sales' if your column name is different)
series = data['Sales']

# Step 3: Plot original data
plt.plot(series)
plt.title("Original Data")
plt.show()

# Step 4: Apply ARIMA model
model = ARIMA(series, order=(1, 1, 1))
model_fit = model.fit()

# Step 5: Forecast next 5 values
forecast = model_fit.forecast(steps=5)

print("Forecasted Values:")
print(forecast)

# Step 6: Plot forecast
plt.plot(series, label='Original')
plt.plot(range(len(series), len(series) + 5), forecast, label='Forecast')

plt.legend()
plt.show()