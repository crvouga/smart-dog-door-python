import cv2
import numpy as np
from typing import Optional
from src.device_camera.interface import DeviceCamera
from src.library.life_cycle import LifeCycle
import logging
import time
import threading


class RtspDeviceCamera(DeviceCamera, LifeCycle):
    _logger: logging.Logger
    _rtsp_url: str
    _cap: Optional[cv2.VideoCapture]
    _is_running: bool
    _retry_interval: float = 5.0  # seconds between retries
    _lock: threading.Lock

    def __init__(self, logger: logging.Logger, rtsp_url: str) -> None:
        self._logger = logger.getChild("rtsp_device_camera")
        self._rtsp_url = rtsp_url
        self._cap = None
        self._is_running = False
        self._lock = threading.Lock()

    def start(self) -> None:
        self._logger.info("Starting RtspDeviceCamera...")
        self._is_running = True
        self._start_connection_loop()

    def _start_connection_loop(self) -> None:
        while self._is_running:
            try:
                with self._lock:
                    if self._cap is not None:
                        self._cap.release()
                    self._cap = cv2.VideoCapture(self._rtsp_url)

                    if not self._cap.isOpened():
                        raise RuntimeError("Failed to open RTSP stream")

                    self._logger.info(
                        f"Successfully connected to RTSP stream: {self._rtsp_url}"
                    )
                    return  # Successfully connected, exit the loop
            except Exception as e:
                self._logger.error(f"Failed to connect to RTSP stream: {e}")
                self._logger.info(f"Retrying in {self._retry_interval} seconds...")
                time.sleep(self._retry_interval)

    def stop(self) -> None:
        self._logger.info("Stopping RtspDeviceCamera...")
        self._is_running = False
        with self._lock:
            if self._cap is not None:
                self._cap.release()
                self._cap = None

    def read(self) -> Optional[np.ndarray]:
        with self._lock:
            if self._cap is None or not self._cap.isOpened():
                self._logger.warning("Camera not connected, attempting to reconnect...")
                self._start_connection_loop()
                return None

            try:
                ret, frame = self._cap.read()
                if not ret:
                    self._logger.warning("Failed to read frame from camera")
                    self._start_connection_loop()
                    return None
                return frame
            except Exception as e:
                self._logger.error(f"Error reading from camera: {e}")
                self._start_connection_loop()
                return None

    def get_resolution(self) -> tuple[int, int]:
        with self._lock:
            if self._cap is None or not self._cap.isOpened():
                return (0, 0)
            width = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            return (width, height)

    def get_fps(self) -> float:
        with self._lock:
            if self._cap is None or not self._cap.isOpened():
                return 0.0
            return self._cap.get(cv2.CAP_PROP_FPS)
