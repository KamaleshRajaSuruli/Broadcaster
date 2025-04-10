import sounddevice as sd

target_name = "CABLE Output (VB-Audio Virtual Cable)"
print("Available audio devices:\n")

found = False
for i, device in enumerate(sd.query_devices()):
    print(f"[{i}] {device['name']} - max input: {device['max_input_channels']}, max output: {device['max_output_channels']}")
    
    if target_name.lower() in device['name'].lower():
        print(f"\n✅ Found target device: '{target_name}' at index [{i}]\n")
        found = True

if not found:
    print(f"\n❌ Device '{target_name}' not found.")