from django.shortcuts import render
from .models import CarListing


def car_list(request):

    cars = CarListing.objects.filter(is_active=True).order_by('-date_posted')

    context = {
        'cars': cars,
        'total_count': cars.count()
    }
    return render(request, 'listings/car_list.html', context)
