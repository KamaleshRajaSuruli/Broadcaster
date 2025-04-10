import sounddevice as sd

print("Available audio devices:\n")
for i, device in enumerate(sd.query_devices()):
    print(f"[{i}] {device['name']} - max input: {device['max_input_channels']}, max output: {device['max_output_channels']}")
