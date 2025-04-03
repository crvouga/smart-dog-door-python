from .pub_sub import PubSub, Sub
from datetime import datetime
import threading
import time


def ticks(interval_seconds: float) -> Sub[datetime]:
    pub_sub = PubSub()

    def tick_thread():
        while True:
            pub_sub.pub(datetime.now())
            time.sleep(interval_seconds)

    thread = threading.Thread(target=tick_thread, daemon=True)
    thread.start()

    return pub_sub
