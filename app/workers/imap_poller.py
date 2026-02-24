"""
MVP: заглушка.
Реально для хакатона можно:
- запускать отдельным процессом (python -m app.workers.imap_poller)
- или как background task внутри FastAPI (но лучше отдельным процессом)
"""

import time
import logging

log = logging.getLogger("imap_poller")

def run_forever():
    log.info("IMAP poller started (MVP stub).")
    while True:
        # TODO: подключить imaplib, fetch unseen, парсить MIME,
        # вызывать POST /tickets/inbound или напрямую сервис create_ticket_from_inbound
        time.sleep(10)