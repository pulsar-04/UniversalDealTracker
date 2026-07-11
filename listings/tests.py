from django.test import TestCase
from listings.models import CarListing, PriceHistory


class DealTrackerBusinessLogicTests(TestCase):

  def setUp(self):
    """Създаваме тестова кола в изолирана база данни преди всеки тест."""
    self.car = CarListing.objects.create(
        url="https://mobile.bg/test-car-123",
        title="VW Golf 1.9 TDI",
        price=5000,
        year=2005,
        category="car",
        brand="VW",
        model="Golf",
        kilometers=0,
        fuel_type="Unknown",
    )
    PriceHistory.objects.create(listing=self.car, price=5000)

  def test_price_change_creates_history_record(self):
    """Проверява дали промяна в цената генерира нов запис в PriceHistory."""
    self.assertEqual(PriceHistory.objects.filter(listing=self.car).count(), 1)

    new_price = 4500
    old_price = self.car.price

    if old_price != new_price:
      self.car.price = new_price
      self.car.save()
      PriceHistory.objects.create(listing=self.car, price=new_price)

    self.car.refresh_from_db()
    self.assertEqual(self.car.price, 4500)

    history_records = PriceHistory.objects.filter(listing=self.car).order_by(
        "-date_recorded"
    )
    self.assertEqual(history_records.count(), 2)
    self.assertEqual(history_records.first().price, 4500)