from django.db import models

class Listing(models.Model):
    CATEGORY_CHOICES = [
        ('car', 'Car'),
        ('job', 'Job'),
    ]
    title = models.CharField(max_length=200, verbose_name="Заглавие")
    url = models.URLField(unique=True, verbose_name="Линк")
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Цена")
    date_posted = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class CarListing(Listing):
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    kilometers = models.PositiveIntegerField()
    fuel_type = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Обява за Кола"

class JobListing(Listing):
    company_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_remote = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Обява за Работа"
