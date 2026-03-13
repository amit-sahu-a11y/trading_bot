import logging
import os


def setup_logging(log_file: str = "trading_bot.log") -> logging.Logger:
    """
    Set up logging so messages go to both a log file and the terminal.
    Log files are stored in the 'logs/' folder.
    """
    os.makedirs("logs", exist_ok=True)
    log_path = os.path.join("logs", log_file)

    log_format = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=[
            # Write logs to a file
            logging.FileHandler(log_path),
            # Also print logs to the terminal
            logging.StreamHandler(),
        ],
    )

    logger = logging.getLogger("trading_bot")
    logger.info(f"Logging started. Log file: {log_path}")
    return logger
