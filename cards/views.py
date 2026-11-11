from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db.models import Q
from .models import WeddingCard, Category, Review, Customization, CartItem, Order, OrderItem, PrinterCardOrder, EmailOTP
from .forms import CustomizationForm, ReviewForm, UserRegistrationForm, PrinterCardOrderForm


def home(request):
    # All active cards ordered by featured first, then newest
    all_cards = list(WeddingCard.objects.filter(is_active=True)
                     .select_related('category')
                     .order_by('-is_featured', '-created_at'))

    # Carousel: up to 10 cards (featured first)
    carousel_cards = all_cards[:10]

    # Grid: up to 12 cards
    grid_cards = all_cards[:12]

    categories = Category.objects.all()
    return render(request, 'cards/home.html', {
        'featured_cards': grid_cards,
        'carousel_cards': carousel_cards,
        'categories': categories,
        'total_cards': len(all_cards),
    })


def marketplace(request):
    cards = WeddingCard.objects.filter(is_active=True)
    category_slug = request.GET.get('category')
    palette = request.GET.get('palette')
    search = request.GET.get('q')
    sort = request.GET.get('sort', 'newest')

    if category_slug:
        cards = cards.filter(category__slug=category_slug)
    if palette:
        cards = cards.filter(palette=palette)
    if search:
        cards = cards.filter(Q(name__icontains=search) | Q(description__icontains=search))

    if sort == 'price_asc':
        cards = cards.order_by('price')
    elif sort == 'price_desc':
        cards = cards.order_by('-price')
    elif sort == 'popular':
        cards = cards.order_by('-reviews__rating')
    else:
        cards = cards.order_by('-created_at')

    categories = Category.objects.all()
    palettes = WeddingCard.PALETTE_CHOICES

    return render(request, 'cards/marketplace.html', {
        'cards': cards,
        'categories': categories,
        'palettes': palettes,
        'selected_category': category_slug,
        'selected_palette': palette,
        'search': search,
        'sort': sort,
    })


def card_detail(request, slug):
    card = get_object_or_404(WeddingCard, slug=slug, is_active=True)
    reviews = card.reviews.all().order_by('-created_at')
    review_form = ReviewForm()
    customization_form = CustomizationForm(initial={
        'palette': card.palette,
        'ornament': card.ornament,
    })

    if request.method == 'POST' and request.user.is_authenticated:
        if 'review_submit' in request.POST:
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.card = card
                review.user = request.user
                review.save()
                messages.success(request, 'Review submitted!')
                return redirect('card_detail', slug=slug)

    return render(request, 'cards/card_detail.html', {
        'card': card,
        'reviews': reviews,
        'review_form': review_form,
        'customization_form': customization_form,
    })


@login_required
def customize_card(request, slug):
    card = get_object_or_404(WeddingCard, slug=slug, is_active=True)

    if request.method == 'POST':
        form = CustomizationForm(request.POST)
        if form.is_valid():
            custom = form.save(commit=False)
            custom.user = request.user
            custom.card = card
            custom.save()
            # Add to cart
            qty = int(request.POST.get('quantity', 100))
            if qty < 100:
                qty = 100
            cart_item, created = CartItem.objects.get_or_create(
                user=request.user,
                card=card,
                customization=custom,
                defaults={'quantity': qty}
            )
            if not created:
                cart_item.quantity = qty
                cart_item.save()
            messages.success(request, f'"{card.name}" added to cart — {qty} cards!')
            return redirect('cart')
    else:
        form = CustomizationForm(initial={'palette': card.palette, 'ornament': card.ornament})

    return render(request, 'cards/customize.html', {'card': card, 'form': form, 'preset_qtys': [100, 150, 200, 250, 300, 500]})


@login_required
def cart(request):
    # Handle quantity update
    if request.method == 'POST' and request.POST.get('action') == 'update_qty':
        item_id = request.POST.get('item_id')
        new_qty = int(request.POST.get('quantity', 100))
        if new_qty < 100:
            messages.error(request, 'Minimum order quantity is 100 cards.')
            new_qty = 100
        item = get_object_or_404(CartItem, id=item_id, user=request.user)
        item.quantity = new_qty
        item.save()
        return redirect('cart')

    items = CartItem.objects.filter(user=request.user).select_related('card', 'customization')
    total = sum(item.subtotal for item in items)
    return render(request, 'cards/cart.html', {
        'items': items,
        'total': total,
        'min_qty': 100,
    })


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.delete()
    messages.success(request, 'Item removed from cart.')
    return redirect('cart')


