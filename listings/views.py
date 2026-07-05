from .models import CarListing, JobListing
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .forms import SearchForm
from .models import Search
from django.contrib import messages
from django.db.models import Q
from .tasks import auto_crawl_cars, auto_crawl_jobs
from django.core.paginator import Paginator
import json
from listings.tasks import auto_crawl_cars, auto_crawl_jobs
from django.core.management import call_command
import csv
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import CarListing, Search


def landing(request):

    if request.user.is_authenticated:
        return redirect('car_list')

    return render(request, 'listings/landing.html')


@login_required
def car_list(request):
    user_searches = Search.objects.filter(user=request.user, category='car')
    user_brands = user_searches.values_list('brand', flat=True).distinct()

    if user_brands:
        cars = CarListing.objects.filter(is_active=True, brand__in=user_brands).order_by('-date_posted')
    else:
        cars = CarListing.objects.none()

    selected_brand = request.GET.get('brand')
    if selected_brand:
        cars = cars.filter(brand=selected_brand)

    paginator = Paginator(cars, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    is_scanning = user_searches.filter(is_initial_scan_done=False).exists()

    context = {
        'cars': page_obj,
        'total_count': paginator.count,
        'brands': user_brands,
        'selected_brand': selected_brand,
        'is_scanning': is_scanning,
    }
    return render(request, 'listings/car_list.html', context)


@login_required
def job_list(request):
    job_searches = Search.objects.filter(user=request.user, category='job')

    if job_searches.exists():
        jobs = JobListing.objects.filter(is_active=True, search__in=job_searches).order_by('-date_posted')
    else:
        jobs = JobListing.objects.none()

    selected_search_id = request.GET.get('search_id')
    if selected_search_id:
        jobs = jobs.filter(search_id=selected_search_id)

    paginator = Paginator(jobs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    is_scanning = job_searches.filter(is_initial_scan_done=False).exists()
    context = {
        'jobs': page_obj,
        'total_count': paginator.count,
        'job_searches': job_searches,
        'selected_search_id': selected_search_id,
        'is_scanning': is_scanning,
    }
    return render(request, 'listings/job_list.html', context)

def about(request):
    return render(request, 'listings/about.html')


@login_required
def dashboard(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            new_search = form.save(commit=False)
            new_search.user = request.user
            new_search.save()

            messages.success(request, "Успешно добави ново търсене! Роботът започва да сканира в бекграунд. Презареди страницата след малко.")

            try:
                if new_search.category == 'car':
                    auto_crawl_cars.delay()
                elif new_search.category == 'job':
                    auto_crawl_jobs.delay()
            except Exception as e:
                print(f"Грешка при пускане на Celery задача: {e}")

            return redirect('dashboard')
    else:
        form = SearchForm()

    searches = Search.objects.filter(user=request.user).order_by('-created_at')
    active_robots = searches.filter(is_paused=False).count()

    user_cars_count = CarListing.objects.filter(brand__in=searches.values_list('brand', flat=True)).count()
    user_jobs_count = JobListing.objects.filter(search__in=searches).count()
    total_items = user_cars_count + user_jobs_count

    return render(request, 'listings/dashboard.html', {
        'form': form,
        'searches': searches,
        'total_items': total_items,
        'active_robots': active_robots
    })


@login_required
def delete_search(request, pk):
    search = get_object_or_404(Search, pk=pk)

    if search.category == 'car':

        cars_to_delete = CarListing.objects.filter(brand=search.brand)

        if search.model:
            cars_to_delete = cars_to_delete.filter(model=search.model)

        deleted_count = cars_to_delete.count()
        cars_to_delete.delete()
        print(f"🗑️ Изтрити са {deleted_count} коли, свързани с {search.brand}")

    elif search.category == 'job':

        jobs_to_delete = JobListing.objects.filter(title__icontains=search.title)

        deleted_count = jobs_to_delete.count()
        jobs_to_delete.delete()
        print(f"🗑️ Изтрити са {deleted_count} обяви за работа, съдържащи '{search.title}'")

    search.delete()

    messages.success(request, "Търсенето и всички свързани с него обяви бяха изтрити!")
    return redirect('dashboard')


@login_required
def car_detail(request, pk):

    car = get_object_or_404(CarListing, pk=pk)


    history = car.price_history.all().order_by('date_recorded')


    dates = []
    prices = []


    if not history.exists():
        dates.append(car.date_posted.strftime('%d %b %Y'))
        prices.append(float(car.price))
    else:
        for entry in history:
            dates.append(entry.date_recorded.strftime('%d %b %Y'))
            prices.append(float(entry.price))


        if float(car.price) != prices[-1]:
            dates.append('Днес')
            prices.append(float(car.price))

    context = {
        'car': car,

        'chart_dates': json.dumps(dates),
        'chart_prices': json.dumps(prices),
    }
    return render(request, 'listings/car_detail.html', context)


@login_required
def toggle_search_status(request, pk):
    search = get_object_or_404(Search, pk=pk, user=request.user)

    search.is_paused = not search.is_paused
    search.save()

    if search.is_paused:
        messages.warning(request, f"⏸️ Търсенето '{search.title}' е поставено на пауза. Роботът спира да го следи.")
    else:
        messages.success(request, f"▶️ Търсенето '{search.title}' отново е активно! Роботът продължава работа.")

    return redirect('dashboard')


@login_required
def export_cars_csv(request):
    response = HttpResponse(content_type='text/csv')

    response['Content-Disposition'] = 'attachment; filename="my_dealtracker_cars.csv"'
    response.write('\ufeff'.encode('utf8'))

    writer = csv.writer(response)

    writer.writerow(['Марка', 'Модел', 'Година', 'Цена (лв)', 'Линк'])

    user_searches = Search.objects.filter(user=request.user, category='car')
    user_brands = user_searches.values_list('brand', flat=True)

    cars = CarListing.objects.filter(brand__in=user_brands)

    for car in cars:
        writer.writerow([car.brand, car.model, car.year, car.price, car.url])

    return response


@login_required
def export_jobs_csv(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="my_dealtracker_jobs.csv"'

    response.write('\ufeff'.encode('utf8'))

    writer = csv.writer(response)
    writer.writerow(['Позиция', 'Компания', 'Локация', 'Remote', 'Линк'])

    user_searches = Search.objects.filter(user=request.user, category='job')
    jobs = JobListing.objects.filter(search__in=user_searches)

    for job in jobs:
        is_remote_bg = 'Да' if job.is_remote else 'Не'
        writer.writerow([job.title, job.company_name, job.location, is_remote_bg, job.url])

    return response


