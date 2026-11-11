# Vows & Blooms — Wedding Card Marketplace
## + Dhananjay Printer Card Form (Bride & Groom)

Full Django wedding card marketplace with 3D carousel, live customization, cart, checkout, AND an integrated Dhananjay Printer card order form.

## Documentation

Comprehensive design specifications and architectural blueprints:
- [System Architecture](docs/ARCHITECTURE.md) — Monolith MVT topology, component layers, deployment, and technology stack.
- [High-Level Design (HLD)](docs/HLD.md) — System scope, functional modules, persona journeys, non-functional requirements, and route map.
- [Low-Level Design (LLD)](docs/LLD.md) — Complete database ER schema, model data dictionary, forms, view algorithms, and sequence diagrams.

## Quick Setup

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_cards
python manage.py createsuperuser
python manage.py runserver
```

Visit http://127.0.0.1:8000

## Key URLs

| URL | Description |
|-----|-------------|
| `/` | Homepage with 3D carousel + printer card promo |
| `/marketplace/` | Browse & filter wedding cards |
| `/card/<slug>/` | Card detail + live preview |
| `/card/<slug>/customize/` | Full customizer → cart |
| `/cart/` | Cart |
| `/checkout/` | Checkout |
| `/orders/` | My marketplace orders |
| `/printer-card/` | Bride or Groom card form (Dhananjay Printer) |
| `/printer-card/success/<pk>/` | Order confirmation + print |
| `/printer-card/my-orders/` | My print orders |
| `/admin/` | Admin panel |

## Models

- WeddingCard, Category, Customization, CartItem, Order, OrderItem, Review
- **PrinterCardOrder** — stores bride/groom printer card form submissions

## Printer Card Form Features

- Toggle between Bride and Groom form
- Bride form: ladki ka naam, pita, dada, pata, sagaai, shaadi, vivah sthal
- Groom form: ladke ka naam, pita, dada, pata, sagaai, shaadi, ghudchadi, barat, reception
- Submit saves to DB; confirmation page shows filled card + print button
- Admin can update status: Pending → Confirmed → Printed → Delivered

## Requirements

- Python 3.8+
- Django 4.2+
- Pillow
