from django.contrib import admin
from .models import Listing, CarListing, JobListing, Search  # <-- Добави Search тук

@admin.register(CarListing)
class CarListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'brand', 'model', 'price')

@admin.register(JobListing)
class JobListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'company_name', 'is_remote')

@admin.register(Search)
class SearchAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'created_at')