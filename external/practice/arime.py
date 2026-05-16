import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA

data = pd.read_csv('sales.csv')

series = data['Sales']

plt.plot(series)
plt.title("Original Data")
plt.show()


model =  ARIMA(series,order = (1,1,1))

model_fit = model.fit()

forecast = model_fit.forecast(steps=5)

plt.plot(series, label='Original')

plt.plot(range(len(series), len(series) + 5), forecast, label='Forecast')
plt.legend()
plt.show()
