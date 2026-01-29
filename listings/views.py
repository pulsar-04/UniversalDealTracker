from django.shortcuts import render
from .models import CarListing, Search


def car_list(request):

    cars = CarListing.objects.filter(is_active=True).order_by('-date_posted')



    selected_brand = request.GET.get('brand')

    if selected_brand:
        cars = cars.filter(brand=selected_brand)


    brands = CarListing.objects.values_list('brand', flat=True).distinct()

    context = {
        'cars': cars,
        'total_count': cars.count(),
        'brands': brands,  # Пращаме марките към шаблона
        'selected_brand': selected_brand,  # Пращаме и какво е избрано (за да го оцветим)
    }
    return render(request, 'listings/car_list.html', context)