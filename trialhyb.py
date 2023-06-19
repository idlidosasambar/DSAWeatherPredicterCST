import heapq
from datetime import datetime
import matplotlib.pyplot as plt
import requests
import json
import time


class Node:
    def __init__(self, timestamp, weather_data):
        self.timestamp = timestamp
        self.weather_data = weather_data
        self.left = BST()
        self.right = BST()


class BST:
    def __init__(self):
        self.root = None

    def insert(self, timestamp, weather_data):
        new_node = Node(timestamp, weather_data)
        if self.root is None:
            self.root = new_node
        else:
            current = self.root
            while True:
                if timestamp < current.timestamp:
                    if current.left.root is None:
                        current.left.root = new_node
                        break
                    else:
                        current = current.left.root
                else:
                    if current.right.root is None:
                        current.right.root = new_node
                        break
                    else:
                        current = current.right.root

    def search_range(self, start_timestamp, end_timestamp):
        results = []
        stack = []
        current = self.root
        while stack or current:
            while current:
                stack.append(current)
                current = current.left.root
            current = stack.pop()
            if start_timestamp <= current.timestamp <= end_timestamp:
                results.append((current.timestamp, current.weather_data))
            if current.timestamp > end_timestamp:
                break
            current = current.right.root
        return results


class RealtimeDataQueue:
    def __init__(self):
        self.queue = []
        self.timestamp_counter = 0

    def enqueue(self, weather_data):
        self.timestamp_counter += 1
        heapq.heappush(self.queue, (self.timestamp_counter, weather_data))

    def dequeue(self):
        if not self.is_empty():
            return heapq.heappop(self.queue)[1]

    def is_empty(self):
        return len(self.queue) == 0


