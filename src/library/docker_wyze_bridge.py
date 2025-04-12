# https://github.com/mrlt8/docker-wyze-bridge
import subprocess
import os
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
    def __init__(self, camera_name: str, host_ip: str, api_key: str):
        self.host_ip = host_ip
        self.camera_name = camera_name
        self.api_key = api_key

    def start(self) -> None:
        """
        Start the Docker Wyze Bridge service using docker-compose.

        This method starts the Docker Wyze Bridge service defined in the docker-compose.yml file.
        The service provides RTSP, HLS, and RTMP streams for Wyze cameras.
        """

        try:
            # Assuming docker-compose.yml is in the infra directory
            compose_file_path = os.path.join("infra", "docker-compose.yml")

            # Check if the file exists
            if not os.path.exists(compose_file_path):
                raise FileNotFoundError(
                    f"Docker compose file not found at {compose_file_path}"
                )

            # Start the docker-compose service
            subprocess.run(
                ["docker-compose", "-f", compose_file_path, "up", "-d"], check=True
            )

            print(f"Docker Wyze Bridge started successfully. RTSP URL: {self.rtsp_url}")

        except subprocess.CalledProcessError as e:
            print(f"Failed to start Docker Wyze Bridge: {e}")
            raise
        except FileNotFoundError as e:
            print(f"Error: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error starting Docker Wyze Bridge: {e}")
            raise

    def stop(self) -> None:
        pass

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
