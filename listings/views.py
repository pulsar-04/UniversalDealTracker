from django.shortcuts import render
from .models import CarListing, Search, JobListing
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .forms import SearchForm
from .models import Search
from django.contrib import messages



def car_list(request):

    if not request.user.is_authenticated:
        return render(request, 'listings/landing.html')


    cars = CarListing.objects.filter(is_active=True).order_by('-date_posted')

    selected_brand = request.GET.get('brand')
    if selected_brand:
        cars = cars.filter(brand=selected_brand)

    brands = CarListing.objects.values_list('brand', flat=True).distinct()

    context = {
        'cars': cars,
        'total_count': cars.count(),
        'brands': brands,
        'selected_brand': selected_brand,
    }
    return render(request, 'listings/car_list.html', context)


@login_required
def job_list(request):
    jobs = JobListing.objects.filter(is_active=True).order_by('-date_posted')

    job_searches = Search.objects.filter(category='job')

    selected_search_id = request.GET.get('search_id')

    if selected_search_id:
        search_obj = get_object_or_404(Search, pk=selected_search_id)
        jobs = jobs.filter(title__icontains=search_obj.title)

    context = {
        'jobs': jobs,
        'total_count': jobs.count(),
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

            form.save()
            messages.success(request, "Успешно добави ново търсене! Роботът ще го обходи скоро.")
            return redirect('dashboard')
    else:
        form = SearchForm()

    # 2. Взимаме всички налични търсения
    searches = Search.objects.all().order_by('-created_at')

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

