from django.shortcuts import render
from .models import CarListing, Search, JobListing
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .forms import SearchForm
from .models import Search
from django.contrib import messages
from django.db.models import Q
from .tasks import auto_crawl_cars, auto_crawl_jobs
from django.core.paginator import Paginator



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


    context = {
        'cars': page_obj,
        'total_count': paginator.count,
        'brands': user_brands,
        'selected_brand': selected_brand,
    }
    return render(request, 'listings/car_list.html', context)


@login_required
def job_list(request):
    job_searches = Search.objects.filter(user=request.user, category='job')

    if job_searches.exists():
        query = Q()
        for search in job_searches:
            query |= Q(title__icontains=search.title)

        jobs = JobListing.objects.filter(is_active=True).filter(query).order_by('-date_posted')
    else:
        jobs = JobListing.objects.none()

    selected_search_id = request.GET.get('search_id')
    if selected_search_id:
        search_obj = get_object_or_404(Search, pk=selected_search_id, user=request.user)
        jobs = jobs.filter(title__icontains=search_obj.title)


    paginator = Paginator(jobs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


    context = {
        'jobs': page_obj,
        'total_count': paginator.count,
        'job_searches': job_searches,
        'selected_search_id': selected_search_id,
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

            messages.success(request, "Успешно добави ново търсене! Роботът започва да сканира веднага.")

            if new_search.category == 'car':
                auto_crawl_cars.delay()
            elif new_search.category == 'job':
                auto_crawl_jobs.delay()
            return redirect('dashboard')
    else:
        form = SearchForm()

    searches = Search.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'listings/dashboard.html', {'form': form, 'searches': searches})


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

