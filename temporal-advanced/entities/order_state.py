from dataclasses import dataclass, field
from typing import Dict, Optional

@dataclass
class OrderState:
    approved: bool = False
    items: Dict[str, int] = field(default_factory=dict)
    email: Optional[str] = None
    payment_receipt: Optional[str] = None