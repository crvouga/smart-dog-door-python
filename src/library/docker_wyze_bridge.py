# https://github.com/mrlt8/docker-wyze-bridge
import requests
import logging
from dataclasses import dataclass
from urllib.parse import quote
from .host_ip import get_host_ip
from typing import Optional

# Web UI: http://localhost:5000/


@dataclass
class WyzeBridgeUrls:
    rtsp: str
    hls: str
    rtmp: str
    stream_list: str


class DockerWyzeBridge:
    def __init__(
        self,
        camera_name: str,
        host_ip: str,
        api_key: str,
        logger: logging.Logger,
    ):
        self.host_ip = host_ip
        self.camera_name = camera_name
        self.api_key = api_key
        self._logger = logger or logging.getLogger(__name__)

    @property
    def rtsp_url(self) -> str:
        # Format: rtsp://username:password@host:port/path
        return f"rtsp://wb:{self.api_key}@{self.host_ip}:8554/{self.camera_name}"

    @property
    def hls_url(self) -> str:
        return f"http://{self.host_ip}:8888/{self.camera_name}/index.m3u8"

    @property
    def rtmp_url(self) -> str:
        return f"rtmp://{self.host_ip}:1935/live/{self.camera_name}"

    @property
    def stream_list_url(self) -> str:
        return f"http://{self.host_ip}:8888/"

    @property
    def urls(self) -> WyzeBridgeUrls:
        return WyzeBridgeUrls(
            rtsp=self.rtsp_url,
            hls=self.hls_url,
            rtmp=self.rtmp_url,
            stream_list=self.stream_list_url,
        )

    @property
    def power_off_url(self) -> str:
        """
        Returns the URL to power off a Wyze camera.

        This endpoint is used to turn off the camera via the Docker Wyze Bridge API.
        """
        return f"http://{self.host_ip}:5001/api/{self.camera_name}/power/off"

    @property
    def power_on_url(self) -> str:
        """
        Returns the URL to power on a Wyze camera.

        This endpoint is used to turn on the camera via the Docker Wyze Bridge API.
        """
        return f"http://{self.host_ip}:5001/api/{self.camera_name}/power/on"

    def power_off(self) -> bool:
        """
        Sends a request to power off the Wyze camera.

        Returns:
            bool: True if the request was successful, False otherwise.
        """

        try:
            url = f"{self.power_off_url}?api={self.api_key}"
            self._logger.info(f"Sending power off request to {url}")
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                self._logger.info(f"Successfully powered off camera {self.camera_name}")
                return True
            else:
                self._logger.warning(
                    f"Failed to power off camera {self.camera_name}: HTTP {response.status_code}"
                )
                return False
        except Exception as e:
            self._logger.error(
                f"Error powering off camera {self.camera_name}: {str(e)}"
            )
            return False

    def power_on(self) -> bool:
        """
        Sends a request to power on the Wyze camera.

        Returns:
            bool: True if the request was successful, False otherwise.
        """

        try:
            url = f"{self.power_on_url}?api={self.api_key}"
            self._logger.info(f"Sending power on request to {url}")
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                self._logger.info(f"Successfully powered on camera {self.camera_name}")
                return True
            else:
                self._logger.warning(
                    f"Failed to power on camera {self.camera_name}: HTTP {response.status_code}"
                )
                return False
        except Exception as e:
            self._logger.error(f"Error powering on camera {self.camera_name}: {str(e)}")
            return False
