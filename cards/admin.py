from django.contrib import admin
from .models import Category, WeddingCard, Review, Customization, CartItem, Order, OrderItem, PrinterCardOrder, EmailOTP


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(WeddingCard)
class WeddingCardAdmin(admin.ModelAdmin):
    list_display  = ['name', 'category', 'palette', 'price', 'is_featured', 'is_active', 'created_at']
    list_filter   = ['palette', 'category', 'is_featured', 'is_active']
    list_editable = ['is_featured', 'is_active', 'price']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'card', 'rating', 'created_at']
    list_filter  = ['rating']


@admin.register(Customization)
class CustomizationAdmin(admin.ModelAdmin):
    list_display = ['bride_name', 'groom_name', 'card', 'user', 'font_choice', 'card_style', 'created_at']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['subtotal']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ['id', 'user', 'status', 'total', 'created_at']
    list_filter   = ['status']
    list_editable = ['status']
    inlines       = [OrderItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['user', 'card', 'quantity', 'added_at']


@admin.register(PrinterCardOrder)
class PrinterCardOrderAdmin(admin.ModelAdmin):
    list_display  = ['id', 'card_type', 'primary_name', 'secondary_name', 'phone', 'status', 'created_at']
    list_filter   = ['card_type', 'status']
    list_editable = ['status']
    search_fields = ['primary_name', 'secondary_name', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Card Type & Status', {'fields': ('card_type', 'status', 'user')}),
        ('Primary Person (Bride/Groom)', {'fields': ('primary_name', 'primary_father_name', 'primary_dada_name', 'primary_address')}),
        ('Secondary Person', {'fields': ('secondary_name', 'secondary_father_name', 'secondary_address')}),
        ('Engagement', {'fields': ('sagaai_date', 'sagaai_time', 'sagaai_preetibhoj')}),
        ('Wedding (Bride)', {'fields': ('shaadi_date', 'barat_swagat', 'shaadi_preetibhoj', 'vivah_sthal')}),
        ('Wedding (Groom)', {'fields': ('ghudchadi_time', 'barat_prasthan', 'barat_destination', 'reception_date', 'reception_preetibhoj', 'reception_sthal')}),
        ('Other Details', {'fields': ('extra_info', 'bal_aakanksha', 'darshanaabhilashi', 'vineet', 'phone')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display  = ['email', 'otp', 'is_verified', 'created_at', 'expires_at']
    list_filter   = ['is_verified']
    search_fields = ['email']
    readonly_fields = ['created_at']
