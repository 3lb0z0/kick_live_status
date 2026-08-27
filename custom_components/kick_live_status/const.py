"""Constants for the Kick Live Status integration."""

DOMAIN = "kick_live_status"

# Kick API Endpoints
OAUTH_AUTHORIZE_URL = "https://id.kick.com/oauth/authorize"
OAUTH_TOKEN_URL = "https://id.kick.com/oauth/token"
KICK_API_BASE_URL = "https://api.kick.com/public/v1"

# Defaults
DEFAULT_SCAN_INTERVAL = 60  # seconds
CONF_STREAMERS = "streamers"
DEFAULT_STREAMERS = ["iceposeidon", "xqc", "asmongold", "adinross"]