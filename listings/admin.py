from django.contrib import admin
from .models import Listing, CarListing, JobListing

@admin.register(CarListing)
class CarListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'brand', 'model', 'price')

@admin.register(JobListing)
class JobListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'company_name', 'is_remote')