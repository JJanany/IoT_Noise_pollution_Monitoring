# Import necessary libraries and constants

import asyncio
import websockets
import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt  # For data visualization
import sqlite3  # For data storage
import datetime  # For timestamp
import json  # For configuration settings
import os  # For file operations
import requests  # For making HTTP requests

# Load configuration settings from a JSON file (config.json)

def load_config():
    config = {}
    if os.path.exists("config.json"):
        with open("config.json", "r") as config_file:
            config = json.load(config_file)
    return config

# Save configuration settings to a JSON file (config.json)

def save_config(config):
    with open("config.json", "w") as config_file:
        json.dump(config, config_file)

# Initialize the configuration

config = load_config()
if not config:
    config = {
        "server_url": "wss://yourserver.com",  # WebSocket server URL
        "server_port": 8080,  # WebSocket port
        "monitor_segment_length": 10,  # Monitoring segment length in seconds
        "data_logging_enabled": True,
        "threshold_alerts_enabled": False,
        "threshold_value": 80,  # Adjust this value as needed
        "sound_classifier_enabled": False,
        "geolocation_enabled": False,
        "database_enabled": True,  # For storing data in a SQLite database
        "api_endpoint": "https://api.example.com/data",  # API endpoint for sending data
        "reporting_interval": 3600,  # Time interval for reporting data (in seconds)
    }
    save_config(config)

# Class for data analysis and visualization

class DataAnalyzer():
    def __init__(self):
        self.timestamps = []
        self.sound_levels = []

    def analyze_data(self, timestamp, sound_level):
        self.timestamps.append(timestamp)
        self.sound_levels.append(sound_level)
        
        # Perform data analysis here, e.g., calculate average noise level

    def plot_data(self):
        plt.figure(figsize=(10, 5))
        plt.plot(self.timestamps, self.sound_levels, label="Sound Level")
        plt.xlabel("Time")
        plt.ylabel("Sound Level")
        plt.legend()
        plt.title("Noise Pollution Monitoring")
        plt.grid(True)
        plt.show()

# Class for data logging

class DataLogger():
    def __init__(self):
        self.conn = sqlite3.connect("noise_data.db")
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS noise_data (timestamp TEXT, sound_level REAL)")

    def log_data(self, timestamp, sound_level):
        self.cursor.execute("INSERT INTO noise_data VALUES (?, ?)", (timestamp, sound_level))
        self.conn.commit()

# Class for sending threshold alerts

class ThresholdAlert():
    def __init__(self, threshold_value):
        self.threshold_value = threshold_value

    def check_threshold(self, sound_level):
        if sound_level > self.threshold_value:
            # Send an alert (e.g., email or push notification)
            pass

# Class for geolocation

class Geolocation():
    def __init__(self):
        self.location = (0.0, 0.0)  # Initialize with default location (latitude, longitude)

    def set_location(self, latitude, longitude):
        self.location = (latitude, longitude)

    def get_location(self):
        return self.location

# Class for sending data to an external API

class DataSender():
    def __init__(self, api_endpoint):
        self.api_endpoint = api_endpoint

    def send_data(self, data):
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(self.api_endpoint, json=data, headers=headers)
            if response.status_code == 200:
                print("Data sent to the API successfully")
            else:
                print("Failed to send data to the API")
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")

# Class for periodic reporting of data

class DataReporter():
    def __init__(self, api_endpoint, interval):
        self.api_endpoint = api_endpoint
        self.interval = interval

    async def report_data_periodically(self, data):
        while True:
            await asyncio.sleep(self.interval)
            self.send_data(data)

    def send_data(self, data):
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(self.api_endpoint, json=data, headers=headers)
            if response.status_code == 200:
                print("Data sent to the API successfully")
            else:
                print("Failed to send data to the API")
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")

# Main class for noise monitoring

class SoundListener():
    def __init__(self):
        self.soundState = []
        self.monitor_segment_length = config["monitor_segment_length"]

    def getSoundState(self, inData, outData, frames, time, status):
        volumeNorm = np.linalg.norm(inData) * 10

        print("*" * int(volumeNorm))  # debug output
        self.soundState.append(volumeNorm.round(4))

    async def websocketConnection(self):
        # get connection name, this can also be called the room
        print("Connection Name:")
        # we are converting input to string to reduce type errors
        self.connectionName = str(input())

        # send the state of the microphone through a websocket
        while (True):
            self.soundState = []

            # gets the microphone state for the next 10 seconds
            # the state is stored inside the soundState[] variable
            # get microphone state outside of websocket
            with sd.Stream(callback=self.getSoundState):
                sd.sleep(self.monitor_segment_length)

     async with websockets.connect(config["server_url"] + ":" + str(config["server_port"])) as self.websocket:
