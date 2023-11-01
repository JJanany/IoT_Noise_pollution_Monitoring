# Import necessary libraries and constants

import asyncio
import websockets
import sounddevice as sd
import numpy as np
import time  # Added for time-related features
import os  # Added for file operations
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
        # Get connection name, this can also be called the room
        print("Connection Name:")
        # We are converting input to string to reduce type errors
        self.connectionName = str(input())

        # Send the state of the microphone through a websocket
        while (True):
            self.soundState = []

            # Gets the microphone state for the next 10 seconds
            # The state is stored inside the soundState[] variable
            # Get microphone state outside of the websocket
            with sd.Stream(callback=self.getSoundState):
                sd.sleep(self.monitor_segment_length)

            async with websockets.connect(SERVER + ":" + str(PORT)) as self.websocket:
                # First header should always be the connection (machine) name
                # Second .send is sending the microphone state from the last 10 seconds
                await self.websocket.send(self.connectionName)
                await self.websocket.send(str(self.soundState))

    def __init__(self):
        asyncio.get_event_loop().run_until_complete(self.websocketConnection())

# Program entry point
# Convert MONITOR_SEGMENT_LENGTH variable to milliseconds
MONITOR_SEGMENT_LENGTH *= 1000

# Start the main program
SoundListenerOBJ = SoundListener()

# Additional features:
# 1. Logging the start time of the monitoring session
start_time = time.time()
print("Monitoring started at:", time.ctime(start_time))

# 2. Creating a directory for saving recorded audio
if not os.path.exists("recorded_audio"):
    os.makedirs("recorded_audio")

# 3. Recording audio to a file
recording_duration = 60  # Record audio for 60 seconds
audio_data = []

with sd.InputStream(callback=audio_data.append):
    print("Recording audio for {} seconds...".format(recording_duration))
    sd.sleep(int(recording_duration * 1000))

# 4. Saving recorded audio to a file
audio_filename = os.path.join("recorded_audio", "audio.wav")
sd.write(audio_filename, np.concatenate(audio_data), 44100)

# 5. Calculate the total recording time
end_time = time.time()
total_recording_time = end_time - start_time
print("Total recording time:", total_recording_time, "seconds")

# 6. Perform additional data processing or analysis

# In this example, we'll calculate the average sound level during the recording period
average_sound_level = np.mean(audio_data)
print("Average sound level during recording:", average_sound_level)

# 7. Implement an automatic stop condition based on specific criteria

# You can define a stop condition based on your requirements, such as sound level threshold
sound_level_threshold = 50  # Define your threshold here
if average_sound_level < sound_level_threshold:
    print("Sound level below threshold. Stopping the monitoring session.")
    exit()  # You can choose to stop the program here

# 8. Add a user interface for starting and stopping the monitoring session

# Here's a basic example of a simple user interface using command-line input
while True:
    user_input = input("Enter 'start' to begin monitoring or 'stop' to exit: ")
    
    if user_input.lower() == "start":
        SoundListenerOBJ = SoundListener()
        print("Monitoring started.")
    elif user_input.lower() == "stop":
        print("Monitoring stopped.")
        break
    else:
        print("Invalid input. Enter 'start' to begin or 'stop' to exit.")
