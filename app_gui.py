"""
=============================================================================
Project Name  : Smart Lost & Found Campus Intelligence System
Module        : app_gui.py
Description   : Modern Tkinter Desktop GUI featuring Live Feeds, Smart Match
                Radar, Secret Claim Verification Challenge, and QR Tag Generation.
=============================================================================
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from typing import Optional, List, Dict, Any

from database import Database
from models import Item, ItemType, Category, ItemStatus, MatchResult
from matcher import find_all_matches, calculate_match
from security import hash_secret_answer, verify_secret_answer, generate_item_id
from sample_data import seed_sample_campus_data
from qr_service import generate_item_qr_image, QRCODE_AVAILABLE


class SmartLostFoundApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Smart Lost & Found Campus Intelligence System")
        self.root.geometry("1060x720")
        self.root.minsize(920, 620)

        self.db = Database("smart_lost_found.db")
        self.current_matches: List[MatchResult] = []

        # Auto-seed if database is empty
        stats = self.db.get_statistics()
        if stats["total_items"] == 0:
            seed_sample_campus_data(self.db)

        self._setup_styles()
        self._build_layout()
        self._refresh_kpis()
        self._refresh_items_table()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TNotebook", background="#f1f5f9")
        style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=[14, 8])
        style.configure("TFrame", background="#ffffff")
        style.configure("Header.TLabel", font=("Segoe UI", 13, "bold"), foreground="#0f172a", background="#ffffff")
        style.configure("Sub.TLabel", font=("Segoe UI", 9), foreground="#64748b", background="#ffffff")

    def _build_layout(self):
        # Top Header Banner
        banner = tk.Frame(self.root, bg="#0f172a", height=75)
        banner.pack(fill="x", side="top")

        lbl_title = tk.Label(
            banner,
            text="Smart Lost & Found Campus Intelligence System",
            font=("Segoe UI", 16, "bold"),
            fg="#38bdf8",
            bg="#0f172a"
        )
        lbl_title.pack(anchor="w", padx=25, pady=(12, 2))

        lbl_sub = tk.Label(
            banner,
            text="AI-Assisted Multi-Factor Matchmaking • Secret Challenge Claim Verification • QR Tagging",
            font=("Segoe UI", 9),
            fg="#94a3b8",
            bg="#0f172a"
        )
        lbl_sub.pack(anchor="w", padx=25, pady=(0, 10))

        # KPI Dashboard Cards Bar
        self.kpi_frame = tk.Frame(self.root, bg="#f8fafc", pady=8, padx=15, relief="solid", bd=1)
        self.kpi_frame.pack(fill="x", side="top")
        self._build_kpi_cards()

        # Tabbed Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=10)

        # Tab 1: Live Feed & Explorer
        self.tab_feed = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_feed, text=" 1. Item Directory & Live Feed ")
        self._build_tab_feed()

        # Tab 2: Report Lost Item
        self.tab_report_lost = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_report_lost, text=" 2. Report Lost Item ")
        self._build_tab_report_lost()

        # Tab 3: Report Found Item
        self.tab_report_found = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_report_found, text=" 3. Report Found Item ")
        self._build_tab_report_found()

        # Tab 4: Smart Match Radar
        self.tab_radar = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_radar, text=" 4. Smart Match Radar (AI) ")
        self._build_tab_radar()

        # Tab 5: Claim Verification Challenge
        self.tab_claim = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_claim, text=" 5. Claim & Verification ")
        self._build_tab_claim()

        # Bottom Status Bar
        self.status_var = tk.StringVar(value="System Active • Database Connected")
        status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            font=("Segoe UI", 9),
            anchor="w",
            bg="#e2e8f0",
            fg="#334155",
            padx=12,
            pady=4
        )
        status_bar.pack(fill="x", side="bottom")

    # -------------------------------------------------------------------------
    # KPI CARDS
    # -------------------------------------------------------------------------
    def _build_kpi_cards(self):
        for widget in self.kpi_frame.winfo_children():
            widget.destroy()

        stats = self.db.get_statistics()
        cards_data = [
            ("TOTAL REPORTED", str(stats["total_items"]), "#0284c7"),
            ("ACTIVE LOST", str(stats["active_lost"]), "#dc2626"),
            ("ACTIVE FOUND", str(stats["active_found"]), "#16a34a"),
            ("SUCCESSFUL RETURNS", str(stats["total_returned"]), "#9333ea"),
            ("RECOVERY RATE", f"{stats['recovery_rate_pct']}%", "#ea580c")
        ]

        for i, (title, value, color) in enumerate(cards_data):
            f = tk.Frame(self.kpi_frame, bg="#ffffff", padx=14, pady=6, relief="groove", bd=1)
            f.pack(side="left", expand=True, fill="both", padx=4)

            tk.Label(f, text=title, font=("Segoe UI", 8, "bold"), fg="#64748b", bg="#ffffff").pack(anchor="w")
            tk.Label(f, text=value, font=("Segoe UI", 14, "bold"), fg=color, bg="#ffffff").pack(anchor="w")

    def _refresh_kpis(self):
        self._build_kpi_cards()

    # -------------------------------------------------------------------------
    # TAB 1: ITEM DIRECTORY & FEED
    # -------------------------------------------------------------------------
    def _build_tab_feed(self):
        filter_bar = tk.Frame(self.tab_feed, bg="#ffffff", pady=8, padx=10)
        filter_bar.pack(fill="x")

        tk.Label(filter_bar, text="Search:", font=("Segoe UI", 9, "bold"), bg="#ffffff").pack(side="left", padx=(0, 4))
        self.entry_search = ttk.Entry(filter_bar, width=20)
        self.entry_search.pack(side="left", padx=(0, 10))
        self.entry_search.bind("<Return>", lambda e: self._refresh_items_table())

        tk.Label(filter_bar, text="Type:", font=("Segoe UI", 9, "bold"), bg="#ffffff").pack(side="left", padx=(0, 4))
        self.combo_type = ttk.Combobox(filter_bar, values=["All Types", "LOST", "FOUND"], state="readonly", width=10)
        self.combo_type.set("All Types")
        self.combo_type.pack(side="left", padx=(0, 10))
        self.combo_type.bind("<<ComboboxSelected>>", lambda e: self._refresh_items_table())

        tk.Label(filter_bar, text="Category:", font=("Segoe UI", 9, "bold"), bg="#ffffff").pack(side="left", padx=(0, 4))
        categories = ["All Categories"] + [c.value for c in Category]
        self.combo_category = ttk.Combobox(filter_bar, values=categories, state="readonly", width=18)
        self.combo_category.set("All Categories")
        self.combo_category.pack(side="left", padx=(0, 10))
        self.combo_category.bind("<<ComboboxSelected>>", lambda e: self._refresh_items_table())

        btn_filter = tk.Button(filter_bar, text="Apply Filter", font=("Segoe UI", 9), bg="#0284c7", fg="#ffffff", command=self._refresh_items_table, padx=10, relief="flat", cursor="hand2")
        btn_filter.pack(side="left", padx=5)

        btn_reset = tk.Button(filter_bar, text="Reset / Re-seed Data", font=("Segoe UI", 9), bg="#64748b", fg="#ffffff", command=self._reseed_data, padx=10, relief="flat", cursor="hand2")
        btn_reset.pack(side="right", padx=5)

        # Split pane: Top table, Bottom item inspector
        paned = ttk.PanedWindow(self.tab_feed, orient="vertical")
        paned.pack(fill="both", expand=True, padx=10, pady=5)

        # Table
        tbl_frame = ttk.Frame(paned)
        paned.add(tbl_frame, weight=3)

        cols = ["ID", "Type", "Title", "Category", "Location", "Date", "Status"]
        self.tree_items = ttk.Treeview(tbl_frame, columns=cols, show="headings", selectmode="browse")
        scroll_y = ttk.Scrollbar(tbl_frame, orient="vertical", command=self.tree_items.yview)
        self.tree_items.configure(yscrollcommand=scroll_y.set)

        self.tree_items.heading("ID", text="Item ID")
        self.tree_items.heading("Type", text="Type")
        self.tree_items.heading("Title", text="Title")
        self.tree_items.heading("Category", text="Category")
        self.tree_items.heading("Location", text="Location")
        self.tree_items.heading("Date", text="Event Date")
        self.tree_items.heading("Status", text="Status")

        self.tree_items.column("ID", width=110, anchor="center")
        self.tree_items.column("Type", width=70, anchor="center")
        self.tree_items.column("Title", width=240, anchor="w")
        self.tree_items.column("Category", width=140, anchor="w")
        self.tree_items.column("Location", width=160, anchor="w")
        self.tree_items.column("Date", width=95, anchor="center")
        self.tree_items.column("Status", width=95, anchor="center")

        self.tree_items.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")
        self.tree_items.bind("<<TreeviewSelect>>", self._on_item_selected)

        # Bottom Item Inspector Card
        self.detail_frame = tk.Frame(paned, bg="#ffffff", padx=12, pady=10, relief="solid", bd=1)
        paned.add(self.detail_frame, weight=2)
        self._build_detail_inspector()

    def _build_detail_inspector(self):
        for w in self.detail_frame.winfo_children():
            w.destroy()

        top_row = tk.Frame(self.detail_frame, bg="#ffffff")
        top_row.pack(fill="x", side="top", pady=(0, 6))

        self.lbl_detail_title = tk.Label(top_row, text="Select an item from the table above to view full details.", font=("Segoe UI", 11, "bold"), fg="#1e293b", bg="#ffffff")
        self.lbl_detail_title.pack(side="left")

        self.btn_detail_qr = tk.Button(top_row, text="Generate / View QR Code", font=("Segoe UI", 9, "bold"), bg="#0284c7", fg="#ffffff", command=self._view_selected_qr, padx=10, pady=3, relief="flat", cursor="hand2", state="disabled")
        self.btn_detail_qr.pack(side="right")

        self.txt_detail = tk.Text(self.detail_frame, height=5, font=("Segoe UI", 9), bg="#f8fafc", fg="#1e293b", relief="flat")
        self.txt_detail.pack(fill="both", expand=True)

    def _on_item_selected(self, event):
        selected = self.tree_items.selection()
        if not selected:
            return
        item_id = self.tree_items.item(selected[0])["values"][0]
        item = self.db.get_item(str(item_id))
        if not item:
            return

        self.selected_item = item
        self.btn_detail_qr.config(state="normal")
        self.lbl_detail_title.config(text=f"[{item.item_type}] {item.title}  ({item.id})")

        safe_loc = f"\n• Safe Storage / Custody: {item.safe_storage_location}" if item.safe_storage_location else ""
        details = (
            f"• Category: {item.category}   |   Status: {item.status}   |   Date: {item.date_event}\n"
            f"• Location: {item.location}{safe_loc}\n"
            f"• Description: {item.description}\n"
            f"• Contact: {item.contact_name} ({item.contact_email} | {item.contact_phone})\n"
            f"• Secret Challenge Question: {item.secret_question}"
        )
        self.txt_detail.delete("1.0", "end")
        self.txt_detail.insert("end", details)

    def _view_selected_qr(self):
        if not hasattr(self, "selected_item") or not self.selected_item:
            return
        qr_path = generate_item_qr_image(self.selected_item.id, self.selected_item.title)
        if qr_path and os.path.exists(qr_path):
            messagebox.showinfo("Digital QR Tag Created", f"QR Code generated for {self.selected_item.id}!\nSaved at:\n{os.path.abspath(qr_path)}")
        else:
            messagebox.showinfo("QR Tag Payload", f"QR Identifier:\nSMART_LOST_FOUND://ITEM?id={self.selected_item.id}\n(Install 'qrcode' library for visual PNG)")

    def _refresh_items_table(self):
        for item in self.tree_items.get_children():
            self.tree_items.delete(item)

        item_type = self.combo_type.get()
        item_type = None if item_type == "All Types" else item_type

        category = self.combo_category.get()
        search = self.entry_search.get().strip()

        items = self.db.list_items(item_type=item_type, category=category, search_query=search)

        for it in items:
            self.tree_items.insert("", "end", values=[
                it.id,
                it.item_type,
                it.title,
                it.category,
                it.location,
                it.date_event,
                it.status
            ])
        self.status_var.set(f"Showing {len(items)} items.")

    def _reseed_data(self):
        if messagebox.askyesno("Confirm Reset", "Reset and re-seed sample college items?"):
            seed_sample_campus_data(self.db)
            self._refresh_kpis()
            self._refresh_items_table()
            self.status_var.set("Database re-seeded with realistic campus test data.")

    # -------------------------------------------------------------------------
    # TAB 2: REPORT LOST ITEM
    # -------------------------------------------------------------------------
    def _build_tab_report_lost(self):
        self._build_item_form(self.tab_report_lost, item_type="LOST")

    # -------------------------------------------------------------------------
    # TAB 3: REPORT FOUND ITEM
    # -------------------------------------------------------------------------
    def _build_tab_report_found(self):
        self._build_item_form(self.tab_report_found, item_type="FOUND")

    def _build_item_form(self, parent: ttk.Frame, item_type: str):
        canvas = tk.Canvas(parent, bg="#ffffff", highlightthickness=0)
        scroll_y = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        form_frame = tk.Frame(canvas, bg="#ffffff", padx=25, pady=20)

        form_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=form_frame, anchor="nw")
        canvas.configure(yscrollcommand=scroll_y.set)

        canvas.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        header_text = "Report a Lost Item (Lost Something on Campus?)" if item_type == "LOST" else "Report a Found Item (Found Something on Campus?)"
        color = "#dc2626" if item_type == "LOST" else "#16a34a"

        tk.Label(form_frame, text=header_text, font=("Segoe UI", 13, "bold"), fg=color, bg="#ffffff").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))

        # Title
        tk.Label(form_frame, text="Item Name / Title *:", font=("Segoe UI", 9, "bold"), bg="#ffffff").grid(row=1, column=0, sticky="w", pady=4)
        entry_title = ttk.Entry(form_frame, width=45)
        entry_title.grid(row=1, column=1, sticky="w", pady=4)

        # Category
        tk.Label(form_frame, text="Category *:", font=("Segoe UI", 9, "bold"), bg="#ffffff").grid(row=2, column=0, sticky="w", pady=4)
        combo_cat = ttk.Combobox(form_frame, values=[c.value for c in Category], state="readonly", width=42)
        combo_cat.set(Category.ELECTRONICS.value)
        combo_cat.grid(row=2, column=1, sticky="w", pady=4)

        # Location
        loc_label = "Last Known Location *:" if item_type == "LOST" else "Location Found *:"
        tk.Label(form_frame, text=loc_label, font=("Segoe UI", 9, "bold"), bg="#ffffff").grid(row=3, column=0, sticky="w", pady=4)
        entry_loc = ttk.Entry(form_frame, width=45)
        entry_loc.grid(row=3, column=1, sticky="w", pady=4)

        # Date
        date_label = "Date Lost (YYYY-MM-DD) *:" if item_type == "LOST" else "Date Found (YYYY-MM-DD) *:"
        tk.Label(form_frame, text=date_label, font=("Segoe UI", 9, "bold"), bg="#ffffff").grid(row=4, column=0, sticky="w", pady=4)
        entry_date = ttk.Entry(form_frame, width=45)
        entry_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        entry_date.grid(row=4, column=1, sticky="w", pady=4)

        # Detailed Description
        tk.Label(form_frame, text="Description & Distinguishing Features *:", font=("Segoe UI", 9, "bold"), bg="#ffffff").grid(row=5, column=0, sticky="nw", pady=4)
        txt_desc = tk.Text(form_frame, width=45, height=4, font=("Segoe UI", 9), relief="solid", bd=1)
        txt_desc.grid(row=5, column=1, sticky="w", pady=4)

        # Safe Storage Location (Found items only)
        entry_safe_loc = None
        current_row = 6
        if item_type == "FOUND":
            tk.Label(form_frame, text="Current Safe Custody / Storage Location *:", font=("Segoe UI", 9, "bold"), bg="#ffffff").grid(row=current_row, column=0, sticky="w", pady=4)
            entry_safe_loc = ttk.Entry(form_frame, width=45)
            entry_safe_loc.insert(0, "Security Office / Reception Desk")
            entry_safe_loc.grid(row=current_row, column=1, sticky="w", pady=4)
            current_row += 1

        # Separator: Contact
        tk.Label(form_frame, text="--- Contact Information ---", font=("Segoe UI", 9, "italic"), fg="#64748b", bg="#ffffff").grid(row=current_row, column=0, columnspan=2, sticky="w", pady=(10, 4))
        current_row += 1

        tk.Label(form_frame, text="Your Full Name *:", font=("Segoe UI", 9, "bold"), bg="#ffffff").grid(row=current_row, column=0, sticky="w", pady=4)
        entry_name = ttk.Entry(form_frame, width=45)
        entry_name.grid(row=current_row, column=1, sticky="w", pady=4)
        current_row += 1

        tk.Label(form_frame, text="Your Campus Email *:", font=("Segoe UI", 9, "bold"), bg="#ffffff").grid(row=current_row, column=0, sticky="w", pady=4)
        entry_email = ttk.Entry(form_frame, width=45)
        entry_email.grid(row=current_row, column=1, sticky="w", pady=4)
        current_row += 1

        tk.Label(form_frame, text="Your Phone Number *:", font=("Segoe UI", 9, "bold"), bg="#ffffff").grid(row=current_row, column=0, sticky="w", pady=4)
        entry_phone = ttk.Entry(form_frame, width=45)
        entry_phone.grid(row=current_row, column=1, sticky="w", pady=4)
        current_row += 1

        # Separator: Smart Security Challenge Question
        tk.Label(form_frame, text="--- Smart Ownership Verification Challenge ---", font=("Segoe UI", 9, "italic"), fg="#0284c7", bg="#ffffff").grid(row=current_row, column=0, columnspan=2, sticky="w", pady=(10, 4))
        current_row += 1

        q_help = "Secret question only the real owner can answer (e.g., 'What sticker is on the back?'):"
        tk.Label(form_frame, text=q_help, font=("Segoe UI", 8), fg="#64748b", bg="#ffffff").grid(row=current_row, column=0, columnspan=2, sticky="w")
        current_row += 1

        tk.Label(form_frame, text="Secret Question *:", font=("Segoe UI", 9, "bold"), bg="#ffffff").grid(row=current_row, column=0, sticky="w", pady=4)
        entry_sec_q = ttk.Entry(form_frame, width=45)
        default_q = "What sticker/serial/color detail is unique?" if item_type == "LOST" else "What unique mark or wallpaper does it have?"
        entry_sec_q.insert(0, default_q)
        entry_sec_q.grid(row=current_row, column=1, sticky="w", pady=4)
        current_row += 1

        tk.Label(form_frame, text="Secret Answer (Salted & Hashed) *:", font=("Segoe UI", 9, "bold"), bg="#ffffff").grid(row=current_row, column=0, sticky="w", pady=4)
        entry_sec_a = ttk.Entry(form_frame, width=45, show="*")
        entry_sec_a.grid(row=current_row, column=1, sticky="w", pady=4)
        current_row += 1

        # Submit button
        def on_submit():
            title = entry_title.get().strip()
            category = combo_cat.get()
            location = entry_loc.get().strip()
            date_event = entry_date.get().strip()
            desc = txt_desc.get("1.0", "end").strip()
            name = entry_name.get().strip()
            email = entry_email.get().strip()
            phone = entry_phone.get().strip()
            sec_q = entry_sec_q.get().strip()
            sec_a = entry_sec_a.get().strip()
            safe_loc = entry_safe_loc.get().strip() if entry_safe_loc else ""

            if not (title and location and date_event and desc and name and email and sec_q and sec_a):
                messagebox.showerror("Missing Information", "Please fill in all required fields!")
                return

            new_id = generate_item_id(item_type)
            new_item = Item(
                id=new_id,
                item_type=item_type,
                title=title,
                category=category,
                description=desc,
                location=location,
                date_event=date_event,
                contact_name=name,
                contact_email=email,
                contact_phone=phone,
                secret_question=sec_q,
                secret_answer_hash=hash_secret_answer(sec_a),
                status=ItemStatus.ACTIVE.value,
                safe_storage_location=safe_loc
            )

            self.db.add_item(new_item)
            generate_item_qr_image(new_id, title)

            self._refresh_kpis()
            self._refresh_items_table()

            # Clear inputs
            entry_title.delete(0, "end")
            entry_loc.delete(0, "end")
            txt_desc.delete("1.0", "end")
            entry_name.delete(0, "end")
            entry_email.delete(0, "end")
            entry_phone.delete(0, "end")
            entry_sec_a.delete(0, "end")

            messagebox.showinfo("Report Logged Successfully", f"{item_type} Item logged with ID: {new_id}!\nCheck the Smart Match Radar tab for instant potential matches.")
            self.notebook.select(self.tab_radar)
            self._run_smart_match()

        btn_submit = tk.Button(form_frame, text=f" Submit {item_type} Report ", font=("Segoe UI", 10, "bold"), bg=color, fg="#ffffff", command=on_submit, padx=16, pady=8, relief="flat", cursor="hand2")
        btn_submit.grid(row=current_row, column=1, sticky="w", pady=(15, 20))

    # -------------------------------------------------------------------------
    # TAB 4: SMART MATCH RADAR (AI FEATURE)
    # -------------------------------------------------------------------------
    def _build_tab_radar(self):
        ctrl = tk.Frame(self.tab_radar, bg="#ffffff", pady=10, padx=15)
        ctrl.pack(fill="x")

        btn_match = tk.Button(ctrl, text=" Run Smart Match Algorithm (AI Radar) ", font=("Segoe UI", 10, "bold"), bg="#9333ea", fg="#ffffff", command=self._run_smart_match, padx=14, pady=6, relief="flat", cursor="hand2")
        btn_match.pack(side="left", padx=(0, 15))

        tk.Label(ctrl, text="Min Confidence Threshold:", font=("Segoe UI", 9, "bold"), bg="#ffffff").pack(side="left", padx=(0, 4))
        self.spin_thresh = ttk.Spinbox(ctrl, from_=20, to=85, width=5)
        self.spin_thresh.set(40)
        self.spin_thresh.pack(side="left", padx=(0, 15))

        self.lbl_match_count = tk.Label(ctrl, text="Click to scan active items across the campus.", font=("Segoe UI", 9), bg="#ffffff", fg="#64748b")
        self.lbl_match_count.pack(side="left")

        # Radar Layout: Split Top (Match list) and Bottom (Side-by-side comparison)
        paned = ttk.PanedWindow(self.tab_radar, orient="vertical")
        paned.pack(fill="both", expand=True, padx=15, pady=(0, 12))

        # Top Table: Matches
        top_frame = ttk.Frame(paned)
        paned.add(top_frame, weight=3)

        cols = ["Confidence", "Lost Item", "Found Item", "Category", "Matching Keywords", "Lost Date", "Found Date"]
        self.tree_radar = ttk.Treeview(top_frame, columns=cols, show="headings", selectmode="browse")
        scroll_y = ttk.Scrollbar(top_frame, orient="vertical", command=self.tree_radar.yview)
        self.tree_radar.configure(yscrollcommand=scroll_y.set)

        self.tree_radar.heading("Confidence", text="Match %")
        self.tree_radar.heading("Lost Item", text="Lost Item Title")
        self.tree_radar.heading("Found Item", text="Found Item Title")
        self.tree_radar.heading("Category", text="Category")
        self.tree_radar.heading("Matching Keywords", text="NLP Keywords")
        self.tree_radar.heading("Lost Date", text="Lost Date")
        self.tree_radar.heading("Found Date", text="Found Date")

        self.tree_radar.column("Confidence", width=85, anchor="center")
        self.tree_radar.column("Lost Item", width=220, anchor="w")
        self.tree_radar.column("Found Item", width=220, anchor="w")
        self.tree_radar.column("Category", width=120, anchor="w")
        self.tree_radar.column("Matching Keywords", width=160, anchor="w")
        self.tree_radar.column("Lost Date", width=90, anchor="center")
        self.tree_radar.column("Found Date", width=90, anchor="center")

        self.tree_radar.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")
        self.tree_radar.bind("<<TreeviewSelect>>", self._on_match_selected)

        # Bottom Frame: Side-by-Side Comparison
        self.comp_frame = tk.Frame(paned, bg="#ffffff", padx=15, pady=10, relief="solid", bd=1)
        paned.add(self.comp_frame, weight=2)
        self._build_comparison_view()

    def _build_comparison_view(self):
        for w in self.comp_frame.winfo_children():
            w.destroy()

        top_row = tk.Frame(self.comp_frame, bg="#ffffff")
        top_row.pack(fill="x", side="top", pady=(0, 6))

        self.lbl_comp_title = tk.Label(top_row, text="Select a candidate match pair above to inspect comparison.", font=("Segoe UI", 10, "bold"), fg="#1e293b", bg="#ffffff")
        self.lbl_comp_title.pack(side="left")

        self.btn_claim_pair = tk.Button(top_row, text="  Verify & Claim This Match  ", font=("Segoe UI", 9, "bold"), bg="#16a34a", fg="#ffffff", command=self._start_claim_from_radar, padx=12, pady=4, relief="flat", cursor="hand2", state="disabled")
        self.btn_claim_pair.pack(side="right")

        self.txt_comp = tk.Text(self.comp_frame, height=5, font=("Consolas", 9), bg="#f8fafc", fg="#1e293b", relief="flat")
        self.txt_comp.pack(fill="both", expand=True)

    def _run_smart_match(self):
        lost_items = self.db.list_items(item_type="LOST", status="ACTIVE")
        found_items = self.db.list_items(item_type="FOUND", status="ACTIVE")

        thresh = float(self.spin_thresh.get()) if self.spin_thresh.get().isdigit() else 40.0
        self.current_matches = find_all_matches(lost_items, found_items, min_confidence=thresh)

        for item in self.tree_radar.get_children():
            self.tree_radar.delete(item)

        for m in self.current_matches:
            kw_str = ", ".join(m.matching_keywords) if m.matching_keywords else "-"
            self.tree_radar.insert("", "end", values=[
                f"{m.confidence_score}%",
                f"[{m.lost_item.id}] {m.lost_item.title}",
                f"[{m.found_item.id}] {m.found_item.title}",
                m.lost_item.category,
                kw_str,
                m.lost_item.date_event,
                m.found_item.date_event
            ])

        self.lbl_match_count.config(text=f"Radar Scan: Found {len(self.current_matches)} high-confidence candidate matches!")
        self.status_var.set(f"Smart Match completed: {len(self.current_matches)} matches detected.")

    def _on_match_selected(self, event):
        selected = self.tree_radar.selection()
        if not selected:
            return
        index = self.tree_radar.index(selected[0])
        if index >= len(self.current_matches):
            return

        match = self.current_matches[index]
        self.active_match = match
        self.btn_claim_pair.config(state="normal")
        self.lbl_comp_title.config(text=f"Match Confidence: {match.confidence_score}%   (Text: {match.text_score}% | Cat: {match.category_score}% | Loc: {match.location_score}% | Date: {match.date_score}%)")

        comp_text = (
            f"LOST ITEM  [{match.lost_item.id}]: {match.lost_item.title}\n"
            f"  • Description: {match.lost_item.description}\n"
            f"  • Location   : {match.lost_item.location}   |   Date: {match.lost_item.date_event}\n"
            f"  • Contact    : {match.lost_item.contact_name} ({match.lost_item.contact_email})\n\n"
            f"FOUND ITEM [{match.found_item.id}]: {match.found_item.title}\n"
            f"  • Description: {match.found_item.description}\n"
            f"  • Location   : {match.found_item.location}   |   Date: {match.found_item.date_event}\n"
            f"  • Safe Custody: {match.found_item.safe_storage_location}\n"
        )
        self.txt_comp.delete("1.0", "end")
        self.txt_comp.insert("end", comp_text)

    def _start_claim_from_radar(self):
        if not hasattr(self, "active_match") or not self.active_match:
            return
        self.notebook.select(self.tab_claim)
        self.entry_claim_item_id.delete(0, "end")
        self.entry_claim_item_id.insert(0, self.active_match.found_item.id)
        self._load_claim_challenge()

    # -------------------------------------------------------------------------
    # TAB 5: CLAIM VERIFICATION CHALLENGE
    # -------------------------------------------------------------------------
    def _build_tab_claim(self):
        frame = tk.Frame(self.tab_claim, bg="#ffffff", padx=25, pady=20)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Smart Ownership Verification Challenge", font=("Segoe UI", 13, "bold"), fg="#0f172a", bg="#ffffff").pack(anchor="w", pady=(0, 4))
        tk.Label(frame, text="To prevent false claims, claimants must correctly answer the registered secret security challenge.", font=("Segoe UI", 9), fg="#64748b", bg="#ffffff").pack(anchor="w", pady=(0, 15))

        search_row = tk.Frame(frame, bg="#ffffff")
        search_row.pack(fill="x", pady=6)

        tk.Label(search_row, text="Target Item ID (Lost or Found):", font=("Segoe UI", 9, "bold"), bg="#ffffff").pack(side="left", padx=(0, 6))
        self.entry_claim_item_id = ttk.Entry(search_row, width=22)
        self.entry_claim_item_id.pack(side="left", padx=(0, 8))

        btn_load = tk.Button(search_row, text="Load Challenge", font=("Segoe UI", 9), bg="#0284c7", fg="#ffffff", command=self._load_claim_challenge, padx=10, relief="flat", cursor="hand2")
        btn_load.pack(side="left")

        # Challenge Container Box
        self.box_challenge = tk.Frame(frame, bg="#f8fafc", padx=16, pady=16, relief="solid", bd=1)
        self.box_challenge.pack(fill="both", expand=True, pady=12)

        self.lbl_challenge_item = tk.Label(self.box_challenge, text="No item loaded.", font=("Segoe UI", 10, "bold"), fg="#1e293b", bg="#f8fafc")
        self.lbl_challenge_item.pack(anchor="w", pady=(0, 6))

        self.lbl_sec_question = tk.Label(self.box_challenge, text="", font=("Segoe UI", 10, "italic"), fg="#0369a1", bg="#f8fafc")
        self.lbl_sec_question.pack(anchor="w", pady=(0, 12))

        # Claimant info form
        form_grid = tk.Frame(self.box_challenge, bg="#f8fafc")
        form_grid.pack(fill="x", pady=4)

        tk.Label(form_grid, text="Claimant Name *:", font=("Segoe UI", 9, "bold"), bg="#f8fafc").grid(row=0, column=0, sticky="w", pady=4)
        self.entry_cl_name = ttk.Entry(form_grid, width=35)
        self.entry_cl_name.grid(row=0, column=1, sticky="w", pady=4)

        tk.Label(form_grid, text="Claimant Email *:", font=("Segoe UI", 9, "bold"), bg="#f8fafc").grid(row=1, column=0, sticky="w", pady=4)
        self.entry_cl_email = ttk.Entry(form_grid, width=35)
        self.entry_cl_email.grid(row=1, column=1, sticky="w", pady=4)

        tk.Label(form_grid, text="Claimant Phone *:", font=("Segoe UI", 9, "bold"), bg="#f8fafc").grid(row=2, column=0, sticky="w", pady=4)
        self.entry_cl_phone = ttk.Entry(form_grid, width=35)
        self.entry_cl_phone.grid(row=2, column=1, sticky="w", pady=4)

        tk.Label(form_grid, text="Secret Challenge Answer *:", font=("Segoe UI", 9, "bold"), fg="#dc2626", bg="#f8fafc").grid(row=3, column=0, sticky="w", pady=4)
        self.entry_cl_answer = ttk.Entry(form_grid, width=35, show="*")
        self.entry_cl_answer.grid(row=3, column=1, sticky="w", pady=4)

        self.btn_verify_claim = tk.Button(self.box_challenge, text="  Verify Ownership & Authorize Return  ", font=("Segoe UI", 10, "bold"), bg="#16a34a", fg="#ffffff", command=self._verify_claim, padx=16, pady=8, relief="flat", cursor="hand2", state="disabled")
        self.btn_verify_claim.pack(anchor="w", pady=(15, 6))

        self.lbl_claim_result = tk.Label(self.box_challenge, text="", font=("Segoe UI", 10), bg="#f8fafc")
        self.lbl_claim_result.pack(anchor="w")

    def _load_claim_challenge(self):
        item_id = self.entry_claim_item_id.get().strip()
        item = self.db.get_item(item_id)
        if not item:
            messagebox.showerror("Item Not Found", f"No item registered with ID '{item_id}'!")
            return

        self.target_claim_item = item
        self.lbl_challenge_item.config(text=f"Target: [{item.item_type}] {item.title}  (Current Status: {item.status})")
        self.lbl_sec_question.config(text=f"Verification Question: \"{item.secret_question}\"")
        self.btn_verify_claim.config(state="normal")
        self.lbl_claim_result.config(text="")

    def _verify_claim(self):
        if not hasattr(self, "target_claim_item") or not self.target_claim_item:
            return

        name = self.entry_cl_name.get().strip()
        email = self.entry_cl_email.get().strip()
        phone = self.entry_cl_phone.get().strip()
        answer = self.entry_cl_answer.get().strip()

        if not (name and email and answer):
            messagebox.showerror("Incomplete Form", "Please provide Claimant Name, Email, and Challenge Answer.")
            return

        is_valid = verify_secret_answer(answer, self.target_claim_item.secret_answer_hash)

        # Log claim into SQLite
        self.db.record_claim(
            item_id=self.target_claim_item.id,
            claimant_name=name,
            claimant_email=email,
            claimant_phone=phone,
            answer_attempt=answer,
            is_successful=is_valid
        )

        if is_valid:
            # Mark as RETURNED
            self.db.update_item_status(self.target_claim_item.id, ItemStatus.RETURNED.value)

            # If there's an associated match pair on the radar, mark that one returned too!
            if hasattr(self, "active_match") and self.active_match:
                if self.active_match.lost_item.id == self.target_claim_item.id:
                    self.db.update_item_status(self.active_match.found_item.id, ItemStatus.RETURNED.value)
                elif self.active_match.found_item.id == self.target_claim_item.id:
                    self.db.update_item_status(self.active_match.lost_item.id, ItemStatus.RETURNED.value)

            self._refresh_kpis()
            self._refresh_items_table()

            retrieval_info = f"\nPickup Custody Location: {self.target_claim_item.safe_storage_location}" if self.target_claim_item.safe_storage_location else ""
            msg = f"SUCCESS! Ownership Verified.\n\nItem '{self.target_claim_item.title}' has been marked as RETURNED.{retrieval_info}\nOwner Contact: {self.target_claim_item.contact_name} ({self.target_claim_item.contact_phone})"
            self.lbl_claim_result.config(text="✓ Ownership verified successfully! Item marked RETURNED.", fg="#16a34a", font=("Segoe UI", 10, "bold"))
            messagebox.showinfo("Claim Authorized", msg)
        else:
            self.lbl_claim_result.config(text="✗ Incorrect answer! Claim attempt rejected and logged.", fg="#dc2626", font=("Segoe UI", 10, "bold"))
            messagebox.showerror("Verification Failed", "Incorrect answer to secret challenge question.\nUnauthorized claim attempt logged.")


def launch_app():
    root = tk.Tk()
    app = SmartLostFoundApp(root)
    root.mainloop()


if __name__ == "__main__":
    launch_app()
