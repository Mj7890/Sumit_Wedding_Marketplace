from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class WeddingCard(models.Model):
    PALETTE_CHOICES = [
        ('floral',    'Blush Floral'),
        ('botanical', 'Forest Botanical'),
        ('gold',      'Midnight Gold'),
        ('minimal',   'Soft Minimal'),
        ('classic',   'Classic Purple'),
        ('rustic',    'Earthy Rustic'),
    ]

    name        = models.CharField(max_length=200)
    slug        = models.SlugField(unique=True)
    category    = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='cards')
    description = models.TextField(blank=True)
    palette     = models.CharField(max_length=20, choices=PALETTE_CHOICES, default='floral')
    ornament    = models.CharField(max_length=10, default='❦')
    price       = models.DecimalField(max_digits=8, decimal_places=2)
    image       = models.ImageField(upload_to='card_images/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('card_detail', kwargs={'slug': self.slug})

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return 0


class Review(models.Model):
    card       = models.ForeignKey(WeddingCard, on_delete=models.CASCADE, related_name='reviews')
    user       = models.ForeignKey(User, on_delete=models.CASCADE)
    rating     = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('card', 'user')

    def __str__(self):
        return f'{self.user.username} – {self.card.name} ({self.rating}★)'


class Customization(models.Model):
    FONT_CHOICES = [
        ('cormorant', 'Cormorant Garamond'),
        ('jost',      'Jost'),
        ('georgia',   'Georgia'),
    ]
    STYLE_CHOICES = [
        ('portrait',  'Portrait'),
        ('landscape', 'Landscape'),
        ('square',    'Square'),
    ]

    user         = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customizations')
    card         = models.ForeignKey(WeddingCard, on_delete=models.CASCADE, related_name='customizations')
    bride_name   = models.CharField(max_length=100)
    groom_name   = models.CharField(max_length=100)
    wedding_date = models.CharField(max_length=100)
    venue        = models.CharField(max_length=200, blank=True)
    font_choice  = models.CharField(max_length=20, choices=FONT_CHOICES, default='cormorant')
    card_style   = models.CharField(max_length=20, choices=STYLE_CHOICES, default='portrait')
    palette      = models.CharField(max_length=20, default='floral')
    ornament     = models.CharField(max_length=10, default='❦')
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.bride_name} & {self.groom_name} – {self.card.name}'


class CartItem(models.Model):
    user          = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    card          = models.ForeignKey(WeddingCard, on_delete=models.CASCADE)
    customization = models.ForeignKey(Customization, on_delete=models.SET_NULL, null=True, blank=True)
    quantity      = models.PositiveIntegerField(default=1)
    added_at      = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} – {self.card.name}'

    @property
    def subtotal(self):
        return self.card.price * self.quantity


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending',    'Pending'),
        ('confirmed',  'Confirmed'),
        ('processing', 'Processing'),
        ('delivered',  'Delivered'),
        ('cancelled',  'Cancelled'),
    ]

    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total      = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Order #{self.pk} – {self.user.username}'


class OrderItem(models.Model):
    order         = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    card          = models.ForeignKey(WeddingCard, on_delete=models.CASCADE)
    customization = models.ForeignKey(Customization, on_delete=models.SET_NULL, null=True, blank=True)
    quantity      = models.PositiveIntegerField(default=1)
    price         = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f'{self.card.name} x{self.quantity}'

    @property
    def subtotal(self):
        return self.price * self.quantity


class PrinterCardOrder(models.Model):
    """Stores filled Dhananjay Printer card form data submitted by users."""

    CARD_TYPE_CHOICES = [
        ('bride', 'लड़की का कार्ड (Bride)'),
        ('groom', 'लड़के का कार्ड (Groom)'),
    ]
    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('confirmed', 'Confirmed'),
        ('printed',   'Printed'),
        ('delivered', 'Delivered'),
    ]

    user      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='printer_orders', null=True, blank=True)
    card_type = models.CharField(max_length=10, choices=CARD_TYPE_CHOICES)
    status    = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # ── Primary person (bride/groom) ──
    primary_name        = models.CharField(max_length=150, verbose_name='लड़की/लड़के का नाम')
    primary_father_name = models.CharField(max_length=150, verbose_name='पिता का नाम')
    primary_dada_name   = models.CharField(max_length=150, blank=True, verbose_name='दादा का नाम')
    primary_address     = models.TextField(verbose_name='पता')

    # ── Secondary person (groom/bride) ──
    secondary_name        = models.CharField(max_length=150, verbose_name='लड़के/लड़की का नाम')
    secondary_father_name = models.CharField(max_length=150, verbose_name='पिता का नाम')
    secondary_address     = models.TextField(verbose_name='पता')

    # ── Engagement ──
    sagaai_date     = models.CharField(max_length=100, blank=True, verbose_name='सगाई की तारीख')
    sagaai_time     = models.CharField(max_length=50,  blank=True, verbose_name='सगाई का समय')
    sagaai_preetibhoj = models.CharField(max_length=100, blank=True, verbose_name='सगाई प्रीतिभोज')

    # ── Wedding ──
    shaadi_date     = models.CharField(max_length=100, blank=True, verbose_name='शादी की तारीख')

    # Bride-specific
    barat_swagat    = models.CharField(max_length=100, blank=True, verbose_name='बारात स्वागत')
    shaadi_preetibhoj = models.CharField(max_length=100, blank=True, verbose_name='शादी प्रीतिभोज')
    vivah_sthal     = models.TextField(blank=True, verbose_name='विवाह स्थल')

    # Groom-specific
    ghudchadi_time  = models.CharField(max_length=100, blank=True, verbose_name='घुड़चढ़ी का समय')
    barat_prasthan  = models.CharField(max_length=100, blank=True, verbose_name='बारात प्रस्थान')
    barat_destination = models.TextField(blank=True, verbose_name='बारात कहाँ जाएगी')
    reception_date  = models.CharField(max_length=100, blank=True, verbose_name='रिशेप्शन की तारीख')
    reception_preetibhoj = models.CharField(max_length=100, blank=True, verbose_name='रिशेप्शन प्रीतिभोज')
    reception_sthal = models.CharField(max_length=150, blank=True, verbose_name='रिशेप्शन स्थल')

    # ── Common ──
    extra_info      = models.TextField(blank=True, verbose_name='अतिरिक्त जानकारी')
    bal_aakanksha   = models.CharField(max_length=200, blank=True, verbose_name='बाल आकांक्षा')
    phone           = models.CharField(max_length=20, blank=True, verbose_name='फोन नं.')
    darshanaabhilashi = models.CharField(max_length=150, blank=True, verbose_name='दर्शनाभिलाषी')
    vineet          = models.CharField(max_length=150, blank=True, verbose_name='विनीत')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Printer Card Order'
        verbose_name_plural = 'Printer Card Orders'

    def __str__(self):
        return f'{self.get_card_type_display()} – {self.primary_name} & {self.secondary_name}'


import random
import string
from django.utils import timezone
from datetime import timedelta

class EmailOTP(models.Model):
    """Stores OTP codes for email verification during registration."""
    email      = models.EmailField(unique=True)
    otp        = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)
    expires_at  = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at

    @classmethod
    def generate_otp(cls, email):
        otp_code = ''.join(random.choices(string.digits, k=6))
        obj, _ = cls.objects.update_or_create(
            email=email,
            defaults={
                'otp': otp_code,
                'is_verified': False,
                'expires_at': timezone.now() + timedelta(minutes=10),
            }
        )
        return otp_code

    def __str__(self):
        return f'{self.email} — {self.otp} ({"verified" if self.is_verified else "pending"})'
