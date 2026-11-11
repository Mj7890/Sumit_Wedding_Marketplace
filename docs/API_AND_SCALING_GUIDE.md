# API Specification, Database Scaling & Code Quality Guide
**System Name:** Arts By Graphic (Vows & Blooms) — Wedding Card Marketplace  
**Document Type:** API Contracts, Scaling Strategy, Refactoring & Code Quality Audit  
**Location:** `wedding_marketplace/wedding_marketplace/docs/API_AND_SCALING_GUIDE.md`  

---

## 1. REST & Internal API Specifications

### 1.1 Navigational Search Autocomplete API

#### Endpoint: `GET /search-suggestions/`
Returns matching active cards for the navbar live autocomplete dropdown.

- **Request Headers:**
  - `Accept: application/json`
- **Query Parameters:**
  | Parameter | Type | Required | Description | Constraints |
  | :--- | :--- | :--- | :--- | :--- |
  | `q` | `string` | Yes | Search term | Triggers if `len(q) >= 2`. Stripped of leading/trailing whitespace. |

- **Response:**
  - **Status Code:** `200 OK`
  - **Content-Type:** `application/json`
  - **Response Payload Schema:**
    ```json
    {
      "results": [
        {
          "name": "Sacred Ganesh",
          "slug": "sacred-ganesh",
          "ornament": "🕉",
          "price": "1499.00",
          "category": "Hindu",
          "palette": "gold"
        }
      ]
    }
    ```
  - **Behavior when `len(q) < 2` or empty:**
    ```json
    {
      "results": []
    }
    ```

---

### 1.2 Dedicated Card Search API (Alternate with Image Thumbnail)

#### Endpoint: `GET /api/search/` (aliased to `search_api`)
- **Query Parameters:**
  | Parameter | Type | Required | Description |
  | :--- | :--- | :--- | :--- |
  | `q` | `string` | Yes | Search query |

- **Response Payload:**
  ```json
  {
    "results": [
      {
        "id": 1,
        "name": "Sacred Ganesh",
        "slug": "sacred-ganesh",
        "ornament": "🕉",
        "palette": "gold",
        "price": "1499.00",
        "category": "Hindu",
        "image": "/media/card_images/sacred_ganesh.jpg"
      }
    ]
  }
  ```

---

### 1.3 External Integration: Mailbuster Transactional Email API

#### Target Endpoint: `POST https://api.mailbuster.io/api/send-email`
- **Payload Contract:**
  ```json
  {
    "api_key": "<MAILBUSTER_API_KEY>",
    "to": "user@example.com",
    "from_email": "noreply@artsbygraphic.com",
    "from_name": "Arts By Graphic",
    "subject": "Your Verification Code — Arts By Graphic",
    "html_body": "<div>...styled OTP box...</div>",
    "text_body": "Your Arts By Graphic verification code is: 123456\nValid for 10 minutes."
  }
  ```
- **Error Handling Strategy:**
  - Network timeout set to `10` seconds.
  - Failures caught in `try...except requests.exceptions.RequestException`.
  - Console fallback: Prints OTP code directly to server log so local testing and registration is never blocked even without internet or API credentials.

---

## 2. Database Indexing & Performance Optimization

### 2.1 Current State Analysis
Currently, the application runs on **SQLite 3** (`db.sqlite3`). Django automatically creates primary key indices (`id`) and unique constraints (`slug` on `WeddingCard` and `Category`, `email` on `EmailOTP`).

### 2.2 Recommended Composite Indexes
To scale the marketplace to tens of thousands of cards and high concurrent order traffic, add explicit database indexes via `Meta.indexes` in `cards/models.py`:

```python
# In WeddingCard.Meta:
indexes = [
    models.Index(fields=['is_active', '-is_featured', '-created_at'], name='active_featured_idx'),
    models.Index(fields=['category', 'is_active'], name='category_active_idx'),
    models.Index(fields=['palette', 'is_active'], name='palette_active_idx'),
    models.Index(fields=['price'], name='price_idx'),
]

# In Order.Meta:
indexes = [
    models.Index(fields=['user', '-created_at'], name='user_orders_idx'),
    models.Index(fields=['status'], name='order_status_idx'),
]

# In PrinterCardOrder.Meta:
indexes = [
    models.Index(fields=['user', '-created_at'], name='user_print_orders_idx'),
    models.Index(fields=['card_type', 'status'], name='print_type_status_idx'),
]
```