@login_required
def checkout(request):
    items = CartItem.objects.filter(user=request.user).select_related('card', 'customization')
    if not items.exists():
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart')

    # Enforce minimum 100 per item
    for item in items:
        if item.quantity < 100:
            item.quantity = 100
            item.save()

    total = sum(item.subtotal for item in items)

    if request.method == 'POST':
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

    return render(request, 'cards/checkout.html', {'items': items, 'total': total})


@login_required
def orders(request):
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'cards/orders.html', {'orders': user_orders})


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, 'cards/order_detail.html', {'order': order})


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.username}! Your account is ready.')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


def printer_card_form(request):
    """Dhananjay Printer card order form — bride or groom selection."""
    card_type = request.GET.get('type', 'bride')
    if card_type not in ('bride', 'groom'):
        card_type = 'bride'

    if request.method == 'POST':
        form = PrinterCardOrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.save()
            messages.success(request, 'आपका कार्ड ऑर्डर सफलतापूर्वक सबमिट हो गया! (Order submitted successfully!)')
            return redirect('printer_card_success', pk=order.pk)
        else:
            card_type = request.POST.get('card_type', card_type)
    else:
        form = PrinterCardOrderForm(initial={'card_type': card_type})

    return render(request, 'cards/printer_card_form.html', {
        'form': form,
        'card_type': card_type,
    })


def printer_card_success(request, pk):
    """Confirmation page after printer card order is submitted."""
    order = get_object_or_404(PrinterCardOrder, pk=pk)
    # Only allow owner or staff to see
    if order.user and order.user != request.user and not request.user.is_staff:
        return redirect('printer_card_form')
    return render(request, 'cards/printer_card_success.html', {'order': order})


@login_required
def my_printer_orders(request):
    """List all printer card orders for the logged-in user."""
    orders = PrinterCardOrder.objects.filter(user=request.user)
    return render(request, 'cards/printer_card_orders.html', {'orders': orders})


# ── EMAIL OTP REGISTRATION ──────────────────────────────────────────────────

def send_otp_email(email, otp_code):
    """
    Send OTP via Mailbuster API (free tier).
    Falls back to console print if API key not configured.
    """
    import requests
    from django.conf import settings as _s

    # Always print to console for debugging
    print(f"\n{'='*50}")
    print(f"  OTP for {email}: {otp_code}")
    print(f"{'='*50}\n")

    api_key = getattr(_s, 'MAILBUSTER_API_KEY', None)

    if not api_key:
        # Fallback: use Django's email backend (console in dev)
        from django.core.mail import send_mail
        subject = 'Your Arts By Graphic Verification Code'
        body = (
            f"Welcome to Arts By Graphic!\n\n"
            f"Your verification code is: {otp_code}\n\n"
            f"Valid for 10 minutes. Do not share this code.\n\n"
            f"— Arts By Graphic Team"
        )
        send_mail(subject, body, _s.DEFAULT_FROM_EMAIL, [email], fail_silently=True)
        return

    # ── Mailbuster API ──────────────────────────────────────
    html_body = f"""
    <div style="font-family:Arial,sans-serif;max-width:500px;margin:0 auto;padding:30px;background:#faf6f0;border-radius:8px;">
      <div style="text-align:center;margin-bottom:20px;">
        <h2 style="color:#3b2a2a;font-size:24px;margin:0;">Arts By Graphic</h2>
        <p style="color:#b8935a;font-size:13px;letter-spacing:2px;text-transform:uppercase;">Email Verification</p>
      </div>
      <p style="color:#4a3728;font-size:15px;">Hello,</p>
      <p style="color:#4a3728;font-size:15px;">Your verification code is:</p>
      <div style="background:#1a0a28;border-radius:10px;padding:24px;text-align:center;margin:24px 0;">
        <span style="font-size:42px;font-weight:bold;letter-spacing:12px;color:#f0d080;font-family:monospace;">
          {otp_code}
        </span>
      </div>
      <p style="color:#666;font-size:13px;">This code expires in <strong>10 minutes</strong>.</p>
      <p style="color:#666;font-size:13px;">If you didn't request this, please ignore this email.</p>
      <hr style="border:none;border-top:1px solid #e8e0d8;margin:20px 0;">
      <p style="color:#aaa;font-size:12px;text-align:center;">
        © Arts By Graphic · Loni, Ghaziabad
      </p>
    </div>
    """

    payload = {{
        "api_key":    api_key,
        "to":         email,
        "from_email": getattr(_s, 'MAILBUSTER_FROM_EMAIL', 'noreply@artsbygraphic.com'),
        "from_name":  getattr(_s, 'MAILBUSTER_FROM_NAME',  'Arts By Graphic'),
        "subject":    "Your Verification Code — Arts By Graphic",
        "html_body":  html_body,
        "text_body":  f"Your Arts By Graphic verification code is: {otp_code}\nValid for 10 minutes.",
    }}

    try:
        resp = requests.post(
            "https://api.mailbuster.io/api/send-email",
            json=payload,
            timeout=10,
        )
        resp.raise_for_status()
        print(f"  [Mailbuster] Email sent successfully to {email}")
    except requests.exceptions.RequestException as e:
        print(f"  [Mailbuster] ERROR sending email: {e}")
        # Don't raise — OTP is still valid, user can see it in console


