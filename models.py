"""
=============================================================================
Project Name  : Smart Lost & Found Campus Intelligence System
Module        : models.py
Description   : Core data models, enumeration definitions, and schemas.
=============================================================================
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any


class ItemType(str, Enum):
    LOST = "LOST"
    FOUND = "FOUND"


class Category(str, Enum):
    ELECTRONICS = "Electronics"
    ID_DOCUMENTS = "ID & Documents"
    KEYS = "Keys & Keychains"
    WALLETS_BAGS = "Wallets & Bags"
    CLOTHING = "Clothing & Accessories"
    BOOKS_STATIONERY = "Books & Stationery"
    JEWELRY_WATCHES = "Jewelry & Watches"
    OTHER = "Other"


class ItemStatus(str, Enum):
    ACTIVE = "ACTIVE"
    CLAIM_PENDING = "CLAIM_PENDING"
    RETURNED = "RETURNED"
    EXPIRED = "EXPIRED"


class ClaimStatus(str, Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


@dataclass
class Item:
    id: str
    item_type: str                   # ItemType: "LOST" or "FOUND"
    title: str                       # e.g., "Apple AirPods Pro (2nd Gen)"
    category: str                    # Category value
    description: str                # Full text description
    location: str                   # e.g., "Main Library 2nd Floor"
    date_event: str                 # Date lost or found (YYYY-MM-DD)
    contact_name: str
    contact_email: str
    contact_phone: str
    secret_question: str            # e.g., "What sticker is on the charging case?"
    secret_answer_hash: str         # Salted SHA-256 hash of secret answer
    status: str = ItemStatus.ACTIVE.value
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    safe_storage_location: Optional[str] = ""  # If FOUND, where the physical item is kept
    resolved_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "item_type": self.item_type,
            "title": self.title,
            "category": self.category,
            "description": self.description,
            "location": self.location,
            "date_event": self.date_event,
            "contact_name": self.contact_name,
            "contact_email": self.contact_email,
            "contact_phone": self.contact_phone,
            "secret_question": self.secret_question,
            "secret_answer_hash": self.secret_answer_hash,
            "status": self.status,
            "created_at": self.created_at,
            "safe_storage_location": self.safe_storage_location or "",
            "resolved_at": self.resolved_at or ""
        }


@dataclass
class MatchResult:
    lost_item: Item
    found_item: Item
    confidence_score: float         # 0.0 to 100.0%
    text_score: float              # NLP description similarity (0-100)
    category_score: float          # Category compatibility (0-100)
    location_score: float          # Geographic text overlap (0-100)
    date_score: float              # Temporal proximity score (0-100)
    matching_keywords: List[str] = field(default_factory=list)
