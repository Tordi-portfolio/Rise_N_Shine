from django.db import models


class QuoteRequest(models.Model):
    SERVICE_CHOICES = [
        ("standard", "Standard cleaning"),
        ("deep", "Deep cleaning"),
        ("move", "Move-in / move-out cleaning"),
        ("rental", "Short-term rental turnover"),
        ("renovation", "Post-renovation cleaning"),
    ]
    BEDROOM_CHOICES = [("studio", "Studio"), ("1", "1 bedroom"), ("2", "2 bedrooms"),
                       ("3", "3 bedrooms"), ("4", "4 bedrooms"), ("5+", "5 or more")]
    BATHROOM_CHOICES = [("1", "1 bathroom"), ("1.5", "1.5 bathrooms"), ("2", "2 bathrooms"),
                        ("2.5", "2.5 bathrooms"), ("3", "3 bathrooms"), ("4+", "4 or more")]
    FREQUENCY_CHOICES = [("once", "One time"), ("weekly", "Weekly"),
                         ("biweekly", "Every two weeks"), ("monthly", "Monthly")]
    TIME_CHOICES = [("flexible", "Flexible"), ("morning", "Morning"), ("afternoon", "Afternoon")]
    STATUS_CHOICES = [("new", "New"), ("contacted", "Contacted"), ("booked", "Booked"), ("closed", "Closed")]

    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    address = models.CharField("Cleaning address", max_length=200)
    zip_code = models.CharField("ZIP code", max_length=10)

    service = models.CharField(max_length=20, choices=SERVICE_CHOICES, default="standard")
    bedrooms = models.CharField(max_length=10, choices=BEDROOM_CHOICES, default="2")
    bathrooms = models.CharField(max_length=10, choices=BATHROOM_CHOICES, default="2")
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default="once")
    preferred_date = models.DateField(null=True, blank=True)
    preferred_time = models.CharField(max_length=20, choices=TIME_CHOICES, default="flexible")

    has_pets = models.BooleanField("There are pets in the home", default=False)
    inside_oven = models.BooleanField("Inside the oven", default=False)
    inside_fridge = models.BooleanField("Inside the fridge", default=False)
    interior_windows = models.BooleanField("Interior windows", default=False)
    laundry = models.BooleanField("Laundry (wash, dry, fold)", default=False)
    message = models.TextField("Anything else we should know?", blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new", db_index=True)
    staff_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.get_service_display()} ({self.created_at:%Y-%m-%d})"

    @property
    def extras(self):
        pairs = [(self.has_pets, "Pets in home"), (self.inside_oven, "Inside oven"),
                 (self.inside_fridge, "Inside fridge"), (self.interior_windows, "Interior windows"),
                 (self.laundry, "Laundry")]
        return [label for flag, label in pairs if flag]