def register_step1(request):
    """Step 1 — collect email & send OTP."""
    from .models import EmailOTP
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        if not email:
            return render(request, 'registration/register_step1.html', {'error': 'Please enter a valid email.'})
        # Check if email already registered
        from django.contrib.auth.models import User
        if User.objects.filter(email=email).exists():
            return render(request, 'registration/register_step1.html',
                          {'error': 'This email is already registered. Please login.'})
        otp_code = EmailOTP.generate_otp(email)
        try:
            send_otp_email(email, otp_code)
        except Exception:
            pass  # In dev mode, email prints to console — never block registration
        request.session['pending_email'] = email
        messages.info(request, f'A 6-digit OTP has been sent to {email}. Please check your inbox (and spam folder).')
        return redirect('register_step2')
    return render(request, 'registration/register_step1.html')


def register_step2(request):
    """Step 2 — verify OTP."""
    from .models import EmailOTP
    email = request.session.get('pending_email')
    if not email:
        return redirect('register_step1')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp', '').strip()
        try:
            record = EmailOTP.objects.get(email=email)
            if record.is_expired():
                messages.error(request, 'OTP has expired. Please request a new one.')
                return redirect('register_step1')
            if record.otp != entered_otp:
                return render(request, 'registration/register_step2.html',
                              {'email': email, 'error': 'Incorrect OTP. Please try again.'})
            record.is_verified = True
            record.save()
            request.session['otp_verified_email'] = email
            return redirect('register_step3')
        except EmailOTP.DoesNotExist:
            messages.error(request, 'OTP record not found. Please start again.')
            return redirect('register_step1')

    return render(request, 'registration/register_step2.html', {'email': email})


def resend_otp(request):
    """Resend OTP to the pending email."""
    from .models import EmailOTP
    email = request.session.get('pending_email')
    if email:
        otp_code = EmailOTP.generate_otp(email)
        try:
            send_otp_email(email, otp_code)
        except Exception:
            pass
        messages.success(request, f'New OTP sent to {email}.')
    return redirect('register_step2')


def register_step3(request):
    """Step 3 — set username & password, create account."""
    from .forms import UserRegistrationForm

    email = request.session.get('otp_verified_email')
    if not email:
        messages.error(request, 'Session expired. Please start registration again.')
        return redirect('register_step1')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Save user — UserCreationForm.save() hashes the password automatically
            user = form.save(commit=False)
            user.email      = email
            user.is_active  = True
            user.save()

            # Clean up
            from .models import EmailOTP
            EmailOTP.objects.filter(email=email).delete()
            request.session.pop('pending_email', None)
            request.session.pop('otp_verified_email', None)
            # Log in immediately using the raw password from cleaned_data
            raw_pw    = form.cleaned_data['password1']
            from django.contrib.auth import authenticate as _auth
            auth_user = _auth(request, username=user.username, password=raw_pw)
            login(request, auth_user if auth_user else user)

            messages.success(request, f'🎉 Welcome, {user.username}! Your account is ready.')
            return redirect('home')
        # form invalid — fall through to render with errors shown
    else:
        form = UserRegistrationForm()

    return render(request, 'registration/register_step3.html', {
        'form':  form,
        'email': email,
    })


