from django.contrib import admin
from .models import Restaurant, Table, MenuItem, Review

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'city', 'cuisine_type', 'price_range', 'rating', 'is_active')
    list_filter = ('is_active', 'is_featured', 'cuisine_type', 'city', 'price_range')
    search_fields = ('name', 'description', 'address', 'city', 'state', 'cuisine_type')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'owner', 'description', 'cuisine_type', 'price_range', 'image')
        }),
        ('Contact Details', {
            'fields': ('phone', 'email', 'website')
        }),
        ('Location', {
            'fields': ('address', 'city', 'state', 'country', 'postal_code')
        }),
        ('Operating Hours', {
            'fields': ('opening_time', 'closing_time')
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured', 'rating')
        }),
        ('System Fields', {
            'classes': ('collapse',),
            'fields': ('slug', 'created_at', 'updated_at')
        }),
    )
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at', 'rating')
    save_on_top = True
    ordering = ('-created_at',)

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'table_number', 'capacity', 'status', 'created_at')
    list_filter = ('status', 'capacity', 'created_at')
    search_fields = ('restaurant__name', 'table_number')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'category', 'price', 'is_available', 'created_at')
    list_filter = ('is_available', 'category', 'created_at')
    search_fields = ('name', 'description', 'restaurant__name')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('restaurant__name', 'user__email', 'comment')
    readonly_fields = ('created_at', 'updated_at')
