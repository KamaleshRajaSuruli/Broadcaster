Step 1: Install VB-Audio Software

    Download and install VB-Audio Virtual Cable from the official website:
    https://vb-audio.com/Cable/
    After installation, follow these steps to configure the audio settings:
    Open Control Panel → Hardware and Sound → Sound
    In the Playback tab, right-click and ensure "Show Disabled Devices" and "Show Disconnected Devices" are enabled.
    Locate CABLE Input, right-click on it, and select "Set as Default Device".
    Switch to the Recording tab, and make sure CABLE Output is enabled and shows as Ready.

Step 2: Install Required Python Libraries

    Install all necessary libraries using the following command:
    pip install -r requirements.txt

Step 3: Run the Application

    Execute the Python script to start the audio broadcasting system:
    python audio_broadcaster.py

Optional: 

    If you want to check the available devices in your system, you can use the following command:
    python available_devices.py
    This will display the available input and output devices, allowing you to verify the configuration.

    If you wnat to check the exact devices like  "CABLE Output (VB-Audio Virtual Cable)", use the following command:
    python targeted_devices.py
    This will display the exact devices that are being used by


You're all set! Enjoy the multi-device audio broadcasting experience.