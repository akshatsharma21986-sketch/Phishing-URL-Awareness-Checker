"""
=============================================================================
Project Name  : Smart Lost & Found Campus Intelligence System
Module        : security.py
Description   : Cryptographic hashing for secret claim questions,
                ownership verification challenges, and unique token generation.
=============================================================================
"""

import hashlib
import random
import re
from datetime import datetime


SALT = "SmartLostFound_CampusSecurity_Salt_2026"


def normalize_text(text: str) -> str:
    """Standardizes text for robust comparison by removing punctuation and extra spaces."""
    if not text:
        return ""
    clean = re.sub(r"[^\w\s]", "", text.lower())
    return " ".join(clean.split())


def hash_secret_answer(answer: str) -> str:
    """
    Computes a salted SHA-256 hash of the secret ownership verification answer.
    Answer is normalized first so minor capitalizations or spaces don't lock out true owners.
    """
    normalized = normalize_text(answer)
    salted_string = f"{SALT}:{normalized}:{SALT}"
    return hashlib.sha256(salted_string.encode("utf-8")).hexdigest()


def verify_secret_answer(candidate_answer: str, stored_hash: str) -> bool:
    """
    Validates a claim attempt against the stored cryptographic hash.
    Returns True if the normalized answer matches the hash.
    """
    candidate_hash = hash_secret_answer(candidate_answer)
    return candidate_hash == stored_hash


def generate_item_id(item_type: str) -> str:
    """Generates an intuitive, readable unique identifier like LOST-4921 or FND-7812."""
    prefix = "LOST" if item_type.upper() == "LOST" else "FND"
    random_num = random.randint(1000, 9999)
    timestamp_suffix = datetime.now().strftime("%y%m")
    return f"{prefix}-{timestamp_suffix}-{random_num}"
