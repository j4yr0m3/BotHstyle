import time
import threading
import logging
from logger_config import log_event_jsonl

class SurveillanceEngine:
    def __init__(self, store, msg_queue):
        self.store = store
        self.msg_queue = msg_queue
        self.running = False

    def start_surveillance(self, active_markets):
        self.running = True
        thread = threading.Thread(
            target=self._surveillance_loop,
            args=(active_markets,),
            daemon=True,
            name="SurveillanceThread"
        )
        thread.start()

    def _surveillance_loop(self, active_markets):
        logging.info(f"Boucle de surveillance démarrée pour : {active_markets}")
        while self.running:
            for market in active_markets:
                time.sleep(1)
                signal_event = {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "market": market,
                    "action": "BUY",
                    "price": 50000.0
                }
                self.store.add_signal(signal_event)
                self.msg_queue.put({"type": "SIGNAL", "data": signal_event})
                log_event_jsonl(signal_event)
            time.sleep(5)

    def stop(self):
        self.running = False
        logging.info("Arrêt de la surveillance demandé.")