### 2.3 Migration to Production PostgreSQL
To transition from SQLite to enterprise PostgreSQL:

1. Install psycopg adapter:
   ```bash
   pip install psycopg2-binary
   ```
2. Configure `settings.py`:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': os.environ.get('DB_NAME', 'wedding_db'),
           'USER': os.environ.get('DB_USER', 'postgres'),
           'PASSWORD': os.environ.get('DB_PASSWORD', 'secret'),
           'HOST': os.environ.get('DB_HOST', 'localhost'),
           'PORT': os.environ.get('DB_PORT', '5432'),
           'CONN_MAX_AGE': 600,  # Persistent database connections
       }
   }
   ```
3. Run migrations:
   ```bash
   python manage.py migrate
   python manage.py seed_cards
   ```

---

## 3. Code Quality & Architectural Refactoring Audit

During a static code analysis of `wedding_marketplace/wedding_marketplace/cards/views.py`, the following architectural observations and optimization opportunities were identified:

### 3.1 Duplicate View Definitions in `views.py`
- **Observation:** `contact` is defined twice:
  - Line 634: `def contact(request):` (sends email to `DEFAULT_FROM_EMAIL` using `django.core.mail.send_mail`).
  - Line 678: `def contact(request):` (only prints to console `print(f"[CONTACT] {name}...")`).
  - *Effect:* The second declaration at line 678 unintentionally overwrites the email-sending version at line 634.
- **Recommendation:** Consolidate `contact` into a single, clean view function combining DB logging with transactional email dispatch.

- **Observation:** `about` is defined twice:
  - Line 630: `def about_us(request):`
  - Line 674: `def about(request):`
  - *Recommendation:* Remove the redundant `about_us` alias or redirect it cleanly.

### 3.2 Atomic Database Transactions in Checkout
- **Observation:** In `views.py:checkout`, `Order.objects.create`, `OrderItem.objects.create`, and `items.delete()` run as independent queries without a database transaction block. If an exception occurs halfway through creating order items, a dangling order without items could be created while cart items remain.
- **Recommendation:** Wrap checkout operations in `django.db.transaction.atomic`:
  ```python
  from django.db import transaction

  @login_required
  def checkout(request):
      # ...
      if request.method == 'POST':
          with transaction.atomic():
              order = Order.objects.create(user=request.user, total=total, status='confirmed')
              for item in items:
                  OrderItem.objects.create(
                      order=order,
                      card=item.card,
                      customization=item.customization,
                      quantity=item.quantity,
                      price=item.card.price,
                  )
              items.delete()
          messages.success(request, f'Order #{order.pk} placed successfully! 🎉')
          return redirect('order_detail', pk=order.pk)
  ```

### 3.3 Rate Limiting on OTP Endpoints
- **Observation:** An automated script could flood `register_step1` or `resend_otp`, depleting transactional email quotas.
- **Recommendation:** Introduce a throttling cooldown:
  ```python
  # Check if an OTP was generated within the last 60 seconds for this email
  last_otp = EmailOTP.objects.filter(email=email).first()
  if last_otp and (timezone.now() - last_otp.created_at).total_seconds() < 60:
      messages.warning(request, 'Please wait 60 seconds before requesting another code.')
      return redirect('register_step2')
  ```

---

## 4. Production Readiness Checklist

- [x] Static files compressed with hash manifests (`WhiteNoise`).
- [x] Security headers and CSRF trusted origins configured.
- [x] Minimum commercial quantity (100 cards) enforced on backend.
- [x] Fail-safe OTP console logging when third-party mailer is offline.
- [ ] Migrate database from SQLite to PostgreSQL for high write concurrency.
- [ ] Implement Redis cache for hot catalog queries (`featured_cards`, `categories`).
- [ ] Implement atomic checkout transaction wrapper.
- [ ] Setup scheduled Celery or cron job to purge expired `EmailOTP` records (`EmailOTP.objects.filter(expires_at__lt=timezone.now()).delete()`).

