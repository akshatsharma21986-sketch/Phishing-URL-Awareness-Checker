"""
=============================================================================
Project Name  : Smart Lost & Found Campus Intelligence System
Module        : sample_data.py
Description   : Realistic college campus sample dataset generator with intentional
                cross-matched pairs to demonstrate the Smart Matchmaker instantly.
=============================================================================
"""

from database import Database
from models import Item, ItemStatus, Category
from security import hash_secret_answer


def seed_sample_campus_data(db: Database) -> int:
    """Pre-populates the database with realistic student items."""
    db.reset_database()

    sample_items = [
        # --- PAIR 1: Apple AirPods Pro (Intentional High-Confidence Match) ---
        Item(
            id="LOST-2610-101",
            item_type="LOST",
            title="Apple AirPods Pro (2nd Gen)",
            category=Category.ELECTRONICS.value,
            description="Lost in Central Library 2nd floor cubicle. White charging case with a small yellow Pikachu sticker on the back.",
            location="Central Library 2nd Floor",
            date_event="2026-10-25",
            contact_name="Rohan Verma",
            contact_email="rohan.verma@campus.edu",
            contact_phone="9876543210",
            secret_question="What sticker is attached to the charging case?",
            secret_answer_hash=hash_secret_answer("Pikachu"),
            status=ItemStatus.ACTIVE.value
        ),
        Item(
            id="FND-2610-201",
            item_type="FOUND",
            title="White Apple AirPods Wireless Earbuds",
            category=Category.ELECTRONICS.value,
            description="Found left behind on a study desk in Central Library 2nd floor reading hall.",
            location="Central Library 2nd Floor",
            date_event="2026-10-26",
            contact_name="Pooja Sharma (Librarian)",
            contact_email="library.desk@campus.edu",
            contact_phone="9811223344",
            secret_question="Describe any distinguishing marks or stickers on the case.",
            secret_answer_hash=hash_secret_answer("Pikachu"),
            status=ItemStatus.ACTIVE.value,
            safe_storage_location="Library Reception Desk, Shelf 2"
        ),

        # --- PAIR 2: Scientific Calculator (Intentional Match) ---
        Item(
            id="LOST-2610-102",
            item_type="LOST",
            title="Casio FX-991EX Classwiz Scientific Calculator",
            category=Category.BOOKS_STATIONERY.value,
            description="Black scientific calculator with slide cover. Lost after Advanced Calculus exam in Engineering Block Room 204.",
            location="Engineering Block Room 204",
            date_event="2026-10-27",
            contact_name="Aman Gupta",
            contact_email="aman.g@campus.edu",
            contact_phone="9876501234",
            secret_question="What name or initials are engraved on the back cover?",
            secret_answer_hash=hash_secret_answer("Aman"),
            status=ItemStatus.ACTIVE.value
        ),
        Item(
            id="FND-2610-202",
            item_type="FOUND",
            title="Casio Scientific Calculator FX-991",
            category=Category.BOOKS_STATIONERY.value,
            description="Found black Casio calculator left on desk in Engineering Block hallway.",
            location="Engineering Block 2nd Floor",
            date_event="2026-10-28",
            contact_name="Security Desk",
            contact_email="security@campus.edu",
            contact_phone="9800112233",
            secret_question="What word is written on the back cover?",
            secret_answer_hash=hash_secret_answer("Aman"),
            status=ItemStatus.ACTIVE.value,
            safe_storage_location="Main Gate Security Guard Room"
        ),

        # --- PAIR 3: College Student ID Card (Intentional Match) ---
        Item(
            id="LOST-2610-103",
            item_type="LOST",
            title="Student Identity Card - Akshat Sharma",
            category=Category.ID_DOCUMENTS.value,
            description="College ID card in navy blue lanyard. Roll number CS-2024-042. Lost near Cafeteria.",
            location="Student Cafeteria / Canteen",
            date_event="2026-10-28",
            contact_name="Akshat Sharma",
            contact_email="akshat.sharma@campus.edu",
            contact_phone="9899887766",
            secret_question="What is the roll number printed on the ID card?",
            secret_answer_hash=hash_secret_answer("CS-2024-042"),
            status=ItemStatus.ACTIVE.value
        ),
        Item(
            id="FND-2610-203",
            item_type="FOUND",
            title="College Student ID Card with Navy Blue Lanyard",
            category=Category.ID_DOCUMENTS.value,
            description="Found near Cafeteria dining counter.",
            location="Student Cafeteria",
            date_event="2026-10-29",
            contact_name="Vikram Singh",
            contact_email="canteen.admin@campus.edu",
            contact_phone="9822334455",
            secret_question="Provide the student roll number on the card.",
            secret_answer_hash=hash_secret_answer("CS-2024-042"),
            status=ItemStatus.ACTIVE.value,
            safe_storage_location="Cafeteria Manager Office"
        ),

        # --- PAIR 4: Titan Wristwatch (Intentional Match) ---
        Item(
            id="LOST-2610-104",
            item_type="LOST",
            title="Titan Analog Men's Watch",
            category=Category.JEWELRY_WATCHES.value,
            description="Titan wrist watch with silver metallic dial and dark brown leather strap. Lost in Sports Complex Gym.",
            location="Sports Complex Gym",
            date_event="2026-10-24",
            contact_name="Karan Malhotra",
            contact_email="karan.m@campus.edu",
            contact_phone="9812345678",
            secret_question="What color is the watch dial?",
            secret_answer_hash=hash_secret_answer("Silver"),
            status=ItemStatus.ACTIVE.value
        ),
        Item(
            id="FND-2610-204",
            item_type="FOUND",
            title="Titan Silver Dial Watch with Brown Strap",
            category=Category.JEWELRY_WATCHES.value,
            description="Found on bench in Sports Complex locker changing room.",
            location="Sports Complex Locker Room",
            date_event="2026-10-25",
            contact_name="Coach Dev",
            contact_email="sports@campus.edu",
            contact_phone="9855667788",
            secret_question="Specify the dial color of the watch.",
            secret_answer_hash=hash_secret_answer("Silver"),
            status=ItemStatus.ACTIVE.value,
            safe_storage_location="Sports Department Equipment Room"
        ),

        # --- UNMATCHED ACTIVE ITEMS ---
        Item(
            id="LOST-2610-105",
            item_type="LOST",
            title="Wildcraft Black College Backpack",
            category=Category.WALLETS_BAGS.value,
            description="Black Wildcraft backpack containing notebook and red water bottle. Lost in Auditorium.",
            location="Main Auditorium Row G",
            date_event="2026-10-29",
            contact_name="Sneha Rao",
            contact_email="sneha.r@campus.edu",
            contact_phone="9844332211",
            secret_question="What brand is the water bottle inside the bag?",
            secret_answer_hash=hash_secret_answer("Milton"),
            status=ItemStatus.ACTIVE.value
        ),
        Item(
            id="FND-2610-205",
            item_type="FOUND",
            title="Dell 65W Laptop Charger Type-C",
            category=Category.ELECTRONICS.value,
            description="Found black Dell 65W USB-C laptop power adapter plugged in Computer Lab 3.",
            location="Computer Science Lab 3",
            date_event="2026-10-30",
            contact_name="Lab Assistant Suresh",
            contact_email="cs.lab@campus.edu",
            contact_phone="9877665544",
            secret_question="What is the charger wattage and connector type?",
            secret_answer_hash=hash_secret_answer("65W Type C"),
            status=ItemStatus.ACTIVE.value,
            safe_storage_location="CS Lab 3 Instructor Desk"
        ),
        Item(
            id="FND-2610-206",
            item_type="FOUND",
            title="Hyundai Car Key with Remote Fob",
            category=Category.KEYS.value,
            description="Single car key with Hyundai black remote fob found on walking path near Parking Lot B.",
            location="Parking Lot B",
            date_event="2026-10-30",
            contact_name="Campus Security",
            contact_email="security@campus.edu",
            contact_phone="9800112233",
            secret_question="What color is the silicone protector cover?",
            secret_answer_hash=hash_secret_answer("Red"),
            status=ItemStatus.ACTIVE.value,
            safe_storage_location="Main Security Office Locker 4"
        ),

        # --- RESOLVED / RETURNED ITEM (Demonstrates recovery statistics) ---
        Item(
            id="LOST-2610-100",
            item_type="LOST",
            title="Spectacles with Black Ray-Ban Frame",
            category=Category.CLOTHING.value,
            description="Reading spectacles with black rectangular Ray-Ban frame in hard case.",
            location="Seminar Hall 1",
            date_event="2026-10-20",
            contact_name="Prof. Verma",
            contact_email="verma@campus.edu",
            contact_phone="9811002299",
            secret_question="What is the case color?",
            secret_answer_hash=hash_secret_answer("Black"),
            status=ItemStatus.RETURNED.value,
            resolved_at="2026-10-22 14:30:00"
        ),
        Item(
            id="FND-2610-200",
            item_type="FOUND",
            title="Ray-Ban Spectacles in Black Case",
            category=Category.CLOTHING.value,
            description="Found Ray-Ban spectacles on speaker podium after conference.",
            location="Seminar Hall 1",
            date_event="2026-10-20",
            contact_name="Student Volunteer",
            contact_email="volunteer@campus.edu",
            contact_phone="9811002299",
            secret_question="What is the case color?",
            secret_answer_hash=hash_secret_answer("Black"),
            status=ItemStatus.RETURNED.value,
            safe_storage_location="Returned to Owner",
            resolved_at="2026-10-22 14:30:00"
        )
    ]

    for it in sample_items:
        db.add_item(it)

    return len(sample_items)
