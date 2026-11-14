import logging
import json

def setup_logging():
    # 1. Logger système global (TXT)
    logging.basicConfig(
        filename="trading_system.log",
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(threadName)s: %(message)s",
        encoding="utf-8"
    )
    logging.info("Système de journalisation initialisé.")

def log_event_jsonl(event_data, filepath="trading_events.jsonl"):
    # 2. Écriture d'événements JSONL
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(json.dumps(event_data, ensure_ascii=False) + "\n")