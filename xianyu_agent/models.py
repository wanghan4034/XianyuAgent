from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional


@dataclass
class Product:
    title: str
    price: Optional[float]
    location: Optional[str]
    item_url: Optional[str]
    seller: Optional[str]
    item_id: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
