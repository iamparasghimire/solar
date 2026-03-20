from django.contrib import admin

from .models import Cart, CartItem, Order, OrderItem, WarrantyDocument


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('unit_price', 'line_total')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_items', 'grand_total', 'updated_at')
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'sku', 'unit_price', 'quantity',
                       'include_installation', 'installation_fee', 'line_total')


class WarrantyInline(admin.TabularInline):
    model = WarrantyDocument
    extra = 0
    fk_name = 'order_item'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'status', 'payment_status', 'grand_total', 'payment_method', 'created_at')
    list_filter = ('status', 'payment_method', 'payment_status')
    search_fields = ('order_number', 'user__email', 'coupon_code')
    readonly_fields = ('order_number', 'coupon_code', 'discount_amount', 'created_at', 'updated_at',
                       'cancelled_at', 'cancellation_reason')
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_name', 'quantity', 'unit_price')
    inlines = [WarrantyInline]
