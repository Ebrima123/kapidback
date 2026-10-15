from decimal import Decimal

from django.conf import settings
from django.db import models


class TimeStamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class Source(models.TextChoices):
    WEBSITE = "website", "Website"
    REFERRAL = "referral", "Referral"
    PHONE = "phone", "Phone"
    SOCIAL = "social", "Social media"
    OTHER = "other", "Other"


class Customer(TimeStamped):
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80, blank=True)
    company = models.CharField(max_length=120, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=80, blank=True)
    postcode = models.CharField(max_length=20, blank=True)
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.WEBSITE)

    class Meta(TimeStamped.Meta):
        pass

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return self.full_name


class Lead(TimeStamped):
    class Status(models.TextChoices):
        NEW = "new", "New"
        CONTACTED = "contacted", "Contacted"
        QUOTED = "quoted", "Quoted"
        WON = "won", "Won"
        LOST = "lost", "Lost"

    class PropertyType(models.TextChoices):
        RESIDENTIAL = "residential", "Residential"
        COMMERCIAL = "commercial", "Commercial"

    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    address = models.CharField(max_length=255, blank=True)
    service = models.CharField(max_length=120, blank=True)
    property_type = models.CharField(
        max_length=20, choices=PropertyType.choices, default=PropertyType.RESIDENTIAL
    )
    message = models.TextField(blank=True)
    preferred_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.WEBSITE)
    estimated_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    customer = models.ForeignKey(
        Customer, null=True, blank=True, related_name="leads", on_delete=models.SET_NULL
    )

    class Meta(TimeStamped.Meta):
        pass

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"


class Job(TimeStamped):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        IN_PROGRESS = "in_progress", "In progress"
        ON_HOLD = "on_hold", "On hold"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    customer = models.ForeignKey(Customer, related_name="jobs", on_delete=models.CASCADE)
    lead = models.ForeignKey(Lead, null=True, blank=True, related_name="jobs", on_delete=models.SET_NULL)
    title = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    assigned_to = models.CharField(max_length=120, blank=True)

    class Meta(TimeStamped.Meta):
        pass

    def __str__(self):
        return self.title


class Estimate(TimeStamped):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SENT = "sent", "Sent"
        ACCEPTED = "accepted", "Accepted"
        DECLINED = "declined", "Declined"

    number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    customer = models.ForeignKey(
        Customer, null=True, blank=True, related_name="estimates", on_delete=models.SET_NULL
    )
    lead = models.ForeignKey(
        Lead, null=True, blank=True, related_name="estimates", on_delete=models.SET_NULL
    )
    job = models.ForeignKey(Job, null=True, blank=True, related_name="estimates", on_delete=models.SET_NULL)
    title = models.CharField(max_length=160, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    issue_date = models.DateField(null=True, blank=True)
    valid_until = models.DateField(null=True, blank=True)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0"))
    notes = models.TextField(blank=True)

    class Meta(TimeStamped.Meta):
        pass

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.number:
            self.number = f"EST-{self.pk:05d}"
            super().save(update_fields=["number"])

    @property
    def subtotal(self):
        return sum((i.line_total for i in self.items.all()), Decimal("0"))

    @property
    def tax(self):
        return (self.subtotal * self.tax_rate / Decimal("100")).quantize(Decimal("0.01"))

    @property
    def total(self):
        return self.subtotal + self.tax

    def __str__(self):
        return self.number


class EstimateItem(models.Model):
    estimate = models.ForeignKey(Estimate, related_name="items", on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("1"))
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    @property
    def line_total(self):
        return (self.quantity * self.unit_price).quantize(Decimal("0.01"))


class Note(models.Model):
    customer = models.ForeignKey(
        Customer, null=True, blank=True, related_name="notes", on_delete=models.CASCADE
    )
    lead = models.ForeignKey(Lead, null=True, blank=True, related_name="notes", on_delete=models.CASCADE)
    job = models.ForeignKey(Job, null=True, blank=True, related_name="notes", on_delete=models.CASCADE)
    body = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.body[:50]
