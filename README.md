# 🔍 Smart Lost & Found Campus Intelligence System

> **Academic College Mini-Project Edition**  
> Developed in **Python 3.10+** utilizing **SQLite3, Tkinter GUI, NLP Matchmaking, Cryptographic Hashing & QR Generation**.

---

## 📌 1. Project Abstract & Motivation
Traditional college lost-and-found systems suffer from fragmented communication (WhatsApp groups, notice boards, social media posts) where owners rarely find what they lost, and finders have no streamlined way to safely return items. Furthermore, traditional systems face security vulnerabilities where fraudulent claimants falsely claim valuable items (laptops, AirPods, watches) without verification.

This **Smart Lost & Found Campus Intelligence System** provides a centralized, secure, and intelligent platform with four core innovations:
1. **AI-Assisted Multi-Factor Matchmaking**: Automatically correlates newly reported lost items with found items using Natural Language Processing (NLP), category compatibility, campus spatial text matching, and temporal proximity decay.
2. **Smart Ownership Verification Challenge**: Prevents fraudulent claims by challenging claimants with a secret security question (e.g. unique wallpaper, engraving, hidden mark) validated via salted SHA-256 cryptographic hashes before releasing custody.
3. **Digital QR Code Tagging**: Generates unique QR tags for physical items that encode verification lookups.
4. **Dual Interface**: Modern tabbed **Desktop GUI (Tkinter)** for regular students/staff, and a **Command-Line Interface (CLI)** for system administrators.

---

## 🚀 2. System Architecture & Workflow

```
[Student Reports Lost Item]               [Student Reports Found Item]
         │                                            │
         ▼                                            ▼
 ┌───────────────┐                             ┌───────────────┐
 │ Set Secret    │                             │ Safe Custody  │
 │ Challenge Q&A │                             │ Location Info │
 └───────┬───────┘                             └───────┬───────┘
         │                                            │
         └─────────────► ┌───────────────────┐ ◄──────┘
                         │ SQLite Persistent │
                         │ Database Storage  │
                         └─────────┬─────────┘
                                   │
                                   ▼
                   ┌───────────────────────────────┐
                   │    AI Smart Match Radar       │
                   │ (NLP + Category + Spatial +   │
                   │      Temporal Proximity)      │
                   └───────────────┬───────────────┘
                                   │
                    High-Confidence Candidate Match
                                   │
                                   ▼
                   ┌───────────────────────────────┐
                   │  Secret Challenge Validation  │
                   │   (Salted SHA-256 Checking)   │
                   └───────────────┬───────────────┘
                        ┌──────────┴──────────┐
                   Valid Answer         Wrong Answer
                        │                     │
                        ▼                     ▼
               ┌─────────────────┐   ┌─────────────────┐
               │ Status Updated: │   │ Claim Logged As │
               │    RETURNED     │   │ FAILED / REJECT │
               └─────────────────┘   └─────────────────┘
```

---

## 🧠 3. Smart Matchmaking Algorithm & Weight Distribution

When scanning for potential matches between a Lost item $L$ and a Found item $F$, the system computes an overall confidence percentage ($0\%$ to $100\%$):

$$\text{Confidence Score} = (0.40 \times S_{\text{Text}}) + (0.25 \times S_{\text{Category}}) + (0.20 \times S_{\text{Location}}) + (0.15 \times S_{\text{Temporal}})$$

### Metric Breakdown:
1. **$S_{\text{Text}}$ — NLP Description Similarity (Weight: 40%)**:
   - Tokenizes title and description, removes English stop-words, and calculates a weighted Jaccard similarity index.
   - Distinctive hardware brands, colors, and object keywords (e.g., `Apple`, `AirPods`, `Black`, `Casio`, `Wildcraft`) are assigned $3\times$ higher weighting than generic terms.
2. **$S_{\text{Category}}$ — Category Compatibility (Weight: 25%)**:
   - Exact category match = $100\%$. Incompatible category pairs (e.g., `Clothing` vs. `ID Documents`) penalize the score heavily.
3. **$S_{\text{Location}}$ — Spatial Location Overlap (Weight: 20%)**:
   - Compares campus building and room identifiers (e.g., `Central Library 2nd Floor` vs. `Library Reading Room`).
