from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class ChargeInput:
    order_id: str
    amount_euro: float
    idempotency_key: Optional[str] = None


