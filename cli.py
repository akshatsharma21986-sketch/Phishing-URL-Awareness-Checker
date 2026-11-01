"""
=============================================================================
Project Name  : Smart Lost & Found Campus Intelligence System
Module        : cli.py
Description   : Interactive command-line interface for radar scanning,
                item listing, secret challenge verification, and statistics.
=============================================================================
"""

import sys
import argparse
from database import Database
from models import Item, ItemStatus
from matcher import find_all_matches
from sample_data import seed_sample_campus_data
from security import verify_secret_answer
from qr_service import generate_item_qr_image, generate_ascii_qr


def print_banner() -> None:
    print("=" * 80)
    print("       SMART LOST & FOUND CAMPUS INTELLIGENCE SYSTEM (Python 3.10+)")
    print("          AI Multi-Factor Matchmaking • Secret Challenge Verification")
    print("=" * 80)


def cmd_scan(min_confidence: float = 40.0) -> None:
    db = Database()
    lost_items = db.list_items(item_type="LOST", status="ACTIVE")
    found_items = db.list_items(item_type="FOUND", status="ACTIVE")

    print(f"\n[*] Scanning Smart Match Radar across {len(lost_items)} active Lost & {len(found_items)} active Found items...")
    matches = find_all_matches(lost_items, found_items, min_confidence=min_confidence)

    if not matches:
        print("    [-] No candidate matches found meeting the threshold.")
        return

    print(f"[+] Found {len(matches)} candidate matches (Threshold >= {min_confidence}%):\n")
    print("-" * 80)
    print(f"{'CONFIDENCE':<12} | {'LOST ITEM':<30} | {'FOUND ITEM':<32}")
    print("-" * 80)

    for m in matches:
        score_str = f"{m.confidence_score}%"
        print(f"{score_str:<12} | {m.lost_item.title[:28]:<30} | {m.found_item.title[:30]:<32}")
        print(f"             | ID: {m.lost_item.id:<26} | ID: {m.found_item.id:<28}")
        print(f"             | Score Breakdown: Text={m.text_score}% | Cat={m.category_score}% | Loc={m.location_score}% | Date={m.date_score}%")
        if m.matching_keywords:
            print(f"             | Matching Keywords: {', '.join(m.matching_keywords)}")
        print("-" * 80)


def cmd_list(item_type: str = None) -> None:
    db = Database()
    items = db.list_items(item_type=item_type)
    print(f"\n[*] Registered Campus Items ({len(items)} items):\n")
    print("-" * 80)
    print(f"{'ID':<15} | {'TYPE':<6} | {'TITLE':<30} | {'CATEGORY':<18} | {'STATUS':<9}")
    print("-" * 80)
    for it in items:
        print(f"{it.id:<15} | {it.item_type:<6} | {it.title[:28]:<30} | {it.category[:16]:<18} | {it.status:<9}")
    print("-" * 80)


def cmd_stats() -> None:
    db = Database()
    stats = db.get_statistics()
    print("\n" + "=" * 50)
    print("      CAMPUS LOST & FOUND RECOVERY ANALYTICS")
    print("=" * 50)
    print(f" Total Registered Items : {stats['total_items']}")
    print(f" Active Lost Reports    : {stats['active_lost']}")
    print(f" Active Found Reports   : {stats['active_found']}")
    print(f" Successfully Returned  : {stats['total_returned']}")
    print(f" Campus Recovery Rate   : {stats['recovery_rate_pct']}%")
    print("-" * 50)
    print(" Category Breakdown:")
    for cat, count in stats["category_distribution"].items():
        print(f"   • {cat:<24} : {count} items")
    print("=" * 50 + "\n")


def cmd_verify(item_id: str, candidate_answer: str) -> None:
    db = Database()
    item = db.get_item(item_id)
    if not item:
        print(f"\n[-] Error: Item '{item_id}' not found.")
        return

    print(f"\n[*] Item: [{item.item_type}] {item.title} ({item.id})")
    print(f"[*] Secret Challenge Question: \"{item.secret_question}\"")
    print(f"[*] Testing Candidate Answer : \"{candidate_answer}\"")

    is_valid = verify_secret_answer(candidate_answer, item.secret_answer_hash)
    if is_valid:
        db.update_item_status(item.id, ItemStatus.RETURNED.value)
        print("\n[+] SUCCESS: Secret challenge answer verified!")
        print(f"[+] Status updated to: RETURNED")
        if item.safe_storage_location:
            print(f"[+] Safe Custody Location : {item.safe_storage_location}")
        print(f"[+] Contact Person        : {item.contact_name} ({item.contact_phone})")
    else:
        print("\n[-] FAILED: Incorrect answer to secret challenge question. Access denied.")


def cmd_qr(item_id: str) -> None:
    db = Database()
    item = db.get_item(item_id)
    if not item:
        print(f"\n[-] Error: Item '{item_id}' not found.")
        return

    print(f"\n[*] Generating Digital QR Tag for [{item.id}] {item.title}...")
    ascii_qr = generate_ascii_qr(item.id)
    try:
        print(ascii_qr)
    except (UnicodeEncodeError, Exception):
        print(f"    [Digital QR Payload]: SMART_LOST_FOUND://ITEM?id={item.id}")

    png_path = generate_item_qr_image(item.id, item.title)
    if png_path:
        print(f"[+] Saved high-resolution PNG QR tag to: {png_path}")


def main():
    parser = argparse.ArgumentParser(description="Smart Lost & Found Campus Intelligence System")
    parser.add_argument("--scan", action="store_true", help="Run AI Smart Match Radar across all active items")
    parser.add_argument("--threshold", type=float, default=40.0, help="Minimum confidence threshold for radar matching (default: 40.0)")
    parser.add_argument("--list", choices=["ALL", "LOST", "FOUND"], const="ALL", nargs="?", help="List registered items")
    parser.add_argument("--stats", action="store_true", help="Display recovery rate and campus analytics")
    parser.add_argument("--seed", action="store_true", help="Re-seed database with realistic sample campus items")
    parser.add_argument("--verify", nargs=2, metavar=("ITEM_ID", "ANSWER"), help="Verify ownership of an item using the secret challenge")
    parser.add_argument("--qr", metavar="ITEM_ID", help="Generate QR code for a specific item ID")
    parser.add_argument("--gui", action="store_true", help="Launch interactive Tkinter desktop GUI")

    args = parser.parse_args()

    print_banner()

    if args.gui:
        import app_gui
        app_gui.launch_app()
    elif args.scan:
        cmd_scan(min_confidence=args.threshold)
    elif args.list:
        cmd_list(item_type=None if args.list == "ALL" else args.list)
    elif args.stats:
        cmd_stats()
    elif args.seed:
        db = Database()
        count = seed_sample_campus_data(db)
        print(f"\n[+] Successfully seeded {count} realistic campus items into database.")
    elif args.verify:
        cmd_verify(args.verify[0], args.verify[1])
    elif args.qr:
        cmd_qr(args.qr)
    else:
        # Default behavior if run without flags: display scan and help
        cmd_stats()
        cmd_scan(min_confidence=args.threshold)
        print("Tip: Run 'python cli.py --gui' to open the interactive desktop application!\n")


if __name__ == "__main__":
    main()
