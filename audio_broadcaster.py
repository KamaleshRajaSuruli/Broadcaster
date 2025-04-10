import sounddevice as sd
import numpy as np
import tkinter as tk
import threading
import queue
import resampy

# Configuration
DEVICE_NAME = "CABLE Output (VB-Audio Virtual Cable)"
SAMPLE_RATE = 48000
CHANNELS = 2
BUFFER_SIZE = 1024
NORMALIZE = True
MAX_QUEUE_SIZE = 100

# Global state
playback_queues = {}
volume_controls = {}
volume_levels = {}
volume_scale_values = {}
device_names = {}
stop_threads = threading.Event()
active_threads = []

def get_wasapi_hostapi_index():
    for idx, api in enumerate(sd.query_hostapis()):
        if "WASAPI" in api['name']:
            return idx
    return None

def get_wasapi_output_devices():
    wasapi_index = get_wasapi_hostapi_index()
    return [(i, d['name']) for i, d in enumerate(sd.query_devices())
            if d['hostapi'] == wasapi_index and d['max_output_channels'] >= CHANNELS]

def find_input_devices_by_name(name):
    return [(i, d['name']) for i, d in enumerate(sd.query_devices())
            if name.lower() in d['name'].lower() and d['max_input_channels'] >= CHANNELS]

def validate_loopback_device(device_id):
    try:
        dev = sd.query_devices(device_id)
        return dev['max_input_channels'] >= CHANNELS
    except Exception:
        return False

def capture_audio(selected_input_id):
    try:
        with sd.InputStream(device=selected_input_id, channels=CHANNELS,
                            samplerate=SAMPLE_RATE, blocksize=BUFFER_SIZE,
                            dtype='float32', latency='low') as stream:
            while not stop_threads.is_set():
                data, _ = stream.read(BUFFER_SIZE)
                if NORMALIZE:
                    data = normalize_audio(data)
                for dev_id, q in playback_queues.items():
                    if not q.full():
                        q.put_nowait(data.copy())
    except Exception as e:
        print(f"[ERROR] Audio capture failed: {e}")

def normalize_audio(data):
    data -= np.mean(data)
    peak = np.max(np.abs(data))
    if peak > 0:
        data = np.clip((data / peak) * 0.9, -1.0, 1.0)
    return data

def play_audio(device_id):
    try:
        dev = sd.query_devices(device_id)
        target_samplerate = int(dev['default_samplerate'])

        with sd.OutputStream(device=device_id, channels=CHANNELS,
                             samplerate=target_samplerate, blocksize=BUFFER_SIZE,
                             dtype='float32', latency='low') as stream:
            while not stop_threads.is_set():
                try:
                    chunk = playback_queues[device_id].get(timeout=1)

                    if target_samplerate != SAMPLE_RATE:
                        chunk = resampy.resample(chunk.T, SAMPLE_RATE, target_samplerate).T

                    volume = volume_scale_values[device_id].get()
                    chunk *= volume

                    peak = np.max(np.abs(chunk))
                    bar = "█" * int(peak * 20)
                    volume_levels[device_id].set(f"🔊 [{bar:<20}] {int(volume * 100)}%")

                    if chunk.shape[0] < BUFFER_SIZE:
                        padding = np.zeros((BUFFER_SIZE - chunk.shape[0], CHANNELS), dtype=np.float32)
                        chunk = np.vstack((chunk, padding))
                    elif chunk.shape[0] > BUFFER_SIZE:
                        chunk = chunk[:BUFFER_SIZE]

                    stream.write(chunk.astype(np.float32))
                except queue.Empty:
                    stream.write(np.zeros((BUFFER_SIZE, CHANNELS), dtype=np.float32))
    except Exception as e:
        print(f"[ERROR] Playback failed on device {device_id}: {e}")

def make_scrollable_frame(parent):
    canvas = tk.Canvas(parent)
    scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas)

    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    return scroll_frame