# ── DASHBOARD ──────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    from django.db.models import Sum, Count
    user = request.user

    # Stats
    total_orders    = Order.objects.filter(user=user).count()
    total_spent     = Order.objects.filter(user=user).aggregate(t=Sum('total'))['t'] or 0
    print_orders    = PrinterCardOrder.objects.filter(user=user).count()
    customizations  = Customization.objects.filter(user=user).count()

    recent_orders   = Order.objects.filter(user=user).order_by('-created_at')[:5]
    recent_print    = PrinterCardOrder.objects.filter(user=user).order_by('-created_at')[:4]
    recent_custom   = Customization.objects.filter(user=user).select_related('card').order_by('-created_at')[:4]
    cart_items      = CartItem.objects.filter(user=request.user).select_related('card')

    return render(request, 'cards/dashboard.html', {
        'total_orders':   total_orders,
        'total_spent':    total_spent,
        'print_orders':   print_orders,
        'customizations': customizations,
        'recent_orders':  recent_orders,
        'recent_print':   recent_print,
        'recent_custom':  recent_custom,
        'cart_items':     cart_items,
    })


# ── ADMIN UPLOAD COLLECTION ─────────────────────────────────────────────────

from django.contrib.admin.views.decorators import staff_member_required
from django.utils.text import slugify

@staff_member_required
def admin_upload_collection(request):
    cards      = WeddingCard.objects.all().order_by('-created_at')
    categories = Category.objects.all()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_card':
            name        = request.POST.get('name', '').strip()
            category_id = request.POST.get('category')
            description = request.POST.get('description', '')
            palette     = request.POST.get('palette', 'floral')
            ornament    = request.POST.get('ornament', '❦')
            price       = request.POST.get('price', '999')
            is_featured = request.POST.get('is_featured') == 'on'
            image_file  = request.FILES.get('image')

            if name:
                base_slug = slugify(name)
                slug = base_slug
                counter = 1
                while WeddingCard.objects.filter(slug=slug).exists():
                    slug = f'{base_slug}-{counter}'
                    counter += 1

                card = WeddingCard.objects.create(
                    name=name, slug=slug,
                    category_id=category_id if category_id else None,
                    description=description, palette=palette,
                    ornament=ornament, price=price,
                    is_featured=is_featured, is_active=True,
                )
                if image_file:
                    card.image = image_file
                    card.save()
                messages.success(request, f'✅ Card "{name}" added successfully!')
            return redirect('admin_upload_collection')

        elif action == 'add_category':
            cat_name = request.POST.get('cat_name', '').strip()
            if cat_name:
                cat_slug = slugify(cat_name)
                Category.objects.get_or_create(name=cat_name, defaults={'slug': cat_slug})
                messages.success(request, f'Category "{cat_name}" added!')
            return redirect('admin_upload_collection')

        elif action == 'toggle_card':
            card_id = request.POST.get('card_id')
            card = get_object_or_404(WeddingCard, pk=card_id)
            card.is_active = not card.is_active
            card.save()
            messages.success(request, f'Card "{card.name}" {"activated" if card.is_active else "deactivated"}.')
            return redirect('admin_upload_collection')

        elif action == 'toggle_featured':
            card_id = request.POST.get('card_id')
            card = get_object_or_404(WeddingCard, pk=card_id)
            card.is_featured = not card.is_featured
            card.save()
            return redirect('admin_upload_collection')

        elif action == 'delete_card':
            card_id = request.POST.get('card_id')
            card = get_object_or_404(WeddingCard, pk=card_id)
            card_name = card.name
            card.delete()
            messages.success(request, f'Card "{card_name}" deleted.')
            return redirect('admin_upload_collection')

    return render(request, 'cards/admin_upload.html', {
        'cards': cards,
        'categories': categories,
        'palette_choices': WeddingCard.PALETTE_CHOICES,
    })


