class AudioStreamer:
    def __init__(self):
        self.connected_devices = []
        self.audio_data = None

    def connect_device(self, device):
        self.connected_devices.append(device)
        print(f"Connected to {device}")

    def disconnect_device(self, device):
        self.connected_devices.remove(device)
        print(f"Disconnected from {device}")

    def start_stream(self):
        if not self.connected_devices:
            print("No devices connected.")
            return
        print("Starting audio stream to devices:")
        for device in self.connected_devices:
            self.stream_to_device(device)

    def stream_to_device(self, device):
        print(f"Streaming audio to {device}")

    def stop_stream(self):
        print("Stopping audio stream.")
        self.connected_devices.clear()