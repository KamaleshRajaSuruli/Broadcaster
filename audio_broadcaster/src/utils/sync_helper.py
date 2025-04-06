def calculate_delay(device_index, base_delay, offset):
    return base_delay + offset[device_index]

def manage_audio_buffer(audio_data, buffer_size):
    if len(audio_data) > buffer_size:
        return audio_data[-buffer_size:]
    return audio_data

def synchronize_playback(devices, base_delay, offsets):
    delays = [calculate_delay(i, base_delay, offsets) for i in range(len(devices))]
    return delays