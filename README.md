# Microphone status to Home Assistant synchronizer

This is a simple Python script that synchronizes the status of a microphone inside Linux OS
with Home Assistant.
It checks microphone status inside: /proc/asound/card0/pcm0p/sub0/status file and then sends it to Home Assistant
using a REST API call.

# Configuration

## Home Assistant configuration

1. Create long-lived access token for your
   account: https://developers.home-assistant.io/docs/auth_api/#making-authenticated-requests
2. Create helper boolean input that will represent microphone status: https://www.home-assistant.io/integrations/input_boolean/

## Getting microphone device name

1. Install `pactl` tool by running:
   ```bash
   sudo apt update
   sudo apt install pulseaudio-utils
   ```
   
2. Find your monitored microphone device name by using `pactl list sources` command. 
   Example device name: `alsa_input.usb-046d_Brio_500_2238LZ515048-02.iec958-stereo`

## Systemd Service Configuration

To start the script on system startup, follow these steps:

1. Copy example file by removing `.example` from its name:
   ```bash
   cp mic-status-to-ha.service.example mic-status-to-ha.service
   ```

2. Edit the `mic-status-to-ha.service` file and replace the following:

   * Change script path in `ExecStart` directive
   * Change `HA_URL` to your ha instance url
   * Change `HA_BEARER_TOKEN` to your ha long-lived access token
   * Change `HA_ENTITY_ID` to your ha entity id
   * Change `MONITORED_DEVICE` to your monitored device name

3. Move the renamed file to the Systemd user directory as root:
   ```bash
   sudo mv mic-status-to-ha.service /etc/systemd/user/
   ```
   
4. Reload systemd user service:
   ```bash
   systemctl --user daemon-reload
   ```

5. Enable the service to start on boot:
   ```bash
   systemctl --user enable mic-status-to-ha.service
   ```

6. Start the service:
   ```bash
   systemctl start mic-status-to-ha.service
   ```

7. Verify the status of the service using:
   ```bash
   systemctl --user status mic-status-to-ha.service
   ```

# Running the script manually

Export all required variables to environment and run the script:
```bash
export HA_URL=
export HA_BEARER_TOKEN=
export HA_ENTITY_ID=
export MONITORED_DEVICE=
python3 mic_status_to_ha.py
```
