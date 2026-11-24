import logging
import sys

from .loader import load_tickets

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
result = load_tickets(sys.argv[1])
print(f"{len(result.valid)} valid, {len(result.invalid)} invalid")