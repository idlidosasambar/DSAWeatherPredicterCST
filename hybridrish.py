import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt

# Generate sample data (replace this with real historical data)
np.random.seed(42)
timestamps = np.arange(1, 101)
temperatures = 20 + 0.1 * timestamps + 2 * np.random.randn(len(timestamps))

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(timestamps.reshape(-1, 1), temperatures, test_size=0.2, random_state=42)

# Create a simple linear regression model and fit it to the training data
model = LinearRegression()
model.fit(X_train, y_train)

# Predict temperatures for the test data
y_pred = model.predict(X_test)

# Calculate the mean squared error
mse = mean_squared_error(y_test, y_pred)
print(f"Mean squared error: {mse:.2f}")

# Visualize the original data, the model's predictions, and the test data
plt.scatter(timestamps, temperatures, label="Original data")
plt.scatter(X_test, y_pred, color="red", label="Predicted temperatures")
plt.xlabel("Timestamp")
plt.ylabel("Temperature")
plt.legend()
plt.show()