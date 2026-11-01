"""
=============================================================================
Project Name  : Smart Lost & Found Campus Intelligence System
Module        : tests/test_system.py
Description   : Automated unit test suite verifying database CRUD, multi-factor
                smart matching accuracy, secret challenge hashing, and QR logic.
=============================================================================
"""

import os
import unittest
from database import Database
from models import Item, ItemStatus, Category
from matcher import calculate_match, compute_text_similarity
from security import hash_secret_answer, verify_secret_answer
from qr_service import generate_item_qr_image


TEST_DB = "test_smart_lost_found.db"


class TestSmartLostFoundSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = Database(TEST_DB)

    def setUp(self):
        self.db.reset_database()

    def test_database_crud(self):
        """Verify inserting, querying, and updating items in SQLite."""
        item = Item(
            id="LOST-TEST-001",
            item_type="LOST",
            title="HP Pavilion Laptop Charger",
            category=Category.ELECTRONICS.value,
            description="Blue tip HP 45W charger lost in Lab 2.",
            location="Computer Lab 2",
            date_event="2026-10-25",
            contact_name="Test Student",
            contact_email="student@campus.edu",
            contact_phone="9988776655",
            secret_question="What is the charger wattage?",
            secret_answer_hash=hash_secret_answer("45W"),
            status=ItemStatus.ACTIVE.value
        )
        self.db.add_item(item)

        retrieved = self.db.get_item("LOST-TEST-001")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.title, "HP Pavilion Laptop Charger")
        self.assertEqual(retrieved.status, ItemStatus.ACTIVE.value)

        # Update status
        self.db.update_item_status("LOST-TEST-001", ItemStatus.RETURNED.value)
        updated = self.db.get_item("LOST-TEST-001")
        self.assertEqual(updated.status, ItemStatus.RETURNED.value)

    def test_security_challenge_hashing(self):
        """Verify secret answer hashing and case-insensitive verification."""
        secret = "Pikachu Sticker"
        hashed = hash_secret_answer(secret)

        # Exact match
        self.assertTrue(verify_secret_answer("Pikachu Sticker", hashed))
        # Case insensitive match
        self.assertTrue(verify_secret_answer("pikachu sticker", hashed))
        # Extra whitespace match
        self.assertTrue(verify_secret_answer("  Pikachu   Sticker  ", hashed))
        # Wrong answer
        self.assertFalse(verify_secret_answer("Charizard", hashed))

    def test_smart_matching_high_confidence(self):
        """Verify high confidence score for matching items."""
        lost = Item(
            id="LOST-001",
            item_type="LOST",
            title="Apple AirPods Pro White",
            category=Category.ELECTRONICS.value,
            description="Lost white Apple AirPods Pro wireless earbuds in Central Library.",
            location="Central Library 2nd Floor",
            date_event="2026-10-26",
            contact_name="Alice",
            contact_email="alice@test.com",
            contact_phone="1234567890",
            secret_question="Sticker?",
            secret_answer_hash="hash"
        )
        found = Item(
            id="FND-001",
            item_type="FOUND",
            title="White Apple AirPods Wireless Earbuds",
            category=Category.ELECTRONICS.value,
            description="Found white Apple AirPods in Central Library study cubicle.",
            location="Central Library 2nd Floor",
            date_event="2026-10-26",
            contact_name="Bob",
            contact_email="bob@test.com",
            contact_phone="0987654321",
            secret_question="Sticker?",
            secret_answer_hash="hash"
        )

        match = calculate_match(lost, found)
        self.assertGreaterEqual(match.confidence_score, 70.0)
        self.assertEqual(match.category_score, 100.0)
        self.assertIn("airpods", [k.lower() for k in match.matching_keywords])

    def test_smart_matching_low_confidence_mismatch(self):
        """Verify near-zero score for completely incompatible items."""
        lost = Item(
            id="LOST-002",
            item_type="LOST",
            title="Black Wildcraft Backpack",
            category=Category.WALLETS_BAGS.value,
            description="College backpack with books.",
            location="Auditorium",
            date_event="2026-10-20",
            contact_name="Alice",
            contact_email="alice@test.com",
            contact_phone="1234567890",
            secret_question="Brand?",
            secret_answer_hash="hash"
        )
        found = Item(
            id="FND-002",
            item_type="FOUND",
            title="Hyundai Car Keys Remote",
            category=Category.KEYS.value,
            description="Car key fob found in Parking Lot B.",
            location="Parking Lot B",
            date_event="2026-10-29",
            contact_name="Bob",
            contact_email="bob@test.com",
            contact_phone="0987654321",
            secret_question="Color?",
            secret_answer_hash="hash"
        )

        match = calculate_match(lost, found)
        self.assertLess(match.confidence_score, 30.0)

    def test_qr_generation(self):
        """Verify QR tag generation."""
        path = generate_item_qr_image("TEST-ITEM-123", "Test Title")
        if path:
            self.assertTrue(os.path.exists(path))
            if os.path.exists(path):
                os.remove(path)


if __name__ == "__main__":
    unittest.main()
