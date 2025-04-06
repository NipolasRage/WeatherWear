# WeatherWear Flask Server

**WeatherWear** is a Flask-based server that provides weather-based clothing recommendations. This project runs on a Raspberry Pi using `systemd` for process management.

## Table of Contents

1. [Setup](#setup)
2. [Run the Server](#run-the-server)
3. [Restart the Server with Code Changes](#restart-the-server-with-code-changes)
4. [Logs](#logs)
5. [Troubleshooting](#troubleshooting)

---

## Setup

### Prerequisites

- Raspberry Pi or Linux-based system
- Python 3 and `pip` installed
- Virtual environment (`venv`) set up for the project

### Install Dependencies

1. Clone the repository to your local machine:

   ```bash
   git clone https://github.com/yourusername/WeatherWear.git
   cd WeatherWear
   ```

2. Set up a virtual environment and activate it:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

4. Ensure the `.env` file with the necessary environment variables (e.g., `API_KEY`) is set up in the project directory.

## Run the server

The Flask server is managed by `systemd` to ensure that it runs automatically when the Raspberry Pi boots up.

### Start the Flask server

1. Start the Flask server using `systemd`:

   ```bash
   sudo systemctl start weatherwear.service
   ```

2. Enable the server to start on boot:

   ```bash
   sudo systemctl enable weatherwear.service
   ```

The server will be running and accessible on port `5000`. The endpoint `http://<raspberry-pi-ip>:5000/what_to_wear` will return a weather-based clothing recommendation.
NOTE: I'm using tailscale to access the server from outside of my home network. My Mac, iPhone, and Raspberry Pi are setup to communicate with each other.

## Restart the Server with Code Changes

If you've made changes to the code (e.g., `server.py`), you’ll need to restart the server to apply those updates.

### Steps to Restart the Server:

1. Stop the running service:

   ```bash
   sudo systemctl stop weatherwear.service
   ```

2. Reload the systemd service to ensure it reads any changes made:

   ```bash
   sudo systemctl daemon-reload
   ```

3. Start the service again:

   ```bash
   sudo systemctl start weatherwear.service
   ```

4. Verify that the service is running:

   ```bash
   sudo systemctl status weatherwear.service
   ```

5. If you want to view logs for debugging:

   ```bash
   journalctl -u weatherwear.service -f
   ```

## Logs

You can check the status and logs for the server using `journalctl`.

To view logs in real-time:
`bash
    journalctl -u weatherwear.service -f
    `

For full logs:
`bash
    journalctl -u weatherwear.service
    `

## Troubleshooting

- **Service not starting:** If you see errors in the logs, verify that your virtual environment is correctly set up and that your environment variables (e.g., `API_KEY`) are configured properly.
- **Changes not reflected:** Ensure you've stopped the service before reloading and restarting it.
- **Flask is not running:** Check that Flask is binding to the correct IP and port (use `0.0.0.0` for all interfaces and `port=5000`).
