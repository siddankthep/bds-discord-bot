import logging
import logging.handlers

logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)
logging.getLogger("discord.http").setLevel(logging.INFO)

# File handler for logging to discord.log
file_handler = logging.handlers.RotatingFileHandler(
    filename="discord.log",
    encoding="utf-8",
    maxBytes=32 * 1024 * 1024,  # 32 MiB
    backupCount=5,  # Rotate through 5 files
)

# Console handler for logging to terminal
console_handler = logging.StreamHandler()

# Formatter for both handlers
dt_fmt = "%Y-%m-%d %H:%M:%S"
formatter = logging.Formatter("[{asctime}] {levelname:<8} {name}: {message}", dt_fmt, style="{")

# Apply formatter to both handlers
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add both handlers to logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Export the file handler for Discord.py to use
handler = file_handler
