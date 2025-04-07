from .pub_sub import PubSub, Sub
from datetime import datetime, timedelta
import threading
import time


def ticks(interval: timedelta) -> Sub[datetime]:
    pub_sub = PubSub[datetime]()

    def tick_thread():
        while True:
            pub_sub.publish(datetime.now())
            time.sleep(interval.total_seconds())

    thread = threading.Thread(target=tick_thread, daemon=True)
    thread.start()

    return pub_sub
