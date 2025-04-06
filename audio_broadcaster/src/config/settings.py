# Configuration settings for the audio broadcaster application

# Bluetooth device parameters
BLUETOOTH_DEVICE_NAME = "AudioBroadcaster"
BLUETOOTH_DEVICE_ADDRESS = "00:00:00:00:00:00"  # Replace with actual device address

# Audio format settings
AUDIO_FORMAT = "PCM"  # Options: PCM, AAC, MP3
SAMPLE_RATE = 44100  # Sample rate in Hz
CHANNELS = 2  # Number of audio channels (1 for mono, 2 for stereo)

# Default delay settings (in milliseconds)
DEFAULT_DELAY = 100  # Default delay for audio playback
DEVICE_DELAY_SETTINGS = {
    "Device1": 100,
    "Device2": 200,
    "Device3": 300,
}  # Custom delays for specific devices