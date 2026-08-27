# Kick Live Status for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/default)

A Home Assistant custom integration to monitor the live status, stream titles, categories, and viewer counts of Kick.com streamers.

---

## Features

- **Live Status Sensors:** Creates a sensor for each tracked streamer (`live` or `offline`).
- **Rich Attributes:** Exposes stream title, category/game, current viewer count, and stream start time.
- **Config Flow Setup:** Easy UI configuration directly in Home Assistant—no YAML required.
- **Options Flow:** Easily add or remove tracked streamers anytime via the integration settings.

---

## Requirements

To use this integration, you need a **Client ID** and **Client Secret** from Kick.

1. Log in to kick [Go to Settings>Developer](https://kick.com/settings/developer)
2. Click **Create** to create a new application and retrieve your credentials(Client ID and Client Secret).

---

## Installation

### Method 1: HACS (Recommended)

1. Open **HACS** in your Home Assistant instance.
2. Click the three dots in the top right corner and select **Custom repositories**.
3. Add the repository URL: `https://github.com/3lb0z0/kick_live_status`
4. Select **Integration** as the category and click **Add**.
5. Search for **Kick Live Status** in HACS, click **Download**, and restart Home Assistant.

### Method 2: Manual Installation

1. Download the latest release source code.
2. Copy the `custom_components/kick_live_status` directory into your Home Assistant `/config/custom_components/` directory.
3. Restart Home Assistant.

---

## Configuration

1. In Home Assistant, go to **Settings > Devices & Services**.
2. Click **Add Integration** and search for **Kick Live Status**.
3. Enter your **Client ID**, **Client Secret**, and a comma-separated list of streamer handles (e.g., `iceposeidon, xqc, asmongold, adinross`).
4. Click **Submit**.

---

## Available Attributes

Each streamer entity (`sensor.kick_live_status_<streamer_name>`) provides the following state attributes when live:

| Attribute | Description |
| :--- | :--- |
| `streamer` | Streamer's handle |
| `stream_title` | Title of the current stream |
| `category` | Game or category name |
| `viewer_count` | Current number of concurrent viewers |
| `start_time` | Timestamp when the stream started |

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.