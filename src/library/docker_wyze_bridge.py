# https://github.com/mrlt8/docker-wyze-bridge
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
    def __init__(self, camera_name: str, host_ip: Optional[str] = None):
        self.host_ip = (host_ip or get_host_ip()).strip()
        self.camera_name = camera_name

    @property
    def rtsp_url(self) -> str:
        return f"rtsp://{self.host_ip}:8554/{self.camera_name}"

    @property
    def hls_url(self) -> str:
        return f"http://{self.host_ip}:8888/{self.camera_name}/index.m3u8"

    @property
    def rtmp_url(self) -> str:
        return f"rtmp://{self.host_ip}:1935/live/{self.camera_name}"

    @property
    def stream_list_url(self) -> str:
        return f"http://{self.host_ip}:8888/"

    def all_urls(self) -> WyzeBridgeUrls:
        return WyzeBridgeUrls(
            rtsp=self.rtsp_url,
            hls=self.hls_url,
            rtmp=self.rtmp_url,
            stream_list=self.stream_list_url,
        )