from django.http import JsonResponse

def search_suggestions(request):
    """AJAX endpoint for nav search live suggestions."""
    q = request.GET.get('q', '').strip()
    if not q or len(q) < 2:
        return JsonResponse({'results': []})
    cards = WeddingCard.objects.filter(
        is_active=True
    ).filter(
        Q(name__icontains=q) | Q(description__icontains=q)
    ).select_related('category').order_by('-is_featured', '-created_at')[:8]

    results = [{
        'name':     c.name,
        'slug':     c.slug,
        'ornament': c.ornament,
        'price':    str(c.price),
        'category': c.category.name if c.category else '',
        'palette':  c.palette,
    } for c in cards]
    return JsonResponse({'results': results})


# ── NAV SEARCH API (live suggestions) ──────────────────────────────────────
from django.http import JsonResponse

def search_api(request):
    """Returns JSON card suggestions for the nav search bar."""
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'results': []})
    cards = WeddingCard.objects.filter(
        is_active=True
    ).filter(
        Q(name__icontains=q) | Q(description__icontains=q) | Q(category__name__icontains=q)
    ).select_related('category')[:8]

    results = []
    for card in cards:
        results.append({
            'id':       card.pk,
            'name':     card.name,
            'slug':     card.slug,
            'ornament': card.ornament,
            'palette':  card.palette,
            'price':    str(card.price),
            'category': card.category.name if card.category else '',
            'image':    card.image.url if card.image else '',
        })
    return JsonResponse({'results': results})


def custom_403(request, exception=None):
    return render(request, '403.html', status=403)


def custom_404(request, exception=None):
    return render(request, '404.html', status=404)


# ── CUSTOM LOGOUT (works on Django 4 + 5, GET and POST) ──────────────────
from django.contrib.auth import logout as auth_logout

def custom_logout(request):
    """Handles logout via GET or POST — compatible with all Django versions."""
    auth_logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


# ── ABOUT US & CONTACT ─────────────────────────────────────────────────────

from django.core.mail import send_mail
from django.conf import settings as django_settings

def about_us(request):
    return render(request, 'cards/about.html')


def contact(request):
    sent = False
    error = None

    if request.method == 'POST':
        name    = request.POST.get('name', '').strip()
        email   = request.POST.get('email', '').strip()
        phone   = request.POST.get('phone', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if not name or not email or not message:
            error = 'Please fill in all required fields.'
        else:
            try:
                full_msg = (
                    f"New contact form submission from Arts By Graphic website\n\n"
                    f"Name:    {name}\n"
                    f"Email:   {email}\n"
                    f"Phone:   {phone or 'Not provided'}\n"
                    f"Subject: {subject or 'General Enquiry'}\n\n"
                    f"Message:\n{message}\n"
                )
                send_mail(
                    subject=f"Contact Form: {subject or 'Enquiry'} from {name}",
                    message=full_msg,
                    from_email=django_settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[django_settings.DEFAULT_FROM_EMAIL],
                    fail_silently=False,
                )
                sent = True
                messages.success(request, f"Thank you {name}! We'll get back to you shortly.")
            except Exception:
                error = 'Message could not be sent. Please call us directly.'

    return render(request, 'cards/contact.html', {'sent': sent, 'error': error})


# ── ABOUT & CONTACT PAGES ──────────────────────────────────────────────────

def about(request):
    return render(request, 'cards/about.html')


def contact(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        # Save to DB or email — for now just show success via JS
        name    = request.POST.get('name', '')
        phone   = request.POST.get('phone', '')
        message = request.POST.get('message', '')
        if name and phone and message:
            # Print to console (can wire to email later)
            print(f"[CONTACT] {name} | {phone} | {message}")
            messages.success(request, f'Thanks {name}! We\'ll contact you on {phone} soon.')
        else:
            messages.error(request, 'Please fill all required fields.')
        return redirect('contact')
    return render(request, 'cards/contact.html', {'categories': categories})