4. **$S_{\text{Temporal}}$ — Temporal Proximity Decay (Weight: 15%)**:
   - Items found within $0$ to $5$ days of being lost receive $100\%$. Beyond $14$ days, the temporal score gradually decays. Items found before the reported lost date receive an error penalty.

---

## 🔒 4. Secret Claim Verification Security
To prevent impostors from claiming valuable items:
- During reporting, the owner or finder specifies a secret challenge question known only to the real owner (e.g., *"What sticker is on the charging case?"* or *"What is the student roll number on the card?"*).
- The secret answer is normalized (lowercase, punctuation stripped, whitespace collapsed) and stored as a **Salted SHA-256 Cryptographic Hash**:
  $$\text{Hash} = \text{SHA256}(\text{Salt} + \text{NormalizedAnswer} + \text{Salt})$$
- When an ownership claim is initiated, the candidate answer is hashed and checked against the stored hash in $O(1)$ time without ever storing the plaintext answer in the database!

---

## 💻 5. Installation & Execution

### Prerequisites
- Python 3.10 or newer
- Core Dependencies:
```bash
pip install qrcode pillow
```

### Running the System

#### 1. Launch Interactive Desktop GUI (Recommended)
```bash
python main.py
```
*(Or run `python app_gui.py`)*

#### 2. Run via Command-Line Interface (CLI)
- **Scan Smart Match Radar**:
  ```bash
  python cli.py --scan
  ```
- **View Campus Recovery Analytics & KPIs**:
  ```bash
  python cli.py --stats
  ```
- **List All Registered Items**:
  ```bash
  python cli.py --list
  ```
- **Verify Ownership Challenge via CLI**:
  ```bash
  python cli.py --verify <ITEM_ID> "<SECRET_ANSWER>"
  ```
- **Generate Digital QR Tag**:
  ```bash
  python cli.py --qr <ITEM_ID>
  ```
- **Reset & Re-seed Realistic Test Campus Items**:
  ```bash
  python cli.py --seed
  ```

#### 3. Run Automated Unit Test Suite
```bash
python -m unittest -v tests/test_system.py
```

---

## 📁 6. Project File Structure
```
d:/mini_project/
├── main.py                    # Universal launcher (starts Desktop GUI or CLI)
├── app_gui.py                 # Modern Tkinter Graphical User Interface
├── cli.py                     # Command-line interface with radar scanning & verification
├── database.py                # SQLite persistent database layer & analytics
├── matcher.py                 # Smart NLP multi-factor matching engine
├── models.py                  # Data classes, enums, and schema definitions
├── security.py                # Salted SHA-256 hashing and claim challenge logic
├── qr_service.py              # High-resolution PNG QR tag generator
├── sample_data.py             # Realistic campus dataset seeder with cross-matched pairs
├── test.py                    # Health-check validation script
├── requirements.txt           # Package dependencies
├── smart_lost_found.db        # SQLite database file
├── qr_codes/                  # Generated QR code image directory
├── tests/
│   └── test_system.py         # Automated unit test suite
└── README.md                  # Comprehensive academic documentation
```

---

## 🎓 7. College Viva-Voce / Oral Exam Q&A Preparation

**Q1: What makes this system "Smart" compared to a standard CRUD application?**  
*Answer:* Standard systems only allow keyword lookups. This system includes an **AI Matchmaking Radar** that automatically scans lost and found records across 4 dimensions (NLP text semantics, category compatibility, spatial location overlap, and time decay) to compute a confidence percentage and proactively notify users.

**Q2: How does the system prevent unauthorized or fraudulent claims?**  
*Answer:* By implementing a **Secret Verification Challenge**. Plaintext answers are never stored; instead, they are hashed using a salted SHA-256 algorithm. When someone claims an item, they must answer the challenge correctly to unlock owner contact information and authorize physical retrieval.

**Q3: Why was SQLite chosen as the database backend?**  
*Answer:* SQLite is serverless, self-contained, transactional (ACID-compliant), zero-configuration, and integrated directly into Python's standard library. It requires no database server installations, making it ideal for campus kiosks and desktop deployments.

**Q4: How does the Jaccard similarity handle stop-words and distinctive tokens?**  
*Answer:* Generic English stop-words (*the, is, at, in*) are stripped during tokenization. Distinctive tokens representing brands (*Apple, Casio, Dell*), colors (*Black, Navy, Silver*), and item types (*AirPods, Calculator*) are assigned $3\times$ higher weighting so that critical identifiers drive the matching score.
