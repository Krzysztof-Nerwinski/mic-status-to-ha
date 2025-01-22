# Microphone status to Home Assistant synchronizer

This is a simple Python script that synchronizes the status of a microphone inside Linux OS 
with Home Assistant. 
It checks microphone status inside: /proc/asound/card0/pcm0p/sub0/status file and then sends it to Home Assistant
using a REST API call.

# Configuration

## Home Assistant configuration

1. Create long-lived access token for your account: https://developers.home-assistant.io/docs/auth_api/#making-authenticated-requests
2. Create helper boolean input that will represent mic status: https://www.home-assistant.io/integrations/input_boolean/

## Systemd Service Configuration

To use the provided `mic-status-to-ha.service.example` file, follow these steps:

1. Copy example file by removing `.example` from its name:
   ```bash
   cp mic-status-to-ha.service.example mic-status-to-ha.service
   ```

2. Edit the `mic-status-to-ha.service` file and replace the following:

   * Change username in `User` directive
   * Change script path in `ExecStart` directive
   * Change `HA_URL` to your ha instance url
   * Change `HA_BEARER_TOKEN` to your ha long-lived access token
   * Change `HA_ENTITY_ID` to your ha entity id

3. Move the renamed file to the Systemd directory as root:
   ```bash
   sudo mv mic-status-to-ha.service /etc/systemd/system/
   ```

4. Enable the service to start on boot:
   ```bash
   sudo systemctl enable mic-status-to-ha.service
   ```

5. Start the service:
   ```bash
   sudo systemctl start mic-status-to-ha.service
   ```

You can verify the status of the service using:

```bash
sudo systemctl status mic-status-to-ha.service
```