def start_gui():
    root = tk.Tk()
    root.title("🎧 Audio Broadcaster")

    # Set dynamic window size
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    width = min(600, screen_width - 100)
    height = min(800, screen_height - 100)
    root.geometry(f"{width}x{height}")

    input_frame = tk.Frame(root)
    input_frame.pack(pady=10)

    output_container = tk.LabelFrame(root, text="🎧 Select Output Devices")
    output_container.pack(pady=10, fill="both", expand=True)
    output_frame = make_scrollable_frame(output_container)

    control_frame = tk.Frame(root)
    control_frame.pack(pady=20)

    volume_container = tk.LabelFrame(root, text="🔊 Volume Controls")
    volume_container.pack(pady=10, fill="both", expand=True)
    volume_frame = make_scrollable_frame(volume_container)

    selected_input_id = tk.IntVar()
    check_vars = []

    def stop_all_threads():
        stop_threads.set()
        for t in active_threads:
            t.join(timeout=1)
        playback_queues.clear()
        volume_levels.clear()
        volume_scale_values.clear()
        stop_threads.clear()
        for widget in volume_frame.winfo_children():
            widget.destroy()

    def refresh_devices():
        stop_all_threads()
        for widget in input_frame.winfo_children():
            widget.destroy()
        for widget in output_frame.winfo_children():
            widget.destroy()
        check_vars.clear()
        start_btn.config(state="normal", text="Start Broadcasting", bg="#b9fbc0", fg="black")

        tk.Label(input_frame, text="🎙 Select Input Device (System Audio):", font=("Arial", 12, "bold")).pack()
        input_devices = find_input_devices_by_name(DEVICE_NAME)
        selected_input_id.set(input_devices[0][0] if input_devices else -1)
        for dev_id, name in input_devices:
            state = 'normal' if validate_loopback_device(dev_id) else 'disabled'
            suffix = "" if state == "normal" else " [⚠️ Invalid]"
            tk.Radiobutton(input_frame, text=f"{name} (ID {dev_id}){suffix}",
                           variable=selected_input_id, value=dev_id, state=state).pack(anchor='w')

        for dev_id, name in get_wasapi_output_devices():
            var = tk.BooleanVar()
            tk.Checkbutton(output_frame, text=f"{name} (ID {dev_id})", variable=var).pack(anchor='w')
            check_vars.append((dev_id, var))
            device_names[dev_id] = name

    def start_or_stop():
        if start_btn['text'] == "Start Broadcasting":
            selected_input = selected_input_id.get()
            selected_outputs = [dev_id for dev_id, var in check_vars if var.get()]
            if selected_input < 0 or not validate_loopback_device(selected_input):
                print("[ERROR] Invalid input device selected.")
                return
            if not selected_outputs:
                print("[ERROR] No output devices selected.")
                return

            for dev_id in selected_outputs:
                playback_queues[dev_id] = queue.Queue(maxsize=MAX_QUEUE_SIZE)
                volume_scale_values[dev_id] = tk.DoubleVar(value=1.0)
                volume_levels[dev_id] = tk.StringVar(value="🔊 [                    ] 100%")

                frame = tk.Frame(volume_frame)
                frame.pack(anchor='w', pady=4)

                label_text = f"Volume ({device_names.get(dev_id, f'Device {dev_id}')})"
                tk.Label(frame, text=label_text, font=("Arial", 10, "bold")).pack(anchor='w')

                scale = tk.Scale(frame, variable=volume_scale_values[dev_id], from_=0.0, to=1.0,
                                 resolution=0.01, orient="horizontal", length=300)
                scale.pack(anchor='w')

                vol_label = tk.Label(frame, textvariable=volume_levels[dev_id], font=("Courier", 10))
                vol_label.pack(anchor='w')

                t = threading.Thread(target=play_audio, args=(dev_id,), daemon=True)
                t.start()
                active_threads.append(t)

            t = threading.Thread(target=capture_audio, args=(selected_input,), daemon=True)
            t.start()
            active_threads.append(t)

            start_btn.config(text="Stop Broadcasting", bg="#ffb3b3", fg="black")
        else:
            stop_all_threads()
            start_btn.config(text="Start Broadcasting", bg="#b9fbc0", fg="black")

    start_btn = tk.Button(control_frame, text="Start Broadcasting", command=start_or_stop, bg="#b9fbc0", fg="black", width=20, height=2)
    start_btn.grid(row=0, column=0, padx=10)

    refresh_btn = tk.Button(control_frame, text="🔄 Refresh Devices", command=refresh_devices, bg="#dddddd", width=20, height=2)
    refresh_btn.grid(row=0, column=1, padx=10)

    refresh_devices()
    root.mainloop()

if __name__ == "__main__":
    start_gui()



# import sounddevice as sd

# print("Available audio devices:\n")
# for i, device in enumerate(sd.query_devices()):
#     print(f"[{i}] {device['name']} - max input: {device['max_input_channels']}, max output: {device['max_output_channels']}")



# import sounddevice as sd

# target_name = "CABLE Output (VB-Audio Virtual Cable)"
# print("Available audio devices:\n")

# found = False
# for i, device in enumerate(sd.query_devices()):
#     print(f"[{i}] {device['name']} - max input: {device['max_input_channels']}, max output: {device['max_output_channels']}")
    
#     if target_name.lower() in device['name'].lower():
#         print(f"\n✅ Found target device: '{target_name}' at index [{i}]\n")
#         found = True

# if not found:
#     print(f"\n❌ Device '{target_name}' not found.")