class WeatherForecast:
    def __init__(self):
        self.locations = {}
        self.realtime_data_queue = RealtimeDataQueue()

    def add_location(self, location):
        self.locations[location] = BST()

    def store_historical_data(self, location, timestamp, weather_data):
        if location in self.locations:
            bst = self.locations[location]
            bst.insert(timestamp, weather_data)
        else:
            print("Location not found!")

    def fetch_realtime_weather(self, location, api_key):
        base_url = "http://api.weatherapi.com/v1/current.json"
        params = {
            "key": api_key,
            "q": location
        }
        response = requests.get(base_url, params=params)
        print("CHECKING RESPONSE")
        print(response.json())
        #print(response.status_code)
        if response.status_code == 200:
            return (response.json())
        else:
            return None

    def receive_realtime_data(self, location, api_key):
        weather_data = self.fetch_realtime_weather(location, api_key)
        if weather_data is not None:
            localtime_str = weather_data['location']['localtime']
            current_timestamp = int(datetime.strptime(localtime_str, '%Y-%m-%d %H:%M').timestamp())
            self.realtime_data_queue.enqueue((current_timestamp, weather_data))
            self.store_historical_data(location, current_timestamp, {"temp_c": weather_data['current']['temp_c']})
    
    def make_predictions(self, location, start_timestamp, end_timestamp):
        if location in self.locations:
            bst = self.locations[location] 
            historical_data = bst.search_range(start_timestamp, end_timestamp)
        
            realtime_data = []       
            while not self.realtime_data_queue.is_empty():
                data = self.realtime_data_queue.dequeue()  
                realtime_data.append(data[1])
            return historical_data, realtime_data   
        else:
            return [], []

    def average_temperature(self, location, start_timestamp, end_timestamp):
        if location in self.locations:
            temperature_sum = 0
            count = 0
            bst = self.locations[location]
            historical_data = bst.search_range(start_timestamp, end_timestamp)
            print("HISTORICAL DATA")
            print(historical_data)

            for data in historical_data:
                temperature = self.extract_temperature(data[1])
                if temperature is not None:
                    temperature_sum += temperature
                    count += 1
            if count > 0:
                return temperature_sum / count
            else:
                return None
        else:
            print("Location not found!")
            return None

    def extract_temperature(self, weather_data):
        if 'current' in weather_data:
            return weather_data['current']['temp_c']
        elif 'temp_c' in weather_data:
            return weather_data['temp_c']
        else:
            return None
    def plot_temperature(self, location, start_timestamp, end_timestamp):        
        historical_data, realtime_data = self.make_predictions(location, start_timestamp, end_timestamp) 
        historical_timestamps = [data[0] for data in historical_data]
        historical_temps = [self.extract_temperature(data[1]) for data in historical_data]
        all_realtime_timestamps = [data['location']['localtime'] for data in realtime_data]
        all_realtime_temps = [self.extract_temperature(data) for data in realtime_data]  

    # Convert string timestamps to UNIX timestamps
        all_realtime_timestamps_unix = []
        for ts in all_realtime_timestamps:
            dt = datetime.strptime(ts, "%Y-%m-%d %H:%M")
            unix_ts = int(dt.timestamp())
            all_realtime_timestamps_unix.append(unix_ts)

    # Filter data based on timestamp range
        historical_temps = [temp for ts, temp in zip(historical_timestamps, historical_temps) if start_timestamp <= ts <= end_timestamp]
        historical_timestamps = [ts for ts in historical_timestamps if start_timestamp <= ts <= end_timestamp] 

        realtime_temps = [temp for ts, temp in zip(all_realtime_timestamps_unix, all_realtime_temps) if start_timestamp <= ts <= end_timestamp] 
        print(realtime_temps)
        realtime_timestamps = [ts for ts in all_realtime_timestamps_unix if start_timestamp <= ts <= end_timestamp]
        print(realtime_timestamps)

    # Re-enqueue new realtime data after filtering
        for idx, ts in enumerate(all_realtime_timestamps_unix):
            if start_timestamp <= ts <= end_timestamp:
                self.realtime_data_queue.enqueue((ts, realtime_data[idx]))

        # print("REALTIME TEMPS")
        # print(realtime_temps)
        # print(realtime_timestamps)

        # print("Historical Temps")
        # print(historical_temps)
        # print(historical_timestamps)

        #modification for testing
        realtime_temps.append(17.4)
        realtime_temps.append(18.4)
        realtime_temps.append(19.8)
        realtime_temps.append(20.4)

        realtime_timestamps.append(1623902400)
        realtime_timestamps.append(1623988800)
        realtime_timestamps.append(1624075200)
        realtime_timestamps.append(1624161600)
        

        plt.plot(historical_timestamps, historical_temps, label="Historical Data")        
        plt.plot(realtime_timestamps, realtime_temps, label="API Data") 
        plt.xlabel("Timestamp")
        plt.ylabel("Temperature (°C)")
        plt.legend()
        plt.show()

# Example usage
weather_forecast = WeatherForecast()
weather_forecast.add_location("San Francisco")

# Add historical data
weather_forecast.store_historical_data("San Francisco", 1623902400, {"temp_c": 20.0})
weather_forecast.store_historical_data("San Francisco", 1623988800, {"temp_c": 21.1})
weather_forecast.store_historical_data("San Francisco", 1624075200, {"temp_c": 19.5})
weather_forecast.store_historical_data("San Francisco", 1624161600, {"temp_c": 22.0})
weather_forecast.store_historical_data("San Francisco", 1624248000, {"temp_c": 18.9})

# Add realtime data
api_key = "3bd4883bba2e4bb5b6183755231706"
for _ in range(2):
    weather_forecast.receive_realtime_data("San Francisco", api_key)
    time.sleep(5)  # Wait for 60 seconds between each API call to fetch more realtime data points

# Calculate average temperature
start_timestamp = 1623902400
end_timestamp = 1687166406
avg_temperature = weather_forecast.average_temperature("San Francisco", start_timestamp, end_timestamp)
print(f"Average Temperature between {start_timestamp} and {end_timestamp}: {avg_temperature:.2f}°C")

# Plot temperature data
weather_forecast.plot_temperature("San Francisco", start_timestamp, end_timestamp)

