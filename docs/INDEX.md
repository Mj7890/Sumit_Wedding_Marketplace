# Arts By Graphic — Technical Documentation Hub
**Project:** Wedding Card Marketplace & Dhananjay Printer Order System  
**Framework:** Django 4.2+ (Python 3.8+)  
**Location:** `wedding_marketplace/wedding_marketplace`  

---

## Documentation Navigation

This documentation suite provides a complete end-to-end architectural and design blueprint for the existing codebase:

| Document | Description | Key Focus Areas |
| :--- | :--- | :--- |
| **[1. System Architecture](ARCHITECTURE.md)** | Top-level system architecture, tiers, and topologies. | Monolithic MVT paradigm, C4 container views, component interactions, deployment topology, technology stack. |
| **[2. High-Level Design (HLD)](HLD.md)** | High-level functional specifications and user journeys. | Business model, dual marketplace & print shop modules, persona matrix, end-to-end sequence diagrams, NFRs, route directory. |
| **[3. Low-Level Design (LLD)](LLD.md)** | Technical implementations, database schema, and view algorithms. | Complete Mermaid ER diagram, data dictionary for all 9 models, form classes, business logic algorithms, 3-step OTP state machine. |
| **[4. Data Flow & Security (DFD)](DATA_FLOW_AND_SECURITY.md)** | Process decompositions and threat modeling. | DFD Levels 0, 1, and 2, STRIDE threat model, authorization boundaries, CSRF/XSS defenses. |
| **[5. API & Scaling Guide](API_AND_SCALING_GUIDE.md)** | Interface contracts and production readiness. | Live autocomplete API specification, Mailbuster contract, database indexing, PostgreSQL migration, code quality audit. |

---

## Project Structure Overview

```
wedding_marketplace/
└── wedding_marketplace/
    ├── manage.py
    ├── requirements.txt
    ├── README.md
    ├── db.sqlite3
    ├── docs/                                  <-- Full Documentation Suite
    │   ├── INDEX.md
    │   ├── ARCHITECTURE.md
    │   ├── HLD.md
    │   ├── LLD.md
    │   ├── DATA_FLOW_AND_SECURITY.md
    │   └── API_AND_SCALING_GUIDE.md
    ├── wedding_marketplace/                   <-- Project Configuration
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    ├── cards/                                 <-- Main Core Application
    │   ├── admin.py
    │   ├── context_processors.py
    │   ├── forms.py
    │   ├── models.py
    │   ├── urls.py
    │   ├── views.py
    │   ├── management/commands/seed_cards.py
    │   └── migrations/
    ├── static/                                <-- Static Assets (Logo, CSS, JS)
    ├── media/                                 <-- Dynamic Uploads (card_images/)
    └── templates/                             <-- Jinja / DTL HTML Templates
        ├── base.html
        ├── cards/
        └── registration/
```

