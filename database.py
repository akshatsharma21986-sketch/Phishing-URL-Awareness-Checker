"""
=============================================================================
Project Name  : Smart Lost & Found Campus Intelligence System
Module        : database.py
Description   : SQLite persistent database layer for storing items, claims,
                and reporting metrics with zero setup overhead.
=============================================================================
"""

import sqlite3
import os
from typing import Optional, List, Dict, Any
from datetime import datetime
from models import Item, ItemStatus, ItemType


DEFAULT_DB_PATH = "smart_lost_found.db"


class Database:
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self) -> None:
        """Creates items and claims tables if they don't exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id TEXT PRIMARY KEY,
                item_type TEXT NOT NULL,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                location TEXT NOT NULL,
                date_event TEXT NOT NULL,
                contact_name TEXT NOT NULL,
                contact_email TEXT NOT NULL,
                contact_phone TEXT NOT NULL,
                secret_question TEXT NOT NULL,
                secret_answer_hash TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                safe_storage_location TEXT,
                resolved_at TEXT
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS claims (
                claim_id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id TEXT NOT NULL,
                claimant_name TEXT NOT NULL,
                claimant_email TEXT NOT NULL,
                claimant_phone TEXT NOT NULL,
                answer_attempt TEXT NOT NULL,
                is_successful INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (item_id) REFERENCES items(id)
            )
            """)

            # Indices for rapid search and retrieval
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_type_status ON items (item_type, status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_category ON items (category)")
            conn.commit()

    def add_item(self, item: Item) -> bool:
        """Inserts a new lost or found item record."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO items (
                id, item_type, title, category, description, location,
                date_event, contact_name, contact_email, contact_phone,
                secret_question, secret_answer_hash, status, created_at,
                safe_storage_location, resolved_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item.id, item.item_type, item.title, item.category, item.description,
                item.location, item.date_event, item.contact_name, item.contact_email,
                item.contact_phone, item.secret_question, item.secret_answer_hash,
                item.status, item.created_at, item.safe_storage_location, item.resolved_at
            ))
            conn.commit()
            return True

    def get_item(self, item_id: str) -> Optional[Item]:
        """Fetches a single item by its unique ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
            row = cursor.fetchone()
            if row:
                return Item(
                    id=row["id"],
                    item_type=row["item_type"],
                    title=row["title"],
                    category=row["category"],
                    description=row["description"],
                    location=row["location"],
                    date_event=row["date_event"],
                    contact_name=row["contact_name"],
                    contact_email=row["contact_email"],
                    contact_phone=row["contact_phone"],
                    secret_question=row["secret_question"],
                    secret_answer_hash=row["secret_answer_hash"],
                    status=row["status"],
                    created_at=row["created_at"],
                    safe_storage_location=row["safe_storage_location"],
                    resolved_at=row["resolved_at"]
                )
            return None

    def list_items(
        self,
        item_type: Optional[str] = None,
        status: Optional[str] = None,
        category: Optional[str] = None,
        search_query: Optional[str] = None
    ) -> List[Item]:
        """Lists items with optional multi-criteria filtering."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM items WHERE 1=1"
            params = []

            if item_type:
                query += " AND item_type = ?"
                params.append(item_type.upper())
            if status:
                query += " AND status = ?"
                params.append(status.upper())
            if category and category != "All Categories":
                query += " AND category = ?"
                params.append(category)
            if search_query:
                term = f"%{search_query.strip().lower()}%"
                query += " AND (LOWER(title) LIKE ? OR LOWER(description) LIKE ? OR LOWER(location) LIKE ?)"
                params.extend([term, term, term])

            query += " ORDER BY created_at DESC"
            cursor.execute(query, params)
            rows = cursor.fetchall()

            items = []
            for r in rows:
                items.append(Item(
                    id=r["id"],
                    item_type=r["item_type"],
                    title=r["title"],
                    category=r["category"],
                    description=r["description"],
                    location=r["location"],
                    date_event=r["date_event"],
                    contact_name=r["contact_name"],
                    contact_email=r["contact_email"],
                    contact_phone=r["contact_phone"],
                    secret_question=r["secret_question"],
                    secret_answer_hash=r["secret_answer_hash"],
                    status=r["status"],
                    created_at=r["created_at"],
                    safe_storage_location=r["safe_storage_location"],
                    resolved_at=r["resolved_at"]
                ))
            return items

    def update_item_status(self, item_id: str, new_status: str) -> bool:
        """Updates the item status and sets resolved_at timestamp when returned."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            resolved_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if new_status == ItemStatus.RETURNED.value else None
            cursor.execute(
                "UPDATE items SET status = ?, resolved_at = COALESCE(?, resolved_at) WHERE id = ?",
                (new_status, resolved_at, item_id)
            )
            conn.commit()
            return cursor.rowcount > 0

    def record_claim(
        self,
        item_id: str,
        claimant_name: str,
        claimant_email: str,
        claimant_phone: str,
        answer_attempt: str,
        is_successful: bool
    ) -> int:
        """Logs an ownership claim challenge attempt in the database."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO claims (
                item_id, claimant_name, claimant_email, claimant_phone,
                answer_attempt, is_successful, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                item_id, claimant_name, claimant_email, claimant_phone,
                answer_attempt, 1 if is_successful else 0,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            conn.commit()
            return cursor.lastrowid

    def get_statistics(self) -> Dict[str, Any]:
        """Computes executive statistics and recovery rates."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM items")
            total_items = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM items WHERE item_type = 'LOST'")
            total_lost = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM items WHERE item_type = 'FOUND'")
            total_found = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM items WHERE status = 'RETURNED'")
            total_returned = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM items WHERE status = 'ACTIVE' AND item_type = 'LOST'")
            active_lost = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM items WHERE status = 'ACTIVE' AND item_type = 'FOUND'")
            active_found = cursor.fetchone()[0]

            cursor.execute("SELECT category, COUNT(*) as cnt FROM items GROUP BY category ORDER BY cnt DESC")
            cat_rows = cursor.fetchall()
            category_distribution = {r["category"]: r["cnt"] for r in cat_rows}

            # Recovery Rate %: Returned items / Total Lost items
            recovery_rate = (total_returned / max(1, total_lost)) * 100.0

            return {
                "total_items": total_items,
                "total_lost": total_lost,
                "total_found": total_found,
                "total_returned": total_returned,
                "active_lost": active_lost,
                "active_found": active_found,
                "recovery_rate_pct": round(recovery_rate, 1),
                "category_distribution": category_distribution
            }

    def reset_database(self) -> None:
        """Clears all records for clean re-seeding."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM claims")
            cursor.execute("DELETE FROM items")
            conn.commit()
