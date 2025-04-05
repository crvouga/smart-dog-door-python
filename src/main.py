from src.client_console.client_console import ConsoleClient
from src.client_desktop.client_desktop import DesktopClient
import logging


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()
    desktop_client = DesktopClient(logger=logger)
    desktop_client.start()


if __name__ == "__main__":
    main()
